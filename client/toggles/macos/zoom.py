from toggles.macos.lib import app_cpu_with_headset

def run_and_call(callback, poll_interval_s=1, start_threshold=5, cpu_threshold=15):
    app_cpu_with_headset.run_and_call(callback, "zoom.us.app", poll_interval_s, start_threshold, cpu_threshold)

