#!/bin/bash

echo "######################################"
echo "#     Welcome to Foxy Install!     #"
echo "#####################################"
echo

# Allow the script to continue even if errors occur


OS_HOST=$(uname)
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
ENV_FILE="$SCRIPT_DIR/config/os_general.env"
IMAGE_NAME="bueltan/foxy-system-base:libs"
TAR_FILE="$SCRIPT_DIR/foxy-system/foxy-system-base-libs.tar"
COMPOSE_FILE="$SCRIPT_DIR/foxy-system/docker-compose-dev.yaml"
USER_UID=$(id -u)
USER_GID=$(id -g)

ICON_COLLECTOR="$SCRIPT_DIR/foxy-system/icons/foxy_icon_collector.png"
ICON_PROCESSOR="$SCRIPT_DIR/foxy-system/icons/foxy_icon_processor.png"
ICON_STOP="$SCRIPT_DIR/foxy-system/icons/foxy_icon_stop.png"
DESKTOP_FOLDER="$HOME/Desktop/"
APPLICATIONS_FOLDER="$HOME/.local/share/applications/"

set +e
create_shortcut() {
    local script_name=$1
    local shortcut_name=$2
    local icon_path=$3
    local script_path="$SCRIPT_DIR/$script_name"
    
    if [ "$OS_HOST" == "Darwin" ]; then
        echo "macOS detected. Creating app shortcut..."

        if [ -f "$script_path" ]; then
            chmod +x "$script_path"
            
            # Create a macOS .app bundle
            local app_dir="$APPLICATIONS_FOLDER/$shortcut_name.app/Contents"
            mkdir -p "$app_dir/MacOS"
            mkdir -p "$app_dir/Resources"

            # Create the Info.plist file
            echo '<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>CFBundleExecutable</key>
                <string>'"$script_name"'</string>
                <key>CFBundleIconFile</key>
                <string>icon.icns</string>
                <key>CFBundleIdentifier</key>
                <string>com.yourdomain.'"$shortcut_name"'</string>
                <key>CFBundleName</key>
                <string>'"$shortcut_name"'</string>
                <key>CFBundleVersion</key>
                <string>1.0</string>
            </dict>
            </plist>' > "$app_dir/Info.plist"

            # Copy the script to the app's MacOS directory
            cp "$script_path" "$app_dir/MacOS/$script_name"
            chmod +x "$app_dir/MacOS/$script_name"

            # Copy the icon to the app's Resources directory
            cp "$icon_path" "$app_dir/Resources/icon.icns"

            echo "App shortcut for $shortcut_name created in $APPLICATIONS_FOLDER"
        else
            echo "Script $script_path not found. Skipping..."
        fi
    else
        echo "Linux detected. Creating desktop shortcuts..."

        if [ -f "$script_path" ]; then
            chmod +x "$script_path"
            
            # Create desktop shortcut
            local desktop_file="$DESKTOP_FOLDER$shortcut_name.desktop"
            echo "[Desktop Entry]
Name=$shortcut_name
Comment=Run $shortcut_name
Exec=$script_path
Icon=$icon_path
Terminal=true
Type=Application" > "$desktop_file"
            chmod +x "$desktop_file"
            echo "Shortcut for $shortcut_name created at $desktop_file"
            
            # Create shortcut in applications folder (for Ubuntu launcher)
            local applications_file="$APPLICATIONS_FOLDER$shortcut_name.desktop"
            echo "[Desktop Entry]
Name=$shortcut_name
Comment=Run $shortcut_name
Exec=$script_path
Icon=$icon_path
Terminal=true
Type=Application" > "$applications_file"
            chmod +x "$applications_file"
            echo "Shortcut for $shortcut_name created at $applications_file"
        else
            echo "Script $script_path not found. Skipping..."
        fi
    fi
}

# Create shortcuts for foxy-collector.sh, foxy-processor.sh, and foxy-stop.sh
create_shortcut "foxy-collector.sh" "Foxy Collector" $ICON_COLLECTOR
create_shortcut "foxy-processor.sh" "Foxy Processor" $ICON_PROCESSOR
create_shortcut "foxy-stop.sh" "Foxy Stop" $ICON_STOP

# Re-enable exit on error if desired later in the script
set -e


# Check if the .env file already exists
if [ ! -f "$ENV_FILE" ]; then
    # If it doesn't exist, create the file
    touch "$ENV_FILE"
fi

# Function to update or append a variable in the .env file
update_env_file() {
    local key=$1
    local value=$2

    if grep -q "^$key=" "$ENV_FILE"; then
        if [ "$OS_HOST" = "Darwin" ]; then
            # macOS (Darwin) uses BSD sed
            sed -i '' "s|^$key=.*|$key=$value|" "$ENV_FILE"
        else
            # Linux uses GNU sed
            sed -i "s|^$key=.*|$key=$value|" "$ENV_FILE"
        fi
    else
        echo "$key=$value" >> "$ENV_FILE"
    fi
}

# Update or append variables to the .env file
update_env_file "FOXY_PATH" "$SCRIPT_DIR"
update_env_file "OS_HOST" "$OS_HOST"
update_env_file "UID" "$USER_UID"
update_env_file "GID" "$USER_GID"

# Print the operating system name
echo "Operating System: $OS_HOST"

# Check if Docker is installed
if command -v docker > /dev/null 2>&1; then
    echo "Docker is installed."

    # Check if the image is available locally
    if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
        echo "Image $IMAGE_NAME not found locally."

        # Check if the tar file is available
        if [ -f "$TAR_FILE" ]; then
            echo "Loading image from $TAR_FILE..."
            docker load -i "$TAR_FILE"
        else
            echo "Tar file not found. Attempting to pull the image from Docker Hub..."
            if ! docker pull "$IMAGE_NAME"; then
                echo "Failed to pull image from Docker Hub."
                exit 1
            fi
        fi
    else
        echo "Image $IMAGE_NAME is already available locally."
    fi

    # Check if Docker Compose file exists

    if [ -f "$COMPOSE_FILE" ]; then
        echo "Docker Compose file found."

        # Try with "docker-compose" first
        if command -v docker-compose > /dev/null 2>&1; then
            echo "Running Docker Compose with docker-compose..."
            docker-compose -f "$COMPOSE_FILE" up -d
        else
            # If "docker-compose" fails, try "docker compose"
            if command -v docker > /dev/null 2>&1 && docker compose version > /dev/null 2>&1; then
                echo "Running Docker Compose with docker compose..."
                docker compose -f "$COMPOSE_FILE" up -d
            else
                echo "Neither docker-compose nor docker compose is available."
                exit 1
            fi
        fi
    else
        echo "Docker Compose file not found: $COMPOSE_FILE"
    fi
else
    echo "Docker is not installed."
    echo "Please install Docker to continue."
    echo "You can find installation instructions at: https://docs.docker.com/get-docker/"
fi

# Confirmation message
echo "Path saved to $ENV_FILE"
read -p "Press any key to continue."
