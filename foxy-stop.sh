#!/bin/bash
echo "                              .     " 
echo "                           .~5B.    " 
echo "                         ~P#@@@?    " 
echo "                        !@@@@@@@J.  " 
echo "  ^~~^:.                P@@@@@@&&BY." 
echo "  ^5@@&#G?:            !&@@@@@&!.:. "  
echo "    ?@@@@@&!       .^!5@@@@@@@@G    "  
echo "     B@@@@@&:   ^JG&@@@@@@@@@@@?    "  
echo "    .#@@@@@@~ ^P@@@@@@@@@@@@@&7     "  
echo "    ?@@@@@@&.^&@@@@@@@@@@@@@@7      "  
echo "    5@@@@@@G G@@@@@@@@@@@@@@@!      "  
echo "    J@@@@@@#:#@@@@@@@@@@@G?@@G.     "  
echo "    .P@@@@@@P#@@@@@@@@&BY. ~B@G^    "  
echo "      ~YB#&@@@@@@@@@@#P7    .J&&P5! "  
echo "         .::^^^^^^^^^^^:      .^^^: "
# ASCII art header
echo "######################################"
echo "#     Welcome to Foxy Stopper!       #"
echo "#####################################"
echo

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
# Define the path to the Docker Compose file
COMPOSE_FILE="$SCRIPT_DIR/foxy-system/docker-compose-dev.yaml"
#COMPOSE_FILE="./foxy-system/docker-compose-dev.yaml"

# Check if Docker is installed
if command -v docker > /dev/null 2>&1; then
    echo "Docker is installed."

    # Try stopping Docker Compose services
    if command -v docker-compose > /dev/null 2>&1; then
        echo "Stopping Docker Compose services with docker-compose..."
        docker-compose -f "$COMPOSE_FILE" down 2>/dev/null
    elif command -v docker > /dev/null 2>&1 && docker compose version > /dev/null 2>&1; then
        echo "Stopping Docker Compose services with docker compose..."
        docker compose -f "$COMPOSE_FILE" down
    elif command -v docker > /dev/null 2>&1 && docker --help | grep -q 'compose'; then
    	echo "Stopping Docker Compose services with Docker's built-in compose..."
    	docker compose -f "$COMPOSE_FILE" down
    else
        echo "Neither docker-compose nor docker compose is available."
        exit 1
    fi

    # echo "Removing stopped containers and networks..."
    # docker system prune -f

else
    echo "Docker is not installed."
    echo "Please install Docker to continue."
    echo "You can find installation instructions at: https://docs.docker.com/get-docker/"
fi

# Pause the script until a key is pressed
read -p "Press any key to exit..."

