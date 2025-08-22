import ijson
import json
import logging
import os
import requests
import time
from db_insert_calls import insert_calls

# Set up a logger to have a record of downloads/processes
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def download_siri_data():
    """
    Downloads data from an API using streaming and chunks, and writes to a local file.

    Returns:
        filename (string): The filename of the downloaded file.
    """
    
    start = time.perf_counter()

    try:
        response = requests.get(
            url='https://apis.metroinfo.co.nz/rti/siri/v1/sm',
            headers={
                'Cache-Control': 'no-cache',
                'Ocp-Apim-Subscription-Key': os.getenv('OCP_APIM_SUBSCRIPTION_KEY')
            }, 
            stream=True
        )
        response.raise_for_status()

        epoch = int(time.time())
        filename = str(epoch) + '_stop_monitoring.json'

        # Use binary write mode along with chunking for efficiency
        with open(filename, 'wb') as file:
            size = 0
            for chunk in response.iter_content(chunk_size=8192):
                size += len(chunk)
                file.write(chunk)
        
        end = time.perf_counter()
        elapsed = end - start
        
        log.info(f"Saved {(size / 1024 / 1024):.2f} MiB of data in {int(round(elapsed*1000))}ms.")
        
        return filename
    except requests.exceptions.RequestException as e:
        log.error(f"An error occurred: {e}")

    return ""

def process_siri_data(filename: str):
    """
    Processes a file containing the JSON response from the Stop Monitoring SIRI API, and returns a subset of key data 
    for bus delays.

    Parameters:
        filename (string): The file to process.
    """

    start = time.perf_counter()
    
    previous_calls_output = []

    with open(filename, 'r') as f:
        # Extract ResponseTimestamp by returning the next item from the ijson iterator
        response_timestamp = next(ijson.items(f, 'Siri.ServiceDelivery.ResponseTimestamp'))

        # Reset the iterator to the start and iterate through the MonitoredStopVisits
        f.seek(0)
        for visit in ijson.items(f, 'Siri.ServiceDelivery.StopMonitoringDelivery.item.MonitoredStopVisit.item'):
            # Extract journey details
            journey = visit.get('MonitoredVehicleJourney', {})
            journey_info = {
                'LineRef': journey.get('LineRef'),
                'DirectionRef': journey.get('DirectionRef'),
                'VariantRef': journey.get('VariantRef'),
                'TripImportCode': journey.get('TripImportCode'),
                'PublishedLineName': journey.get('PublishedLineName')
            }

            # Extract PreviousCall objects
            for prev_calls in journey.get('PreviousCalls', []):
                prev_call = prev_calls.get('PreviousCall', {})
                actual_departure = prev_call.get('ActualDepartureTime', '')
                aimed_departure = prev_call.get('AimedDepartureTime', '')
                
                # Ensure there are actual/aimed departures recorded. Unpack dicts when appending to output
                if actual_departure and aimed_departure:
                    previous_calls_output.append({**journey_info, **prev_call})

    # Cleanup
    os.remove(filename)

    rows_inserted = insert_calls(previous_calls_output, response_timestamp)

    end = time.perf_counter()
    elapsed = end - start
    
    log.info(f"Processed and inserted {rows_inserted} rows into the database in {int(round(elapsed*1000))}ms.")
    

def main():
    filename = download_siri_data()

    if filename:
        process_siri_data(filename)
    
if __name__ == '__main__':
    main()
