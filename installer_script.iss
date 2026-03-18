; MiniDeck Version 1.0 Installer Script
; Build this using the Inno Setup Compiler

[Setup]
AppId={{A1B2C3D4-E5F6-4G7H-8I9J-K0L1M2N3O4P5}
AppName=MiniDeck
AppVersion=1.0
AppPublisher=YOUR_NAME_HERE
DefaultDirName={autopf}\MiniDeck
DefaultGroupName=MiniDeck
AllowNoIcons=yes
; The installer file will be saved in an 'Output' folder
OutputDir=Output
OutputBaseFilename=MiniDeck_Setup_v1.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Optional: show your license file
LicenseFile=LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 1. The Main Executable (Compiled logic)
Source: "D:\DEV\MiniDeck\dist\MiniDeck\MiniDeck.exe"; DestDir: "{app}"; Flags: ignoreversion

; 2. All supporting DLLs and libraries (But NO raw .py files anymore!)
; We use * to grab everything in the folder EXCEPT what we manually defined above
Source: "D:\DEV\MiniDeck\dist\MiniDeck\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; This creates the Start Menu and Desktop shortcuts pointing to the EXE
Name: "{group}\MiniDeck"; Filename: "{app}\MiniDeck.exe"
Name: "{autodesktop}\MiniDeck"; Filename: "{app}\MiniDeck.exe"; Tasks: desktopicon

[Run]
; Launches the app automatically after installation finishes
Filename: "{app}\MiniDeck.exe"; Description: "{cm:LaunchProgram,MiniDeck}"; Flags: nowait postinstall skipifsilent