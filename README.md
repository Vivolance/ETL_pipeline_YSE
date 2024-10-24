# ETL pipeline for yahoo_search_engine


![image](https://github.com/Vivolance/ETL_pipeline_YSE/assets/99338366/bbd22e5f-e793-48a0-b786-bf2fc414bd3c)


## Brief

Now that yahoo_search_engine saves raw HTML search results in `yahoo_search_engine.search_results`

We need a way to extract the search results in the HTML returned from yahoo, and arrange it neatly into structured data

This ETL pipeline does that efficiently, and runs at a specific time every 5 minutes.

## Process

### Stage 1: Fetch raw yahoo search results
- Queries for rows from yahoo_search_engine.search_results table after a specific date range

### Stage 2: Extract results from yahoo search results (HTML)

### Stage 3: Batch insert into PSQL (yahoo_search_results.extracted_search_results)
- We do a CSV copy if we have millions of rows; the CSV copy would be way faster than bulk inserts
- But in this case, since we have very few users at the moment, with very few records
- A bulk insert is sufficient

## Setup Database

Please visit yahoo_search_engine and run

```commandline
alembic upgrade head
```

This creates 4 tables
- `yahoo_search_engine.last_extracted_user_status` -> table responsible for storing the last time the ETL pipeline ran for a given user's search
- `yahoo_search_engine.users` -> table responsible for storing users
- `yahoo_search_engine.search_results` -> table responsible for storing raw results
- `yahoo_search_engine.extracted_search_results` -> table responsible for storing extracted results from the ETL pipeline

## Creating the virtual environment and installing dependencies

```commandline
poetry shell
```

```commandline
poetry install
```

## Running the ETL pipeline

```commandline
PYTHONPATH-. python3 src/etl_pipeline.py
```

This runs the ETL pipeline, to ingest all raw documents in `yahoo_search_engine.search_results`
- Runs for all users, which have been created after each user's last run in `yahoo_search_engine.last_extracted_user_status`
- Processed data is saved in `yahoo_search_engine.extracted_search_results`

## Scheduling the ETL script to run

TODO: To do this realtime, we can use kafka
- Visit https://github.com/Vivolance/rt-etl-yahoo-search-engine
