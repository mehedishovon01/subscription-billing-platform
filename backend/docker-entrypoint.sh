#!/usr/bin/env bash
set -e

uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput
if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ]; then
  uv run python manage.py ensure_adminuser \
    --email="$DJANGO_SUPERUSER_EMAIL" \
    --password="$DJANGO_SUPERUSER_PASSWORD"
fi

exec "$@"
