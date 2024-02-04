import os
import json
import subprocess

from flask import Flask, jsonify, request

STATE_FILE = "onair-state.dat"

app = Flask(__name__)

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

@app.route('/onair/api/v1/state', methods=['GET'])
def get_state():
    if os.path.isfile(STATE_FILE):
        print(f"State file {STATE_FILE} exists...")
        with open(STATE_FILE, "r") as state_file:
            state_data = json.load(state_file)
        print(f"State data: {state_data}")
        return jsonify(state_data)
    else:
        return jsonify(False)

@app.route('/onair/api/v1/state', methods=['PUT'])
def set_state():
    old_state = get_state()
    new_state = json.loads(request.data.decode('utf-8'))
    
    return jsonify(state_change(old_state, new_state))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
