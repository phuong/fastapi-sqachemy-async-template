#!/bin/bash
set -e

export DB_DATABASE=necktie.test
echo "Applying the new migrations..."
alembic upgrade heads

# Seeding the test data...
python scripts/initial.py

echo "Running tests..."
pytest -s -vv -x tests/
