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
OutputBaseFilename=KSeF_Checker_Installer_z_AccessEngine
OutputDir=installer_output
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=ksef_logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=admin

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "Utworz skrot na pulpicie"; GroupDescription: "Dodatkowe ikony:"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#AccessEngine}"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\{#MyAppName}";      Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Odinstaluj";        Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{tmp}\{#AccessEngine}"; Parameters: "/quiet /norestart"; StatusMsg: "Instaluje sterownik Microsoft Access..."; Check: AccessDriverMissing; Flags: waituntilterminated
Filename: "{app}\{#MyAppExeName}"; Description: "Uruchom {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
function AccessDriverMissing: Boolean;
var
  KeyExists: Boolean;
begin
  KeyExists := RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Office\16.0\Access Connectivity Engine\Engines\ACE');
  if not KeyExists then
    KeyExists := RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Office\15.0\Access Connectivity Engine\Engines\ACE');
  if not KeyExists then
    KeyExists := RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Office\14.0\Access Connectivity Engine\Engines\ACE');
  Result := not KeyExists;
end;
