import subprocess
import json

# determines if a bluetooth headset is connected
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

# gets CPU usage for all processes that share a process name
def get_cpusage_for_process(process):
    cmd="ps aux | cat | grep '" + process + "' | awk '{print $3}'"
    total = 0
    for amt in subprocess.check_output(cmd, shell=True).decode('utf-8').split('\n'):
        if amt:
            total += float(amt)
    
    return total

def get_chromium_browser_tab_urls(browser_name: str = "Google Chrome"):
    """
    Get the URLs of all the tabs open in a Chromium browser.

    Args:
    browser_name (str): The name of the browser to get the tabs from.

    Returns:
    list: A list of URLs as strings
    """
    cmd = f"osascript -e 'if application \"{browser_name}\" is running then tell application \"{browser_name}\" to get the url of every tab of every window'"
    return subprocess.check_output(cmd, shell=True).decode('utf-8').split(', ')
