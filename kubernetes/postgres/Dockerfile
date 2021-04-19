FROM postgres:13.1
ENV POSTGISV 2.5

RUN apt update
RUN apt install -y --no-install-recommends \
    postgresql-$PG_MAJOR-postgis-$POSTGISV \
    postgresql-$PG_MAJOR-postgis-$POSTGISV-scripts \
    postgresql-server-dev-$PG_MAJOR openssh-client

# add init script
RUN mkdir -p /docker-entrypoint-initdb.d
COPY kubernetes/postgres/initdb-postgis.sh /docker-entrypoint-initdb.d/postgis.sh

RUN useradd -r -u 1001 -g appuser appuser
USER appuser

EXPOSE 5432