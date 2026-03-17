from db import load_apps, load_data
from RadialMenu import RadialMenu
from Hotkey import HotKeyListener
from settings import SettingsWindow

from PyQt6.QtWidgets import (
    QApplication,
    QFileIconProvider,
    QSystemTrayIcon,
    QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, QObject

import sys


class AppSignals(QObject):
    show_overlay = pyqtSignal()
    hide_overlay = pyqtSignal()


class MiniDeck:
    def __init__(self):
        self.app = QApplication(sys.argv)

        ## -----------------------------
        # Load config
        # -----------------------------
        data = load_data()
        self.icon_size = int(data.get("icon_size", 48))
        self.radius = int(data.get("radius", 200))
        # Safely get the new setting (defaults to True if missing)
        self.clamp_to_screen = data.get("clamp_to_screen", True) 

        # -----------------------------
        # Load apps
        # -----------------------------
        self.list_apps = load_apps()

        # -----------------------------
        # Load icons (requires QApplication)
        # -----------------------------
        self.icon_provider = QFileIconProvider()
        for app in self.list_apps:
            app.load_icon(self.icon_provider)
            
        # -----------------------------
        # Overlay
        # -----------------------------
        self.overlay = RadialMenu(list_apps=self.list_apps)
        self.overlay.set_icon_size(self.icon_size)
        self.overlay.set_radius(self.radius)
        # Pass the setting to the radial menu
        self.overlay.clamp_to_screen = self.clamp_to_screen

        # -----------------------------
        # Signals
        # -----------------------------
        self.signals = AppSignals()
        self.signals.show_overlay.connect(self.overlay.show)
        self.signals.hide_overlay.connect(self.overlay.hide)

        # -----------------------------
        # Hotkeys
        # -----------------------------
        self.hotkeys = HotKeyListener(
            self.on_hotkey_press,
            self.on_hotkey_release
        )

        # -----------------------------
        # Settings Window
        # -----------------------------
        self.settings_window = SettingsWindow(
            self.list_apps,
            self.overlay,
            self.icon_size,
            self.radius,
            self.hotkeys
        )

        # Start hidden
        self.settings_window.hide()

        # -----------------------------
        # System Tray
        # -----------------------------
        self.tray_icon = QSystemTrayIcon(
            self.app.style().standardIcon(self.app.style().StandardPixmap.SP_ComputerIcon),
            self.app
        )

        tray_menu = QMenu()

        open_settings_action = QAction("Settings")
        exit_action = QAction("Exit")

        tray_menu.addAction(open_settings_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # Tray menu actions
        open_settings_action.triggered.connect(self.settings_window.show)
        exit_action.triggered.connect(self.app.quit)

        # Double click tray icon
        self.tray_icon.activated.connect(self.tray_clicked)

        self.tray_icon.show()

    # -----------------------------
    # Tray double click
    # -----------------------------
    def tray_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.settings_window.show()
            self.settings_window.raise_()
            self.settings_window.activateWindow()

    # -----------------------------
    # Hotkeys
    # -----------------------------
    def on_hotkey_press(self):
        self.signals.show_overlay.emit()

    def on_hotkey_release(self):
        self.signals.hide_overlay.emit()

    # -----------------------------
    # Run app
    # -----------------------------
    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    minideck = MiniDeck()
    minideck.run()