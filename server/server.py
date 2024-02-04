import os
import json
import subprocess
import sqlite3
import time
import validators

from flask import Flask, jsonify, request

STATE_FILE = "onair-state.dat"
API_BASE = "/onair/api"
API_VERSION = "v1"
API_URL = f"{API_BASE}/{API_VERSION}"

app = Flask(__name__)

def init_db():
    con = sqlite3.connect('onair.db')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS signs(url TEXT PRIMARY KEY, registered_ts INTEGER, last_successful_ts INTEGER DEFAULT 0)")
    con.commit()
    con.close()

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

def register_sign(url, state):

    validators.url(url)

    data = {
        'url': url,
        'date': int(time.time())
    }

    con = sqlite3.connect('onair.db')
    cur = con.cursor()

    if state:
        cur.execute("INSERT INTO signs VALUES (:url, :date) ON CONFLICT(url) DO UPDATE SET registered_ts=:date", data)
    else:
        cur.execute("DELETE FROM signs WHERE url=:url", data)
    
    con.commit()
    con.close()

    return state

def get_signs(newer_than=None):
    con = sqlite3.connect('onair.db')
    cur = con.cursor()
    res = cur.execute("SELECT * FROM signs WHERE last_successful_ts>?", str(newer_than if newer_than is not None else 0))
    signs = res.fetchall()
    con.close()
    
    return signs


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

@app.route(f"{API_URL}/state", methods=['PUT'])
def set_state():
    old_state = get_state()
    new_state = json.loads(request.data.decode('utf-8'))
    
    return jsonify(state_change(old_state, new_state))

@app.route(f"{API_URL}/register", methods=['POST'])
def register():
    # get desired callback point (should parse to a url)
    client_text = json.loads(request.data.decode('utf-8'))

    register_sign(client_text, True)

    return jsonify(get_signs())

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host="0.0.0.0")
