#!/usr/bin/env bash
# start-server.sh
echo "Hello from Project Vocabseditor"
echo "starting rabbitmq"
rabbitmq-server > rabbit_mq.log 1>&1 &

echo "starting celery server"
uv run celery -A vocabseditor worker -l INFO  > celery.log 2>&1 &

uv run manage.py collectstatic --no-input
if [ -n "$MIGRATE" ] ; then
    (echo "making migrations and running them"
    uv run manage.py makemigrations --no-input
    uv run manage.py migrate --no-input)
fi
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (echo "creating superuser ${DJANGO_SUPERUSER_USERNAME}" && uv run manage.py createsuperuser --no-input --noinput --email 'blank@email.com')
fi
uv run gunicorn vocabseditor.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3 --timeout 600 & nginx -g "daemon off;"