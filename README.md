# metro-bus-delays

A collection of scripts that access Christchurch Metro's SIRI API to download Stop Monitoring data, and persists it to a SQLite3 database.

Can be used with `cron` for automation.

## Running locally

Requires a key for the Metro API to be set as an environment variable.

```bash
# Clone
git clone https://github.com/shreyasrama/metro-bus-delays.git
cd metro-bus-delays

# Set up env vars
cp .env.example .env

# Ensure uv is installed first. Sync to create virtual env and download dependencies
uv sync

# Run from in the context of the scripts/ folder
cd scripts

# Run once - create database and tables and load stop data into it
uv run db_init.py && uv run db_load_stops.py

# Downloads, processes, and inserts data from the API into the database. Target for automation
uv run --env-file ../.env main.py

# Check the logs
cat app.log
```

### `cron` automation (Unix)

Ensure `uv` is installed on the system, `uv sync` has been run, and the database has been created and initialised with stop data as per the previous section.

Set up a crontab file that runs every 5 minutes:

```bash
# Open the crontab editor
crontab -e

# Add the following to the bottom of the file
*/5 * * * * cd <path of cloned repo>/scripts && uv run --env-file ../.env main.py

# Check the cron is executing
grep metro-bus-delays /var/log/syslog
```
