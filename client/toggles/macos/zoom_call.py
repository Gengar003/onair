import subprocess
import json
import time

from toggles.macos.lib import macos_utils

def run_and_call(callback, poll_interval_s=1, hit_threshold=5, end_threshold=5, cpu_threshold=15):

    on_call = False

    usages = list()

    sequential_hits = 0
    end_hits = 0

    while True:
        
        cpusage = macos_utils.get_cpusage_for_process("zoom.us.app")
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
                print(f"{prefix} Still on a Zoom call...")
            else:
                print(f"{prefix} May have started a Zoom call ({sequential_hits}/{hit_threshold})...")
                sequential_hits = sequential_hits + 1
                if sequential_hits > hit_threshold:
                    headset = macos_utils.is_any_bt_headset_connected()
                    if headset:
                        on_call = callback(True)
                    else:
                        print(f"\t... but no headset!")
                        sequential_hits = 0
        else:
            sequential_hits = 0
            if on_call:
                print(f"{prefix} Zoom call may have ended ({end_hits}/{end_threshold})!")
                end_hits = end_hits + 1
                if end_hits > end_threshold:
                    headset = macos_utils.is_any_bt_headset_connected()
                    if not headset:
                        on_call = callback(False)
                    else:
                        print(f"\t... but headset connected!")
                        end_hits = 0
            else:
                print(f"{prefix} Not on a Zoom call...")
        
        time.sleep(poll_interval_s)

