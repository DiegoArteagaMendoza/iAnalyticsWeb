#!/usr/bin/env bash
# Importa las imágenes exportadas con export_images.sh.
# Uso: scripts/import_images.sh ianalytics_images_<tag>.tar.gz
set -euo pipefail

archive="${1:?Indicar el archivo .tar.gz con las imágenes}"
[ -f "$archive" ] || { echo "No existe el archivo: $archive" >&2; exit 1; }

gunzip -c "$archive" | docker load
echo "Imágenes importadas. Siguiente paso: cp .env.example .env && docker compose up -d --no-build"
