/// <reference types="astro/client" />

declare namespace App {
  interface Locals {
    /** Usuario del panel (/panel/), definido por el middleware cuando hay sesión válida */
    panel_user?: import("./lib/panel_api").PanelUser;
    panel_token?: string;
  }
}
