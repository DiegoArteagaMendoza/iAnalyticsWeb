#!/usr/bin/env bash
# Construye y publica las imágenes en un registro (Docker Hub, GitHub Container Registry, etc.).
# Requiere en .env: IMAGE_PREFIX con el usuario u organización y la barra final.
#   Docker Hub: IMAGE_PREFIX=usuario/
#   GitHub:     IMAGE_PREFIX=ghcr.io/usuario/
# Antes: docker login   (o docker login ghcr.io)
# Uso: scripts/push_images.sh
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

[ -f .env ] || { echo "Falta el archivo .env (copiar desde .env.example)" >&2; exit 1; }
image_prefix="$(grep -E '^IMAGE_PREFIX=' .env | cut -d= -f2 || true)"
if [ -z "$image_prefix" ]; then
    echo "Definir IMAGE_PREFIX en .env (ej: IMAGE_PREFIX=usuario/)" >&2
    exit 1
fi

MYSQL_PASSWORD=build MYSQL_ROOT_PASSWORD=build DJANGO_SECRET_KEY=build docker compose --env-file .env build
MYSQL_PASSWORD=build MYSQL_ROOT_PASSWORD=build DJANGO_SECRET_KEY=build docker compose --env-file .env push

echo "Imágenes publicadas. En otro equipo basta con compose.yaml + .env y: docker compose pull && docker compose up -d"
