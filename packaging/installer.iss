#define MyAppName "AlwaysTrack Watchdog"
#ifndef MyAppVersion
#define MyAppVersion "0.2.0"
#endif
#define MyAppPublisher "AlwaysTrack"
#define MyAppExeName "AlwaysTrackWatchdog.exe"
#ifndef MySourceDir
#define MySourceDir "..\dist\AlwaysTrackWatchdog"
#endif
#ifndef MyOutputDir
#define MyOutputDir "..\dist\installer"
#endif

[Setup]
AppId={{A794716A-A888-4DD4-9259-F613EFFBCBF7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://www.alwaystrack.com.br/
DefaultDirName={localappdata}\Programs\AlwaysTrack\Watchdog
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir={#MyOutputDir}
OutputBaseFilename=AlwaysTrackWatchdog-{#MyAppVersion}-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\assets\alwaystrack.ico
WizardStyle=modern
CloseApplications=force
RestartApplications=no
SetupLogging=yes
UsePreviousAppDir=yes
UsePreviousTasks=yes
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}

[Files]
Source: "{#MySourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppName}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppName}"
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppName}"; Tasks: autostart

[Tasks]
Name: "autostart"; Description: "Iniciar o AlwaysTrack Watchdog com o Windows"; GroupDescription: "Inicialização:"; Flags: unchecked

[InstallDelete]
; Recria ou remove o autostart de acordo com a seleção atual no upgrade.
Type: files; Name: "{userstartup}\{#MyAppName}.lnk"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Dados em LocalAppData\AlwaysTrack\Watchdog são preservados por padrão.
Type: filesandordirs; Name: "{app}"
