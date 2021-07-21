#!/usr/bin/env bash

pip install -r requirements.txt

while ! pg_isready -q -h $PGHOST -p $PGPORT -U $PGUSER
do
  echo "$(date) - waiting for database to start"
  sleep 2
done

# Create database if it doesn't exist.
if [[ -z `psql -Atqc "\\list $PGDATABASE"` ]]; then
  echo "Database $PGDATABASE does not exist. Creating..."
  createdb -E UTF8 $PGDATABASE -l en_US.UTF-8 -T template0
  echo "Database $PGDATABASE created."
fi


# Create database if it doesn't exist.
if [[ -z `psql -Atqc "\\list $PGDATABASETEST"` ]]; then
  echo "Database $PGDATABASETEST does not exist. Creating..."
  createdb -E UTF8 $PGDATABASETEST -l en_US.UTF-8 -T template0
  echo "Database $PGDATABASETEST created."
fi

export FLASK_APP="manage.py"
export FLASK_DEBUG=1

echo db init
flask db init
echo db migrate
flask db migrate
echo db upgrade
flask db upgrade

pytest

flask run -h 0.0.0.0 -p 5000
