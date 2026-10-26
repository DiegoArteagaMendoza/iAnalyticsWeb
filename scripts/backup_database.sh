#!/usr/bin/env bash
# Respalda el contenido del sitio: base de datos MySQL + archivos subidos (imágenes).
# Crea backups/ianalytics_<fecha>/{database.sql.gz, media.tar.gz}
# Sirve también para compartir el contenido ya cargado con otro equipo.
# Uso (con los contenedores levantados): scripts/backup_database.sh
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

timestamp="$(date +%Y%m%d_%H%M%S)"
backup_dir="backups/ianalytics_${timestamp}"
mkdir -p "$backup_dir"

echo "==> Respaldando la base de datos"
docker compose exec -T database sh -c \
    'exec mysqldump --user=root --password="$MYSQL_ROOT_PASSWORD" --single-transaction --routines --triggers --default-character-set=utf8mb4 "$MYSQL_DATABASE"' \
    | gzip > "$backup_dir/database.sql.gz"

echo "==> Respaldando los archivos subidos"
docker compose exec -T backend tar -czf - -C /app media > "$backup_dir/media.tar.gz"

echo "Respaldo listo: $backup_dir"
ls -lh "$backup_dir"
