#!/usr/bin/env bash
# Restaura un respaldo creado con backup_database.sh (REEMPLAZA el contenido actual).
# Uso (con los contenedores levantados): scripts/restore_database.sh backups/ianalytics_<fecha>
set -euo pipefail

backup_dir="${1:?Indicar la carpeta del respaldo, ej: backups/ianalytics_20261025_120000}"
backup_dir="$(cd "$backup_dir" && pwd)"
cd "$(dirname "${BASH_SOURCE[0]}")/.."

[ -f "$backup_dir/database.sql.gz" ] || { echo "No se encontró $backup_dir/database.sql.gz" >&2; exit 1; }

read -r -p "Esto reemplaza la base de datos y las imágenes actuales. ¿Continuar? [s/N] " answer
[ "$answer" = "s" ] || [ "$answer" = "S" ] || { echo "Cancelado."; exit 0; }

echo "==> Restaurando la base de datos"
gunzip -c "$backup_dir/database.sql.gz" | docker compose exec -T database sh -c \
    'exec mysql --user=root --password="$MYSQL_ROOT_PASSWORD" --default-character-set=utf8mb4 "$MYSQL_DATABASE"'

if [ -f "$backup_dir/media.tar.gz" ]; then
    echo "==> Restaurando los archivos subidos"
    docker compose exec -T backend sh -c 'rm -rf /app/media/* && tar -xzf - -C /app' < "$backup_dir/media.tar.gz"
fi

echo "Restauración completa."
