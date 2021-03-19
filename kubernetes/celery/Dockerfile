FROM python:3
ENV PYTHONUNBUFFERED 1

RUN apt update
RUN apt install -y --no-install-recommends binutils libproj-dev gdal-bin \
    postgresql-$PG_MAJOR-postgis-$POSTGISV \
    postgresql-$PG_MAJOR-postgis-$POSTGISV-scripts \
    postgresql-server-dev-$PG_MAJOR

WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_lg
STOPSIGNAL SIGINT

#ENTRYPOINT ["cd /app/src/collaborative_platform && celery -A collaborative_platform worker -B -l DEBUG -E'"]
ENTRYPOINT ["ls /"]
