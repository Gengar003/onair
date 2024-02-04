import os
import json
import subprocess
import sqlite3
import time
import validators
import requests

from flask import Flask, jsonify, request

STATE_FILE = "onair-state.dat"
DB_INIT_FILE = "db-init.sql"
DB_FILE = "onair.db"

MAX_FAILURES=3

API_BASE = "/onair/api"
API_VERSION = "v1"
API_URL = f"{API_BASE}/{API_VERSION}"

app = Flask(__name__)

def init_db():

    with open(DB_INIT_FILE, 'r') as db_init_file:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute(db_init_file.read())
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

    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    if state:
        cur.execute("INSERT INTO signs(url, registered_ts) VALUES (:url, :date) ON CONFLICT(url) DO UPDATE SET registered_ts=:date", data)
    else:
        cur.execute("DELETE FROM signs WHERE url=:url", data)
    
    con.commit()
    con.close()

    return state

def get_signs(newer_than=None):
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    res = cur.execute("SELECT * FROM signs WHERE last_successful_ts>=?", str(newer_than if newer_than is not None else 0))
    signs = res.fetchall()
    con.close()
    
    return [dict(row) for row in signs]

def notify_signs(signs, state):
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    for sign in signs:
        try:
            response = requests.put(f"{sign[0]}", data=state)
            cur.execute("UPDATE signs SET last_successful_ts=:date, num_failures=0 WHERE url=:url",{
                "url": sign['url'],
                "date": int(time.time())
            })
        except BaseException as be:
            if sign['num_failures'] + 1 >= MAX_FAILURES:
                print(f"Dropping sign {sign['url']}; it has failed too many ({sign['num_failures']+1}) times.")
                cur.execute("DELETE FROM signs WHERE url=?", sign['url'])
            else:
                print(f"Sign {sign['url']} failed; incrementing its failure count.")
                res = cur.execute("UPDATE signs SET num_failures=num_failures+1 WHERE url=:url RETURNING num_failures",{
                    "url": sign['url'],
                    "date": int(time.time())
                })
                new_failures = res.fetchone()['num_failures']
                print(f"\tFailed {new_failures} times.")
            

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

    notify_signs(get_signs(), new_state)
    
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
