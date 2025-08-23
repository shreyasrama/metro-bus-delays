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
    WHERE response_timestamp BETWEEN ? AND ?
    AND (
        julianday(substr(replace(actual_departure_time, 'T', ' '), 1, 19)) - 
        julianday(substr(replace(aimed_departure_time, 'T', ' '), 1, 19))
    ) * 24 * 60 > ?;
    """, (start_date, end_date, delay))

    calls = cur.fetchall()
    return calls
