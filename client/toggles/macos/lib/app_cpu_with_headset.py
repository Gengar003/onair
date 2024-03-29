import time
from toggles.macos.lib import macos_utils

def run_and_call(callback, app_name, poll_interval_s=1, start_threshold=5, cpu_threshold=15):

    on_call = False

    usages = list()

    cpu_threshold_delta = 0

    while True:

        was_on_call = on_call
        
        bluetooth_headset = macos_utils.is_any_bt_headset_connected()
        
        cpusage = macos_utils.get_cpusage_for_process(app_name)
        usages = [cpusage] + usages
    
        load_avg_q = min(5,len(usages))
        load_avg = sum(usages[0:load_avg_q]) / load_avg_q
        long_load_avg_q = min(25,len(usages))
        long_load_avg = sum(usages[0:long_load_avg_q]) / long_load_avg_q

        if len(usages) > 25:
            usages = usages[0:25]
        
        if cpusage > cpu_threshold:
            cpu_threshold_delta = cpu_threshold_delta + 1
            if cpu_threshold_delta > start_threshold:
                cpu_threshold_delta = start_threshold
        elif cpusage < cpu_threshold:
            cpu_threshold_delta = cpu_threshold_delta - 1
            if cpu_threshold_delta < 0:
                cpu_threshold_delta = 0
        
        cpu_data = f"{int(cpusage)} {int(load_avg)} {int(long_load_avg)} (likelihood: {cpu_threshold_delta}/{start_threshold})"
        

        if not on_call:
            if cpu_threshold_delta >= start_threshold:
                print(f"High CPU usage for {app_name}: {cpu_data}...")
                # high cpu threshold for the video conferencing app?
                if bluetooth_headset:
                    #high CPU AND a headset? That's a call!
                    print(f"\t... and there's a bluetooth headset!")
                    print("CALL STARTED")
                    on_call = callback(True)
                    continue
        else:
            # need to detect a call end
            # Low CPU & no headset = call end
            if cpu_threshold_delta == 0:
                print(f"Low CPU usage for {app_name}: {cpu_data}...")
                if not bluetooth_headset:
                    # low CPU AND no headset? Call over!
                    print(f"\t... and NO bluetooth headset!")
                    print("CALL ENDED")
                    on_call = callback(False)
                    continue
                else:
                    print("\t... BUT headset still connected!")
        
        if was_on_call == on_call:
            if on_call:
                print("Still on a call...")
            else:
                print("Not on a call...")

        time.sleep(poll_interval_s)
