#!/bin/sh

set -e

# Perform all actions as $POSTGRES_USER
export PGUSER="$POSTGRES_USER"

# create databases
psql -c "CREATE DATABASE collaborative_platform;"

# add extensions to databases
psql gis -c "CREATE EXTENSION IF NOT EXISTS postgis;"