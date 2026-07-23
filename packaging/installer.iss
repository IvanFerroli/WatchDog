#define MyAppName "AlwaysTrack Watchdog"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "AlwaysTrack"
#define MyAppExeName "AlwaysTrackWatchdog.exe"

[Setup]
AppId={{A794716A-A888-4DD4-9259-F613EFFBCBF7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\AlwaysTrack\Watchdog
DefaultGroupName={#MyAppName}
PrivilegesRequired=lowest
OutputDir=..\dist\installer
OutputBaseFilename=AlwaysTrackWatchdog-{#MyAppVersion}-setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\assets\alwaystrack.ico

[Files]
Source: "..\dist\AlwaysTrackWatchdog\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: autostart

[Tasks]
Name: "autostart"; Description: "Iniciar com o Windows"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Dados em LocalAppData\AlwaysTrack\Watchdog são preservados por padrão.
Type: filesandordirs; Name: "{app}"
