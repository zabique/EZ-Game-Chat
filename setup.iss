; Inno Setup Script for EZ-Game-Chat
; Requires Inno Setup 6.0 or newer (iscc.exe)

#define MyAppName "EZ-Game-Chat"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "EZ-Game-Chat"
#define MyAppExeName "EZ-Game-Chat.exe"
#define MyAppAssocName MyAppName + " File"

[Setup]
AppId={{D37E84C1-28B0-4A92-BF3E-8167C5E9B231}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\EZ-Game-Chat
DisableProgramGroupPage=yes
OutputBaseFilename=EZ-Game-Chat_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=icons\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\EZ-Game-Chat\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: shellexec postinstall skipifsilent
