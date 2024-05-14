## Run Integration Tests

### Step 1: Set up config toml (env variables) used in 'alembic.ini'

```commandline
    export user="it_etl_user"
    export password="it_etl_password"
    export host="localhost"
    export port=5432
    export database="it_etl_yahoo_search_engine"
```

### Step 2: Create database + it_etl_user

```commandline
CREATE DATABASE it_etl_yahoo_search_engine;
CREATE USER it_etl_user WITH PASSWORD 'it_etl_password';
GRANT ALL PRIVILEGES ON DATABASE it_etl_yahoo_search_engine TO it_etl_user;
```

### Step 3: Use alembic to create integration test tables and database

```commandline
alembic upgrade head
```

### Step 4: Run the integration tests

```commandline
pytest -p no:asyncio --max-asyncio-tasks 1 integration_tests
```