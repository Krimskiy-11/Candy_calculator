; Скрипт сборщика установщика Inno Setup для CandyCalculator

#define MyAppName "CandyCalculator"
#define MyAppVersion "1.0"
#define MyAppPublisher "CakeStudio"
#define MyAppExeName "CandyCalculator.exe"

[Setup]
; Уникальный идентификатор приложения (сгенерирован для CandyCalculator)
AppId={{9F82B5A1-4B96-4F12-8723-9D1B283A4201}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Куда положить готовый setup.exe
OutputDir=C:\projects\Candy_calculator\installer_output
OutputBaseFilename=CandyCalculator_Setup
; Иконка для самого файла установщика Setup.exe
SetupIconFile=C:\projects\Candy_calculator\assets\Candy.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "C:\projects\Candy_calculator\dist\CandyCalculator\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\projects\Candy_calculator\dist\CandyCalculator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\projects\Candy_calculator\dist\CandyCalculator\db.sqlite3"; DestDir: "{app}"; Flags: ignoreversion uninsneveruninstall; Permissions: users-modify


[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Filename: "{app}\{#MyAppExeName}"; Flags: nowait postinstall skipifsilent
