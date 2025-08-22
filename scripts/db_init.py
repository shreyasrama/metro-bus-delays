import sqlite3

# Create database and load SpatiaLite extension
conn = sqlite3.connect('metro_bus_delays.sqlite')
conn.enable_load_extension(True)
conn.execute("SELECT load_extension('mod_spatialite');")

cur = conn.cursor()

# Create stops table with a spatial column
cur.execute("""
CREATE TABLE stops (
    stop_id TEXT PRIMARY KEY,
    stop_code TEXT,
    stop_name TEXT,
    stop_lat REAL,
    stop_lon REAL
);
""")
cur.execute("""
SELECT InitSpatialMetadata(1);
""")
cur.execute("""
SELECT AddGeometryColumn('stops', 'geom', 4326, 'POINT', 'XY');
""")
cur.execute("""
UPDATE stops SET geom = MakePoint(stop_lon, stop_lat, 4326);
""")

# Create bus_calls table
cur.execute("""
CREATE TABLE bus_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_timestamp TEXT,
    line_ref TEXT,
    direction_ref TEXT,
    variant_ref TEXT,
    trip_import_code TEXT,
    published_line_name TEXT,
    stop_point_ref TEXT,
    visit_number INTEGER,
    stop_point_name TEXT,
    vehicle_at_stop INTEGER,
    aimed_departure_time TEXT,
    actual_departure_time TEXT,
    FOREIGN KEY(stop_point_ref) REFERENCES stops(stop_id)
);
""")

# Indexes for performance
cur.execute("CREATE INDEX idx_bus_calls_stop_point_ref ON bus_calls(stop_point_ref);")
cur.execute("CREATE INDEX idx_bus_calls_response_timestamp ON bus_calls(response_timestamp);")
cur.execute("CREATE INDEX idx_bus_calls_aimed_departure_time ON bus_calls(aimed_departure_time);")
cur.execute("CREATE INDEX idx_bus_calls_actual_departure_time ON bus_calls(actual_departure_time);")

conn.commit()
conn.close()
