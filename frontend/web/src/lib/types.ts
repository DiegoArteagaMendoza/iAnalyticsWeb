/** Estructura del contenido de la página (igual a GET /api/v1/page_content/ del backend). */

export type AccentColor = "yellow" | "green" | "blue" | "base";

/** Campos que solo llegan en la vista previa del panel (?preview=1). */
export interface Publishable {
  order?: number;
  is_published?: boolean;
}

export interface SectionHeader {
  is_visible?: boolean;
  eyebrow: string;
  title_line_1: string;
  title_line_2: string;
  body: string;
  cta_text: string;
  cta_url: string;
}

export interface SiteSettings {
  company_name: string;
  logo_mark: string | null;
  logo_wordmark: string | null;
  logo_wordmark_light: string | null;
  logo_full: string | null;
  favicon: string | null;
  phone_display: string;
  phone_link: string;
  email: string;
  address: string;
  maps_url: string;
  linkedin_url: string;
  facebook_url: string;
  instagram_url: string;
  youtube_url: string;
  meta_title: string;
  meta_description: string;
  business_hours: string;
  footer_tagline: string;
  translation_notice: string;
}

export interface HeroSection {
  eyebrow: string;
  title_line_1: string;
  title_line_2: string;
  lead: string;
  primary_cta_text: string;
  primary_cta_url: string;
  secondary_cta_text: string;
  secondary_cta_url: string;
  background_image: string | null;
  highlights: ({ id: number; text: string; accent_color: AccentColor } & Publishable)[];
}

export interface AboutSection extends SectionHeader {
  mission: string;
  vision: string;
  values: ({ id: number; name: string; description: string; accent_color: AccentColor } & Publishable)[];
}

export interface TeamMember extends Publishable {
  id: number;
  full_name: string;
  initials: string;
  role: string;
  bio: string;
  photo: string | null;
  linkedin_url: string;
  is_founder: boolean;
  accent_color: AccentColor;
}

export interface TeamSection extends SectionHeader {
  founders_label: string;
  members_label: string;
  founders: TeamMember[];
  members: TeamMember[];
}

export interface Service extends Publishable {
  id: number;
  tag: string;
  title: string;
  menu_description: string;
  description: string;
  link_text: string;
  link_url: string;
  accent_color: AccentColor;
  features: { id: number; text: string; order?: number }[];
}

export interface ServicesSection extends SectionHeader {
  items: Service[];
}

export interface DataCapabilitiesSection extends SectionHeader {
  items: ({ id: number; title: string; description: string } & Publishable)[];
}

export interface Technology extends Publishable {
  id: number;
  name: string;
  category: "development" | "data";
  logo: string | null;
  website_url: string;
}

export interface TechnologiesSection extends SectionHeader {
  development_label: string;
  data_label: string;
  items: Technology[];
}

export interface ClientsSection extends SectionHeader {
  items: ({ id: number; name: string; logo: string | null; website_url: string; accent_color: AccentColor } & Publishable)[];
  testimonials: (Publishable & {
    id: number;
    quote: string;
    author_name: string;
    author_role: string;
    company_name: string;
    photo: string | null;
  })[];
  certifications: (Publishable & {
    id: number;
    badge_text: string;
    title: string;
    issuer: string;
    image: string | null;
    accent_color: AccentColor;
  })[];
}

export interface ContactSection extends SectionHeader {
  banner_title: string;
  banner_button_text: string;
  form_submit_text: string;
  form_success_message: string;
  form_other_option: string;
  service_options: string[];
}

/** Las secciones ocultas desde el admin llegan como null. */
export interface PageContent {
  site_settings: SiteSettings;
  hero: HeroSection;
  about: AboutSection | null;
  team: TeamSection | null;
  services: ServicesSection | null;
  data_capabilities: DataCapabilitiesSection | null;
  technologies: TechnologiesSection | null;
  clients: ClientsSection | null;
  contact: ContactSection | null;
}
