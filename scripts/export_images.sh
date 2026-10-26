#!/usr/bin/env bash
# Construye las imágenes y las exporta a un paquete para compartir sin registro:
#   dist/ianalytics_<tag>/
#     ├── ianalytics_images_<tag>.tar.gz   (frontend + backend + base de datos)
#     ├── compose.yaml
#     ├── .env.example
#     └── scripts/                          (importar, respaldar, restaurar)
# Uso: scripts/export_images.sh
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

env_args=()
[ -f .env ] && env_args=(--env-file .env)
image_tag="$(grep -E '^IMAGE_TAG=' .env 2>/dev/null | cut -d= -f2 || true)"
image_tag="${image_tag:-1.0.0}"
image_prefix="$(grep -E '^IMAGE_PREFIX=' .env 2>/dev/null | cut -d= -f2 || true)"

backend_image="${image_prefix}ianalytics_backend:${image_tag}"
database_image="${image_prefix}ianalytics_database:${image_tag}"
frontend_image="${image_prefix}ianalytics_frontend:${image_tag}"
bundle_dir="dist/ianalytics_${image_tag}"

echo "==> Construyendo ${frontend_image}, ${backend_image} y ${database_image}"
MYSQL_PASSWORD=build MYSQL_ROOT_PASSWORD=build DJANGO_SECRET_KEY=build \
    docker compose "${env_args[@]}" build

echo "==> Exportando imágenes"
rm -rf "$bundle_dir"
mkdir -p "$bundle_dir/scripts"
docker save "$frontend_image" "$backend_image" "$database_image" | gzip > "$bundle_dir/ianalytics_images_${image_tag}.tar.gz"

cp compose.yaml .env.example "$bundle_dir/"
cp scripts/import_images.sh scripts/backup_database.sh scripts/restore_database.sh "$bundle_dir/scripts/"

echo "==> Paquete listo: $bundle_dir"
du -sh "$bundle_dir"/*.tar.gz
cat <<EOF

En el otro equipo:
  cd ianalytics_${image_tag}
  scripts/import_images.sh ianalytics_images_${image_tag}.tar.gz
  cp .env.example .env   # completar claves
  docker compose up -d --no-build
EOF
