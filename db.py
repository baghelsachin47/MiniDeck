import json
import os
from application import Application

# APPDATA_PATH = os.path.join(os.environ['APPDATA'], 'MiniDeck')
# if not os.path.exists(APPDATA_PATH):
#     os.makedirs(APPDATA_PATH)

# CONFIG_FILE = os.path.join(APPDATA_PATH, "config.json")
CONFIG_FILE = 'config.json'

def load_data():
    if not os.path.exists(CONFIG_FILE):
        default_data = {
            "icon_size": 48,
            "radius": 180,
            "clamp_to_screen": True,
            "apps": [],
            "hotkey": ["cmd", "shift"]
        }
        save_data(default_data)
        return default_data

    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
        # Fallbacks for updating older config versions
        if "clamp_to_screen" not in data:
            data["clamp_to_screen"] = True
        if "hotkey" not in data:
            data["hotkey"] = ["cmd", "shift"]
        return data

def save_data(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_apps():
    data = load_data()
    apps = []
    for app_data in data.get("apps", []):
        app = Application(
            name=app_data["name"],
            exe_location=app_data.get("exe_location"),
            app_id=app_data.get("app_id")
        )
        apps.append(app)
    return apps

# Added 'hotkey' parameter so it doesn't get wiped
def save_apps(apps, icon_size, radius, clamp_to_screen=True, hotkey=None):
    if hotkey is None:
        # If no hotkey provided, try to preserve the existing one
        hotkey = load_data().get("hotkey", ["cmd", "shift"])

    data = {
        "icon_size": icon_size,
        "radius": radius,
        "clamp_to_screen": clamp_to_screen,
        "apps": [],
        "hotkey": hotkey  
    }

    for app in apps:
        data["apps"].append({
            "name": app.name,
            "exe_location": app.exe_location,
            "app_id": app.app_id
        })

    save_data(data)