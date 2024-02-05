import json
import subprocess
import time
import requests
import argparse

DEFAULT_SERVER = "http://localhost:5000"
API_BASE = "/onair/api"
API_VERSION = "v1"

parser = argparse.ArgumentParser(
    prog='client.py',
    description=""
)
parser.add_argument('-s', '--server', type=str, default=DEFAULT_SERVER, help='The full server or sign endpoint URL to push statuses to.')
parser.add_argument('-t', '--toggle', type=str, action='append', required=True, help='Paths to toggle files to use to toggle status')
args = parser.parse_args()

API_URL = f"{args['server']}{API_BASE}/{API_VERSION}"

def changed_oncall(to):
    requests.put(f"{API_URL}/state", data=json.dumps(to))
    return to

for toggle in args['toggle']:
    print("Togle: " + toggle)
    