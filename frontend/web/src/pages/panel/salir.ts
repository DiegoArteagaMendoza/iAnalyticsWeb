/** Cierra la sesión del panel: invalida el token en el backend y borra la cookie. */
import type { APIRoute } from "astro";
import { clear_session, get_session_token, logout } from "../../lib/panel_api";

export const POST: APIRoute = async ({ cookies, redirect }) => {
  const token = get_session_token(cookies);
  if (token) await logout(token);
  clear_session(cookies, token);
  return redirect("/panel/ingresar", 303);
};

export const GET: APIRoute = ({ redirect }) => redirect("/panel/", 302);
