#define MyAppName      "KSeF Checker"
#define MyAppVersion   "2.1.3"
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
; Uruchom aplikację tylko przy ręcznej instalacji (nie przy cichej aktualizacji).
; Przy cichej aktualizacji aplikacja jest zamykana i użytkownik otwiera ją ponownie
; ręcznie — dzięki temu nowa wersja startuje BEZ uprawnień admina (instalator jest
; elevated, więc auto-restart z niego odpalałby aplikację jako administrator).
Filename: "{app}\{#MyAppExeName}"; \
  Description: "Uruchom {#MyAppName}"; \
  Flags: nowait postinstall skipifsilent

[Code]
// Twarde zamkniecie dzialajacej aplikacji PRZED kopiowaniem plikow.
// CloseApplications/Restart Manager bywa zawodne gdy stara wersja (2.0.x) czeka
// na instalator trzymajac zablokowany wlasny exe — wtedy plik nie da sie podmienic
// i aktualizacja "przechodzi" ale nic nie zmienia. taskkill /F to gwarancja.
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM {#MyAppExeName}', '',
       SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Sleep(800);  // daj systemowi chwile na zwolnienie blokady obrazu exe
  Result := '';
end;

