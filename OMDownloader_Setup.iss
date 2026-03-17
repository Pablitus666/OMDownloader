; ============================================================
; OMDownloader Professional Edition - Installer Script
; Walter Pablo Tellez Ayala - Software Developer
; ============================================================

[Setup]
AppId={{9F2D3E4C-5B1A-4D8E-9C2F-1A2B3C4D5E6F}
AppName=OMDownloader
AppVersion=1.0.0
AppPublisher=Walter Pablo Tellez Ayala
AppPublisherURL=https://github.com/Pablitus666/OMDownloader
AppSupportURL=https://github.com/Pablitus666/OMDownloader/issues
AppUpdatesURL=https://github.com/Pablitus666/OMDownloader/releases
DefaultDirName={autopf}\OMDownloader
DefaultGroupName=OMDownloader
AllowNoIcons=yes
; Icono del instalador
SetupIconFile=assets\images\icomulti.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Solo para sistemas de 64 bits (yt-dlp y telethon lo requieren habitualmente)
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
; Nombre del archivo de salida
OutputBaseFilename=OMDownloader_v1.0.0_Setup

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Incluimos todos los archivos de la carpeta dist\OMDownloader_Folder
Source: "dist\OMDownloader_Folder\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\OMDownloader"; Filename: "{app}\OMDownloader.exe"
Name: "{group}\{cm:UninstallProgram,OMDownloader}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\OMDownloader"; Filename: "{app}\OMDownloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\OMDownloader.exe"; Description: "{cm:LaunchProgram,OMDownloader}"; Flags: nowait postinstall skipifsilent
