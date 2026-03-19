#!/bin/bash

# Default values
MODE=""
DEBUG="false"

show_help() {
    echo "Usage: ./run.sh [OPTIONS]"
    echo "Options:"
    echo "  -l, --local   Run locally"
    echo "  -D, --docker  Run in Docker"
    echo "  -d, --debug   Enable debug mode (attached logs)"
    echo "  -s, --shell   Enter container shell (Docker only)"
    exit 1
}

# Parse arguments
for arg in "$@"
do
    case $arg in
        -l|--local)
        MODE="local"
        ;;
        -D|--docker)
        MODE="docker"
        ;;
        -d|--debug)
        DEBUG="true"
        ;;
        -s|--shell)
        SHELL_MODE="true"
        ;;
    esac
done

if [ -z "$MODE" ]; then
    show_help
fi

# Clean state before starting
echo "Ensuring port 6001 is free..."
./stop.sh >/dev/null 2>&1

start_local() {
    echo "Starting in LOCAL mode..."
    
    # Auto-install/Check
    ./install.sh --local
    
    source .venv/bin/activate
    
    # Check if port is busy
    if lsof -i:6001 -t >/dev/null ; then
        echo "Warning: Port 6001 is locally busy. Trying to start anyway (might fail)..."
        # Optional: ./stop.sh --local
    fi

    # Carrega variáveis do .env se existir
    if [ -f .env ]; then
        set -a
        source .env
        set +a
    fi

    echo "Starting application..."
    python main.py
}

start_docker() {
    echo "Starting in DOCKER mode..."
    
    # Check for docker compose availability
    if docker compose version >/dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker compose"
    elif docker-compose --version >/dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        echo "Error: docker-compose not found."
        exit 1
    fi
    
    # Auto-install/Check (Ensure image exists)
    ./install.sh --docker

    if [ "$SHELL_MODE" = "true" ]; then
        echo "Entering container shell..."
        echo "To start the server inside: python main.py"
        $DOCKER_COMPOSE_CMD run --rm --service-ports app /bin/bash
    elif [ "$DEBUG" = "true" ]; then
        echo "Running in DEBUG mode (attached logs)..."
        $DOCKER_COMPOSE_CMD up
    else
        # Just up, assume installed/built or let up build if missing
        $DOCKER_COMPOSE_CMD up -d
        echo "Container started in background."
    fi
}

if [ "$MODE" = "local" ]; then
    start_local
else
    start_docker
fi
