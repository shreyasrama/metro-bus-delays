import json
import sqlite3

async def get_latest(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        response_timestamp,
        direction_ref,
        published_line_name,
        stop_point_ref,
        stop_point_name,
        aimed_departure_time,
        actual_departure_time,
        s.stop_lat,
        s.stop_lon,
        (
            julianday(substr(replace(bc.actual_departure_time, 'T', ' '), 1, 19)) - 
            julianday(substr(replace(bc.aimed_departure_time, 'T', ' '), 1, 19))
        ) * 24 * 60 AS delay_minutes
    FROM bus_calls bc
    JOIN stops s ON bc.stop_point_ref = s.stop_id
    WHERE response_timestamp = (
        SELECT response_timestamp FROM bus_calls ORDER BY ID DESC LIMIT 1
    );
    """)

    columns = [desc[0] for desc in cur.description]
    latest_calls = [dict(zip(columns, row)) for row in cur.fetchall()]
    response_timestamp = latest_calls[0]['response_timestamp'] if latest_calls else None

    for call in latest_calls:
        call.pop('response_timestamp', None)

    return {
        "response_timestamp": response_timestamp,
        "latest_calls": latest_calls
    }

async def get_calls(db_path: str, start_date: str, end_date: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        direction_ref,
        published_line_name,
        trip_import_code,
        stop_point_ref,
        stop_point_name,
        aimed_departure_time,
        actual_departure_time,
        s.stop_lat,
        s.stop_lon
    FROM bus_calls bc
    JOIN stops s on bc.stop_point_ref = s.stop_id
    WHERE response_timestamp BETWEEN ? AND ?
    """, (start_date, end_date))

    columns = [desc[0] for desc in cur.description]
    calls = [dict(zip(columns, row)) for row in cur.fetchall()]
    return calls

async def get_delays(db_path: str, start_date: str, end_date: str, delay: int):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    WITH delays AS (
        SELECT 
            bc.direction_ref, 
            bc.published_line_name, 
            bc.stop_point_ref, 
            bc.stop_point_name, 
            bc.aimed_departure_time, 
            bc.actual_departure_time,
            s.stop_lat,
            s.stop_lon,
            (
                julianday(substr(replace(bc.actual_departure_time, 'T', ' '), 1, 19)) - 
                julianday(substr(replace(bc.aimed_departure_time, 'T', ' '), 1, 19))
            ) * 24 * 60 AS delay_minutes
        FROM bus_calls bc
        JOIN stops s ON bc.stop_point_ref = s.stop_id
        WHERE bc.response_timestamp BETWEEN ? AND ?
    )
    SELECT * FROM delays WHERE delay_minutes > ?;
    """, (start_date, end_date, delay))

    columns = [desc[0] for desc in cur.description]
    calls = [dict(zip(columns, row)) for row in cur.fetchall()]
    return calls

async def get_route_shapes(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    conn.execute("SELECT load_extension('/opt/homebrew/opt/libspatialite/lib/mod_spatialite');")
    cur = conn.cursor()

    # Query to select the largest shape_geom for each route_id
    cur.execute("""
    SELECT
        route_id,
        route_long_name,
        shape_id,
        AsGeoJSON(shape_geom) AS geometry
    FROM route_shapes
    WHERE ROWID IN (
        SELECT ROWID
        FROM (
            SELECT 
                route_id,
                route_long_name,
                shape_id,
                shape_geom,
                ROWID,
                ST_Length(shape_geom) AS geom_length
            FROM route_shapes
        )
        WHERE geom_length = (
            SELECT MAX(ST_Length(shape_geom))
            FROM route_shapes AS inner_shapes
            WHERE inner_shapes.route_id = route_shapes.route_id
        )
    )
    """)
    
    columns = [desc[0] for desc in cur.description]
    shapes = [dict(zip(columns, row)) for row in cur.fetchall()]
    
    # Convert to GeoJSON FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": json.loads(shape["geometry"]),
                "properties": {
                    "route_id": shape["route_id"],
                    "route_long_name": shape["route_long_name"],
                    "shape_id": shape["shape_id"]
                }
            }
            for shape in shapes if shape["geometry"]  # Ensure geometry is not null
        ]
    }
    
    return geojson
