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
; Zamknij dzialajaca aplikacje przed podmiana plikow (force = ubij gdy nie
; odpowiada na zamkniecie) — bez tego instalator pokazuje dialog "Wybierz operacje"
CloseApplications=force
RestartApplications=no

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
; Cicha aktualizacja z aplikacji (/RELAUNCH=1) — uruchom nową wersję
; jako zwykły użytkownik (nie admin)
Filename: "{app}\{#MyAppExeName}"; Flags: nowait runasoriginaluser; Check: ShouldRelaunch
; Uruchom aplikację tylko przy ręcznej instalacji (nie przy cichej aktualizacji)
Filename: "{app}\{#MyAppExeName}"; \
  Description: "Uruchom {#MyAppName}"; \
  Flags: nowait postinstall skipifsilent

[Code]
function ShouldRelaunch: Boolean;
begin
  Result := ExpandConstant('{param:RELAUNCH|0}') = '1';
end;

