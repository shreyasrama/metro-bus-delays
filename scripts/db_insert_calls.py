import sqlite3

def insert_calls(bus_calls, response_timestamp: str) -> int:
    """
    Inserts bus call data parsed from the SIRI API into the SQLite database.

    Parameters:
        bus_calls (array): Array of bus calls objects that contain details on the previous buses that stopped at a
        given stop.

        response_timestamp (string): The timestamp associated with the API call.

    Returns:
        rows_inserted (int): Number of rows that were inserted into the database.
    """

    conn = sqlite3.connect('metro_bus_delays.sqlite')
    cur = conn.cursor()

    rows_inserted = 0
    for call in bus_calls:
        cur.execute("""
            INSERT INTO bus_calls (
                response_timestamp,
                line_ref,
                direction_ref,
                variant_ref,
                trip_import_code,
                published_line_name,
                stop_point_ref,
                visit_number,
                stop_point_name,
                vehicle_at_stop,
                aimed_departure_time,
                actual_departure_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            response_timestamp,
            call.get('LineRef'),
            call.get('DirectionRef'),
            call.get('VariantRef'),
            call.get('TripImportCode'),
            call.get('PublishedLineName'),
            call.get('StopPointRef'),
            call.get('VisitNumber'),
            call.get('StopPointName'),
            int(call['VehicleAtStop']) if call.get('VehicleAtStop') is not None else None,
            call.get('AimedDepartureTime'),
            call.get('ActualDepartureTime')
        ))
        rows_inserted += 1

    conn.commit()
    conn.close()

    return rows_inserted
