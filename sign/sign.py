import os
import json
import subprocess
import requests
import argparse
import socket
import subprocess

from flask import Flask, jsonify, request

STATE_FILE = "onair-state.dat"

API_BASE = "/onair/api"
API_VERSION = "v1"
API_URL = f"{API_BASE}/{API_VERSION}"

parser = argparse.ArgumentParser(
    prog='sign.py',
    description="A sign that can be toggled on or off"
)
parser.add_argument('-r', '--register', type=str, help='The full server endpoint URL to register with for push updates.')
parser.add_argument('-p', '--port', type=int, default=5000, help='The port to listen on')
parser.add_argument('-t', '--host', type=str, help="The host or IP to register with the server for push  updates, if it isn't just our IP + port")
parser.add_argument('-c', '--command', nargs=argparse.REMAINDER, type=str, help="Command to execute when toggled. %STATUS%, if present, will be replaced with `true' or `false'.")
parser.add_argument('-i', '--idempotent', action='store_true', help="If it is safe to call the --command on every state update. If false (default), commands only run when state CHANGES according to the sign's own memory.")
args = parser.parse_args()

app = Flask(__name__)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# register this sign with a server
def register(server, host, port):
    my_url = f"http://{host}:{port}{API_URL}/state"
    print(f"Registering {my_url} with server {server}...")

    server_state = requests.post(f"{server}",json=my_url)
    print('response:')
    print(server_state.text)
    print('response_json: ')
    print(server_state.json())
    server_state_json = server_state.json()
    state_change(retrieve_state(), server_state_json)

# run the cmds when the state changes
def run_state_cmds(new_state):
    if new_state:
        subprocess.call(args.on_command)
    else:
        subprocess.call(args.off_command)


# change the server's state
def state_change(old, new):
    
    message = "offline"
    if new:
        message = "ON AIR"
    
    banner = subprocess.check_output(f"banner {message}", shell=True).decode('utf-8')
    print(banner)
    
    with open(STATE_FILE, "w") as state_file:
        state_file.write(json.dumps(new))
    return new

def retrieve_state():
    if os.path.isfile(STATE_FILE):
        print(f"State file {STATE_FILE} exists...")
        with open(STATE_FILE, "r") as state_file:
            try:
                state_data = json.load(state_file)
            except:
                state_data = False
        print(f"State data: {state_data}")
        return state_data
    else:
        return False

# view the state
# you can check on your sign
@app.route(f"{API_URL}/state", methods=['GET'])
def get_state():
    return jsonify(retrieve_state())

# llet you set the state
# body: json boolean
@app.route(f"{API_URL}/state", methods=['PUT'])
def set_state():
    old_state = get_state()
    new_state = json.loads(request.data.decode('utf-8'))

    state_change(old_state, new_state)

    if old_state is not new_state or args.idempotent:
        run_state_cmds(new_state)
    
    return jsonify(new_state)

if __name__ == '__main__':
    local_host = args.host
    if args.register:
        if not args.host:
            local_host = get_local_ip()

    params = f"""
Listen on port: {args.port}
Register at endpoint: {args.register}
    {("registered host: " + local_host + ":" + str(args.port)) if args.register else ""}
Toggle Commands:
    ON : {args.on_command}
    OFF: {args.off_command}
    idempotent? {args.idempotent}
"""

    print(params)

    if args.register:
        register(args.register, local_host, args.port)
    
    app.run(debug=True, host="0.0.0.0", port=args.port)
