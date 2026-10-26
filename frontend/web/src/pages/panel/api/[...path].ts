/**
 * Proxy del editor: /panel/api/<recurso>/[<id>/] → backend /api/v1/<recurso>/[<id>/]
 * - Agrega el token de la sesión (cookie HttpOnly); el navegador nunca lo ve.
 * - Solo permite los recursos de contenido de la página.
 * - Después de cada cambio borra la caché de contenido para que el sitio público se actualice.
 */
import type { APIRoute } from "astro";
import { clear_content_cache, relative_media_urls } from "../../../lib/content_api";
import { backend_request, get_session_token } from "../../../lib/panel_api";

const allowed_resources = new Set([
  "site_settings",
  "hero_section",
  "hero_highlights",
  "about_section",
  "company_values",
  "team_section",
  "team_members",
  "services_section",
  "services",
  "service_features",
  "data_capabilities_section",
  "data_capabilities",
  "technologies_section",
  "technologies",
  "clients_section",
  "clients",
  "testimonials",
  "certifications",
  "contact_section",
  "contact_messages",
  "media_files",
]);
const path_pattern = /^([a-z_]+)\/(\d+\/)?$/;
const max_body_bytes = 8 * 1024 * 1024;

const json = (body: unknown, status: number) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });

const handler: APIRoute = async ({ params, request, cookies, url }) => {
  const path = `${params.path ?? ""}${(params.path ?? "").endsWith("/") ? "" : "/"}`;
  const match = path.match(path_pattern);
  if (!match || !allowed_resources.has(match[1])) return json({ detail: "Recurso no permitido." }, 404);

  const token = get_session_token(cookies);
  if (!token) return json({ detail: "Sesión no iniciada." }, 401);

  const is_write = request.method !== "GET" && request.method !== "HEAD";
  if (is_write) {
    // Protección CSRF: solo el editor (mismo origen, cabecera propia) puede escribir
    const fetch_site = request.headers.get("sec-fetch-site");
    if (request.headers.get("x-panel-request") !== "1" || (fetch_site && fetch_site !== "same-origin")) {
      return json({ detail: "Solicitud rechazada." }, 403);
    }
  }

  const headers = new Headers();
  const content_type = request.headers.get("content-type");
  if (content_type) headers.set("Content-Type", content_type);
  let body: ArrayBuffer | undefined;
  if (is_write && request.method !== "DELETE") {
    body = await request.arrayBuffer();
    if (body.byteLength > max_body_bytes) return json({ detail: "El archivo es demasiado grande." }, 413);
  }

  let upstream: Response;
  try {
    upstream = await backend_request(token, `${path}${url.search}`, { method: request.method, headers, body });
  } catch {
    return json({ detail: "No se pudo conectar con el backend." }, 502);
  }

  if (is_write && upstream.ok) clear_content_cache();
  if (upstream.status === 204) return new Response(null, { status: 204 });
  const data = await upstream.json().catch(() => ({ detail: `Error ${upstream.status}` }));
  return json(relative_media_urls(data), upstream.status);
};

export const GET = handler;
export const POST = handler;
export const PATCH = handler;
export const PUT = handler;
export const DELETE = handler;
