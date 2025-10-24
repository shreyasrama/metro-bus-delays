# metro-bus-delays

A monorepo that interacts with Christchurch Metro's SIRI API to visualise bus delays. It consists of the following components:

- `scripts/` - a collection of Python scripts to set up a local SQLite database, interact with Metro's API, and persist data to the database.
    - Can be used with `cron` for automation.
- `api/` - a lightweight implementation of FastAPI designed to connect to the SQLite database and return processed data
    - ~Available at https://metro-bus-delays-api.rama.nz~ _not running currently_
    - Endpoints are protected by API keys
- `frontend/` - Dash/Plotly web visualisations of bus delays using the returned processed data
    - ~Available at https://metro-bus-delays.rama.nz~ _not running currently_

The API and frontend are deployed to a VPS running Coolify.

## Initial setup

Run the following to configure the virtual environment and install packages.

```bash
# Clone the repo
git clone https://github.com/shreyasrama/metro-bus-delays.git
cd metro-bus-delays

# Set up env vars
cp .env.example .env

# Ensure uv is installed first. Sync to create virtual env and download dependencies
uv sync
```

## Scripts setup

Requires a key for the Metro API to be set as an environment variable.

```bash
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

## API setup

`API_KEY`, `DB_PATH`, and `LOG_PATH` are required to be set as environment variables.

```bash
# Local dev server
fastapi dev api/main.py

# Production run command (in Coolify container)
fastapi run /app/api/main.py --port 3000
```

## Frontend setup

`API_KEY` is required to be set as an environment variable. `ENVIRONMENT` is required to be set to `prod` when running the production server.

```bash
# Local dev server
uv run frontend/app.py

# Production run command (in Coolify container). This will use waitress to serve the app.
uv run /app/frontend/app.py --port 3000
```
