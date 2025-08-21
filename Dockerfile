FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install nginx vim postgresql-common libpq-dev python3-gdal rabbitmq-server -y
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

COPY nginx.default /etc/nginx/sites-available/default

# copy source and install dependencies
RUN mkdir -p /opt/app
COPY . /opt/app
WORKDIR /opt/app
RUN uv sync --no-install-project
RUN chown -R www-data:www-data /opt/app && chmod -R 755 /opt/app/media

# start server
EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]