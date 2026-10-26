/**
 * Sesión del panel de administración (/panel/).
 * El token del backend se guarda en una cookie HttpOnly: el JavaScript del navegador
 * nunca lo ve; las llamadas del editor pasan por /panel/api/..., que lo agrega.
 */
import type { AstroCookies } from "astro";
import { backend_url } from "./content_api";

export const session_cookie = "panel_session";
const session_hours = Number(process.env.PANEL_SESSION_HOURS ?? 12);
const me_cache_seconds = 60;

export interface PanelUser {
  username: string;
  email: string;
  full_name: string;
  is_superuser: boolean;
}

/** Dirección pública del admin de Django (para "Gestionar usuarios"). */
export const django_admin_url = (process.env.DJANGO_ADMIN_PUBLIC_URL || "http://localhost:8000/admin/").replace(/\/?$/, "/");

const me_cache = new Map<string, { user: PanelUser; expires_at: number }>();

function use_secure_cookie(url: URL): boolean {
  if (process.env.PANEL_SECURE_COOKIE) return process.env.PANEL_SECURE_COOKIE === "true";
  return url.protocol === "https:" || (process.env.PUBLIC_SITE_URL ?? "").startsWith("https://");
}

export function get_session_token(cookies: AstroCookies): string | undefined {
  return cookies.get(session_cookie)?.value || undefined;
}

export function save_session(cookies: AstroCookies, url: URL, token: string): void {
  cookies.set(session_cookie, token, {
    path: "/panel",
    httpOnly: true,
    sameSite: "strict",
    secure: use_secure_cookie(url),
    maxAge: session_hours * 60 * 60,
  });
}

export function clear_session(cookies: AstroCookies, token?: string): void {
  if (token) me_cache.delete(token);
  cookies.delete(session_cookie, { path: "/panel" });
}

/** Llamada al backend con el token de la sesión. `path` es relativo a /api/v1/. */
export function backend_request(token: string, path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Token ${token}`);
  if (!headers.has("Accept")) headers.set("Accept", "application/json");
  return fetch(`${backend_url}/api/v1/${path}`, { ...init, headers, signal: init.signal ?? AbortSignal.timeout(15000) });
}

export async function login(
  username: string,
  password: string,
  visitor_address: string,
): Promise<{ token: string; user: PanelUser } | { error: string }> {
  try {
    const response = await fetch(`${backend_url}/api/v1/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json", "X-Forwarded-For": visitor_address },
      body: JSON.stringify({ username, password }),
      signal: AbortSignal.timeout(8000),
    });
    if (response.status === 429) return { error: "Demasiados intentos. Espere un minuto e intente nuevamente." };
    if (!response.ok) return { error: "Usuario o contraseña incorrectos." };
    const data = await response.json();
    me_cache.set(data.token, { user: data.user, expires_at: Date.now() + me_cache_seconds * 1000 });
    return data;
  } catch {
    return { error: "No se pudo conectar con el servidor. Intente nuevamente." };
  }
}

export async function logout(token: string): Promise<void> {
  me_cache.delete(token);
  await backend_request(token, "auth/logout/", { method: "POST" }).catch(() => undefined);
}

/** Usuario de la sesión, o null si el token no es válido o venció. */
export async function get_session_user(token: string): Promise<PanelUser | null> {
  const cached = me_cache.get(token);
  if (cached && cached.expires_at > Date.now()) return cached.user;
  try {
    const response = await backend_request(token, "auth/me/", { signal: AbortSignal.timeout(5000) });
    if (!response.ok) {
      me_cache.delete(token);
      return null;
    }
    const user = (await response.json()) as PanelUser;
    me_cache.set(token, { user, expires_at: Date.now() + me_cache_seconds * 1000 });
    return user;
  } catch {
    return null;
  }
}
