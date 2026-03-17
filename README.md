# 🚀 MiniDeck v1.0

**MiniDeck** is a lightweight, premium radial menu for Windows that allows you to launch your favorite apps and tools with a single keyboard shortcut. Designed for speed and minimal distraction, it stays hidden until you need it.

---

## ✨ Features

* **Radial Overlay:** A sleek, animated circular menu that appears at your cursor.
* **Smart App Discovery:** Automatically scans your system for installed Windows (UWP) apps and standard executables.
* **Custom Hotkeys:** Record your own keyboard combinations (Default: `Win + Shift`).
* **Premium Theme:** Modern Dark Mode UI with Cyan accents and smooth hover effects.
* **Intelligent Clamping:** The menu automatically detects screen edges to ensure it never goes off-screen.
* **System Tray Integration:** Runs silently in the background with a dedicated settings dashboard.
* **First-Run Experience:** A native Windows notification greets you on first launch to help you get started.

---

## 🛠️ Installation

### The Easy Way (Installer)
1.  Download `MiniDeck_Setup_v1.0.exe` from the [Releases](https://github.com/yourusername/MiniDeck/releases) page.
2.  Run the installer.
    * *Note: Since the app is unsigned, Windows may show a "SmartScreen" warning. Click **More Info** -> **Run Anyway**.*
3.  Launch MiniDeck from your Desktop or Start Menu.

### Running from Source
If you are a developer and want to run it manually:
1.  Clone the repo: `git clone https://github.com/yourusername/MiniDeck.git`
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run the app: `python main.py`

---

## ⌨️ How to Use

1.  **Open Menu:** Hold `Win + Shift` (Default).
2.  **Launch:** Click any icon to open the app.
3.  **Settings:** Right-click the **Computer Icon** in your System Tray (bottom right of your taskbar).
4.  **Add Apps:** Use the "Scan Apps" button in Settings to automatically find apps, or "Browse" to add a specific `.exe`.
5.  **Exit:** Use the "Quit MiniDeck" button in Settings or right-click the tray icon and select "Exit."

---

## 🏗️ Build & Packaging Instructions

To move from raw code to a professional Windows installer, follow these steps:

### 1. Bundle the Executable
Use **PyInstaller** to compile the Python scripts into a standalone folder. Run this command in your terminal:

```bash
pyinstaller --noconsole --name "MiniDeck" \
--hidden-import="pynput.keyboard._win32" \
--hidden-import="pynput.mouse._win32" \
--add-data "application.py;." \
--add-data "db.py;." \
--add-data "Hotkey.py;." \
--add-data "installedapps.py;." \
--add-data "RadialMenu.py;." \
--add-data "settings.py;." \
--add-data "theme.py;." \
main.py
```

### 2. Create the Installer (Inno Setup)
To generate the single MiniDeck_Setup.exe file:

1. Install Inno Setup 6+.

2. Open the installer_script.iss file included in this repository.

3. Ensure the Source paths in the .iss file point to your local dist/MiniDeck directory.

4. Click Build > Compile (or press F9).

Your production-ready installer will appear in the Output/ folder.