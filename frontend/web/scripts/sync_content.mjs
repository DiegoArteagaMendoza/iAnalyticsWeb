/**
 * Actualiza la sección "content" de los archivos de idioma (src/i18n/es.json y en.json)
 * con el contenido publicado en el backend, incluidas sus traducciones automáticas.
 * La sección "ui" (textos de la interfaz) no se modifica.
 *
 *   BACKEND_INTERNAL_URL=http://localhost:8000 npm run sync_content
 */
import { readFile, writeFile } from "node:fs/promises";

const backend_url = (process.env.BACKEND_INTERNAL_URL || "http://localhost:8000").replace(/\/$/, "");
const languages = ["es", "en"];

/** Convierte las URLs absolutas de archivos subidos en rutas relativas (/media/...). */
function relative_media_urls(value) {
  if (typeof value === "string") {
    const match = value.match(/^https?:\/\/[^/]+(\/media\/.*)$/);
    return match ? match[1] : value;
  }
  if (Array.isArray(value)) return value.map(relative_media_urls);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, relative_media_urls(item)]));
  }
  return value;
}

for (const language of languages) {
  const response = await fetch(`${backend_url}/api/v1/page_content/?lang=${language}`);
  if (!response.ok) {
    console.error(`El backend respondió ${response.status} para "${language}".`);
    process.exit(1);
  }
  const { language: _language, available_languages: _available, ...content } = await response.json();

  const file_url = new URL(`../src/i18n/${language}.json`, import.meta.url);
  const dictionary = JSON.parse(await readFile(file_url, "utf8"));
  dictionary.content = relative_media_urls(content);
  await writeFile(file_url, `${JSON.stringify(dictionary, null, 2)}\n`, "utf8");
  console.log(`src/i18n/${language}.json actualizado desde ${backend_url}`);
}
