#!/bin/bash

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
    # Check if image exists (heuristic: check if build is needed? 
    # Docker compose 'up' usually handles this, but 'install' means 'build' here)
    
    # We will check if the service image is built.
    # Since compose names images predictably or we can just let compose check.
    # User asked: "see if installed or not before installing".
    
    # docker compose build is "installing".
    # Check if image exists.
    
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
