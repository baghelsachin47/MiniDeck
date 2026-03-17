import os
import shutil
import psutil
import ctypes
import win32gui
import win32con
import win32process
import win32api
import pywintypes
import subprocess
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QFileInfo

class Application:
    def __init__(self, name, exe_location=None, app_id=None):
        self.name = name
        self.app_id = app_id  # Only for true UWP apps
        self.icon = None

        # Optimization: Pre-calculate search targets to save CPU cycles later
        self.target_name = self.name.lower()
        
        if exe_location:
            resolved = shutil.which(exe_location)
            self.exe_location = resolved if resolved else exe_location
            # Pre-calculate the clean exe name exactly once
            self.clean_exe = os.path.basename(self.exe_location).lower().replace('"', '').strip()
        else:
            self.exe_location = None
            self.clean_exe = None

    # ---------------- ICON ----------------
    # ---------------- ICON ----------------
    def load_icon(self, provider):
        # If it's a normal EXE and it exists, use PyQt's icon provider
        if self.exe_location and os.path.exists(self.exe_location):
            self.icon = provider.icon(QFileInfo(self.exe_location)).pixmap(48, 48)
        else:
            # If it's a UWP app (or the exe went missing), generate a letter icon
            self.icon = self.generate_fallback_icon()

    def generate_fallback_icon(self):
        # Create a blank 48x48 transparent canvas
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw a nice dark grey circular background
        painter.setBrush(QColor(60, 60, 60)) 
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 48, 48)

        # Draw the first letter of the app's name in the center
        if self.name:
            letter = self.name[0].upper()
            painter.setPen(QColor(255, 255, 255)) # White text
            font = QFont("Segoe UI", 20, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, letter)

        painter.end()
        return pixmap

    # ---------------- WINDOW DETECTION ----------------
    def find_windows(self):
        windows = []
        pid_cache = {} # Caches process names to prevent lag

        def callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return

            title = win32gui.GetWindowText(hwnd).lower()
            if not title:
                return

            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # Optimization: psutil is slow. Only check each PID once and cache it.
            if pid not in pid_cache:
                try:
                    pid_cache[pid] = psutil.Process(pid).name().lower()
                except Exception:
                    pid_cache[pid] = ""
            
            pname = pid_cache[pid]

            # 1. Exact EXE match (Fast Path)
            if self.clean_exe and pname == self.clean_exe:
                windows.append(hwnd)
                
            # 2. Fallback Name Match (For apps like Spotify)
            elif self.target_name in pname or self.target_name in title:
                if hwnd not in windows: # Prevent duplicates
                    windows.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return windows

    # ---------------- ACTIVATE WINDOW ----------------
    def activate_window(self, hwnd):
        if not win32gui.IsWindow(hwnd):
            return

        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

            win32gui.BringWindowToTop(hwnd)

            # Focus trick (Alt key bypass)
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

            win32gui.SetForegroundWindow(hwnd)
        except pywintypes.error:
            pass

    # ---------------- LAUNCH ----------------
    def launch(self):
        try:
            # UWP
            if self.app_id:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "open", f"shell:AppsFolder\\{self.app_id}", None, None, 1
                )
                return

            # EXE
            if self.exe_location:
                exe_folder = os.path.dirname(self.exe_location)
                try:
                    subprocess.Popen(
                        f'start "" "{self.exe_location}"',
                        cwd=exe_folder,
                        shell=True
                    )
                except:
                    pass
                return
        except:
            pass

    # ---------------- MAIN LOGIC ----------------
    def open_instance(self):
        windows = self.find_windows()
        
        # If running -> switch
        if windows:
            current = win32gui.GetForegroundWindow()

            if current in windows:
                idx = windows.index(current)
                next_hwnd = windows[(idx + 1) % len(windows)]
            else:
                next_hwnd = windows[0]

            self.activate_window(next_hwnd)
            return

        # Not running -> launch
        self.launch()