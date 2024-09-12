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
echo "######################################"
echo "# Welcome to Foxy Collector Module   #"
echo "######################################"
echo

#!/bin/bash

APP_CONTAINER_NAME="foxy-apps"
APP_SCRIPT_PATH="collector/app.py"
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
INITIATOR_SCRIPT="$SCRIPT_DIR/foxy-install.sh"

# Function to check if Docker is installed
check_docker_installed() {
    if ! command -v docker > /dev/null 2>&1; then
        echo "Docker is not installed."
        echo "Please install Docker to continue."
        echo "You can find installation instructions at: https://docs.docker.com/get-docker/"
        exit 1
    fi
}

# Function to check if the container exists
container_exists() {
    docker ps -a --format '{{.Names}}' | grep -q "^$APP_CONTAINER_NAME$"
}

# Function to check if the container is running
container_is_running() {
    docker ps -q -f name="$APP_CONTAINER_NAME" > /dev/null 2>&1
}

# Function to run the script inside the container
run_app_script() {
    echo "Running $APP_SCRIPT_PATH inside the container $APP_CONTAINER_NAME..."
    docker exec -it "$APP_CONTAINER_NAME" python "$APP_SCRIPT_PATH"
}

# Function to start the container using the initiator script
start_container() {
    echo "Starting the container using '$INITIATOR_SCRIPT'..."
    if [ -f "$INITIATOR_SCRIPT" ]; then
        bash "$INITIATOR_SCRIPT"
        # Wait a few seconds to give the container time to start
        sleep 2
    else
        echo "Initiator script '$INITIATOR_SCRIPT' not found. Please ensure it is present in the current directory."
        exit 1
    fi
}

# Main script execution

check_docker_installed

if container_exists; then
    echo "Container $APP_CONTAINER_NAME exists."

    if container_is_running; then
        echo "Container $APP_CONTAINER_NAME is running."
        run_app_script
    else
        echo "Container $APP_CONTAINER_NAME is not running."
        start_container

        if container_is_running; then
            echo "Container $APP_CONTAINER_NAME is now running."
            run_app_script
        else
            echo "Container $APP_CONTAINER_NAME failed to start. Please check the '$INITIATOR_SCRIPT' for errors."
            exit 1
        fi
    fi
else
    echo "Container $APP_CONTAINER_NAME does not exist."
    start_container

    if container_exists; then
        echo "Container $APP_CONTAINER_NAME has been created and started."
        run_app_script
    else
        echo "Container $APP_CONTAINER_NAME could not be created. Please check the '$INITIATOR_SCRIPT' for errors."
        exit 1
    fi
fi

# Pause the script until a key is pressed
read -p "Press any key to exit..."

