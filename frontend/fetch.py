import pandas as pd
import requests

def fetch_latest_data(endpoint: str, api_key: str) -> dict:
    try:
        response = requests.get(
            endpoint,
            headers={"X-API-Key": api_key},
            timeout=5
        )
        response.raise_for_status()
        return {"data": pd.DataFrame(response.json()['latest_calls']), "timestamp": response.json().get('response_timestamp', '')}

    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        print(f"Error fetching data: {e}")

        return {"data": pd.DataFrame(), "timestamp": ''}  # Return empty dataframe and timestamp on error
