#!/bin/sh

# process signals
trap 'exit' INT TERM
trap 'kill 0' EXIT

echo "Waiting for PostgreSQL..."
while ! nc -z pgdb 5434; do
  sleep 0.1
done
echo "Done with PostgreSQL"

exec uvicorn auth.main:app --host 0.0.0.0 --port 8083 --reload