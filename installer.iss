; ──────────────────────────────────────────────────────────────
; PyMon – Inno Setup Installer Script
; Builds a single-file Windows installer from the PyInstaller
; output in dist\PyMon\
; ──────────────────────────────────────────────────────────────

#define MyAppName      "PyMon"
#define MyAppVersion   "1.0.0"
#define MyAppPublisher "GeneraBlack"
#define MyAppURL       "https://github.com/GeneraBlack/PyMon"
#define MyAppExeName   "PyMon.exe"

[Setup]
; Unique application ID – do NOT change between versions
AppId={{A3F7B2E1-9C4D-4E8F-B6A1-7D2E3F4C5B6A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=PyMon-{#MyAppVersion}-Setup
Compression=lzma2/ultra64
SolidCompression=yes
; Require Windows 10+
MinVersion=10.0
; Modern wizard style
WizardStyle=modern
; Uninstall icon & info
UninstallDisplayName={#MyAppName}
; No admin required – install in user profile by default
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german";  MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "autostart";   Description: "PyMon beim Windows-Start automatisch starten"; GroupDescription: "Systemintegration:"

[Files]
; Copy entire PyInstaller output directory
Source: "dist\PyMon\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start menu
Name: "{group}\{#MyAppName}";           Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} deinstallieren"; Filename: "{uninstallexe}"
; Desktop shortcut (optional task)
Name: "{autodesktop}\{#MyAppName}";     Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Autostart (optional task)
Name: "{userstartup}\{#MyAppName}";     Filename: "{app}\{#MyAppExeName}"; Tasks: autostart

[Run]
; Option to launch after install
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up app data cache on uninstall (optional)
Type: filesandordirs; Name: "{localappdata}\{#MyAppName}\cache"
