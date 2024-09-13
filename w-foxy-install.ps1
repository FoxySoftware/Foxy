Write-Host "######################################"
Write-Host "#     Welcome to Foxy Install!     #"
Write-Host "#####################################"
Write-Host



$currentDir = Get-Location
$osHost = "Windows"



$ErrorActionPreference = "Continue"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$ICON_COLLECTOR = Join-Path $SCRIPT_DIR "foxy-system\icons\foxy_icon_collector.ico"  # Cambia a .ico
$ICON_PROCESSOR = Join-Path $SCRIPT_DIR "foxy-system\icons\foxy_icon_processor.ico"  # Cambia a .ico
$ICON_STOP = Join-Path $SCRIPT_DIR "foxy-system\icons\foxy_icon_stop.ico"            # Cambia a .ico
$DESKTOP_FOLDER = [System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), "")
$APPLICATIONS_FOLDER = [System.IO.Path]::Combine([Environment]::GetFolderPath('ApplicationData'), "Microsoft\Windows\Start Menu\Programs\")

# Definir la ruta al archivo .env
$imageName = "/bueltan/foxy-system-base:libs"
$envFile =  Join-Path $SCRIPT_DIR "/config/os_general.env"
$tarFile =  Join-Path $SCRIPT_DIR "/foxy-system/foxy-system-base-libs.tar"
$composeFile =  Join-Path $SCRIPT_DIR "/foxy-system/docker-compose-dev.yaml"


function Create-Shortcut {
    param (
        [string]$scriptName,
        [string]$shortcutName,
        [string]$iconPath
    )

    $scriptPath = Join-Path $SCRIPT_DIR $scriptName

    if (Test-Path $scriptPath) {
        $shell = New-Object -ComObject WScript.Shell
        $desktopShortcut = $shell.CreateShortcut([System.IO.Path]::Combine($DESKTOP_FOLDER, "$shortcutName.lnk"))
        $desktopShortcut.TargetPath = "powershell.exe"  # Ejecuta con PowerShell
        $desktopShortcut.Arguments = "-ExecutionPolicy Bypass -File `"$scriptPath`""  # A ade el script como argumento
        $desktopShortcut.IconLocation = $iconPath
        $desktopShortcut.Save()
        Write-Host "Shortcut for $shortcutName created at $($DESKTOP_FOLDER)$shortcutName.lnk"

        $appsShortcut = $shell.CreateShortcut([System.IO.Path]::Combine($APPLICATIONS_FOLDER, "$shortcutName.lnk"))
        $appsShortcut.TargetPath = "powershell.exe"  # Ejecuta con PowerShell
        $appsShortcut.Arguments = "-ExecutionPolicy Bypass -File `"$scriptPath`""  # A ade el script como argumento
        $appsShortcut.IconLocation = $iconPath
        $appsShortcut.Save()
        Write-Host "Shortcut for $shortcutName created at $($APPLICATIONS_FOLDER)$shortcutName.lnk"
    } else {
        Write-Host "Script $scriptPath not found. Skipping..."
    }
}

# Create shortcuts for foxy-collector.ps1, foxy-processor.ps1, and foxy-stop.ps1
Create-Shortcut "w-foxy-collector.ps1" "Foxy Collector" $ICON_COLLECTOR
Create-Shortcut "w-foxy-processor.ps1" "Foxy Processor" $ICON_PROCESSOR
Create-Shortcut "w-foxy-stop.ps1" "Foxy Stop" $ICON_STOP

# Re-enable exit on error if desired later in the script
$ErrorActionPreference = "Stop"




# Verificar si el archivo .env ya existe
if (-not (Test-Path $envFile)) {
    # Si no existe, crear el archivo
    New-Item -Path $envFile -ItemType File | Out-Null
}

# Función para actualizar o agregar variables al archivo .env
function Update-EnvFile {
    param (
        [string]$Key,
        [string]$Value
    )
    if (Select-String -Path $envFile -Pattern "^$Key=") {
        (Get-Content $envFile) -replace "^$Key=.*", "$Key=$Value" | Set-Content $envFile
    } else {
        Add-Content -Path $envFile -Value "$Key=$Value"
    }
}

# Actualizar el archivo .env con las variables
Update-EnvFile -Key "FOXY_PATH" -Value $currentDir
Update-EnvFile -Key "OS_HOST" -Value $osHost

# Imprimir el nombre del sistema operativo
Write-Output "Operating System: $osHost"

# Verificar si Docker está instalado
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Output "Docker is installed."

    # Verificar si la imagen está disponible localmente
    if (-not (docker image inspect $imageName)) {
        Write-Output "Image $imageName not found locally."

        # Verificar si el archivo tar está disponible
        if (Test-Path $tarFile) {
            Write-Output "Loading image from $tarFile..."
            docker load -i $tarFile
        } else {
            Write-Output "Tar file not found. Attempting to pull the image from Docker Hub..."
            try {
                docker pull $imageName
            } catch {
                Write-Output "Failed to pull image from Docker Hub."
                exit 1
            }
        }
    } else {
        Write-Output "Image $imageName is already available locally."
    }

    # Verificar si el archivo Docker Compose existe
    if (Test-Path $composeFile) {
        Write-Output "Docker Compose file found."

        # Intentar con "docker-compose" primero
        if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
            Write-Output "Running Docker Compose with docker-compose..."
            docker-compose -f $composeFile up -d
        } else {
            # Si "docker-compose" falla, intentar con "docker compose"
            if (Get-Command docker -ErrorAction SilentlyContinue -and (docker compose version)) {
                Write-Output "Running Docker Compose with docker compose..."
                docker compose -f $composeFile up -d
            } else {
                Write-Output "Neither docker-compose nor docker compose is available."
                exit 1
            }
        }
    } else {
        Write-Output "Docker Compose file not found: $composeFile"
    }
} else {
    Write-Output "Docker is not installed."
    Write-Output "Please install Docker to continue."
    Write-Output "You can find installation instructions at: https://docs.docker.com/get-docker/"
}

# Mensaje de confirmación
Write-Output "Path saved to $envFile"

# Pausar el script hasta que se presione una tecla
Read-Host -Prompt "Press Enter to continue..."
