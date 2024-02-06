import os
import json
import subprocess
import sqlite3
import time
import validators
import requests
import traceback

from flask import Flask, jsonify, request

STATE_FILE = "onair-state.dat"
DB_INIT_FILE = "db-init.sql"
DB_FILE = "onair.db"

MAX_FAILURES=3

API_BASE = "/onair/api"
API_VERSION = "v1"
API_URL = f"{API_BASE}/{API_VERSION}"

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

# change the server's state
def state_change(old, new):
    
    # TODO: actually evince the change
    message = "offline"
    if new:
        message = "ON AIR"
    
    banner = subprocess.check_output(f"banner {message}", shell=True).decode('utf-8')
    print(banner)
    
    with open(STATE_FILE, "w") as state_file:
        state_file.write(json.dumps(new))
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
        else:
            cur.execute("DELETE FROM signs WHERE url=:url", data)

    return state

# list all signs with their details
def get_signs(newer_than=None):
    with database() as con:
        cur = con.cursor()
        res = cur.execute("SELECT * FROM signs WHERE last_successful_ts>=?", str(newer_than if newer_than is not None else 0))
        signs = res.fetchall()
    
    return [dict(row) for row in signs]

# notify all signs
# drop any that have failed a lot
def notify_signs(signs: list, state: bool):
    with database() as con:
        cur = con.cursor()
        for sign in signs:
            try:
                response = requests.put(sign['url'], json=state)
                cur.execute("UPDATE signs SET last_successful_ts=:date, num_failures=0 WHERE url=:url",{
                    "url": sign['url'],
                    "date": int(time.time())
                })
            except BaseException as be:
                print(traceback.format_exc())
                if sign['num_failures'] + 1 >= MAX_FAILURES:
                    print(f"Dropping sign {sign['url']}; it has failed too many ({sign['num_failures']+1}) times.")
                    cur.execute("DELETE FROM signs WHERE url=:url LIMIT 1", {
                        "url": sign['url']
                    } )
                else:
                    print(f"Sign {sign['url']} failed; incrementing its failure count to [{sign['num_failures']+1}].")
                    res = cur.execute("UPDATE signs SET num_failures=num_failures+1 WHERE url=:url RETURNING num_failures",{
                        "url": sign['url'],
                        "date": int(time.time())
                    })
            

# view the state
# clients can poll this
@app.route(f"{API_URL}/state", methods=['GET'])
def get_state():
    if os.path.isfile(STATE_FILE):
        print(f"State file {STATE_FILE} exists...")
        with open(STATE_FILE, "r") as state_file:
            state_data = json.load(state_file)
        print(f"State data: {state_data}")
        return jsonify(state_data)
    else:
        return jsonify(False)

# lets a client set the state.
# body: json boolean
@app.route(f"{API_URL}/state", methods=['PUT'])
def set_state():
    old_state = get_state()
    new_state = json.loads(request.data.decode('utf-8'))

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

    register_sign(client_text, True)
    print(f"Registered a sign at {client_text}")

    return get_state()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host="0.0.0.0")
