#define MyAppName      "KSeF Checker"
#define MyAppVersion   "2.0.3"
#define MyAppPublisher "KSeF Checker"
#define MyAppExeName   "KSeF_Checker.exe"
#define AccessEngine   "AccessDatabaseEngine_X64.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\KSeF Checker
DefaultGroupName={#MyAppName}
OutputBaseFilename=KSeF_Checker_Installer
OutputDir=installer_output
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
; Ikona instalatora — ta sama co aplikacji
SetupIconFile=ksef_logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
; Wymagane uprawnienia admina (potrzebne do instalacji Access Engine)
PrivilegesRequired=admin

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "Utwórz skrót na pulpicie"; GroupDescription: "Dodatkowe ikony:"; Flags: unchecked

[Files]
; Główna aplikacja
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion


[Icons]
Name: "{group}\{#MyAppName}";      Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Odinstaluj";        Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Uruchom aplikację tylko przy ręcznej instalacji (nie przy cichej aktualizacji)
Filename: "{app}\{#MyAppExeName}"; \
  Description: "Uruchom {#MyAppName}"; \
  Flags: nowait postinstall skipifsilent

