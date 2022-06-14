# Run the project on the local environment
Required environment:
- python >=3.6
- virtual environment

## Create a virtual environment

```sh
# For me i'm using virtualenv
virtualenv -p python3 env
source env/bin/activate
```

## Install python packages
Since this is a simple project, i will not separate to dev and prod requirements
```sh
pip install -r requirements.txt
```

## Create database, run the migration
This step will apply the migrations, seed initial areas, categories and create random doctor data.
```sh
alembic upgrade heads
python scripts/initial.py
```

## Start the server
```sh
uvicorn main:app --reload --port 8006 --host 0.0.0.0
```

## Run test

This test runner will help create a test data, apply the migration, seed data and run test with pytest.
```sh
bash tests.sh
```
