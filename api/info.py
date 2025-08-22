import json

async def get_diagnostic_info(log_path: str):
    output = {}

    # Get log data
    with open(log_path, 'r') as log_file:
        lines = log_file.readlines()
        output['logs'] = json.loads(json.dumps(lines[-150:]))

    return output
