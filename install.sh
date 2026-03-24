#!/bin/bash

# Verifica se um comando existe, aborta se não
require_cmd() {
    local cmd=$1 msg=$2
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: '$cmd' not found. $msg"
        exit 1
    fi
}

show_help() {
    echo "Usage: ./install.sh [OPTIONS]"
    echo "Options:"
    echo "  -l, --local   Install dependencies in a local .venv"
    echo "  -D, --docker  Build the Docker image"
    echo "  -f, --force   Force uninstallation before installing"
    exit 1
}

MODE=""
FORCE="false"

for arg in "$@"
do
    case $arg in
        -l|--local)
        MODE="local"
        ;;
        -D|--docker)
        MODE="docker"
        ;;
        -f|--force)
        FORCE="true"
        ;;
    esac
done

if [ -z "$MODE" ]; then
    show_help
fi

if [ "$FORCE" = "true" ]; then
    echo "Force mode detected. Uninstalling existing setup..."
    if [ "$MODE" = "local" ]; then
        ./uninstall.sh --local
    else
        ./uninstall.sh --docker
    fi
fi

if [ "$MODE" = "local" ]; then
    require_cmd python3 "Install Python 3: sudo apt install python3 (Ubuntu) | brew install python3 (Mac)"
    if ! python3 -m pip --version >/dev/null 2>&1; then
        echo "Error: pip not found for python3. Install: sudo apt install python3-pip (Ubuntu)"
        exit 1
    fi

    if [ -d ".venv" ]; then
        echo "Local environment (.venv) already exists. Checking dependencies..."
        source .venv/bin/activate
        # We run pip install because it's fast if requirements match, ensuring correctness.
        # But if you want to strictly SKIP:
        # echo "Skipping installation."
        pip install -r requirements.txt
    else
        echo "Creating .venv..."
        python3 -m venv .venv
        source .venv/bin/activate
        echo "Installing dependencies..."
        pip install -r requirements.txt
    fi
    echo "Local setup ready."
else
    # Docker mode
    require_cmd docker "Install Docker: https://docs.docker.com/get-docker/"

    if docker compose version >/dev/null 2>&1; then
        CMD="docker compose"
    else
        CMD="docker-compose"
    fi
    
    # Check if images exist for the service.
    if [ -z "$($CMD images -q app)" ]; then
        echo "Docker image not found. Building..."
        $CMD build
    else
        echo "Docker image exists. Skipping build (run ./install.sh --force to force rebuild if needed)."
    fi
    echo "Docker setup ready."
fi
