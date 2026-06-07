#define MyAppName      "KSeF Checker"
#define MyAppVersion   "1.0"
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

; Sterownik Microsoft Access — instalowany tylko gdy brak
Source: "{#AccessEngine}"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\{#MyAppName}";      Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Odinstaluj";        Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Zainstaluj Access Engine cicho jeśli sterownik jeszcze nie istnieje
Filename: "{tmp}\{#AccessEngine}"; \
  Parameters: "/quiet /norestart"; \
  StatusMsg: "Instaluję sterownik Microsoft Access..."; \
  Check: AccessDriverMissing; \
  Flags: waituntilterminated

; Uruchom aplikację po instalacji (też w trybie cichym /SILENT)
Filename: "{app}\{#MyAppExeName}"; \
  Description: "Uruchom {#MyAppName}"; \
  Flags: nowait postinstall

[Code]
function AccessDriverMissing: Boolean;
var
  KeyExists: Boolean;
begin
  // Sprawdź czy sterownik Access 64-bit jest już zainstalowany
  KeyExists := RegKeyExists(
    HKEY_LOCAL_MACHINE,
    'SOFTWARE\Microsoft\Office\16.0\Access Connectivity Engine\Engines\ACE'
  );
  if not KeyExists then
    KeyExists := RegKeyExists(
      HKEY_LOCAL_MACHINE,
      'SOFTWARE\Microsoft\Office\15.0\Access Connectivity Engine\Engines\ACE'
    );
  if not KeyExists then
    KeyExists := RegKeyExists(
      HKEY_LOCAL_MACHINE,
      'SOFTWARE\Microsoft\Office\14.0\Access Connectivity Engine\Engines\ACE'
    );
  Result := not KeyExists;
end;
