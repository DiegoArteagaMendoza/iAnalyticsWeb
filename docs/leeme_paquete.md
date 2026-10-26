# Sitio iAnalytics · cómo verlo en tu equipo

Este paquete trae el sitio completo (página, panel de edición y base de datos) listo para
correr con Docker. No necesitas el código fuente.

## Qué necesitas

- **Docker Desktop** (Windows, Mac o Linux): https://www.docker.com/products/docker-desktop/
  Ábrelo y espera a que diga que está funcionando.
- Unos 3 GB libres en disco.

> En Mac con chip Apple (M1/M2/M3…) funciona, aunque más lento, porque las imágenes son para
> procesadores Intel/AMD.

## Pasos

Abre una terminal en esta carpeta (en Windows, usa **Git Bash** o **WSL**) y ejecuta:

```bash
# 1. Cargar las imágenes (una sola vez; tarda un par de minutos)
scripts/import_images.sh ianalytics_images_1.0.0.tar.gz

# 2. Crear la configuración
cp .env.example .env
```

Abre `.env` con un editor de texto y cambia estas líneas (solo letras y números en las claves):

```ini
MYSQL_PASSWORD=unaClaveCualquiera123
MYSQL_ROOT_PASSWORD=otraClaveCualquiera456
DJANGO_SECRET_KEY=escribeAquiUnTextoLargoYAleatorio1234567890
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=laClaveConQueEntrarasAlPanel
```

```bash
# 3. Encender el sitio (la primera vez tarda ~1 minuto)
docker compose up -d --no-build

# 4. Cargar el contenido actual de la página (responder "s")
scripts/restore_database.sh contenido
```

## Ver el sitio

| Qué | Dirección |
|---|---|
| Página en español | http://localhost:4321/ |
| Página en inglés | http://localhost:4321/en/ |
| Panel de edición | http://localhost:4321/panel/ (usuario y clave de `DJANGO_SUPERUSER_*`) |

## Apagar y volver a encender

```bash
docker compose down        # apagar (los datos se conservan)
docker compose up -d       # volver a encender
docker compose down -v     # apagar y BORRAR todo el contenido
```

## Si algo falla

- **"port is already allocated"**: otro programa usa ese puerto. En `.env` cambia
  `FRONTEND_PUBLISHED_PORT` (ej. `4400`), `BACKEND_PUBLISHED_PORT` (ej. `8002`) o
  `MYSQL_PUBLISHED_PORT` (ej. `3310`) y vuelve a ejecutar `docker compose up -d --no-build`.
- **La página no carga**: espera un minuto y revisa `docker compose ps` (los tres servicios deben
  decir *healthy*). Para ver el detalle: `docker compose logs backend`.
