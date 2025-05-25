# Use official Python image
FROM python:3.11-slim

# Install system dependencies for Pygame and X11
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-pip \
        python3-dev \
        build-essential \
        libsdl2-dev \
        libsdl2-image-dev \
        libsdl2-mixer-dev \
        libsdl2-ttf-dev \
        libportmidi-dev \
        libswscale-dev \
        libavformat-dev \
        libavcodec-dev \
        libfreetype6-dev \
        xvfb \
        x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy code and assets
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir pygame

# By default, run with Xvfb (headless, for testing)
CMD ["sh", "-c", "xvfb-run -a python main.py"]

# To run with X11 forwarding (for GUI), override CMD at runtime:
# docker run -e DISPLAY=host.docker.internal:0.0 -v /tmp/.X11-unix:/tmp/.X11-unix deadhold-game
