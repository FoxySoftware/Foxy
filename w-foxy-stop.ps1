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
Write-Host "#     Welcome to Foxy Stopper!       #"
Write-Host "######################################"
Write-Host


$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
# Define the path to the Docker Compose file
$COMPOSE_FILE = Join-Path $SCRIPT_DIR "/foxy-system/docker-compose-dev.yaml"


# Check if Docker is installed
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Docker is installed."

    # Try stopping Docker Compose services
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        Write-Host "Stopping Docker Compose services with docker-compose..."
        docker-compose -f $COMPOSE_FILE down
    } elseif ((docker compose version) -ne $null) {
        Write-Host "Stopping Docker Compose services with docker compose..."
        docker compose -f $COMPOSE_FILE down
    } else {
        Write-Host "Neither docker-compose nor docker compose is available."
        Exit 1
    }

    # Optionally remove stopped containers, networks, and volumes
    # Uncomment the following lines if you want to clean up resources
    # Write-Host "Removing stopped containers and networks..."
    # docker system prune -f
} else {
    Write-Host "Docker is not installed."
    Write-Host "Please install Docker to continue."
    Write-Host "You can find installation instructions at: https://docs.docker.com/get-docker/"
}

# Confirmation message
Write-Host "Containers stopped and removed (if `docker-compose down` was used)."

# Pause the script until a key is pressed
Read-Host "Press any key to exit..."

