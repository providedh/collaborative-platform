FROM python:3
ENV PYTHONUNBUFFERED 1
#ENV PG_MAJOR 11
#ENV POSTGISV 2.5
#
RUN apt update
RUN apt install -y --no-install-recommends binutils libproj-dev gdal-bin
#RUN apt install -y --no-install-recommends binutils libproj-dev gdal-bin \
#    postgresql-$PG_MAJOR-postgis-$POSTGISV \
#    postgresql-$PG_MAJOR-postgis-$POSTGISV-scripts \
#    postgresql-server-dev-$PG_MAJOR

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_lg
EXPOSE 8000
EXPOSE 8001
STOPSIGNAL SIGINT

COPY . /code/
RUN chgrp -R 0 /code && chmod -R g=u /code
ENTRYPOINT ["./startup.sh"]
