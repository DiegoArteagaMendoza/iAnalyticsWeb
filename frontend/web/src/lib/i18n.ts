/**
 * Idiomas del sitio. Cada idioma tiene su archivo en src/i18n/<idioma>.json con:
 * - "ui": textos fijos de la interfaz (menú, etiquetas, formulario)
 * - "content": copia del contenido del backend (respaldo si el backend no responde;
 *   se actualiza con `npm run sync_content`)
 */
import en_dictionary from "../i18n/en.json";
import es_dictionary from "../i18n/es.json";
import type { PageContent } from "./types";

export const languages = ["es", "en"] as const;
export type Language = (typeof languages)[number];
export const default_language: Language = "es";
export const language_cookie = "preferred_language";

type UiStrings = typeof es_dictionary.ui;

const dictionaries: Record<Language, { ui: UiStrings; content: PageContent }> = {
  es: es_dictionary as unknown as { ui: UiStrings; content: PageContent },
  en: en_dictionary as unknown as { ui: UiStrings; content: PageContent },
};

export function is_language(value: unknown): value is Language {
  return typeof value === "string" && (languages as readonly string[]).includes(value);
}

export function get_ui(language: Language): UiStrings {
  return dictionaries[language].ui;
}

export function get_fallback_content(language: Language): PageContent {
  return structuredClone(dictionaries[language].content);
}

/** Ruta de inicio de cada idioma: "/" (español) y "/en/" (inglés). */
export function home_path(language: Language): string {
  return language === default_language ? "/" : `/${language}/`;
}

/** Enlace para cambiar de idioma: guarda la preferencia y redirige (ver middleware). */
export function switch_language_path(language: Language): string {
  return `${home_path(language)}?lang=${language}`;
}

export function language_from_path(pathname: string): Language {
  const first_segment = pathname.split("/").filter(Boolean)[0];
  return is_language(first_segment) ? first_segment : default_language;
}

/** "Hola {name}" + { name: "Ana" } -> "Hola Ana" */
export function format_text(template: string, values: Record<string, string>): string {
  return template.replace(/\{(\w+)\}/g, (match, key: string) => values[key] ?? match);
}

/** Elige el idioma preferido según la cabecera Accept-Language del navegador. */
export function language_from_accept_header(header: string | null): Language {
  if (!header) return default_language;
  const ranked = header
    .split(",")
    .map((part) => {
      const [tag, ...params] = part.trim().toLowerCase().split(";");
      const quality_param = params.find((param) => param.trim().startsWith("q="));
      return { tag: tag.split("-")[0], quality: quality_param ? Number(quality_param.split("=")[1]) : 1 };
    })
    .filter((item) => item.tag && !Number.isNaN(item.quality))
    .sort((a, b) => b.quality - a.quality);
  const match = ranked.find((item) => is_language(item.tag));
  return match && is_language(match.tag) ? match.tag : default_language;
}
