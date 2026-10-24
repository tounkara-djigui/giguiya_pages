#!/bin/bash
# Starts PostgreSQL with its data stored inside /app so it survives container restarts.
set -e
PGBIN=/usr/lib/postgresql/15/bin
PGDATA=/app/.pgdata
DB_USER=giguiya
DB_PASS=giguiya_pg_2026
DB_NAME=giguiya

mkdir -p "$PGDATA" /var/run/postgresql
chown -R postgres:postgres "$PGDATA" /var/run/postgresql
chmod 700 "$PGDATA"

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  su postgres -c "$PGBIN/initdb -D $PGDATA -U postgres --auth-local=trust --auth-host=scram-sha-256"
fi

(
  until su postgres -c "$PGBIN/pg_isready -h /var/run/postgresql -q"; do sleep 1; done
  su postgres -c "psql -h /var/run/postgresql -tc \"SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'\"" | grep -q 1 \
    || su postgres -c "psql -h /var/run/postgresql -c \"CREATE USER $DB_USER WITH PASSWORD '$DB_PASS'\""
  su postgres -c "psql -h /var/run/postgresql -tc \"SELECT 1 FROM pg_database WHERE datname='$DB_NAME'\"" | grep -q 1 \
    || su postgres -c "psql -h /var/run/postgresql -c \"CREATE DATABASE $DB_NAME OWNER $DB_USER\""
) &

exec su postgres -c "$PGBIN/postgres -D $PGDATA -c listen_addresses=localhost -c port=5432 -c unix_socket_directories=/var/run/postgresql"
