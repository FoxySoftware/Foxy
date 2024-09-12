# PowerShell script version

# ASCII Art
Write-Host "                              .     " 
Write-Host "                           .~5B.    " 
Write-Host "                         ~P#@@@?    " 
Write-Host "                        !@@@@@@@J.  " 
Write-Host "  ^~~^:.                P@@@@@@&&BY." 
Write-Host "  ^5@@&#G?:            !&@@@@@&!.:. "  
Write-Host "    ?@@@@@&!       .^!5@@@@@@@@G    "  
Write-Host "     B@@@@@&:   ^JG&@@@@@@@@@@@?    "  
Write-Host "    .#@@@@@@~ ^P@@@@@@@@@@@@@&7     "  
Write-Host "    ?@@@@@@&.^&@@@@@@@@@@@@@@7      "  
Write-Host "    5@@@@@@G G@@@@@@@@@@@@@@@!      "  
Write-Host "    J@@@@@@#:#@@@@@@@@@@@G?@@G.     "  
Write-Host "    .P@@@@@@P#@@@@@@@@&BY. ~B@G^    "  
Write-Host "      ~YB#&@@@@@@@@@@#P7    .J&&P5! "  
Write-Host "         .::^^^^^^^^^^^:      .^^^: "
Write-Host "######################################"
Write-Host "# Welcome to Foxy Processor Module   #"
Write-Host "######################################"
Write-Host

# Variables
$APP_CONTAINER_NAME = "foxy-apps"
$APP_SCRIPT_PATH = "processor/app.py"
$INITIATOR_SCRIPT = "./w-foxy-install.ps1"

# Set PowerShell Execution Policy
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Function to check if Docker is installed
function Check-DockerInstalled {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "Docker is not installed."
        Write-Host "Please install Docker to continue."
        Write-Host "You can find installation instructions at: https://docs.docker.com/get-docker/"
        Exit 1
    }
}

# Function to check if the container exists
function Container-Exists {
    $containers = docker ps -a --format '{{.Names}}'
    return $containers -contains $APP_CONTAINER_NAME
}

# Function to check if the container is running
function Container-IsRunning {
    $runningContainers = docker ps --format '{{.Names}}'
    return $runningContainers -contains $APP_CONTAINER_NAME
}

# Function to restart the container if it's not running properly
function Restart-Container {
    Write-Host "Attempting to restart container $APP_CONTAINER_NAME..."
    docker restart $APP_CONTAINER_NAME
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to restart container $APP_CONTAINER_NAME. Please check the Docker logs for more details."
        Exit 1
    }
}

# Function to run the script inside the container
function Run-AppScript {
    if (Container-IsRunning) {
        Write-Host "Running $APP_SCRIPT_PATH inside the container $APP_CONTAINER_NAME..."
        docker exec -it $APP_CONTAINER_NAME python $APP_SCRIPT_PATH
    } else {
        Write-Host "Error: The container is no longer running."
        Restart-Container
        if (Container-IsRunning) {
            Write-Host "Container restarted successfully."
            Run-AppScript
        } else {
            Write-Host "Error: Could not restart the container."
            Exit 1
        }
    }
}

# Function to start the container using the initiator script
function Start-Container {
    Write-Host "Starting the container using '$INITIATOR_SCRIPT'..."
    if (Test-Path $INITIATOR_SCRIPT) {
        try {
            & "$INITIATOR_SCRIPT"
            Start-Sleep -Seconds 2
        } catch {
            Write-Host "Error while starting the container. Exception: $_"
            Exit 1
        }
    } else {
        Write-Host "Initiator script '$INITIATOR_SCRIPT' not found. Please ensure it is present in the current directory."
        Exit 1
    }
}

# Main script execution
Check-DockerInstalled

# Verificar si el contenedor existe
if (-not (Container-Exists)) {
    Write-Host "Container $APP_CONTAINER_NAME does not exist."
    Start-Container
}

# Verificar si el contenedor se ha iniciado
if (Container-Exists) {
    Write-Host "Container $APP_CONTAINER_NAME exists."
    if (Container-IsRunning) {
        Write-Host "Container $APP_CONTAINER_NAME is running."
    } else {
        Write-Host "Container $APP_CONTAINER_NAME is not running."
        Restart-Container
    }

    # Ejecutar el script dentro del contenedor
    if (Container-IsRunning) {
        Run-AppScript
    } else {
        Write-Host "Error: Container could not be started."
        Exit 1
    }
} else {
    Write-Host "Error: Container could not be created."
    Exit 1
}

# Pause the script until a key is pressed
Read-Host "Press any key to exit..."

