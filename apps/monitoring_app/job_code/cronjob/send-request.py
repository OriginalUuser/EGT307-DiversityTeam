import requests
import sys
import os

TABLES = os.getenv("TABLES")
COLUMNS = os.getenv("COLUMNS")
RANGE = os.getenv("RANGE")

INDEX = os.getenv("JOB_COMPLETION_INDEX")

# Convert to correct types
TABLES = TABLES.split(",")
COLUMNS = COLUMNS.split(",")
RANGE = int(RANGE)
INDEX = int(INDEX)

# Send request to...
MONITORING_DNS = os.getenv("MONITORING_DNS")
MONITORING_PORT = os.getenv("MONITORING_PORT")
MONITORING_URL = f"http://{MONITORING_DNS}:{MONITORING_PORT}"

# Send the request
assert INDEX <= len(TABLES)
payload = {
    "table_name": TABLES[INDEX],
    "columns": COLUMNS,
    "report_range": RANGE
}
response = requests.post(url=MONITORING_URL, json=payload)

print(f"Status code:    {response.status_code}")
print(f"Response body:  {response.text}")

if response.status_code == 200:
    sys.exit(0)
else:
    sys.exit(1)