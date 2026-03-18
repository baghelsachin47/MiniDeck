import json
import os
import subprocess

import win32com.client
from PyQt6.QtWidgets import QFileIconProvider

from application import Application

icon_provider = QFileIconProvider()


def get_start_menu_apps():
    """
    Scans the Windows Start Menu folders for shortcuts (.lnk).
    """
    folders = [
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
    ]

    apps = []
    seen_exes = set()
    shell = win32com.client.Dispatch("WScript.Shell")

    for base in folders:
        if not os.path.exists(base):
            continue

        for root, _dirs, files in os.walk(base):
            for file in files:
                if file.lower().endswith(".lnk"):
                    lnk_path = os.path.join(root, file)

                    try:
                        shortcut = shell.CreateShortCut(lnk_path)
                        target_exe = shortcut.Targetpath

                        if target_exe.lower().endswith(".exe") and os.path.exists(
                            target_exe
                        ):
                            if target_exe.lower() not in seen_exes:
                                seen_exes.add(target_exe.lower())

                                name = file.replace(".lnk", "")
                                if "uninstall" in name.lower():
                                    continue

                                app = Application(name=name, exe_location=target_exe)
                                app.load_icon(icon_provider)
                                apps.append(app)

                    except Exception:
                        pass
    return apps


def get_uwp_apps():
    """
    Fetches UWP apps via PowerShell and prevents internal ID duplicates.
    """
    command = ["powershell", "-Command", "Get-StartApps | ConvertTo-Json"]
    CREATE_NO_WINDOW = 0x08000000

    result = subprocess.run(
        command, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW
    )

    apps = []
    seen_ids = set()  # Prevent duplicate AppIDs

    try:
        data = json.loads(result.stdout)
        if isinstance(data, dict):
            data = [data]

        for app_data in data:
            name = app_data.get("Name")
            app_id = app_data.get("AppID")

            if name and app_id and app_id not in seen_ids:
                seen_ids.add(app_id)
                app = Application(name=name, app_id=app_id)
                app.load_icon(icon_provider)
                apps.append(app)
    except Exception:
        pass

    return apps


def detect_all_apps():
    apps = []
    apps.extend(get_start_menu_apps())
    apps.extend(get_uwp_apps())
    apps.sort(key=lambda x: x.name.lower())
    return apps
