
Write-Output "######################################"
Write-Output "#     Welcome to Foxy Initiator!     #"
Write-Output "#####################################"
Write-Output ""

$currentDir = Get-Location
$osHost = "Windows"

# Definir la ruta al archivo .env
$envFile = "config/os_general.env"
$imageName = "bueltan/foxy-system-base:libs"
$tarFile = "./foxy-system/foxy-system-base-libs.tar"
$composeFile = "./foxy-system/docker-compose-dev.yaml"

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

