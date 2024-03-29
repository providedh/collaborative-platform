# Collaborative Platform

[1. Running Collaborative Platform for development with Docker](#1-running-collaborative-platform-for-development-with-docker) <br>
[2. Running Collaborative Platform for development without Docker](#2-running-collaborative-platform-for-development-without-docker) <br>
[3. Running Collaborative Platform in production environment](#3-running-collaborative-platform-in-production-environment) <br>
[4. Useful commands](#4-useful-commands) <br>
[5. Common problems](#5-common-problems) <br>


## 1. Running Collaborative Platform for development with Docker

### 1.0. Install & run docker, docker-compose and add yourself to docker group to allow executing docker command without sudo
* Before installing any new packets, it is recommended to perform full system update  
`$ yay -Syu`  
and reboot, to load any changed kernel modules.  
* Then, we'll install docker and docker-compose on our system:  
`$ yay -S docker docker-compose`  
* To enable docker on system start, run:
`# systemctl enable docker`
* Then, to start docker right now:
`#systemctl start docker`
* To enable access to docker commands without using sudo, we'll add ourselves to _docker_ group:
```
$ sudo usermod -aG docker $USER
```
  then logout and login to get our permissions reevaluated.
  
### 1.1. clone this repository and go to created directory
```
$ git clone https://github.com/providedh/collaborative-platform`
$ cd collaborative-platform`
```

### 1.2. prepare settings file
```
cp src/collaborative_platform/collaborative_platform/settings.py_template src/collaborative_platform/collaborative_platform/settings.py
```
then edit `settings.py` – comment out these lines:
```
RECAPTCHA_PUBLIC_KEY = 'put_public_key_here'
RECAPTCHA_PRIVATE_KEY = 'put_private_key_here'
```

and uncomment this line:

`SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']`

to disable captcha on register.

it is advised to go trough the content of settings file and possibly tweak some settings, like media storage paths.

### 1.3. go to project directory and build project
```docker-compose build```
>note: this command has to be re-run after each change in `requirements.txt`

### 1.4. (optional) open PyCharm and open the project in it
* Open settings and go to Build, Execution, Deployment -> Docker
* If there are no docker machines add one, default settings should prefer connecting by Unix socket, if not, select it.
* Then go to File | Settings | Project: collaborative-platform | Project Interpreter
* in interpreters list click on "Show All"
* click on the plus sign on the right side of the window, and add a configuration according to a screenshot below:
 [](https://github.com/providedh/collaborative-platform/blob/master/interpreter_conf.png?raw=true)
* pick the newly-created interpreter and add path mapping: `collaborative-platform (Project Root)` to `/code`

Now we've configured interpreter, and after pycharm finishes it's processing we should be able to use configurations pulled from git.

### 1.5. initialize databases
To initialize databases simply run following configurations in PyCharm in this exact order:
```
makemigrations
migrate
initialize ES
load fixtures
``` 

OR, in project directory run the following commands:
```
docker-compose run web python src/collaborative_platform/manage.py makemigrations
docker-compose run web python src/collaborative_platform/manage.py migrate
docker-compose run web python src/collaborative_platform/manage.py shell -c "from apps.index_and_search.initialize import initialize; initialize()"
docker-compose run web python src/collaborative_platform/manage.py loaddata core_initial.json
```

### 1.6. Done
to run or debug project use `runserver 8000` configuration. There is also a `web` configuration included in git. It allows to run PyCharm docker extensions and get logs from all containers in those. It can be used to run (but not debug) project instead of `runserver 8000`.

If not using pycharm you can use `docker-compose up` or more verbose 
```
docker-compose run web python src/collaborative_platform/manage.py runserver 0.0.0.0:8000
```


## 2. Running Collaborative Platform for development without Docker
Based on Ubuntu 20.04 LTS.

### 2.1. PostgreSQL installation
Add a PostgreSQL repository (for PostGIS version 2.5):
```
sudo apt-get install gnupg2
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
```

Update the list of packages:
```
sudo apt-get update
```

Install PostgreSQL with the PostGIS extension:
```
sudo apt-get install postgresql-12
sudo apt-get install postgresql-12-postgis-2.5
```

Install the packages required by PostGIS:
```
sudo apt-get install binutils libproj-dev gdal-bin
```

### 2.2. Database configuration
Switch to a `postgres` user:
```
sudo su - postgres
```

Create a new user:
```
createuser providedh_pg_user
```

Create a new database:
```
createdb providedh_db
```

Add a password for a new user:
```
psql -c "alter user providedh_pg_user with encrypted password '<your password here>';"
```

Add database permissions to a user:
```
psql -c "grant all privileges on database providedh_db to providedh_pg_user;"
```

Open a database:
```
psql providedh_db
```

Add the PostGIS extension:
```
CREATE EXTENSION postgis;
```

Close a database:
```
\q
```

Switch to a default user:
```
exit
```

### 2.3. Redis installation
Add the Redis repository (for Redis version 6):
```
sudo add-apt-repository ppa:chris-lea/redis-server
```

Update the list of packages:
```
sudo apt-get update
```

Install Redis:
```
sudo apt-get install redis-server
```

Enable start of Redis on boot:
```
sudo systemctl enable redis-server.service
```

### 2.4. Elasticsearch installation
Add the Elasticsearch repository:
```
curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
```

Update the list of packages:
```
sudo apt-get update
```

Install Elasticsearch:
```
sudo apt-get install elasticsearch
```

Enable start of Elasticsearch on boot:
```
sudo systemctl enable elasticsearch.service 
```

Start Elasticsearch:
```
sudo systemctl start elasticsearch.service 
```

### 2.5. Virtual environment creation
Add the required package:
```
sudo apt-get install python3.8-venv
```

Create a virtual environment:
```
python3 -m venv /path/to/venvs/collaborative-platform/
```

Activate a virtual environment:
```
source /path/to/venvs/collaborative-platform/bin/activate
```

### 2.6. Cloning the repository
Go to a target directory and clone the repository:
```
cd /path/to/project/
git clone https://github.com/providedh/collaborative-platform.git
```

Go to the project directory:
```
cd collaborative_platform/
```

### 2.7. Dependencies installation
Install required packages:
```
sudo apt-get install g++ python3-dev
```

Install dependencies:
```
pip install -r requirements.txt
```
Make sure there are no errors and all dependencies are installed correctly. If in doubt, you can run the command again.

Download library for `spacy` module:
```
python -m spacy download en_core_web_lg
```

### 2.8. Setting up `settings.py` file

These settings apply to local development only. When deploying the application, adjust the settings according to 
the requirements of the production environment.

Make local copy of `settings.py` file:
```
cp src/collaborative_platform/collaborative_platform/settings_template.py src/collaborative_platform/collaborative_platform/settings.py
```

#### 2.8.1. In `settings.py` file:

Turn on debugging:
```
DEBUG = True
```

Set up hosts:
```
ES_HOST = 'localhost'
POSTGRES_HOST = 'localhost'
REDIS_HOST = 'localhost'
```

Turn off (comment) csp middleware:
```
MIDDLEWARE = [
    ...
    # 'csp.middleware.CSPMiddleware',
    ...
]
```

Set up database access:
```
DATABASES = {
    'default': {
        ...
        'NAME': 'providedh_db',
        'USER': 'providedh_pg_user',
        'PASSWORD': '<your password here>',
        ...
    }
}
```

Turn off (comment) ReCaptcha keys:
```
# RECAPTCHA_PUBLIC_KEY = 'put_public_key_here'
# RECAPTCHA_PRIVATE_KEY = 'put_private_key_here'
```

Add (uncomment) system check exception:
```
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
```

## 2.9. Application initialization
Go to source code directory:
```
cd src/collaborative_platform/
```

Create and apply migrations:
```
python manage.py makemigrations
python manage.py migrate
```

Initialize Elasticsearch:
```
python manage.py shell -c "from apps.index_and_search.initialize import initialize; initialize()"
```

Load initial data to database:
```
python manage.py loaddata core_initial.json
```

## 2.10. Running application

Run Django server:
```
python manage.py runserver
```
The running server is available at http://127.0.0.1:8000/


## 3. Running Collaborative Platform in production environment

### 3.1. copy this repository to a server on which the platform will run
```git clone https://github.com/providedh/collaborative-platform```

### 3.2. install pip
```sudo apt update && sudo apt upgrade && sudo apt install python3-pip```

### 3.3. install requirements via pip
```
cd collaborative-platform
sudo pip3 install -r requirements.txt
sudo pip3 install uwsgi
sudo pip3 install daphne
```

### 3.4. install external packages
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

### 3.5. create postgres database
```
sudo su postgres
psql
CREATE DATABASE collaborative_platform;
CREATE USER collaborative_platform WITH PASSWORD 'here_insert_the_password';
GRANT ALL PRIVILEGES ON DATABASE collaborative_platform TO collaborative_platform;
\q
exit
```

### 3.6. populate database with tables
```
cd src/collaborative_platform
python3 manage.py makemigrations
python3 manage.py migrate
```
then connect to database and in table django_site fill first row with correct domain and name for instance of the server.

### 3.7. initialize ElasticSearch indexes
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

### 3.8. in /etc/nginx/sites-enabled/ create file collaborative_platform_nginx.conf with following content:
```
upstream django {
    server unix:///home/ubuntu/collaborative-platform/src/collaborative_platform/collaborative_platform.sock;
}

upstream ws {
    server unix:///home/ubuntu/collaborative-platform/src/collaborative_platform/collaborative_platform_websockets.sock;
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
        alias /home/ubuntu/collaborative_platform/static; # your Django project's static files - amend as required
    }

    location /ws/ {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_pass http://ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
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

### 3.9. prepare settings:
At first copy settings template to same location byt without _template suffix:
```
cp src/collaborative_platform/collaborative_platform/settings.py_template src/collaborative_platform/collaborative_platform/settings.py
```
then fill settings file with keys to social media auth, credentials to database, and add domain to allowed_hosts. Set paths for files storage.

### 3.10. run uwsgi and daphne:
go to src/collaborative_platform
```
screen uwsgi --socket /home/ubuntu/collaborative-platform/src/collaborative_platform/collaborative_platform.sock --chmod-socket=666 --module collaborative_platform.wsgi
```
and detach from screen session by pressing ctrl+a, ctrl+d

then
```
screen daphne -u collaborative_platform_websockets.sock collaborative_platform.asgi:application
```
and like before, detach by pressing ctrl+a, ctrl+d.

### Congrats, your environment should be working now.


## 4. Useful commands
```
docker system prune -a
docker volume prune

docker-compose run web python src/collaborative_platform/manage.py [migrate|makemigrations|shell|...]
docker-compose run web python src/collaborative_platform/manage.py loaddata core_initial.json
```


## 5. Common problems
Collect statics while updating production server, or else .js files will be out of date and annotator probably won't work!
