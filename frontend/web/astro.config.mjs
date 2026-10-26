// @ts-check
import node from "@astrojs/node";
import { defineConfig } from "astro/config";

// Renderizado en el servidor: cada visita usa el contenido actual del backend (con caché corto).
export default defineConfig({
  site: process.env.PUBLIC_SITE_URL || "https://ianalytics.cl",
  output: "server",
  adapter: node({ mode: "standalone" }),
  trailingSlash: "ignore",
  compressHTML: true,
  server: { host: true, port: 4321 },
  build: { inlineStylesheets: "auto" },
});
