#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "  Whatnot Giveaway Bot - Starting..."
echo "========================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${RED}[ERROR]${NC} Virtual environment not found!"
    echo "Please run setup.sh first:"
    echo "  chmod +x setup.sh && ./setup.sh"
    echo ""
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Dependencies not installed!"
    echo "Please run setup.sh first."
    echo ""
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Virtual environment activated"
echo -e "${BLUE}[INFO]${NC} Starting web server..."
echo ""
echo "========================================"
echo -e "  ${CYAN}Open your browser and go to:${NC}"
echo -e "  ${CYAN}http://localhost:5000${NC}"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

# Start the Flask application
python app.py

# If we get here, the server stopped
echo ""
echo -e "${BLUE}[INFO]${NC} Server stopped."
