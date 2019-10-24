FROM postgres
ENV POSTGISV 2.5

RUN apt update
RUN apt install -y --no-install-recommends \
    postgresql-$PG_MAJOR-postgis-$POSTGISV \
    postgresql-$PG_MAJOR-postgis-$POSTGISV-scripts \
    postgresql-server-dev-$PG_MAJOR

# add init script
RUN mkdir -p /docker-entrypoint-initdb.d
COPY ./initdb-postgis.sh /docker-entrypoint-initdb.d/postgis.sh