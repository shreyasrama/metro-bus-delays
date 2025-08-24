import sqlite3

async def get_latest(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        direction_ref, 
        published_line_name, 
        stop_point_ref, 
        stop_point_name, 
        aimed_departure_time, 
        actual_departure_time 
        FROM bus_calls 
        
        WHERE response_timestamp = (
            SELECT response_timestamp FROM bus_calls ORDER BY ID DESC LIMIT 1
        );
    """)

    latest_calls = cur.fetchall()
    return latest_calls

async def get_delays(db_path: str, start_date: str, end_date: str, delay: int):
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    conn.execute("SELECT load_extension('mod_spatialite');")
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
            AsText(s.geom) as geom,
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
