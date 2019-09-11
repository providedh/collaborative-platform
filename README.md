#Running Collaborative Platform in production environment

##1. copy this repository to a server on which the platform will run
```git clone https://github.com/providedh/collaborative-platform```

##2. install pip
```sudo apt update && sudo apt upgrade && sudo apt install python3-pip```

##3. install requirements via pip
```
cd collaborative-platform
sudo pip3 install -r requirements.txt
sudo pip3 install uwsgi
```

##4. install external packages
```
sudo apt install postgresql
sudo systemctl enable postgresql && sudo systemctl start postgresql

sudo apt install apt-transport-https
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
add-apt-repository "deb https://artifacts.elastic.co/packages/7.x/apt stable main"

sudo apt update
sudo apt install elasticsearch
sudo systemctl enable elasticsearch && sudo systemctl start elasticsearch

sudo apt install redis-server
sudo systemctl enable redis-server && sudo systemctl start redis-server

sudo apt install nginx
sudo systemctl enable nginx && sudo systemctl start nginx
```

##5. create postgres database
```
sudo su postgres
psql
CREATE DATABASE collaborative_platform;
CREATE USER collaborative_platform WITH PASSWORD 'here_insert_the_password';
GRANT ALL PRIVILEGES ON DATABASE collaborative_platform TO collaborative_platform;
\q
exit
```

##6. populate database with tables
```
cd src/collaborative_platform
python3 manage.py makemigrations
python3 manage.py migrate
```
then connect to database and in table django_site fill first row with correct domain and name for instance of the server.

##7. initialize ElasticSearch indexes
```
python3 manage.py shell
from apps.index_and_search.models import *
from elasticsearch_dsl import connections
connections.create_connection()
Person.init()
Event.init()
Organization.init()
Place.init()
User.init()
exit()
```

##8. in /etc/nginx/sites-enabled/ create file collaborative_platform_nginx.conf with following content:
```
upstream django {
    server unix:///home/ubuntu/collaborative-platform/src/collaborative_platform/collaborative_platform.sock; # for a file socket
}

server {
    listen      80;
    server_name providedh.ehum.psnc.pl;
    return  301 https://$host$request_uri;
}

# configuration of the server
server {
    # the port your site will be served on
    listen      443 ssl http2;
    # the domain name it will serve for
    server_name providedh.ehum.psnc.pl; # substitute your machine's IP address or FQDN
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;   # adjust to taste

    # Django media
    location /media  {
        alias /home/ubuntu/collaborative_platform/media;  # your Django project's media files - amend as required
    }

    location /static {
        alias /home/ubuntu/collaborative-platform/src/collaborative_platform/static; # your Django project's static files - amend as required
    }

    # Finally, send all non-media requests to the Django server.
    location / {
        uwsgi_pass  django;
        include     /home/ubuntu/collaborative-platform/src/collaborative_platform/uwsgi_params; # the uwsgi_params file you installed
    }
    ssl_certificate_key /etc/ssl/private.pem;
    ssl_certificate     /etc/ssl/certs.pem;

    ssl_protocols TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256';
    ssl_prefer_server_ciphers on;

    add_header Strict-Transport-Security max-age=31536000;

}

```
adjust domain and paths in above config, copy SSL certs to /etc/ssl/.

restart nginx:
```
sudo systemctl restart nginx
```

##9. prepare settings:
At first copy settings template to same location byt without _template suffix:
```
cp src/collaborative_platform/collaborative_platform/settings.py_template src/collaborative_platform/collaborative_platform/settings.py
```
then fill settings file with keys to social media auth, credentials to database, and add domain to allowed_hosts. Set paths for files storage.

##10. run uwsgi:
go to src/collaborative_platform
```
screen uwsgi --socket /home/ubuntu/collaborative-platform/src/collaborative_platform/collaborative_platform.sock --chmod-socket=666 --module collaborative_platform.wsgi
```
and detach from screen session by pressing ctrl+a, ctrl+d

##Congrats, your environment should be working now.