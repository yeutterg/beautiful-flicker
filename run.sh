#!/bin/bash

# Beautiful Flicker Run Script
# Usage: ./run.sh [port]
# Example: ./run.sh 3000

# Default port
PORT=${1:-8080}

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Beautiful Flicker - Flask Web Application${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use!"
    echo ""
    echo "You can either:"
    echo "1. Stop the process using port $PORT"
    echo "2. Choose a different port: ./run.sh 3000"
    echo ""
    exit 1
fi

echo -e "Starting Beautiful Flicker on port ${GREEN}$PORT${NC}..."
echo ""

# Export the port for docker-compose
export PORT=$PORT

# Build and run with docker-compose
docker-compose up --build

# Note: Use Ctrl+C to stop the application