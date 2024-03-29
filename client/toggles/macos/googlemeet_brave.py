from toggles.macos.lib import googlemeet_chromium

def run_and_call(callback, poll_interval_s=5, start_threshold=5, cpu_threshold=15):
    googlemeet_chromium.run_and_call(callback, "Brave Browser", poll_interval_s, start_threshold, cpu_threshold)

