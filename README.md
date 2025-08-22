# metro-bus-delays

A collection of scripts that access Christchurch Metro's SIRI API to download Stop Monitoring data, and persists it to a SQLite3 database.

Designed to be used with `cron` for automation.

## Run

Requires a key for the Metro API to be set as an environment variable.

```bash
# Run from in the context of the scripts/ folder
cd scripts

# Create database and load stop data into it. One time setup
uv run db_init.py && uv run db_load_stops.py

# Downloads, processes, and inserts data from the API into the database. Target for cron automation
uv run --env-file ../.env main.py
```
