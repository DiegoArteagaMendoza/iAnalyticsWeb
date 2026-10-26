/**
 * Recibe el formulario de contacto y lo reenvía al backend (POST /api/v1/contact_messages/).
 * - Con JavaScript: JSON → responde JSON { status }.
 * - Sin JavaScript: formulario normal → redirige a la página con ?contact=<estado>#contacto.
 * El backend queda en la red interna: el navegador nunca habla directo con él.
 */
import type { APIRoute } from "astro";
import { backend_url } from "../../lib/content_api";
import { home_path, is_language } from "../../lib/i18n";

const allowed_fields = ["full_name", "company", "email", "phone", "service_of_interest", "message", "language", "website"];

// Detrás de un proxy (nginx, Caddy) todas las visitas llegan desde la IP del proxy.
// Con TRUST_FORWARDED_FOR=true se usa la IP del visitante que el proxy envía en X-Forwarded-For.
// Activarlo solo si el frontend no es accesible directamente desde internet.
const trust_forwarded_for = process.env.TRUST_FORWARDED_FOR === "true";

function visitor_address(request: Request, client_address: string): string {
  if (trust_forwarded_for) {
    const forwarded = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim();
    if (forwarded) return forwarded;
  }
  return client_address;
}

type SubmissionStatus = "sent" | "invalid" | "rate_limited" | "error";

async function read_payload(request: Request): Promise<Record<string, string>> {
  const content_type = request.headers.get("content-type") ?? "";
  const raw: Record<string, unknown> = content_type.includes("application/json")
    ? await request.json()
    : Object.fromEntries(await request.formData());
  return Object.fromEntries(
    allowed_fields.filter((field) => typeof raw[field] === "string").map((field) => [field, String(raw[field]).trim()]),
  );
}

export const POST: APIRoute = async ({ request, clientAddress, redirect }) => {
  const wants_json = (request.headers.get("accept") ?? "").includes("application/json");
  let payload: Record<string, string> = {};
  let status: SubmissionStatus = "error";
  let errors: unknown = undefined;

  try {
    payload = await read_payload(request);
    const response = await fetch(`${backend_url}/api/v1/contact_messages/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        // Para que el límite de envíos del backend se aplique por visitante y no al frontend
        "X-Forwarded-For": visitor_address(request, clientAddress),
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(8000),
    });
    if (response.ok) status = "sent";
    else if (response.status === 429) status = "rate_limited";
    else if (response.status === 400) {
      status = "invalid";
      errors = await response.json().catch(() => undefined);
    }
  } catch (error) {
    console.error("[api/contact] No se pudo enviar el mensaje:", (error as Error).message);
  }

  if (wants_json) {
    const http_status = { sent: 201, invalid: 400, rate_limited: 429, error: 502 }[status];
    return new Response(JSON.stringify({ status, errors }), {
      status: http_status,
      headers: { "Content-Type": "application/json" },
    });
  }
  const language = is_language(payload.language) ? payload.language : "es";
  return redirect(`${home_path(language)}?contact=${status}#contacto`, 303);
};
