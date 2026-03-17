; MiniDeck Version 1.0 Installer Script
; Build this using the Inno Setup Compiler

[Setup]
AppId={{A1B2C3D4-E5F6-4G7H-8I9J-K0L1M2N3O4P5}
AppName=MiniDeck
AppVersion=1.0
AppPublisher=baghelsachin47
DefaultDirName={autopf}\MiniDeck
DefaultGroupName=MiniDeck
AllowNoIcons=yes
; The installer file will be saved in an 'Output' folder
OutputDir=Output
OutputBaseFilename=MiniDeck_Setup_v1.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Point this to your main EXE inside the dist folder
Source: "D:\DEV\MiniDeck\dist\MiniDeck\MiniDeck.exe"; DestDir: "{app}"; Flags: ignoreversion
; This line includes everything else in the dist\MiniDeck folder
Source: "D:\DEV\MiniDeck\dist\MiniDeck\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\MiniDeck"; Filename: "{app}\MiniDeck.exe"
Name: "{autodesktop}\MiniDeck"; Filename: "{app}\MiniDeck.exe"; Tasks: desktopicon

[Run]
; Option to launch the app immediately after installation
Filename: "{app}\MiniDeck.exe"; Description: "{cm:LaunchProgram,MiniDeck}"; Flags: nowait postinstall skipifsilent