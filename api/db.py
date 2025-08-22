import sqlite3

async def get_latest(db_path: str):
    print("calling db")
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
