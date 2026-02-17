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
MONITORING_URL = os.getenv("MONITORING_URL")

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

sys.exit(0)