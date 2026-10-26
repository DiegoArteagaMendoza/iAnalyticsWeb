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
cp docs/leeme_paquete.md "$bundle_dir/leeme.md"

# Contenido actual de la página (si el sitio está corriendo). Solo las tablas de contenido:
# se excluyen usuarios, contraseñas, tokens, sesiones, mensajes de contacto y tablas internas.
if docker compose "${env_args[@]}" ps --status running --services 2>/dev/null | grep -qx database; then
    echo "==> Incluyendo el contenido actual (sin usuarios ni mensajes)"
    mkdir -p "$bundle_dir/contenido"
    docker compose "${env_args[@]}" exec -T database sh -c '
        tables=$(mysql --user=root --password="$MYSQL_ROOT_PASSWORD" -N -e "SHOW TABLES" "$MYSQL_DATABASE" 2>/dev/null \
            | grep -vE "^(auth_|authtoken_|django_)|^contact_contactmessage$")
        exec mysqldump --user=root --password="$MYSQL_ROOT_PASSWORD" --single-transaction \
            --default-character-set=utf8mb4 "$MYSQL_DATABASE" $tables 2>/dev/null' \
        | gzip > "$bundle_dir/contenido/database.sql.gz"
    docker compose "${env_args[@]}" exec -T backend tar -czf - -C /app media > "$bundle_dir/contenido/media.tar.gz"
else
    echo "==> El sitio no está corriendo: el paquete parte con el contenido inicial"
fi
cp scripts/import_images.sh scripts/backup_database.sh scripts/restore_database.sh "$bundle_dir/scripts/"

echo "==> Paquete listo: $bundle_dir"
du -sh "$bundle_dir"/*.tar.gz
cat <<EOF

En el otro equipo:
  cd ianalytics_${image_tag}
  scripts/import_images.sh ianalytics_images_${image_tag}.tar.gz
  cp .env.example .env   # completar claves
  docker compose up -d --no-build
  scripts/restore_database.sh contenido   # si el paquete trae contenido
(instrucciones completas en leeme.md)
EOF
