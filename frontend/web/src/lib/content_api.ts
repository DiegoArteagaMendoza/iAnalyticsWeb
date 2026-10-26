/**
 * Obtiene el contenido de la página desde el backend (GET /api/v1/page_content/?lang=xx).
 * - Guarda cada idioma en memoria unos segundos (CONTENT_CACHE_SECONDS) para no
 *   consultar el backend en cada visita.
 * - Si el backend no responde, usa la última copia en memoria o, si no hay,
 *   el contenido de respaldo del archivo de idioma (src/i18n/<idioma>.json).
 */
import { get_fallback_content, type Language } from "./i18n";
import type { PageContent } from "./types";

export const backend_url = (process.env.BACKEND_INTERNAL_URL || "http://localhost:8000").replace(/\/$/, "");
const cache_seconds = Number(process.env.CONTENT_CACHE_SECONDS ?? 30);
const request_timeout_ms = Number(process.env.BACKEND_TIMEOUT_MS ?? 3000);

type CacheEntry = { content: PageContent; expires_at: number };
const content_cache = new Map<Language, CacheEntry>();

export type ContentResult = { content: PageContent; source: "backend" | "cache" | "fallback" };

/** Borra la copia en memoria (después de editar en el panel, para que el cambio se vea al tiro). */
export function clear_content_cache(): void {
  content_cache.clear();
}

/** Las URLs absolutas de archivos del backend pasan a /media/..., que el frontend sirve como proxy. */
export function relative_media_urls<T>(value: T): T {
  if (typeof value === "string") {
    const match = value.match(/^https?:\/\/[^/]+(\/media\/.*)$/);
    return (match ? match[1] : value) as T;
  }
  if (Array.isArray(value)) return value.map(relative_media_urls) as T;
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, relative_media_urls(item)])) as T;
  }
  return value;
}

/** Sin backend no hay archivos subidos: se quitan para que se usen los logos incluidos en el sitio. */
function without_media_urls<T>(value: T): T {
  if (typeof value === "string") return (value.startsWith("/media/") ? "" : value) as T;
  if (Array.isArray(value)) return value.map(without_media_urls) as T;
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, without_media_urls(item)])) as T;
  }
  return value;
}

/**
 * Contenido para el editor del panel: incluye lo no publicado y las secciones ocultas.
 * No usa caché ni respaldo: si el backend falla, el editor muestra el error.
 */
export async function get_preview_content(language: Language, token: string): Promise<PageContent> {
  const response = await fetch(`${backend_url}/api/v1/page_content/?lang=${language}&preview=1`, {
    headers: { Accept: "application/json", Authorization: `Token ${token}` },
    signal: AbortSignal.timeout(request_timeout_ms * 2),
  });
  if (!response.ok) throw new Error(`El backend respondió ${response.status}`);
  const { language: _language, available_languages: _available, is_preview: _preview, ...data } = await response.json();
  return relative_media_urls(data) as PageContent;
}

export async function get_page_content(language: Language): Promise<ContentResult> {
  const cached = content_cache.get(language);
  if (cached && cached.expires_at > Date.now()) {
    return { content: cached.content, source: "cache" };
  }

  try {
    const response = await fetch(`${backend_url}/api/v1/page_content/?lang=${language}`, {
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(request_timeout_ms),
    });
    if (!response.ok) throw new Error(`El backend respondió ${response.status}`);
    const { language: _language, available_languages: _available, ...data } = await response.json();
    const content = relative_media_urls(data) as PageContent;
    content_cache.set(language, { content, expires_at: Date.now() + cache_seconds * 1000 });
    return { content, source: "backend" };
  } catch (error) {
    console.warn(`[content_api] Contenido de respaldo para "${language}":`, (error as Error).message);
    if (cached) return { content: cached.content, source: "cache" };
    return { content: without_media_urls(get_fallback_content(language)), source: "fallback" };
  }
}
