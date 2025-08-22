import sqlite3
import csv

# Connect to the database and load SpatiaLite extension
conn = sqlite3.connect('metro_bus_delays.sqlite')
conn.enable_load_extension(True)
conn.execute("SELECT load_extension('mod_spatialite');")

cur = conn.cursor()

# Use csv module to extract each row
with open("gtfs-static/stops.txt", mode='r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    stops = []
    for row in reader:
        stops.append((
            row['\ufeffstop_id'].strip(),
            row['stop_code'].strip(),
            row['stop_name'].strip(),
            float(row['stop_lat']),
            float(row['stop_lon'])
        ))

# Insert, ignoring if there are duplicate entries
cur.executemany("""
INSERT OR IGNORE INTO stops (stop_id, stop_code, stop_name, stop_lat, stop_lon)
VALUES (?, ?, ?, ?, ?);
""", stops)

# Add geometry for each stop
cur.execute("""
UPDATE stops SET geom = MakePoint(stop_lon, stop_lat, 4326)
WHERE stop_lon IS NOT NULL AND stop_lat IS NOT NULL;
""")

conn.commit()
conn.close()
