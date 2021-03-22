FROM nginx:latest

RUN rm /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -rf /docker-entrypoint.d
COPY kubernetes/nginx/nginx.conf /etc/nginx/
COPY kubernetes/nginx/collaborative_platform_nginx.conf /etc/nginx/sites-enabled/

EXPOSE 8080
EXPOSE 8443
