import requests
import os
import json
import tempfile

pond_raw = os.getenv("POND","{}")
POND_FILES = json.loads(pond_raw)

# This list will hold ALL data points from ALL ponds
master_output = []

for display_name, iot_id in POND_FILES.items():

        d = {
            "table_name": iot_id
        }
        try:
            # Make the request
            response = requests.post("http://inference-service.inference-ns.svc.cluster.local:85/", json=d)
            response.raise_for_status() # Check for errors
            
            pond_data = response.json() # This is your list of timestamps/values
            
            # Tag each individual data point so we know which pond it belongs to
            for entry in pond_data:
                entry["pond_name"] = display_name
                entry["iot_id"] = iot_id
                
            # Add this pond's tagged data to our master list
            master_output.extend(pond_data)
            
        except Exception as e:
            print(f"Failed to fetch data for {display_name}: {e}")

# Save the combined data to your shared volume safely
output_path = "/app/data/all_ponds_forecast.json"
temp_fd, temp_path = tempfile.mkstemp(dir="/app/data")

try:
    with os.fdopen(temp_fd, 'w') as tmp:
        json.dump(master_output, tmp)
    # This replaces the old file instantly (Atomic move)
    os.replace(temp_path, output_path)
    print(f"Successfully updated forecast for {len(POND_FILES)} ponds.")
except Exception as e:
    if os.path.exists(temp_path):
        os.remove(temp_path)
    print(f"Error saving forecast file: {e}")