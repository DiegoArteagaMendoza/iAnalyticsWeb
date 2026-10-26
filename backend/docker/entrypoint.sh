#!/bin/sh
# Arranque del contenedor del backend:
# espera la base de datos, aplica migraciones, carga el contenido inicial
# (solo si la base está vacía) y crea el administrador si se definió.
set -e

python manage.py wait_for_database --timeout "${DATABASE_WAIT_TIMEOUT:-90}"
python manage.py migrate --noinput

if [ "${LOAD_INITIAL_CONTENT:-True}" = "True" ]; then
    python manage.py load_initial_content
fi

python manage.py ensure_superuser

exec "$@"
