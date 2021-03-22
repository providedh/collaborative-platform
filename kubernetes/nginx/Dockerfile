FROM nginx:latest

COPY kubernetes/nginx/nginx.conf /etc/nginx/nginx.conf
COPY kubernetes/nginx/collaborative_platform_nginx.conf /etc/nginx/sites-enabled/collaborative_platform_nginx.conf

RUN chgrp -R 0 /etc && chmod -R g=u /etc
RUN chgrp -R 0 /var && chmod -R g=u /var

EXPOSE 80
EXPOSE 443
