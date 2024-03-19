import importlib
import json
import requests
import argparse
import traceback
import threading

parser = argparse.ArgumentParser(
    prog='client.py',
    description="Determines whether the current user is 'on-air' or not."
)
parser.add_argument('-p', '--push', type=str, required=True, help='The full server or sign endpoint URL to push statuses to.')
parser.add_argument('-t', '--toggle', type=str, action='append', required=True, help='Paths to toggle files to use to toggle status')
args = parser.parse_args()



def changed_oncall(to: bool):
    try:
        requests.put(args.push, data=json.dumps(to), timeout=10)
    except Exception as be:
        print(traceback.format_exc())

    return to
    # TODO need to toggle better if fail

threads = list()

for toggle in args.toggle:
    print("Toggle selected: " + toggle)
    newmod = importlib.import_module(toggle)
    # TODO: this is not parallel, can only work with one toggle for now
    t = threading.Thread(target=newmod.run_and_call, args=[changed_oncall])
    t.start()
    threads += [t]

for t in threads:
    t.join()

