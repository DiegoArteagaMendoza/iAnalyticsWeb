# iAnalytics · sitio web

Monorepo del nuevo sitio de [Informatic Analytics](https://ianalytics.cl/).

```
iAnalytics/
├── backend/            API de gestión de contenido (Python · Django · Django REST framework)
│   ├── config/         settings, urls, wsgi/asgi
│   └── apps/           una app por sección de la página
│       ├── core/               modelos base, traducción automática, permisos, validadores
│       ├── site_settings/      logo, favicon, contacto, horario, SEO, redes sociales
│       ├── hero/               portada y etiquetas destacadas
│       ├── about/              nosotros, misión, visión y valores
│       ├── team/               equipo y fundadores
│       ├── services/           servicios y sus características
│       ├── data_capabilities/  carrusel de visibilidad de datos
│       ├── technologies/       tecnologías de desarrollo y de datos
│       ├── clients/            clientes destacados, testimonios, certificaciones
│       ├── contact/            textos de contacto y mensajes del formulario
│       ├── media_library/      subir, descargar y eliminar archivos
│       └── page_content/       endpoint público con toda la página en es / en
├── database/           imagen Docker de MySQL 8.4 (configuración utf8mb4)
├── frontend/
│   ├── web/            sitio público (Astro, renderizado en servidor)
│   │   ├── src/i18n/           es.json y en.json: textos de interfaz + contenido de respaldo
│   │   ├── src/components/
│   │   │   ├── layout/         encabezado, footer, logo, selector de idioma, aviso de traducción
│   │   │   ├── sections/       un componente por sección (hero, about, team, services, ...)
│   │   │   ├── editor/         editor visual del panel (barra de elementos, botón agregar)
│   │   │   └── common/         piezas compartidas (encabezado de sección)
│   │   ├── src/lib/            cliente del backend, idiomas y tipos del contenido
│   │   ├── src/pages/          / (es), /en/ (en), /panel/*, /api/contact, /media/*, /health, 404
│   │   └── scripts/            sync_content.mjs: copia el contenido del backend a los .json
│   └── mockup/         mockup estático aprobado (referencia de diseño)
├── scripts/            exportar/importar/publicar imágenes, respaldar/restaurar la base
├── docs/               contenido original, análisis de diseño y logo original
├── compose.yaml        despliegue con Docker (frontend + backend + MySQL)
└── .env.example        configuración del despliegue (copiar a .env)
```

## Frontend (Astro)

El sitio se renderiza en el servidor: en cada visita pide el contenido al backend
(`/api/v1/page_content/?lang=es|en`) y lo guarda en memoria `CONTENT_CACHE_SECONDS` (30 s),
así que lo que se edita en el panel aparece sin volver a construir el sitio.

### Idiomas

- `/` es la versión en español y `/en/` la versión en inglés (con `hreflang` para buscadores).
- En la primera visita a `/` se redirige a `/en/` si el navegador prefiere inglés; el selector
  ES | EN guarda la elección en una cookie. En inglés se muestra el aviso de traducción automática.
- Cada idioma tiene su archivo en `frontend/web/src/i18n/`:
  - `ui`: textos fijos de la interfaz (menú, etiquetas del formulario, accesibilidad).
  - `content`: copia del contenido del backend, ya traducido. Se usa si el backend no responde.
    Se actualiza con:

    ```bash
    cd frontend/web
    BACKEND_INTERNAL_URL=http://localhost:8000 npm run sync_content
    ```

### Desarrollo

```bash
cd frontend/web
npm install
BACKEND_INTERNAL_URL=http://localhost:8000 npm run dev    # http://localhost:4321
npm run check                                             # verificación de tipos
```

El formulario de contacto envía a `/api/contact` del propio frontend, que lo reenvía al backend
(funciona también sin JavaScript). Las imágenes subidas se sirven en `/media/...` a través del
frontend, así que el sitio usa un solo dominio y el backend no necesita estar expuesto.

Las secciones sin contenido publicado no se muestran (por ejemplo, Equipo aparece cuando hay al
menos una persona publicada en el panel).

## Panel de administración (`/panel/`)

Editor visual del sitio para usuarios del staff, servido por el frontend:

- **Inicio:** mensajes sin leer, contenido publicado y accesos rápidos.
- **Editar:** la página real dentro de un marco (`/panel/vista_previa`), en español o inglés y en
  tamaño escritorio, tablet o móvil. Textos editables en su lugar, cambio de imágenes y enlaces,
  y por cada elemento: publicar, mover, cambiar color y eliminar. Secciones visibles u ocultas.
- **Gestionar usuarios:** lista de administradores y acceso al admin de Django para registrarlos.
- **Salir:** cierra la sesión e invalida el token.

Cómo funciona:

- Al ingresar, el backend entrega un token (`/api/v1/auth/login/`) que vence a las
  `TOKEN_TTL_HOURS` horas; el frontend lo guarda en una cookie `HttpOnly`, `SameSite=Strict`,
  limitada a `/panel`.
- El editor guarda a través de `/panel/api/<recurso>/`, que agrega el token, solo acepta los
  recursos de contenido y exige una cabecera propia y mismo origen (protección CSRF).
- La vista previa pide `page_content/?preview=1`, que para el staff incluye lo no publicado.
- Los componentes marcan lo editable con `src/lib/edit_attrs.ts`; el editor está en
  `src/components/editor/page_editor.astro`. Fuera del panel no agregan nada a la página pública.

## Despliegue con Docker

Tres imágenes:

| Imagen | Contenido |
|---|---|
| `ianalytics_frontend` | Node.js 22, Astro (servidor standalone). Corre con un usuario sin privilegios. |
| `ianalytics_backend` | Python 3.12, Django + DRF, Gunicorn, WhiteNoise. Corre con un usuario sin privilegios. |
| `ianalytics_database` | MySQL 8.4 LTS con utf8mb4 (tildes, eñes y emojis) y healthcheck. |

```bash
cp .env.example .env          # completar claves (solo letras y números en las de MySQL)
docker compose up -d --build
```

Al iniciar, el backend espera a MySQL, aplica las migraciones, carga el contenido inicial
(solo si la base está vacía) y crea el administrador definido en `DJANGO_SUPERUSER_*`.
El frontend arranca cuando el backend está sano.

- Sitio: http://localhost:4321/ (español) y http://localhost:4321/en/ (inglés)
- Admin: http://localhost:8000/admin/
- API: http://localhost:8000/api/v1/docs/
- MySQL (solo desde este equipo): `127.0.0.1:3307`

Los datos se guardan en los volúmenes `mysql_data` (base de datos) y `media_data` (imágenes
subidas), así que sobreviven a `docker compose down` y a actualizar las imágenes.
`docker compose down -v` **borra** ambos volúmenes.

### Compartir las imágenes

**Sin registro (archivo):**

```bash
scripts/export_images.sh
# crea dist/ianalytics_<tag>/ con las imágenes (.tar.gz), compose.yaml, .env.example y scripts
```

En el otro equipo, con el contenido de esa carpeta:

```bash
scripts/import_images.sh ianalytics_images_1.0.0.tar.gz
cp .env.example .env          # completar claves
docker compose up -d --no-build
```

**Con registro (Docker Hub o GitHub Container Registry):** definir `IMAGE_PREFIX=usuario/`
en `.env`, hacer `docker login` y ejecutar `scripts/push_images.sh`. En el otro equipo basta con
`compose.yaml` y `.env`: `docker compose pull && docker compose up -d`.

### Respaldar y compartir el contenido

Las imágenes no llevan datos: cada instalación nueva parte con el contenido inicial. Para
llevar el contenido ya editado (textos e imágenes) a otro equipo o guardar una copia:

```bash
scripts/backup_database.sh                       # crea backups/ianalytics_<fecha>/
scripts/restore_database.sh backups/ianalytics_<fecha>   # reemplaza el contenido actual
```

### Producción con dominio y HTTPS

Publicar el **frontend** (puerto 4321) en el dominio principal y, si el panel debe ser accesible
desde fuera, el backend en un subdominio (ej. `admin.ianalytics.cl`), ambos detrás de un proxy con
certificado (nginx, Caddy, Traefik). Definir `PUBLIC_SITE_URL` antes de construir la imagen del
frontend y en `.env`:
`DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` con el dominio, `DJANGO_SECURE_COOKIES=True`,
`DJANGO_SECURE_SSL_REDIRECT=True` y `DJANGO_SECURE_HSTS_SECONDS=31536000`.

## Backend

### Puesta en marcha (desarrollo)

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env                       # revisar valores
.venv/bin/python manage.py migrate
.venv/bin/python manage.py load_initial_content
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

- Panel de gestión: http://127.0.0.1:8000/admin/
- Documentación de la API (Swagger): http://127.0.0.1:8000/api/v1/docs/
- Contenido público: http://127.0.0.1:8000/api/v1/page_content/?lang=es

### Tests

```bash
cd backend
.venv/bin/python manage.py test
```

### Gestión del contenido

Hay dos formas de editar la página:

1. **Admin de Django** (`/admin/`): formularios listos para cada sección, con los textos en
   español e inglés lado a lado, subida de imágenes y biblioteca de archivos.
2. **API REST** (`/api/v1/`): para el futuro panel propio o integraciones. Requiere un usuario
   del staff con permisos sobre cada modelo. Autenticación por token:

   ```bash
   curl -X POST -d "username=USUARIO&password=CLAVE" http://127.0.0.1:8000/api/v1/auth/token/
   curl -H "Authorization: Token <token>" http://127.0.0.1:8000/api/v1/hero_section/
   ```

| Recurso | Endpoint | Métodos |
|---|---|---|
| Contenido público (es/en) | `page_content/?lang=en` | GET (público) |
| Configuración del sitio | `site_settings/` | GET, PUT, PATCH |
| Textos de cada sección | `hero_section/`, `about_section/`, `team_section/`, `services_section/`, `data_capabilities_section/`, `technologies_section/`, `clients_section/`, `contact_section/` | GET, PUT, PATCH |
| Elementos de cada sección | `hero_highlights/`, `company_values/`, `team_members/`, `services/`, `service_features/`, `data_capabilities/`, `technologies/`, `clients/`, `testimonials/`, `certifications/` | GET, POST, PUT, PATCH, DELETE |
| Mensajes del formulario | `contact_messages/` | POST (público, con límite) · GET, PATCH, DELETE (staff) |
| Biblioteca de archivos | `media_files/`, `media_files/<id>/download/` | GET, POST, PATCH, DELETE · descarga |

Las imágenes se suben como `multipart/form-data`. Al reemplazar o eliminar una imagen, el
archivo anterior se borra del disco. Se aceptan png, jpg, webp, gif e ico (y documentos en la
biblioteca), hasta `MAX_UPLOAD_SIZE_MB`, y se comprueba que las imágenes sean imágenes reales.

### Traducción automática al inglés

Cada texto se guarda en dos columnas (`<campo>_es`, `<campo>_en`). Al guardar:

- si el inglés está vacío, se traduce automáticamente;
- si el inglés fue generado automáticamente y el español cambia, se vuelve a traducir;
- si alguien corrigió el inglés a mano, se respeta y no se sobrescribe.

El proveedor se elige con `TRANSLATION_PROVIDER` en `.env`:

| Valor | Servicio |
|---|---|
| `none` | Sin traducción automática (se escribe a mano). Valor por defecto. |
| `deepl` | API de DeepL (`DEEPL_API_KEY`; existe plan gratuito de 500.000 caracteres/mes). |
| `libretranslate` | Servidor LibreTranslate propio (`LIBRETRANSLATE_URL`), puede correr en Docker. |

Si el servicio falla, el contenido se guarda igual y la página muestra el texto en español.

### Contenido inicial

`load_initial_content` carga los textos del mockup en ambos idiomas, los logos y el favicon.
Las fichas de **equipo**, **clientes** y el **testimonio** se crean como ejemplo **sin publicar**:
hay que completarlas con los datos reales en el admin y marcarlas como publicadas.
