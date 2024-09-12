FROM python:3.10.2-bullseye

# Create a non-root user and group
RUN groupadd -r foxy && useradd -r -g foxy foxy

# Set working directory
WORKDIR /apps

# Install necessary packages with retry logic
RUN apt-get update && \
    apt-get install -y --no-install-recommends apt-utils && \
    for package in sudo git gcc libglib2.0-0 tesseract-ocr wget unzip jq libxss1 libappindicator1 libgconf-2-4 fonts-liberation libasound2 libnspr4 libnss3 libx11-xcb1 libxtst6 lsb-release xdg-utils libgbm1 libatk-bridge2.0-0 libgtk-3-0 libxcb-dri3-0 ffmpeg curl jq; do \
        echo "Installing $package" && \
        for i in 1 2 3 4 5; do \
            apt-get install -y $package && break || \
            echo "Retrying $package ($i/5)" && sleep 2; \
        done; \
    done && \
    rm -rf /var/lib/apt/lists/*
RUN sudo apt-get install -y x11-apps xauth xvfb libx11-dev    
RUN sudo apt install gnome-screenshot


# Fetch the latest version numbers and URLs for Chrome and ChromeDriver
RUN curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json > /tmp/versions.json && \
    CHROME_URL=$(jq -r '.channels.Stable.downloads.chrome[] | select(.platform=="linux64") | .url' /tmp/versions.json) && \
    wget -q --continue -O /tmp/chrome-linux64.zip $CHROME_URL && \
    unzip /tmp/chrome-linux64.zip -d /opt/chrome && \
    chmod +x /opt/chrome/chrome-linux64/chrome && \
    CHROMEDRIVER_URL=$(jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url' /tmp/versions.json) && \
    wget -q --continue -O /tmp/chromedriver-linux64.zip $CHROMEDRIVER_URL && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/chromedriver && \
    chmod +x /opt/chromedriver/chromedriver-linux64/chromedriver && \
    rm /tmp/chrome-linux64.zip /tmp/chromedriver-linux64.zip /tmp/versions.json

# Set up Chromedriver Environment variables
ENV CHROMEDRIVER_DIR /opt/chromedriver
ENV PATH $CHROMEDRIVER_DIR:$PATH

# Install and update pip
RUN python -m pip install --upgrade pip

# Install Python packages from requirements.txt
COPY requirements.txt /apps/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip3 install pyautogui
# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Change ownership and set permissions for /apps and /home/foxy
RUN chown -R foxy:foxy /apps && \
    chmod -R 777 /apps && \
    mkdir -p /home/foxy && \
    chown -R foxy:foxy /home/foxy && \
    chmod -R 777 /home/foxy
    
# Update PATH for non-root user
ENV PATH="/home/foxy/.local/bin:${PATH}"

# Switch to the non-root user
USER foxy

# Set the working directory to 'foxy's home
WORKDIR /home/foxy

RUN if [ -e /home/foxy/.Xauthority ]; then rm /home/foxy/.Xauthority; fi && \
    export DISPLAY=:99 && \
    COOKIE=$(mcookie) && \
    touch /home/foxy/.Xauthority && \
    xauth add $DISPLAY . $COOKIE && \
    cat /home/foxy/.Xauthority
    
    
EXPOSE 3053

