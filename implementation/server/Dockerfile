# Start with a Debian base image
FROM debian:latest

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    mosquitto \
    mosquitto-clients \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for the virtual environment
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the Python application and environment file
WORKDIR /app
COPY .env ./
COPY mosquitto.conf /etc/mosquitto/
COPY mqtt_tictactoe.py ./
COPY mqtt_laby.py ./

# Create and activate the virtual environment
RUN python3 -m venv $VIRTUAL_ENV

# Install Python packages
RUN pip3 install openai paho-mqtt python-dotenv

# Expose the default MQTT port
EXPOSE 1885