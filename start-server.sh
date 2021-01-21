#!/usr/bin/env bash
# start-server.sh
echo "hallo"
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (echo "creating superuser ${DJANGO_SUPERUSER_USERNAME}" && python vocabseditor/manage.py createsuperuser --no-input --noinput --email 'blank@email.com' --settings=vocabseditor.settings.docker)
fi
cd vocabseditor && python manage.py collectstatic --no-input --settings=vocabseditor.settings.docker &&
python manage.py migrate --no-input --settings=vocabseditor.settings.docker &&
gunicorn vocabseditor.wsgi_docker --user www-data --bind 0.0.0.0:8010 --workers 3 & nginx -g "daemon off;"
