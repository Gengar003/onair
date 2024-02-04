import os
import json
import subprocess
import sqlite3
<<<<<<< HEAD
import time
import validators
import requests
import traceback
import argparse
=======
import urllib
>>>>>>> cc7cb59 (its sqlite3)

from flask import Flask, jsonify, request

STATE_FILE = "onair-state.dat"
DB_INIT_FILE = "db-init.sql"
DB_FILE = "onair.db"

MAX_FAILURES=3

API_BASE = "/onair/api"
API_VERSION = "v1"
API_URL = f"{API_BASE}/{API_VERSION}"

parser = argparse.ArgumentParser(
    prog='server.py',
    description="A server that can push updates to multiple 'on-air' signs."
)
parser.add_argument('-p', '--port', type=int, default=5000, help='The port to listen on')
args = parser.parse_args()

app = Flask(__name__)

# helper to get a database connection
# use with database() as con:
# to ensure it always closes
def database():
    con = sqlite3.connect(DB_FILE, isolation_level=None)
    con.row_factory = sqlite3.Row
    return con

# only call once: set up the DB if no DB exists
def init_db():

    with open(DB_INIT_FILE, 'r') as db_init_file:
        with database() as con:
            cur = con.cursor()
            cur.execute(db_init_file.read())
            cur.close()

# change the server's state
def state_change(old: bool, new: bool):

    with open(STATE_FILE, "w") as state_file:
        state_file.write(json.dumps(new))

    print(f"Changed state from {old} -> {new}")

    return new

# register a new sign for push notifications
def register_sign(url, state):

    validators.url(url)

    data = {
        'url': url,
        'date': int(time.time())
    }

    with database() as con:
        cur = con.cursor()

        if state:
            cur.execute("INSERT INTO signs(url, registered_ts) VALUES (:url, :date) ON CONFLICT(url) DO UPDATE SET registered_ts=:date", data)
            print(f"Registered a sign at {url}")
        else:
            cur.execute("DELETE FROM signs WHERE url=:url", data)
            print(f"Removed the sign at {url}")
        
        cur.close()

    return state

# list all signs with their details
def get_signs(newer_than=None):
    with database() as con:
        cur = con.cursor()
        res = cur.execute("SELECT * FROM signs WHERE last_successful_ts>=?", str(newer_than if newer_than is not None else 0))
        signs = res.fetchall()
        cur.close()
    
    return [dict(row) for row in signs]

# notify all signs
# drop any that have failed a lot
def notify_signs(signs: list, state: bool):
    for sign in signs:
        response = None
        print(f"Notifying sign at {sign['url']}...")
        try:
            response = requests.put(sign['url'], json=state)
            print(f"    ... notified sign at {sign['url']}")
        except BaseException as be:
            print(traceback.format_exc())
            if sign['num_failures'] + 1 >= MAX_FAILURES:
                print(f"    Dropping sign {sign['url']}; it has failed too many ({sign['num_failures']+1}) times.")
                with database() as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM signs WHERE url=:url LIMIT 1", {
                        "url": sign['url']
                    } )
                    cur.close()
            else:
                print(f"    Sign {sign['url']} failed; incrementing its failure count to [{sign['num_failures']+1}].")
                with database() as con:
                    cur = con.cursor()
                    res = cur.execute("UPDATE signs SET num_failures=num_failures+1 WHERE url=:url RETURNING num_failures",{
                        "url": sign['url'],
                        "date": int(time.time())
                    })
                    cur.close()
        if response:
            with database() as con:
                cur = con.cursor()
                cur.execute("UPDATE signs SET last_successful_ts=:date, num_failures=0 WHERE url=:url",{
                    "url": sign['url'],
                    "date": int(time.time())
                })
                cur.close()
        

def retrieve_state():
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE, "r") as state_file:
            try:
                state_data = json.load(state_file)
            except:
                state_data = False
        return state_data
    else:
        return False

# view the state
# you can check on your sign
@app.route(f"{API_URL}/state", methods=['GET'])
def get_state():
    return jsonify(retrieve_state())

# lets a client set the state.
# body: json boolean
@app.route(f"{API_URL}/state", methods=['PUT'])
def set_state():
    old_state = retrieve_state()
    new_state = json.loads(request.data.decode('utf-8'))

    print(f"State update received: {new_state}")

    changed = state_change(old_state, new_state)

    notify_signs(get_signs(), changed)
    
    return jsonify(changed)

# signs can register for push notifications
# returns current state so sign can set itself properly
# body: json string, a url to json boolean state updates to
@app.route(f"{API_URL}/register", methods=['POST'])
def register():
    # get desired callback point (should parse to a url)
    client_text = json.loads(request.data.decode('utf-8'))

    print(f"Registering a sign at {client_text} ...")
    register_sign(client_text, True)
    current_state = retrieve_state()

    return jsonify(current_state)

if __name__ == '__main__':
    init_db()
    print(f"State: {retrieve_state()}")
    print(f"Signs: {get_signs()}")
    app.run(debug=True, host="0.0.0.0", port=args.port)
