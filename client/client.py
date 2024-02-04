import json
import subprocess
import time
import requests

SERVER_API_BASE="http://localhost:5000/onair/api/v1"

def is_any_bt_headset_connected():
    headset_types = ["Headphones", "Headset"]
    cmd="system_profiler -json SPBluetoothDataType"
    bt_devs = json.loads(subprocess.check_output(cmd, shell=True).decode('utf-8'))["SPBluetoothDataType"][0]
    connected_devs = bt_devs["device_connected"]
    for devobj in connected_devs:
        for device, device_props in devobj.items():
            if device_props["device_minorType"] in headset_types:
                return True

    return False

def get_cpusage_for_process(process):
    cmd="ps aux | cat | grep '" + process + "' | awk '{print $3}'"
    total = 0
    for amt in subprocess.check_output(cmd, shell=True).decode('utf-8').split('\n'):
        if amt:
            total += float(amt)
    
    return total


on_call = False
def changed_oncall(to):
    requests.put(f"{SERVER_API_BASE}/state", data=json.dumps(to))
    return to

usages = list()

poll_interval_s = 1
sequential_hits = 0
hit_threshold = 5
end_hits = 0
end_threshold = 5
cpu_threshold = 15


while True:
    
    cpusage = get_cpusage_for_process("Google Chrome Helper (Renderer).app")
    usages = [cpusage] + usages
    
    load_avg_q = min(5,len(usages))
    load_avg = sum(usages[0:load_avg_q]) / load_avg_q
    long_load_avg_q = min(25,len(usages))
    long_load_avg = sum(usages[0:long_load_avg_q]) / long_load_avg_q
    
    if len(usages) > 25:
        usages = usages[0:25]
    
    prefix = f"{int(cpusage)} {int(load_avg)} {int(long_load_avg)}"
    
    if cpusage > cpu_threshold:
        end_hits = 0
        if on_call:
            print(f"{prefix} Still on a call...")
        else:
            print(f"{prefix} May have started a call ({sequential_hits}/{hit_threshold})...")
            sequential_hits = sequential_hits + 1
            if sequential_hits > hit_threshold:
                headset = is_any_bt_headset_connected()
                if headset:
                    on_call = changed_oncall(True)
                else:
                    print(f"\t... but no headset!")
                    sequential_hits = 0
    else:
        sequential_hits = 0
        if on_call:
            print(f"{prefix} Call may have ended ({end_hits}/{end_threshold})!")
            end_hits = end_hits + 1
            if end_hits > end_threshold:
                headset = is_any_bt_headset_connected()
                if not headset:
                    on_call = changed_oncall(False)
                else:
                    print(f"\t... but headset connected!")
                    end_hits = 0
        else:
            print(f"{prefix} Not on a call...")
    
    time.sleep(poll_interval_s)

