import os

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFileIconProvider,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSlider,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from application import Application
from db import save_apps
from installedapps import detect_all_apps
from theme import MODERN_THEME  # Ensure you have created theme.py!


class AppTreeWidget(QTreeWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.settings_window = settings_window

    def dropEvent(self, event):
        super().dropEvent(event)
        self.settings_window.rebuild_app_order()


class SettingsWindow(QWidget):
    def __init__(self, applications, radial_menu, icon_size, radius, hotkey_listener):
        super().__init__()

        self.setWindowTitle("MiniDeck Settings")
        self.resize(550, 650)

        # Apply the premium theme
        self.setStyleSheet(MODERN_THEME)

        self.applications = applications
        self.radial_menu = radial_menu
        self.hotkey_listener = hotkey_listener
        self.icon_provider = QFileIconProvider()
        self.recorded_keys = set()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ==========================
        # RADIAL MENU VISUALS
        # ==========================
        settings_group = QGroupBox("Radial Menu & Hotkeys")
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(15, 20, 15, 15)
        settings_layout.setSpacing(12)

        # Icon Size
        settings_layout.addWidget(QLabel("Icon Size"))
        self.icon_slider = QSlider(Qt.Orientation.Horizontal)
        self.icon_slider.setMinimum(24)
        self.icon_slider.setMaximum(64)
        self.icon_slider.setValue(icon_size)
        self.icon_slider.valueChanged.connect(self.change_icon_size)
        settings_layout.addWidget(self.icon_slider)

        # Radius
        settings_layout.addWidget(QLabel("Menu Spread (Radius)"))
        self.radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.radius_slider.setMinimum(100)
        self.radius_slider.setMaximum(300)
        self.radius_slider.setValue(radius)
        self.radius_slider.valueChanged.connect(self.change_radius)
        settings_layout.addWidget(self.radius_slider)

        # --- HOTKEY SECTION ---
        settings_layout.addWidget(QLabel("Global Hotkey"))

        # 1. Create the button object first
        self.hotkey_button = QPushButton()

        # 2. Set the text based on current hotkey
        current_keys = " + ".join(self.hotkey_listener.target_keys).upper()
        self.hotkey_button.setText(f"Hotkey: {current_keys}")

        # 3. Apply the Focus fix so 'Space' can be recorded
        self.hotkey_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.hotkey_button.clicked.connect(self.start_recording)
        settings_layout.addWidget(self.hotkey_button)

        # Screen Clamp Checkbox
        self.clamp_checkbox = QCheckBox("Keep menu inside screen bounds")
        self.clamp_checkbox.setChecked(
            getattr(self.radial_menu, "clamp_to_screen", True)
        )
        self.clamp_checkbox.stateChanged.connect(self.change_clamp)
        settings_layout.addWidget(self.clamp_checkbox)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # ==========================
        # APPLICATION LIST
        # ==========================
        app_group = QGroupBox("Manage Applications")
        app_layout = QVBoxLayout()
        app_layout.setContentsMargins(15, 20, 15, 15)

        self.app_list = AppTreeWidget(self)
        self.app_list.setColumnCount(2)
        self.app_list.setHeaderLabels(["Application", "Path"])
        self.app_list.setColumnWidth(0, 180)
        self.app_list.setRootIsDecorated(False)
        self.app_list.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)

        app_layout.addWidget(self.app_list)

        # Button Row
        button_layout = QHBoxLayout()
        self.installed_apps_btn = QPushButton("Scan Apps")
        self.add_button = QPushButton("Browse")
        self.remove_button = QPushButton("Remove")
        self.quit_button = QPushButton("Quit MiniDeck")
        self.quit_button.setStyleSheet("""
            QPushButton { 
                background-color: #3E3E42; 
                color: #FF4B4B; /* Red text to indicate closing */
                border: 1px solid #FF4B4B;
            }
            QPushButton:hover { 
                background-color: #FF4B4B; 
                color: white; 
            }
        """)
        self.quit_button.clicked.connect(self.quit_application)
        self.save_button = QPushButton("Save Config")
        self.save_button.setStyleSheet(
            "QPushButton { background-color: #00D2FF; color: #121212; border: none; } QPushButton:hover { background-color: #55E0FF; }"
        )

        self.add_button.clicked.connect(self.add_app)
        self.remove_button.clicked.connect(self.remove_app)
        self.save_button.clicked.connect(self.save_settings)
        self.installed_apps_btn.clicked.connect(self.open_installed_apps)

        button_layout.addWidget(self.quit_button)  # Add it first
        button_layout.addSpacing(20)  # Give it some room
        button_layout.addWidget(self.installed_apps_btn)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)

        app_layout.addLayout(button_layout)
        app_group.setLayout(app_layout)
        main_layout.addWidget(app_group)

        self.setLayout(main_layout)
        self.refresh_app_list()

    # ==========================
    # LOGIC: HOTKEY RECORDING
    # ==========================
    def start_recording(self):
        self.recorded_keys = set()
        self.hotkey_button.setText("Recording... (Release keys to stop)")
        self.hotkey_button.setStyleSheet("background-color: #FF4B4B; color: white;")

        from pynput import keyboard

        self.recorder = keyboard.Listener(
            on_press=self._record_press, on_release=self._record_release
        )
        self.recorder.start()

    def _record_press(self, key):
        if hasattr(key, "name"):
            name = key.name
        elif hasattr(key, "char"):
            name = key.char
        else:
            name = str(key)

        if name:
            self.recorded_keys.add(name)

    def _record_release(self, key):
        keys_list = list(self.recorded_keys)
        self.recorder.stop()

        # Update logic and UI
        self.hotkey_button.setText(f"Hotkey: {' + '.join(keys_list).upper()}")
        self.hotkey_button.setStyleSheet("")  # Reset style

        # Update actual listener in memory
        self.hotkey_listener.update_keys(keys_list)

    # ==========================
    # LOGIC: SETTINGS
    # ==========================
    def change_icon_size(self, value):
        self.radial_menu.set_icon_size(value)

    def change_radius(self, value):
        self.radial_menu.set_radius(value)

    def change_clamp(self, state):
        self.radial_menu.clamp_to_screen = bool(state)

    def refresh_app_list(self):
        self.app_list.clear()
        for app in self.applications:
            item = QTreeWidgetItem()
            item.setFlags(
                Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsDragEnabled
            )
            item.setText(0, app.name)
            path_text = (
                str(app.exe_location) if app.exe_location else f"[UWP] {app.app_id}"
            )
            item.setText(1, path_text)
            if app.icon:
                item.setIcon(0, QIcon(app.icon))
            self.app_list.addTopLevelItem(item)

    def add_app(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select App", "", "Executables (*.exe)"
        )
        if file_path:
            name = os.path.splitext(os.path.basename(file_path))[0]
            new_app = Application(name, file_path)
            new_app.load_icon(self.icon_provider)
            self.applications.append(new_app)
            self.refresh_app_list()
            self.radial_menu.update_apps(self.applications)

    def remove_app(self):
        item = self.app_list.currentItem()
        if item:
            row = self.app_list.indexOfTopLevelItem(item)
            self.applications.pop(row)
            self.refresh_app_list()
            self.radial_menu.update_apps(self.applications)

    def rebuild_app_order(self):
        new_order = []
        for i in range(self.app_list.topLevelItemCount()):
            name = self.app_list.topLevelItem(i).text(0)
            for app in self.applications:
                if app.name == name:
                    new_order.append(app)
                    break
        self.applications[:] = new_order
        self.radial_menu.update_apps(self.applications)

    def save_settings(self):
        icon_size = self.radial_menu.icon_size
        radius = self.radial_menu.radius
        clamp = self.radial_menu.clamp_to_screen
        keys = self.hotkey_listener.target_keys

        save_apps(self.applications, icon_size, radius, clamp, keys)

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    # ==========================
    # LOGIC: INSTALLED APPS
    # ==========================
    def open_installed_apps(self):
        self.apps = detect_all_apps()
        self.show_apps_dialog()

    def show_apps_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Installed Apps")
        dialog.resize(500, 600)
        dialog.setStyleSheet(MODERN_THEME)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search apps...")
        self.search_bar.textChanged.connect(self.filter_apps)
        layout.addWidget(self.search_bar)

        self.app_list_widget = QListWidget()
        self.app_list_widget.setIconSize(QSize(32, 32))
        layout.addWidget(self.app_list_widget)

        # Status Label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Message Timer
        self.msg_timer = QTimer()
        self.msg_timer.setSingleShot(True)
        self.msg_timer.timeout.connect(
            lambda: (
                self.status_label.setText("")
                if not self.status_label.isHidden()
                else None
            )
        )

        # --- THE FIX ---
        # Stop the timer if the dialog is closed before the 3 seconds are up
        dialog.finished.connect(lambda: self.msg_timer.stop())

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add Selected")
        add_btn.setStyleSheet(
            "QPushButton { background-color: #00D2FF; color: #121212; border: none; }"
        )

        cancel_btn = QPushButton("Close")
        cancel_btn.clicked.connect(dialog.reject)
        add_btn.clicked.connect(self.add_selected_app)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(add_btn)
        layout.addLayout(btn_row)

        self.populate_app_list(self.apps)
        dialog.exec()

    def populate_app_list(self, apps):
        self.app_list_widget.clear()
        for app in apps:
            item = QListWidgetItem(app.name)
            if app.icon:
                item.setIcon(QIcon(app.icon))
            item.setData(Qt.ItemDataRole.UserRole, app)
            self.app_list_widget.addItem(item)

    def filter_apps(self, text):
        filtered = [app for app in self.apps if text.lower() in app.name.lower()]
        self.populate_app_list(filtered)

    def add_selected_app(self):
        selected = self.app_list_widget.currentItem()
        if not selected:
            return

        new_app = selected.data(Qt.ItemDataRole.UserRole)

        # Check for duplicates
        is_duplicate = any(
            (app.exe_location == new_app.exe_location and app.exe_location is not None)
            or (app.app_id == new_app.app_id and app.app_id is not None)
            for app in self.applications
        )

        if is_duplicate:
            # Show red error message
            self.status_label.setStyleSheet("color: #FF4B4B; font-weight: bold;")
            self.status_label.setText(f"'{new_app.name}' is already in the menu.")
            self.msg_timer.start(3000)  # Clear after 3 seconds
            return

        # Success path
        self.applications.append(new_app)
        self.refresh_app_list()
        self.radial_menu.update_apps(self.applications)

        # Show cyan success message
        self.status_label.setStyleSheet("color: #00D2FF; font-weight: bold;")
        self.status_label.setText(f"Added {new_app.name} successfully!")
        # Stop and restart ensures we don't crash if they click 5 times fast
        self.msg_timer.stop()
        self.msg_timer.start(3000)

    def quit_application(self):
        from PyQt6.QtWidgets import QApplication

        # This is the cleanest way to shut down a PyQt app from a child window
        QApp = QApplication.instance()
        if QApp:
            QApp.quit()
