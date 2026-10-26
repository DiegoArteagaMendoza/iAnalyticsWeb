"""
Carga el contenido inicial de la página (textos del mockup en español e inglés,
logos y favicon). No llama al servicio de traducción: las traducciones vienen incluidas.

    python manage.py load_initial_content          # solo si la base está vacía
    python manage.py load_initial_content --reset  # reemplaza el contenido existente
"""
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.about.models import AboutSection, CompanyValue
from apps.clients.models import Certification, Client, ClientsSection, Testimonial
from apps.contact.models import ContactSection
from apps.data_capabilities.models import DataCapabilitiesSection, DataCapability
from apps.hero.models import HeroHighlight, HeroSection
from apps.services.models import Service, ServiceFeature, ServicesSection
from apps.site_settings.models import SiteSettings
from apps.team.models import TeamMember, TeamSection
from apps.technologies.models import TechnologiesSection, Technology

BRAND_ASSETS_DIR = Path(__file__).resolve().parents[2] / "seed_assets"


def translated(**fields):
    """translated(title=("Hola", "Hello")) -> {"title_es": "Hola", "title_en": "Hello"}"""
    values = {}
    for name, (spanish, english) in fields.items():
        values[f"{name}_es"] = spanish
        values[f"{name}_en"] = english
    return values


def save_translated(instance, **plain_fields):
    for name, value in plain_fields.items():
        setattr(instance, name, value)
    instance.mark_as_auto_translated()
    instance.save()
    return instance


def update_section(model, **fields):
    return save_translated(model.load(), **fields)


def create_item(model, **fields):
    return save_translated(model(), **fields)


ITEM_MODELS = [
    HeroHighlight,
    CompanyValue,
    TeamMember,
    ServiceFeature,
    Service,
    DataCapability,
    Technology,
    Client,
    Testimonial,
    Certification,
]


class Command(BaseCommand):
    help = "Carga el contenido inicial de la página de iAnalytics."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Borra y vuelve a cargar los elementos.")

    @transaction.atomic
    def handle(self, *args, reset=False, **options):
        if Service.objects.exists() and not reset:
            self.stdout.write(self.style.WARNING("Ya hay contenido cargado. Usa --reset para reemplazarlo."))
            return
        for model in ITEM_MODELS:
            for instance in model.objects.all():
                instance.delete()

        self.load_site_settings()
        self.load_hero()
        self.load_about()
        self.load_team()
        self.load_services()
        self.load_data_capabilities()
        self.load_technologies()
        self.load_clients()
        self.load_contact()
        self.stdout.write(self.style.SUCCESS("Contenido inicial cargado."))

    # --- Secciones -----------------------------------------------------------

    def load_site_settings(self):
        site_settings = update_section(
            SiteSettings,
            company_name="Informatic Analytics",
            phone_display="42-225 20 35",
            phone_link="+56422252035",
            email="contacto@ianalytics.cl",
            address="Constitución 162, Chillán",
            maps_url="https://goo.gl/maps/p57mE1qcWAjyYgaTA",
            **translated(
                meta_title=("iAnalytics | Soluciones informáticas en Chillán", "iAnalytics | IT solutions in Chillán, Chile"),
                meta_description=(
                    "iAnalytics: desarrollo de aplicaciones a medida, asesorías TI e inteligencia de negocios desde Chillán, Región de Ñuble.",
                    "iAnalytics: custom software development, IT consulting and business intelligence from Chillán, Ñuble Region, Chile.",
                ),
                business_hours=("Lunes a viernes, 9:00 a 18:00 hrs", "Monday to Friday, 9:00 a.m. to 6:00 p.m."),
                footer_tagline=(
                    "Soluciones informáticas de excelencia desde Chillán, Región de Ñuble.",
                    "Excellent IT solutions from Chillán, Ñuble Region, Chile.",
                ),
                translation_notice=(
                    "Esta versión fue traducida automáticamente.",
                    "This English version was translated automatically.",
                ),
            ),
        )
        brand_files = {
            "logo_mark": "logo_mark.png",
            "logo_wordmark": "logo_wordmark.png",
            "logo_wordmark_light": "logo_wordmark_light.png",
            "logo_full": "logo_full.png",
            "favicon": "favicon.png",
        }
        for field_name, file_name in brand_files.items():
            path = BRAND_ASSETS_DIR / file_name
            if path.exists() and not getattr(site_settings, field_name):
                with path.open("rb") as brand_file:
                    getattr(site_settings, field_name).save(file_name, File(brand_file), save=False)
        site_settings.save()

    def load_hero(self):
        update_section(
            HeroSection,
            primary_cta_url="#contacto",
            secondary_cta_url="#servicios",
            **translated(
                eyebrow=("Informatic Analytics · Chillán", "Informatic Analytics · Chillán"),
                title_line_1=("No solo desarrollamos software.", "We don't just build software."),
                title_line_2=("Creamos soluciones que funcionan.", "We build solutions that work."),
                lead=(
                    "Transformación digital, aplicaciones web y mobile e inteligencia de negocios para que su empresa crezca, con relaciones de largo plazo basadas en el respeto, la seriedad y la confianza.",
                    "Digital transformation, web and mobile applications and business intelligence to help your company grow, through long-term relationships built on respect, reliability and trust.",
                ),
                primary_cta_text=("Conversemos", "Let's talk"),
                secondary_cta_text=("Ver servicios", "View services"),
            ),
        )
        highlights = [
            ("Transformación Digital", "Digital Transformation", "yellow"),
            ("Aplicaciones Web y Mobile", "Web and Mobile Applications", "green"),
            ("Inteligencia de Negocios", "Business Intelligence", "blue"),
        ]
        for order, (spanish, english, color) in enumerate(highlights):
            create_item(HeroHighlight, order=order, accent_color=color, **translated(text=(spanish, english)))

    def load_about(self):
        update_section(
            AboutSection,
            cta_url="#contacto",
            **translated(
                eyebrow=("Quiénes somos", "Who we are"),
                title_line_1=("Nacimos en Chillán", "Born in Chillán"),
                title_line_2=("para crecer junto a su empresa", "to grow alongside your business"),
                body=(
                    "Somos una empresa de la ciudad de Chillán, capital de la Región de Ñuble. Proveemos soluciones informáticas de excelencia y nos preocupamos de construir lazos de largo plazo con nuestros clientes.",
                    "We are a company from Chillán, capital of the Ñuble Region in Chile. We deliver excellent IT solutions and focus on building long-term relationships with our clients.",
                ),
                cta_text=("Escríbanos", "Write to us"),
                mission=(
                    "Proporcionar a nuestros clientes compromiso y seriedad para entregarles soluciones con altos estándares de calidad. Procuramos con todo el entorno, especialmente clientes y colaboradores, relaciones de largo plazo, basadas en la confianza y respeto mutuo.",
                    "To offer our clients commitment and reliability, delivering solutions that meet high quality standards. We seek long-term relationships with everyone around us, especially clients and team members, based on trust and mutual respect.",
                ),
                vision=(
                    "Aspiramos a ser una empresa sólida y en constante crecimiento. Buscamos ser referente en nuestra área y cultivamos la colaboración, respeto, seriedad y confianza entre clientes y proveedores.",
                    "We aspire to be a solid, constantly growing company. We aim to be a benchmark in our field, fostering collaboration, respect, reliability and trust between clients and suppliers.",
                ),
            ),
        )
        values = [
            (("Honestidad", "Honesty"), ("Transparencia en cada etapa del proyecto.", "Transparency at every stage of the project."), "yellow"),
            (("Profesionalismo", "Professionalism"), ("Equipo experto y procesos rigurosos.", "An expert team and rigorous processes."), "green"),
            (("Compromiso", "Commitment"), ("Nos hacemos cargo hasta el final.", "We see every project through to the end."), "blue"),
            (("Servicio personalizado", "Personalized service"), ("Soluciones pensadas para su negocio.", "Solutions designed for your business."), "base"),
        ]
        for order, (name, description, color) in enumerate(values):
            create_item(CompanyValue, order=order, accent_color=color, **translated(name=name, description=description))

    def load_team(self):
        update_section(
            TeamSection,
            **translated(
                eyebrow=("Nuestro equipo", "Our team"),
                title_line_1=("Las personas detrás", "The people behind"),
                title_line_2=("de cada solución", "every solution"),
                body=(
                    "Un equipo de profesionales de Ñuble que combina desarrollo de software, consultoría y análisis de datos para acompañar a su empresa en cada etapa.",
                    "A team of professionals from Ñuble combining software development, consulting and data analytics to support your company at every stage.",
                ),
                founders_label=("Fundadores", "Founders"),
                members_label=("Equipo", "Team"),
            ),
        )
        # Fichas de ejemplo sin publicar: se completan con los datos reales y se publican desde el admin.
        founders = [
            (("Cofundador · Gerente General", "Co-founder · CEO"), "yellow"),
            (("Cofundador · Director de Tecnología", "Co-founder · CTO"), "green"),
        ]
        for order, (role, color) in enumerate(founders):
            create_item(
                TeamMember,
                full_name="Nombre Fundador",
                is_founder=True,
                is_published=False,
                order=order,
                accent_color=color,
                **translated(role=role, bio=("", "")),
            )
        members = [
            (("Desarrollo Web y Mobile", "Web and Mobile Development"), "blue"),
            (("Inteligencia de Negocios", "Business Intelligence"), "yellow"),
            (("Consultoría TI", "IT Consulting"), "green"),
            (("Arquitectura de Datos", "Data Architecture"), "blue"),
        ]
        for order, (role, color) in enumerate(members):
            create_item(
                TeamMember,
                full_name="Nombre Persona",
                is_published=False,
                order=order,
                accent_color=color,
                **translated(role=role),
            )

    def load_services(self):
        update_section(
            ServicesSection,
            cta_url="#contacto",
            **translated(
                eyebrow=("Servicios", "Services"),
                title_line_1=("Tecnología a la medida", "Technology tailored"),
                title_line_2=("de cada desafío", "to every challenge"),
                body=(
                    "Desde una aplicación web hasta la estrategia de datos de toda la organización: ayudamos a optimizar el uso de sus recursos y maximizar sus utilidades.",
                    "From a single web application to an organization-wide data strategy: we help you make the most of your resources and maximize your profits.",
                ),
                cta_text=("Cuéntenos su proyecto", "Tell us about your project"),
            ),
        )
        services = [
            {
                "accent_color": "yellow",
                "link_url": "#tecnologias",
                "tag": ("Desarrollo", "Development"),
                "title": ("Aplicaciones a Medida", "Custom Applications"),
                "menu_description": ("Web y mobile, desde el diseño hasta el soporte", "Web and mobile, from design to support"),
                "description": (
                    "Desarrollamos aplicaciones a medida usando diferentes lenguajes de programación.",
                    "We build custom applications using a range of programming languages.",
                ),
                "link_text": ("Ver tecnologías", "View technologies"),
                "features": [
                    ("Desarrollo integral de aplicaciones web interactivas y seguras.", "End-to-end development of interactive, secure web applications."),
                    ("Código desarrollado por profesionales.", "Code written by professionals."),
                    ("Alojamiento en el servidor adecuado, mantención y soporte.", "Hosting on the right server, plus maintenance and support."),
                    ("Aplicaciones web con diseño personalizado.", "Web applications with custom design."),
                ],
            },
            {
                "accent_color": "green",
                "link_url": "#contacto",
                "tag": ("Consultoría", "Consulting"),
                "title": ("Asesorías", "Consulting"),
                "menu_description": ("Procesos, seguridad y transformación digital", "Processes, security and digital transformation"),
                "description": (
                    "Asesoramos a empresas de distintos rubros para optimizar recursos y maximizar utilidades.",
                    "We advise companies across industries on optimizing resources and maximizing profits.",
                ),
                "link_text": ("Agendar una asesoría", "Book a consultation"),
                "features": [
                    ("Seguridad de la información.", "Information security."),
                    ("Consultoría de procesos.", "Process consulting."),
                    ("Requerimientos comerciales y de arquitectura TI.", "Business requirements and IT architecture."),
                    ("Transformación digital.", "Digital transformation."),
                    ("Consultoría estratégica.", "Strategic consulting."),
                ],
            },
            {
                "accent_color": "blue",
                "link_url": "#datos",
                "tag": ("Datos", "Data"),
                "title": ("Visibilidad de Datos", "Data Visibility"),
                "menu_description": ("Datawarehouse, BI e informes gerenciales", "Data warehousing, BI and executive reporting"),
                "description": (
                    "Damos mayor valor y visibilidad a sus datos para transformarlos en información y ventajas competitivas.",
                    "We add value and visibility to your data, turning it into information and competitive advantage.",
                ),
                "link_text": ("Explorar capacidades", "Explore capabilities"),
                "features": [
                    ("Datawarehouse y Datamart.", "Data warehouses and data marts."),
                    ("Modelamiento de datos relacional y multidimensional.", "Relational and multidimensional data modeling."),
                    ("Reportería e informes gerenciales.", "Reporting and executive dashboards."),
                    ("Data Mining y Data Analytics.", "Data mining and data analytics."),
                ],
            },
        ]
        for order, data in enumerate(services):
            features = data.pop("features")
            plain = {key: data.pop(key) for key in ("accent_color", "link_url")}
            service = create_item(Service, order=order, **plain, **translated(**data))
            for feature_order, text in enumerate(features):
                create_item(ServiceFeature, service=service, order=feature_order, **translated(text=text))

    def load_data_capabilities(self):
        update_section(
            DataCapabilitiesSection,
            cta_url="#contacto",
            **translated(
                eyebrow=("La importancia de los datos", "Why data matters"),
                title_line_1=("Sus datos ya tienen respuestas.", "Your data already has the answers."),
                title_line_2=("Nosotros las hacemos visibles.", "We make them visible."),
                body=(
                    "Colaboramos con las empresas para transformar sus datos en información y así lograr ventajas competitivas en sus respectivas áreas.",
                    "We work with companies to turn their data into information and gain a competitive edge in their fields.",
                ),
                cta_text=("Hablemos de sus datos", "Let's talk about your data"),
            ),
        )
        capabilities = [
            (("Datawarehouse", "Data Warehouse"), ("Diseño y construcción de Datawarehouse.", "Data warehouse design and implementation.")),
            (("Modelamiento de Datos", "Data Modeling"), ("Diseño y construcción de modelos de datos relacionales y multidimensionales.", "Design and implementation of relational and multidimensional data models.")),
            (("Datamart", "Data Mart"), ("Diseño y construcción de Datamart.", "Data mart design and implementation.")),
            (("Multiplataformas", "Multiplatform"), ("Integración en un mismo proyecto de múltiples plataformas de desarrollo.", "Integration of multiple development platforms within a single project.")),
            (("Informes", "Reporting"), ("Diseño y construcción de reportería e informes gerenciales.", "Design and implementation of reports and executive dashboards.")),
            (("Data Mining & Analytics", "Data Mining & Analytics"), ("Descubrimiento de patrones y análisis avanzado de datos.", "Pattern discovery and advanced data analysis.")),
        ]
        for order, (title, description) in enumerate(capabilities):
            create_item(DataCapability, order=order, **translated(title=title, description=description))

    def load_technologies(self):
        update_section(
            TechnologiesSection,
            **translated(
                eyebrow=("Tecnologías", "Technologies"),
                title_line_1=("Las herramientas correctas", "The right tools"),
                title_line_2=("para cada proyecto", "for every project"),
                body=(
                    "Trabajamos con frameworks modernos de desarrollo y con las principales plataformas de bases de datos e inteligencia de negocios del mercado.",
                    "We work with modern development frameworks and the leading database and business intelligence platforms on the market.",
                ),
                development_label=("Desarrollo web y mobile", "Web and mobile development"),
                data_label=("Datos e inteligencia de negocios", "Data and business intelligence"),
            ),
        )
        groups = {
            Technology.Category.DEVELOPMENT: ["Angular", "Flutter", "Ionic", "Node.js", "Python", "React", "Spring Boot", "Vue.js"],
            Technology.Category.DATA: ["Teradata", "SQL Server", "Qlik", "Power BI", "Oracle", "MySQL", "MicroStrategy"],
        }
        for category, names in groups.items():
            for order, name in enumerate(names):
                Technology.objects.create(name=name, category=category, order=order)

    def load_clients(self):
        update_section(
            ClientsSection,
            cta_url="#contacto",
            **translated(
                eyebrow=("Clientes destacados", "Featured clients"),
                title_line_1=("Empresas que confían", "Companies that trust"),
                title_line_2=("en nuestro trabajo", "our work"),
                body=(
                    "Acompañamos a organizaciones de distintos rubros en su transformación digital y en la gestión de sus datos.",
                    "We support organizations across industries in their digital transformation and data management.",
                ),
                cta_text=("Sea nuestro próximo caso de éxito", "Be our next success story"),
            ),
        )
        # Clientes y testimonio de ejemplo sin publicar: se reemplazan por los reales desde el admin.
        colors = ["yellow", "green", "blue"]
        for order in range(6):
            Client.objects.create(name=f"Cliente {order + 1}", order=order, accent_color=colors[order % 3], is_published=False)
        create_item(
            Testimonial,
            author_name="Nombre del cliente",
            company_name="Empresa",
            is_published=False,
            **translated(
                quote=(
                    "Aquí irá el testimonio de un cliente sobre el trabajo realizado con iAnalytics.",
                    "A client testimonial about working with iAnalytics will go here.",
                ),
                author_role=("Cargo", "Role"),
            ),
        )
        create_item(
            Certification,
            accent_color="green",
            **translated(
                badge_text=("40 h", "40 h"),
                title=("Certificación 40 horas", "40-hour workweek certification"),
                issuer=("Ministerio del Trabajo y Previsión Social.", "Chilean Ministry of Labor and Social Security."),
            ),
        )

    def load_contact(self):
        update_section(
            ContactSection,
            **translated(
                eyebrow=("¿Cómo encontrarnos?", "How to find us"),
                title_line_1=("Información de contacto", "Contact information"),
                title_line_2=("", ""),
                body=(
                    "Si tiene alguna duda o consulta, comuníquese con nosotros por cualquiera de nuestros medios o escríbanos un correo.",
                    "If you have any questions, reach out through any of our channels or send us an email.",
                ),
                banner_title=(
                    "Construyamos juntos la próxima etapa de su empresa.",
                    "Let's build your company's next chapter together.",
                ),
                banner_button_text=("Póngase en contacto", "Get in touch"),
                form_submit_text=("Enviar mensaje", "Send message"),
                form_success_message=(
                    "¡Gracias! Le responderemos a la brevedad.",
                    "Thank you! We'll get back to you shortly.",
                ),
                form_other_option=("Otro", "Other"),
            ),
        )
