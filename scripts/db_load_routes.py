import sqlite3
import csv

# Create database and load SpatiaLite extension
conn = sqlite3.connect('metro_bus_delays.sqlite')
conn.enable_load_extension(True)
conn.execute("SELECT load_extension('mod_spatialite');")

cur = conn.cursor()

# Create tables from CSV files to be able to join them in SQL
def create_table_from_csv(cur, csv_path, table_name):
    with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        original_cols = reader.fieldnames

        if not original_cols:
            raise RuntimeError(f"No columns found in {csv_path}")

        # Sanitize header names (remove BOM and surrounding whitespace)
        cols = [c.lstrip('\ufeff').strip() for c in original_cols]

        # Create the table
        col_defs = ", ".join(f"\"{c}\" TEXT" for c in cols)
        cur.execute(f"DROP TABLE IF EXISTS \"{table_name}\";")
        cur.execute(f"CREATE TABLE \"{table_name}\" ({col_defs});")
        placeholders = ", ".join("?" for _ in cols)
        insert_sql = f"INSERT INTO \"{table_name}\" ({', '.join('\"'+c+'\"' for c in cols)}) VALUES ({placeholders});"
        
        rows = []
        for row in reader:
            rows.append(tuple(row.get(orig) for orig in original_cols))

        cur.executemany(insert_sql, rows)

        return cols

create_table_from_csv(cur, "gtfs-static/routes.txt", "routes")
create_table_from_csv(cur, "gtfs-static/trips.txt", "trips")
create_table_from_csv(cur, "gtfs-static/shapes.txt", "shapes")
conn.commit()

# Build a linestring WKT for each shape_id
cur.execute("DROP TABLE IF EXISTS shape_lines;")
cur.execute("""
CREATE TABLE shape_lines AS
SELECT
  s.shape_id,
  'LINESTRING(' ||
    COALESCE((
      SELECT group_concat(sh.shape_pt_lon || ' ' || sh.shape_pt_lat, ',')
      FROM shapes sh
      WHERE sh.shape_id = s.shape_id
      ORDER BY CAST(sh.shape_pt_sequence AS INTEGER)
    ), '') || ')' AS wkt
FROM shapes s
GROUP BY s.shape_id;
""")
conn.commit()

# Create a temp table joining routes -> trips -> shapes (one row per route_id + shape_id)
cur.execute("DROP TABLE IF EXISTS route_shapes_wkt;")
cur.execute("""
CREATE TABLE route_shapes_wkt AS
SELECT DISTINCT r.route_id,
       r.route_short_name,
       r.route_long_name,
       r.route_type,
       r.route_color,
       r.route_text_color,
       sl.shape_id,
       sl.wkt
FROM trips t
JOIN routes r ON t.route_id = r.route_id
JOIN shape_lines sl ON t.shape_id = sl.shape_id;
""")
conn.commit()

# Register geometry column
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='geometry_columns';")
if not cur.fetchone():
    try:
        cur.execute("SELECT InitSpatialMetadata(1);")
    except sqlite3.DatabaseError:
        cur.execute("SELECT InitSpatialMetadata();")

# If the geometry column doesn't exist, add it otherwise attempt to register it
cur.execute("PRAGMA table_info('route_shapes_wkt');")
cols = [row[1] for row in cur.fetchall()]
if 'shape_geom' not in cols:
    try:
        cur.execute("SELECT AddGeometryColumn('route_shapes_wkt','shape_geom',4326,'LINESTRING',2);")
    except sqlite3.DatabaseError:
        # Fallback for some builds that require schema-qualified call
        cur.execute("SELECT AddGeometryColumn('main','route_shapes_wkt','shape_geom',4326,'LINESTRING',2);")
else:
    try:
        cur.execute("SELECT RecoverGeometryColumn('route_shapes_wkt','shape_geom',4326,'LINESTRING',2);")
    except sqlite3.DatabaseError:
        # If registration fails, continue — column exists and will be populated below
        pass

cur.execute("UPDATE route_shapes_wkt SET shape_geom = GeomFromText(wkt, 4326) WHERE wkt IS NOT NULL;")
conn.commit()

# Rename to final table name (preserves the geometry column/metadata)
cur.execute("DROP TABLE IF EXISTS route_shapes;")
cur.execute("ALTER TABLE route_shapes_wkt RENAME TO route_shapes;")
conn.commit()

print('Created table "route_shapes" with columns: route_id, route_short_name, route_long_name, route_type, route_color, route_text_color, shape_id, shape_geom')

cur.close()
conn.close()
