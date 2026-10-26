/**
 * Sirve las imágenes subidas desde el panel (/media/...) pidiéndolas al backend interno.
 * Así el sitio funciona con un solo dominio y el backend no necesita estar expuesto.
 */
import type { APIRoute } from "astro";
import { backend_url } from "../../lib/content_api";

const passthrough_headers = ["content-type", "content-length", "last-modified", "etag"];

export const GET: APIRoute = async ({ params, request }) => {
  const path = params.path ?? "";
  if (!path || path.split("/").some((segment) => segment === ".." || segment === "")) {
    return new Response("Not found", { status: 404 });
  }

  try {
    const upstream = await fetch(`${backend_url}/media/${path.split("/").map(encodeURIComponent).join("/")}`, {
      headers: { "If-None-Match": request.headers.get("if-none-match") ?? "", "If-Modified-Since": request.headers.get("if-modified-since") ?? "" },
      signal: AbortSignal.timeout(10000),
    });
    if (upstream.status === 304) return new Response(null, { status: 304 });
    if (!upstream.ok || !upstream.body) return new Response("Not found", { status: 404 });

    const headers = new Headers({ "Cache-Control": "public, max-age=3600", "X-Content-Type-Options": "nosniff" });
    for (const name of passthrough_headers) {
      const value = upstream.headers.get(name);
      if (value) headers.set(name, value);
    }
    return new Response(upstream.body, { status: 200, headers });
  } catch {
    return new Response("Backend unavailable", { status: 502 });
  }
};
