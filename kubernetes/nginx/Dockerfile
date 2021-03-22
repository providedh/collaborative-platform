FROM nginx:latest

COPY kubernetes/nginx/nginx.conf /etc/nginx/
COPY kubernetes/nginx/collaborative_platform_nginx.conf /etc/nginx/sites-enabled/

RUN rm -rf /docker-entrypoint.d
RUN chgrp -R 0 /etc && chmod -R g=u /etc
RUN chgrp -R 0 /var && chmod -R g=u /var

EXPOSE 8080
EXPOSE 8443

ENTRYPOINT ["cat", "/etc/nginx/nginx.conf"]