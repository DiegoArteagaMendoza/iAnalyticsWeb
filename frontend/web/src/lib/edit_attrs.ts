/**
 * Atributos que marcan qué partes de la página se pueden editar en el panel (/panel/editar).
 * Fuera del panel (`editing` = false) devuelven {} y la página pública no lleva nada extra.
 *
 * Un "destino" indica qué guardar: endpoint de la API de gestión + id (vacío en las secciones
 * de registro único) + campo. Ej: ["team_members", 5, "role"] → PATCH team_members/5/ { role_es }.
 */
export type EditTarget = [endpoint: string, id: number | null, field: string];

type Attributes = Record<string, string>;

const encode = ([endpoint, id, field]: EditTarget) => `${endpoint}|${id ?? ""}|${field}`;

export interface TextOptions {
  /** false para campos sin versión por idioma (nombres, teléfono, correo). */
  translatable?: boolean;
  multiline?: boolean;
  placeholder?: string;
}

export function edit_text(editing: boolean, target: EditTarget, options: TextOptions = {}): Attributes {
  if (!editing) return {};
  const attributes: Attributes = { "data-edit-text": encode(target) };
  if (options.translatable === false) attributes["data-edit-plain"] = "true";
  if (options.multiline) attributes["data-edit-multiline"] = "true";
  attributes["data-placeholder"] = options.placeholder ?? "Escribir texto…";
  return attributes;
}

export function edit_link(editing: boolean, target: EditTarget): Attributes {
  return editing ? { "data-edit-link": encode(target) } : {};
}

export function edit_image(editing: boolean, target: EditTarget, label = "Cambiar imagen"): Attributes {
  return editing ? { "data-edit-image": encode(target), "data-edit-image-label": label } : {};
}

export interface ItemOptions {
  is_published?: boolean;
  accent_color?: string;
  /** Nombre visible en los avisos (ej. "integrante"). */
  label?: string;
}

/** Elemento de una lista (persona, logo, valor...): publicar, mover, color y eliminar. */
export function edit_item(editing: boolean, endpoint: string, id: number, options: ItemOptions = {}): Attributes {
  if (!editing) return {};
  const attributes: Attributes = {
    "data-edit-item": `${endpoint}|${id}`,
    "data-edit-label": options.label ?? "elemento",
  };
  if (options.is_published !== undefined) attributes["data-published"] = String(options.is_published);
  if (options.accent_color) attributes["data-accent"] = options.accent_color;
  return attributes;
}

/** Sección completa: mostrar u ocultar en el sitio. */
export function edit_section(editing: boolean, endpoint: string, is_visible: boolean | undefined, label: string): Attributes {
  if (!editing) return {};
  return { "data-edit-section": endpoint, "data-visible": String(is_visible !== false), "data-edit-label": label };
}
