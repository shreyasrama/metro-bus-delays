import os

async def get_diagnostic_info(log_path: str, db_path: str):
    output = {}

    # Get log data
    with open(log_path, 'r') as log_file:
        logs = []
        
        # Remove newline and split each line into [timestamp, level, message]
        lines = log_file.readlines()
        for line in lines[-150:]:
            line = line.strip()  # Remove newline
            parts = line.split(' - ', 2) # Split by ' - ', max 2 splits
            logs.append(parts)

        output['logs'] = logs

    # Get database file size
    output['db_size'] = os.path.getsize(db_path) / 1024 / 1024

    return output
