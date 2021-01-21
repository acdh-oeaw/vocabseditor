FROM csae8092/djangobaseimage

# install nginx
RUN apt-get update -y && apt-get upgrade -y
COPY nginx.default /etc/nginx/sites-available/default

# copy source and install dependencies
RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/vocabseditor
COPY requirements.txt start-server.sh /opt/app/
COPY . /opt/app/vocabseditor/
WORKDIR /opt/app
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install gunicorn --no-cache-dir
RUN chown -R www-data:www-data /opt/app

# start server
EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]