# Guía de despliegue · iAnalytics

Cómo poner en marcha el sitio de Informatic Analytics en un servidor o en un equipo local.
Hay tres caminos; elegir uno:

| Opción | Cuándo usarla | Requiere |
|---|---|---|
| **A. Docker desde el código fuente** | Tienes el repositorio y quieres construir las imágenes | Docker + código |
| **B. Docker con imágenes ya construidas** | Recibiste el paquete `.tar.gz` o las imágenes están en un registro | Docker, sin código |
| **C. Proyecto en crudo (sin Docker)** | El servidor no admite Docker o prefieres servicios del sistema | Python, Node.js, MySQL, nginx |
| **D. Railway (nube administrada)** | No quieres administrar un servidor | Cuenta en Railway + GitHub o Docker Hub |

Las secciones [Producción con dominio y HTTPS](#5-producción-con-dominio-y-https),
[Operación](#6-operación) y [Solución de problemas](#7-solución-de-problemas) aplican a las tres.

---

## 1. Cómo está armado

```
                  Internet
                     │
         ┌───────────┴────────────┐
         │  Proxy HTTPS (nginx /  │   solo en producción
         │  Caddy / Traefik)      │
         └─────┬─────────────┬────┘
   ianalytics.cl│             │admin.ianalytics.cl (opcional)
               ▼             ▼
   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
   │ frontend (Astro) │──▶│ backend (Django) │──▶│ database (MySQL) │
   │ puerto 4321      │   │ puerto 8000      │   │ puerto 3306      │
   └──────────────────┘   └──────────────────┘   └──────────────────┘
     sitio público          panel /admin/,         contenido, usuarios,
     /  y  /en/             API /api/v1/           mensajes de contacto
                            archivos /media/
```

- El **frontend** renderiza cada página pidiendo el contenido al backend por la red interna
  (con 30 s de caché). También reenvía el formulario de contacto y las imágenes subidas, así que
  el público solo necesita llegar al frontend.
- El **backend** se expone solo si el panel de administración debe usarse desde fuera.
- La **base de datos** nunca se expone a internet.

| Servicio | Puerto interno | Puerto en el equipo (por defecto) | Variable para cambiarlo |
|---|---|---|---|
| frontend | 4321 | 4321 | `FRONTEND_PUBLISHED_PORT` |
| backend | 8000 | 8000 | `BACKEND_PUBLISHED_PORT` |
| database | 3306 | 127.0.0.1:3307 | `MYSQL_PUBLISHED_PORT` |

---

## 2. Opción A · Docker desde el código fuente

### Requisitos

- Docker Engine 24 o superior con Docker Compose v2 (`docker compose version`).
- 2 GB de RAM libres y ~3 GB de disco para las imágenes.

### Pasos

```bash
git clone <url-del-repositorio> iAnalytics      # o copiar la carpeta del proyecto
cd iAnalytics
cp .env.example .env
```

Editar `.env`. Mínimo obligatorio:

| Variable | Qué poner |
|---|---|
| `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD` | Claves largas, **solo letras y números** (van dentro de una URL). |
| `DJANGO_SECRET_KEY` | `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_SUPERUSER_EMAIL` | Administrador inicial del panel (se crea solo la primera vez). |
| `BACKEND_PUBLISHED_PORT` | Cambiar si el 8000 está ocupado (ej. `8001`). |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | La dirección exacta con que se abre el panel, con el mismo puerto (ej. `http://localhost:8001`). |
| `PUBLIC_SITE_URL` | Dirección del sitio público (`http://localhost:4321` en local, `https://ianalytics.cl` en producción). |

Construir y levantar:

```bash
docker compose up -d --build
docker compose ps          # los tres servicios deben decir "healthy"
```

Al iniciar, el backend espera a MySQL, aplica las migraciones, carga el contenido inicial (solo
si la base está vacía) y crea el administrador. El frontend arranca cuando el backend está sano.

| Qué | Dirección (valores por defecto) |
|---|---|
| Sitio en español | http://localhost:4321/ |
| Sitio en inglés | http://localhost:4321/en/ |
| Panel de administración | http://localhost:8000/admin/ |
| Documentación de la API | http://localhost:8000/api/v1/docs/ |

> `PUBLIC_SITE_URL` se aplica **al construir** la imagen del frontend. Si se cambia, volver a
> ejecutar `docker compose up -d --build frontend`.

---

## 3. Opción B · Docker con imágenes ya construidas

### B.1 Desde el paquete `.tar.gz` (sin registro)

En el equipo que tiene el código:

```bash
scripts/export_images.sh
# crea dist/ianalytics_<versión>/ con:
#   ianalytics_images_<versión>.tar.gz   (frontend + backend + base de datos)
#   compose.yaml, .env.example, scripts/
```

Copiar la carpeta `dist/ianalytics_<versión>/` al servidor (USB, `scp`, unidad compartida) y allí:

```bash
cd ianalytics_1.0.0
scripts/import_images.sh ianalytics_images_1.0.0.tar.gz
cp .env.example .env               # completar como en la Opción A
docker compose up -d --no-build
```

`--no-build` es necesario porque el paquete no incluye el código fuente.

### B.2 Desde un registro (Docker Hub, GitHub Container Registry)

Publicar (equipo con el código):

```bash
# en .env:  IMAGE_PREFIX=usuario/            (Docker Hub)
#           IMAGE_PREFIX=ghcr.io/usuario/    (GitHub)
docker login                                  # o: docker login ghcr.io
scripts/push_images.sh
```

En el servidor solo se necesitan `compose.yaml` y `.env` (con el mismo `IMAGE_PREFIX` e `IMAGE_TAG`):

```bash
docker compose pull
docker compose up -d --no-build
```

> Las imágenes **no contienen datos**: cada instalación nueva parte con el contenido inicial.
> Para llevar el contenido ya editado ver [Respaldos](#respaldos-y-traspaso-de-contenido).

---

## 4. Opción C · Proyecto en crudo (sin Docker)

Ejemplo para **Ubuntu 24.04 / Debian 12**, instalando en `/srv/ianalytics` con el usuario de
sistema `ianalytics`. Adaptar rutas y dominio según el servidor.

### 4.1 Paquetes del sistema

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-dev build-essential pkg-config \
    default-libmysqlclient-dev mysql-server nginx git curl
# Node.js 22 LTS
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
sudo useradd --system --create-home --home-dir /srv/ianalytics --shell /usr/sbin/nologin ianalytics
```

Requisitos de versión: Python 3.10 o superior, Node.js 22.12 o superior, MySQL 8.0 o superior.

### 4.2 Base de datos MySQL

```bash
sudo mysql <<'SQL'
CREATE DATABASE ianalytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ianalytics'@'localhost' IDENTIFIED BY 'CLAVE_SOLO_LETRAS_Y_NUMEROS';
GRANT ALL PRIVILEGES ON ianalytics.* TO 'ianalytics'@'localhost';
FLUSH PRIVILEGES;
SQL
```

Opcional: copiar la configuración usada en Docker (`database/conf/ianalytics.cnf`) a
`/etc/mysql/conf.d/` y reiniciar MySQL (`sudo systemctl restart mysql`).

### 4.3 Código

```bash
sudo -u ianalytics git clone <url-del-repositorio> /srv/ianalytics/app
cd /srv/ianalytics/app
```

### 4.4 Backend (Django + Gunicorn)

```bash
cd /srv/ianalytics/app/backend
sudo -u ianalytics python3 -m venv .venv
sudo -u ianalytics .venv/bin/pip install -r requirements_production.txt
sudo -u ianalytics cp .env.example .env
sudo -u ianalytics chmod 600 .env
```

Editar `backend/.env`:

```ini
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<clave larga y aleatoria>
DJANGO_ALLOWED_HOSTS=admin.ianalytics.cl
DJANGO_CSRF_TRUSTED_ORIGINS=https://admin.ianalytics.cl
DJANGO_SECURE_COOKIES=True
DJANGO_SECURE_SSL_REDIRECT=False        # la redirección a HTTPS la hace nginx
DJANGO_SECURE_HSTS_SECONDS=31536000
DATABASE_URL=mysql://ianalytics:CLAVE_SOLO_LETRAS_Y_NUMEROS@127.0.0.1:3306/ianalytics
DJANGO_SERVE_MEDIA=False                # nginx sirve /media/ directamente
FRONTEND_PUBLIC_URL=https://ianalytics.cl/
```

Preparar la base, los archivos estáticos y el administrador:

```bash
sudo -u ianalytics .venv/bin/python manage.py migrate
sudo -u ianalytics .venv/bin/python manage.py collectstatic --noinput
sudo -u ianalytics .venv/bin/python manage.py load_initial_content
sudo -u ianalytics .venv/bin/python manage.py createsuperuser
sudo -u ianalytics .venv/bin/python manage.py check --deploy
```

Servicio del sistema `/etc/systemd/system/ianalytics_backend.service`:

```ini
[Unit]
Description=iAnalytics backend (Django + Gunicorn)
After=network.target mysql.service

[Service]
User=ianalytics
Group=ianalytics
WorkingDirectory=/srv/ianalytics/app/backend
ExecStart=/srv/ianalytics/app/backend/.venv/bin/gunicorn config.wsgi:application \
    --bind 127.0.0.1:8000 --workers 3 --timeout 60 --access-logfile - --error-logfile -
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 4.5 Frontend (Astro + Node.js)

```bash
cd /srv/ianalytics/app/frontend/web
sudo -u ianalytics npm ci
sudo -u ianalytics env PUBLIC_SITE_URL=https://ianalytics.cl ASTRO_TELEMETRY_DISABLED=1 npm run build
sudo -u ianalytics npm prune --omit=dev
```

Servicio del sistema `/etc/systemd/system/ianalytics_frontend.service`:

```ini
[Unit]
Description=iAnalytics frontend (Astro)
After=network.target ianalytics_backend.service

[Service]
User=ianalytics
Group=ianalytics
WorkingDirectory=/srv/ianalytics/app/frontend/web
Environment=NODE_ENV=production
Environment=HOST=127.0.0.1
Environment=PORT=4321
Environment=BACKEND_INTERNAL_URL=http://127.0.0.1:8000
Environment=CONTENT_CACHE_SECONDS=30
Environment=TRUST_FORWARDED_FOR=true
Environment=DJANGO_ADMIN_PUBLIC_URL=https://admin.ianalytics.cl/admin/
Environment=PUBLIC_SITE_URL=https://ianalytics.cl
Environment=ASTRO_TELEMETRY_DISABLED=1
ExecStart=/usr/bin/node ./dist/server/entry.mjs
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Activar ambos servicios:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ianalytics_backend ianalytics_frontend
sudo systemctl status ianalytics_backend ianalytics_frontend
curl http://127.0.0.1:8000/api/v1/health/     # {"status":"ok","database":"ok"}
curl http://127.0.0.1:4321/health             # {"status":"ok"}
```

### 4.6 nginx

`/etc/nginx/sites-available/ianalytics` (luego `ln -s` a `sites-enabled/`). El certificado se
obtiene en el paso 5.

```nginx
# Sitio público
server {
    listen 80;
    server_name ianalytics.cl www.ianalytics.cl;
    client_max_body_size 6m;

    # Imágenes subidas desde el panel, servidas directo desde el disco
    location /media/ {
        alias /srv/ianalytics/app/backend/media/;
        expires 1h;
        add_header X-Content-Type-Options nosniff;
    }

    location / {
        proxy_pass http://127.0.0.1:4321;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Panel de administración y API
server {
    listen 80;
    server_name admin.ianalytics.cl;
    client_max_body_size 6m;

    location /media/ {
        alias /srv/ianalytics/app/backend/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ianalytics /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

nginx necesita poder leer `backend/media/`: `sudo chmod o+x /srv/ianalytics /srv/ianalytics/app /srv/ianalytics/app/backend`.

---

## 4b. Opción D · Railway

Railway ejecuta los contenedores del frontend y del backend, ofrece MySQL administrado (con
respaldos) y volúmenes persistentes. Cada servicio de `compose.yaml` se crea como un servicio
de Railway dentro de un mismo proyecto; se comunican por la red privada `<servicio>.railway.internal`.

| Servicio en Railway | Origen | Notas |
|---|---|---|
| `MySQL` | **+ New → Database → MySQL** | Reemplaza a `ianalytics_database` (no se usa esa imagen). |
| `backend` | Repositorio (Root Directory `backend`) o imagen `ianalytics_backend` | Volumen en `/app/media`. |
| `frontend` | Repositorio (Root Directory `frontend/web`) o imagen `ianalytics_frontend` | Dominio público del sitio. |

### D.1 Crear el proyecto y la base de datos

1. En railway.com: **New Project → Empty project**.
2. **+ New → Database → MySQL**. Dejar el nombre `MySQL`.

### D.2 Backend

1. **+ New → GitHub Repo** (elegir el repositorio) o **+ New → Docker Image**
   (`usuario/ianalytics_backend:1.0.0`, publicada con `scripts/push_images.sh`). Renombrar el servicio a `backend`.
2. Si viene del repositorio: **Settings → Source → Root Directory** = `backend`, y la variable
   `RAILWAY_DOCKERFILE_PATH=dockerfile` (el archivo está en minúsculas).
3. **Settings → Volumes → Add Volume**, Mount Path `/app/media`.
4. **Variables → Raw Editor**:

   ```ini
   DATABASE_URL=${{MySQL.MYSQL_URL}}
   DJANGO_SECRET_KEY=<clave larga y aleatoria>
   DJANGO_DEBUG=False
   PORT=8000
   GUNICORN_BIND=[::]:8000
   GUNICORN_WORKERS=2
   RAILWAY_RUN_UID=0
   DJANGO_ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
   DJANGO_INTERNAL_HOSTS=${{RAILWAY_PRIVATE_DOMAIN}}
   DJANGO_CSRF_TRUSTED_ORIGINS=https://${{RAILWAY_PUBLIC_DOMAIN}}
   DJANGO_SECURE_COOKIES=True
   FRONTEND_PUBLIC_URL=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
   DJANGO_SUPERUSER_USERNAME=<usuario>
   DJANGO_SUPERUSER_PASSWORD=<clave fuerte>
   DJANGO_SUPERUSER_EMAIL=<correo>
   LOAD_INITIAL_CONTENT=True
   ```

   - `GUNICORN_BIND=[::]:8000`: la red privada de Railway usa IPv6; así el backend acepta IPv4 e IPv6.
   - `RAILWAY_RUN_UID=0`: el volumen se monta con permisos de root y la imagen corre con un usuario
     sin privilegios; sin esto no se pueden guardar las imágenes subidas.
5. **Settings → Networking → Generate Domain**, puerto **8000** (para el admin de Django).
   **Settings → Deploy → Healthcheck Path** = `/api/v1/health/`.

### D.3 Frontend

1. **+ New → GitHub Repo** (Root Directory `frontend/web`, `RAILWAY_DOCKERFILE_PATH=dockerfile`)
   o **+ New → Docker Image** (`usuario/ianalytics_frontend:1.0.0`). Renombrar a `frontend`.
2. **Variables**:

   ```ini
   BACKEND_INTERNAL_URL=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:8000
   PORT=4321
   PUBLIC_SITE_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
   DJANGO_ADMIN_PUBLIC_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}/admin/
   TRUST_FORWARDED_FOR=true
   TOKEN_TTL_HOURS=12
   ```

   `PUBLIC_SITE_URL` se usa al construir (enlaces canónicos): con la opción repositorio Railway la
   pasa al build; con una imagen de Docker Hub queda el valor con que se construyó.
3. **Settings → Networking → Generate Domain**, puerto **4321**. **Healthcheck Path** = `/health`.

### D.4 Desplegar y verificar

1. **Deploy** (o aplicar los cambios en pantalla). El backend aplica migraciones, carga el
   contenido inicial y crea el administrador al iniciar.
2. Abrir el dominio del frontend (`/`, `/en/`, `/panel/`) y el del backend (`/admin/`).
3. Revisar **Deploy Logs** de cada servicio si algo falla.

### D.5 Llevar el contenido ya editado (opcional)

1. En local: `scripts/backup_database.sh`.
2. En Railway, servicio MySQL → **Settings → Networking → Public Networking** (activa
   `MYSQL_PUBLIC_URL`) y copiar host, puerto, usuario y clave.
3. Importar (reemplaza el contenido):

   ```bash
   gunzip -c backups/ianalytics_<fecha>/database.sql.gz | \
     docker run -i --rm mysql:8.4 mysql -h <host> -P <puerto> -u root -p'<clave>' railway
   ```

4. Desactivar el acceso público de MySQL. Las imágenes subidas se vuelven a cargar desde el panel.

### D.6 Dominio propio

En el servicio `frontend` → **Settings → Networking → Custom Domain** → `ianalytics.cl`, y crear
los registros `CNAME` y `TXT` que indica Railway. Para el admin, lo mismo en `backend` con
`admin.ianalytics.cl`. Actualizar `PUBLIC_SITE_URL`, `FRONTEND_PUBLIC_URL`,
`DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` y `DJANGO_ADMIN_PUBLIC_URL` con los dominios nuevos.

---

## 5. Producción con dominio y HTTPS

1. **DNS:** registros `A` de `ianalytics.cl`, `www.ianalytics.cl` y (opcional) `admin.ianalytics.cl`
   apuntando a la IP del servidor.
2. **Proxy con certificado:**
   - Opción C: el `server` de nginx de la sección 4.6 + `sudo apt install certbot python3-certbot-nginx`
     y `sudo certbot --nginx -d ianalytics.cl -d www.ianalytics.cl -d admin.ianalytics.cl`.
   - Opciones A y B: un nginx (o Caddy) en el servidor con los mismos dos `server`, apuntando a los
     puertos publicados por Docker (`127.0.0.1:4321` y `127.0.0.1:<BACKEND_PUBLISHED_PORT>`).
     En Docker la ruta `/media/` la resuelve el frontend, así que no hace falta el bloque `location /media/`.
     Para no exponer los puertos directamente, publicar en `compose.yaml` como `"127.0.0.1:4321:4321"`.
3. **Variables** (`.env` en Docker o `backend/.env` en crudo):

   ```ini
   PUBLIC_SITE_URL=https://ianalytics.cl            # Docker: reconstruir el frontend
   TRUST_FORWARDED_FOR=true                         # límite del formulario por visitante
   DJANGO_ADMIN_PUBLIC_URL=https://admin.ianalytics.cl/admin/
   DJANGO_ALLOWED_HOSTS=admin.ianalytics.cl
   DJANGO_CSRF_TRUSTED_ORIGINS=https://admin.ianalytics.cl
   DJANGO_SECURE_COOKIES=True
   DJANGO_SECURE_HSTS_SECONDS=31536000
   ```

   Dejar `DJANGO_SECURE_SSL_REDIRECT=False` si el proxy ya redirige HTTP → HTTPS.
   `TRUST_FORWARDED_FOR=true` hace que el frontend use la IP del visitante que envía el proxy;
   sin él, todas las visitas parecen venir del proxy y el límite de envíos del formulario se
   comparte entre todos. Activarlo solo si el puerto del frontend no está abierto a internet.
4. Comprobar: `https://ianalytics.cl/`, `https://ianalytics.cl/en/` y `https://admin.ianalytics.cl/admin/`.

### Lista de seguridad antes de publicar

- [ ] `DJANGO_DEBUG=False`.
- [ ] `DJANGO_SECRET_KEY` y claves de MySQL nuevas y aleatorias (no las de ejemplo).
- [ ] Clave del administrador fuerte, distinta de la usada en pruebas.
- [ ] MySQL no accesible desde internet (en Docker queda en `127.0.0.1:3307`).
- [ ] HTTPS activo y `DJANGO_SECURE_COOKIES=True`.
- [ ] Respaldo automático programado (ver abajo).
- [ ] `.env` con permisos `600` y fuera del control de versiones.

---

## 6. Operación

### Administración del contenido

**Panel de edición visual** en `/panel/` del sitio (ej. `https://ianalytics.cl/panel/`), para
cualquier usuario del staff:

| Menú | Qué hace |
|---|---|
| **Inicio** | Mensajes sin leer, contenido publicado y accesos rápidos. |
| **Editar** | La página tal como se ve, en español o inglés, con vista de escritorio, tablet o móvil. Clic en un texto para editarlo (se guarda al salir del campo); al pasar el mouse sobre fotos y botones aparecen las opciones para cambiar imágenes y enlaces; cada elemento tiene una barra para **publicar**, mover, cambiar color o eliminar, y cada sección un interruptor para mostrarla u ocultarla. Los elementos nuevos se crean **sin publicar**. |
| **Gestionar usuarios** | Lista de administradores y acceso al admin de Django para registrar nuevos (marcar **Es staff**). |
| **Salir** | Cierra la sesión. |

Los cambios se guardan al instante y se ven en el sitio público de inmediato. La sesión dura
`TOKEN_TTL_HOURS` (12 h por defecto) y se guarda en una cookie que el navegador no expone a scripts.

**Admin de Django** en `/admin/` del backend, para lo que no está en el editor visual:
mensajes de contacto completos, biblioteca de archivos, usuarios y permisos, y textos SEO
(título y descripción de la pestaña).

### Traducción automática al inglés

Por defecto está desactivada (`TRANSLATION_PROVIDER=none`): el inglés se escribe en el panel.
Para activarla con DeepL (plan gratuito de 500.000 caracteres/mes):

```ini
TRANSLATION_PROVIDER=deepl
DEEPL_API_KEY=<clave de https://www.deepl.com/pro-api>
```

Desde entonces, al guardar un texto en español se completa su versión en inglés; si alguien la
corrige a mano, esa corrección se respeta.

Para actualizar el contenido de respaldo del frontend (`frontend/web/src/i18n/*.json`):

```bash
cd frontend/web
BACKEND_INTERNAL_URL=http://localhost:8000 npm run sync_content
```

### Avisos por correo de mensajes de contacto

```ini
EMAIL_URL=smtp+tls://usuario:clave@smtp.servidor.cl:587
DEFAULT_FROM_EMAIL=no-reply@ianalytics.cl
CONTACT_NOTIFICATION_EMAILS=contacto@ianalytics.cl
```

### Usuarios del panel

```bash
# Docker
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py changepassword <usuario>
# En crudo
cd /srv/ianalytics/app/backend && sudo -u ianalytics .venv/bin/python manage.py changepassword <usuario>
```

### Respaldos y traspaso de contenido

**Docker:**

```bash
scripts/backup_database.sh                                # crea backups/ianalytics_<fecha>/
scripts/restore_database.sh backups/ianalytics_<fecha>    # REEMPLAZA el contenido actual
```

Cada respaldo contiene `database.sql.gz` (base de datos) y `media.tar.gz` (imágenes subidas).
Sirve también para llevar el contenido de un equipo a otro. Programarlo con `cron`, por ejemplo
todos los días a las 03:00:

```cron
0 3 * * * cd /ruta/a/iAnalytics && scripts/backup_database.sh >> backups/backup.log 2>&1
```

**En crudo:**

```bash
mysqldump --single-transaction --default-character-set=utf8mb4 -u ianalytics -p ianalytics | gzip > ianalytics_$(date +%F).sql.gz
tar -czf media_$(date +%F).tar.gz -C /srv/ianalytics/app/backend media
```

### Actualizar a una versión nueva

**Docker (Opción A):**

```bash
git pull
docker compose up -d --build          # las migraciones se aplican solas al iniciar
```

**Docker (Opción B):** importar o hacer `pull` de las imágenes nuevas, actualizar `IMAGE_TAG`
en `.env` y `docker compose up -d --no-build`.

**En crudo:**

```bash
cd /srv/ianalytics/app && sudo -u ianalytics git pull
cd backend && sudo -u ianalytics .venv/bin/pip install -r requirements_production.txt \
  && sudo -u ianalytics .venv/bin/python manage.py migrate \
  && sudo -u ianalytics .venv/bin/python manage.py collectstatic --noinput
cd ../frontend/web && sudo -u ianalytics npm ci \
  && sudo -u ianalytics env PUBLIC_SITE_URL=https://ianalytics.cl npm run build \
  && sudo -u ianalytics npm prune --omit=dev
sudo systemctl restart ianalytics_backend ianalytics_frontend
```

Hacer un respaldo antes de cada actualización.

### Comandos útiles (Docker)

| Acción | Comando |
|---|---|
| Ver estado | `docker compose ps` |
| Ver logs | `docker compose logs -f backend` (o `frontend`, `database`) |
| Reiniciar | `docker compose restart` |
| Detener (conserva los datos) | `docker compose down` |
| Detener y **borrar los datos** | `docker compose down -v` |
| Consola de Django | `docker compose exec backend python manage.py shell` |
| Consola de MySQL | `docker compose exec database sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"'` |

---

## 7. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `port is already allocated` al levantar | El puerto ya lo usa otro programa | Cambiar `BACKEND_PUBLISHED_PORT` / `FRONTEND_PUBLISHED_PORT` / `MYSQL_PUBLISHED_PORT` en `.env`. |
| El login del admin dice "Verificación CSRF fallida" | La dirección del panel no está en `DJANGO_CSRF_TRUSTED_ORIGINS` | Agregar la dirección exacta, con protocolo y puerto (ej. `http://localhost:8001`), y `docker compose up -d`. |
| `Bad Request (400)` al abrir el backend | El dominio no está en `DJANGO_ALLOWED_HOSTS` | Agregarlo y reiniciar. |
| El backend no queda "healthy" | MySQL no responde o la clave no coincide | `docker compose logs backend database`. Si se cambió `MYSQL_PASSWORD` después de crear el volumen, la base conserva la clave antigua: restaurar la clave o recrear con `down -v` (borra datos). |
| El sitio muestra el contenido inicial y no los cambios | El frontend no llega al backend y usa el respaldo | `docker compose logs frontend` muestra `Contenido de respaldo`; revisar que el backend esté sano. |
| Equipo o Clientes no aparecen en el sitio | No hay fichas publicadas | Marcar **publicado** en el panel. |
| Las imágenes subidas no se ven | En crudo, nginx no puede leer `backend/media/` | Revisar el `alias` y los permisos (sección 4.6). |
| Enlaces canónicos u Open Graph con el dominio incorrecto | `PUBLIC_SITE_URL` se definió después de construir | Reconstruir el frontend. |
| El formulario responde "No pudimos enviar su mensaje" | El backend no está disponible | Revisar el estado del backend. Los mensajes rechazados por exceso de envíos devuelven otro aviso (límite: `CONTACT_THROTTLE_RATE`, 5 por hora por visitante). |

---

## 8. Referencia de variables

Variables del despliegue con Docker (`.env` en la raíz). En la Opción C las del backend van en
`backend/.env` y las del frontend en el servicio de systemd.

| Variable | Por defecto | Descripción |
|---|---|---|
| `IMAGE_PREFIX` / `IMAGE_TAG` | vacío / `1.0.0` | Nombre del registro y versión de las imágenes. |
| `MYSQL_DATABASE` / `MYSQL_USER` | `ianalytics` | Base de datos y usuario. |
| `MYSQL_PASSWORD` / `MYSQL_ROOT_PASSWORD` | **obligatorias** | Claves de MySQL (solo letras y números). |
| `DJANGO_SECRET_KEY` | **obligatoria** | Clave de firma de Django. |
| `DJANGO_DEBUG` | `False` | Nunca `True` en producción. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Dominios con que se accede al backend. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `http://localhost:8000` | Direcciones desde donde se usa el panel. |
| `DJANGO_SECURE_COOKIES` / `DJANGO_SECURE_SSL_REDIRECT` / `DJANGO_SECURE_HSTS_SECONDS` | `False` / `False` / `0` | Ajustes de HTTPS. |
| `DJANGO_SUPERUSER_USERNAME` / `_PASSWORD` / `_EMAIL` | vacío | Administrador inicial (solo si no existe). |
| `LOAD_INITIAL_CONTENT` | `True` | Carga los textos iniciales si la base está vacía. |
| `PUBLIC_SITE_URL` | `https://ianalytics.cl` | Dirección pública del sitio (se aplica al construir el frontend). |
| `CONTENT_CACHE_SECONDS` | `30` | Segundos de caché del contenido en el frontend. |
| `TRUST_FORWARDED_FOR` | `false` | `true` detrás de un proxy, para limitar el formulario por visitante. |
| `DJANGO_ADMIN_PUBLIC_URL` | `http://localhost:8000/admin/` | Dirección del admin de Django que usa "Gestionar usuarios" en el panel. |
| `TOKEN_TTL_HOURS` | `12` | Horas que dura una sesión del panel. |
| `FRONTEND_PUBLIC_URL` (backend) | `PUBLIC_SITE_URL` | Destino del enlace "Ver el sitio" del admin (en Docker se toma de `PUBLIC_SITE_URL`). |
| `BACKEND_PUBLISHED_PORT` / `FRONTEND_PUBLISHED_PORT` / `MYSQL_PUBLISHED_PORT` | `8000` / `4321` / `3307` | Puertos en el equipo. |
| `GUNICORN_WORKERS` | `3` | Procesos del backend (≈ 2 × núcleos + 1). |
| `GUNICORN_BIND` | `0.0.0.0:$PORT` (u 8000) | Dirección en que escucha el backend; `[::]:8000` para IPv4 + IPv6 (Railway). |
| `TRANSLATION_PROVIDER` | `none` | `none`, `deepl` o `libretranslate`. |
| `DEEPL_API_KEY` / `LIBRETRANSLATE_URL` / `LIBRETRANSLATE_API_KEY` | vacío | Credenciales del traductor. |
| `EMAIL_URL` / `DEFAULT_FROM_EMAIL` / `CONTACT_NOTIFICATION_EMAILS` | consola / `no-reply@ianalytics.cl` / vacío | Avisos por correo. |
| `MAX_UPLOAD_SIZE_MB` | `5` | Tamaño máximo de archivos subidos. |
| `CORS_ALLOWED_ORIGINS` | vacío | Solo si otra web consume la API desde el navegador. |
