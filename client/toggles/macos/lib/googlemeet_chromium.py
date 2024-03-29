import time
import re

from toggles.macos.lib import macos_utils

def run_and_call(callback, browser_name, poll_interval_s=1, start_threshold=5, cpu_threshold=15):

    on_call = False

    usages = list()

    cpu_threshold_delta = 0

    while True:

        was_on_call = on_call

        google_meet_open = False
        
        tab_urls = macos_utils.get_chromium_browser_tab_urls(browser_name)
        for tab_url in tab_urls:
            if re.search(r'^https://meet\.google\.com/.*', tab_url):
                google_meet_open = True
                break
        
        bluetooth_headset = macos_utils.is_any_bt_headset_connected()
        
        cpusage = macos_utils.get_cpusage_for_process(f"{browser_name} Helper (Renderer).app")
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
            # Need to detect a call start
            # if google meet open AND headset, that starts a call.
            # if google meet open AND no headset AND high CPU, that starts a call.

            if google_meet_open:
                print(f"Google Meet open...")
                if bluetooth_headset:
                    # google meet open AND a headset? That's a call!
                    print(f"\t... and there's a bluetooth headset!")
                    print("CALL STARTED")
                    on_call = callback(True)
                    continue
                else:
                    print(f"\t... with no headset! CPU Load: {cpu_data}")
                    # google meet open but NO headset? Check CPU usage
                    if cpu_threshold_delta >= start_threshold:
                        # google meet open, no headset, and high CPU? That's a call!
                        print(f"\t... with high CPU!")
                        print("CALL STARTED")
                        on_call = callback(True)
                        continue
        else:
            # need to detect a call end
            # if google meet closed, that starts a call
            # if google meet open, AND no headset, AND low cpu, that ends a call
            if not google_meet_open:
                # no google meet? no call!
                print("CALL ENDED")
                on_call = callback(False)
                continue
            else:
                # google meet is open. Are we just idling on the webpage?
                if not bluetooth_headset:
                    print(f"\t... with no headset! CPU Load: {cpu_data}")
                    if cpu_threshold_delta == 0:
                        # google meet open, no headset, and low CPU? That's the end of a call!
                        print(f"\t... with low CPU!")
                        print("CALL ENDED")
                        on_call = callback(False)
                        continue
        
        if was_on_call == on_call:
            if on_call:
                print("Still on a call...")
            else:
                print("Not on a call...")

        time.sleep(poll_interval_s)
