/**
 * - Idioma: en "/" redirige a "/en/" si el visitante prefiere inglés (cookie o navegador).
 *   Los enlaces del selector (?lang=xx) guardan la preferencia en una cookie.
 * - Panel (/panel/): exige una sesión válida, salvo en la página de ingreso.
 * - Agrega cabeceras de seguridad a todas las respuestas.
 */
import { defineMiddleware } from "astro:middleware";
import { home_path, is_language, language_cookie, language_from_accept_header, type Language } from "./lib/i18n";
import { clear_session, get_session_token, get_session_user } from "./lib/panel_api";

const one_year_seconds = 60 * 60 * 24 * 365;

const security_headers: Record<string, string> = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
};

const panel_public_paths = new Set(["/panel/ingresar", "/panel/ingresar/"]);

export const onRequest = defineMiddleware(async (context, next) => {
  const { url, cookies, request, redirect, locals } = context;
  const is_home = url.pathname === "/" || url.pathname === "/en" || url.pathname === "/en/";
  const is_panel = url.pathname === "/panel" || url.pathname.startsWith("/panel/");
  const is_panel_api = url.pathname.startsWith("/panel/api/");

  if (is_home && request.method === "GET") {
    const requested = url.searchParams.get("lang");
    if (is_language(requested)) {
      cookies.set(language_cookie, requested, { path: "/", maxAge: one_year_seconds, sameSite: "lax" });
      return redirect(home_path(requested), 302);
    }

    if (url.pathname === "/") {
      const saved = cookies.get(language_cookie)?.value;
      const preferred: Language = is_language(saved) ? saved : language_from_accept_header(request.headers.get("accept-language"));
      if (preferred !== "es") {
        const target = new URL(home_path(preferred), url);
        target.search = url.search;
        return redirect(target.pathname + target.search, 302);
      }
    }
  }

  // Las páginas del panel requieren sesión (la API del panel responde 401 por su cuenta)
  if (is_panel && !is_panel_api && !panel_public_paths.has(url.pathname)) {
    const token = get_session_token(cookies);
    const user = token ? await get_session_user(token) : null;
    if (!token || !user) {
      clear_session(cookies, token);
      const next_path = url.pathname === "/panel/vista_previa" ? "/panel/editar" : url.pathname;
      return redirect(`/panel/ingresar?next=${encodeURIComponent(next_path)}`, 302);
    }
    locals.panel_user = user;
    locals.panel_token = token;
  }

  const response = await next();
  for (const [name, value] of Object.entries(security_headers)) {
    if (!response.headers.has(name)) response.headers.set(name, value);
  }
  if (is_home) {
    response.headers.append("Vary", "Accept-Language, Cookie");
    // Siempre se revalida: el contenido cambia cuando se edita en el panel
    if (!response.headers.has("Cache-Control")) response.headers.set("Cache-Control", "no-cache");
  }
  if (is_panel) {
    response.headers.set("Cache-Control", "no-store");
    response.headers.set("X-Robots-Tag", "noindex, nofollow");
    if (url.pathname.startsWith("/panel/vista_previa")) {
      // La vista previa se muestra dentro del panel (iframe del mismo sitio)
      response.headers.set("X-Frame-Options", "SAMEORIGIN");
      response.headers.set("Content-Security-Policy", "frame-ancestors 'self'");
    }
  }
  return response;
});
