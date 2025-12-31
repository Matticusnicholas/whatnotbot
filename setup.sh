#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "  Whatnot Giveaway Bot - Mac/Linux Setup"
echo "========================================"
echo ""

# Check if Python 3 is installed
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    PYTHON_VERSION=$(python --version 2>&1 | grep -oP '(?<=Python )\d')
    if [ "$PYTHON_VERSION" == "3" ]; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    else
        echo -e "${RED}[ERROR]${NC} Python 3 is required but not found!"
        echo ""
        echo "Please install Python 3.8+ using one of these methods:"
        echo "  - macOS: brew install python3"
        echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "  - Or download from: https://www.python.org/downloads/"
        echo ""
        exit 1
    fi
else
    echo -e "${RED}[ERROR]${NC} Python is not installed!"
    echo ""
    echo "Please install Python 3.8+ using one of these methods:"
    echo "  - macOS: brew install python3"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  - Or download from: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Python found:"
$PYTHON_CMD --version
echo ""

# Check if pip is available
if ! command -v $PIP_CMD &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} pip is not available!"
    echo "Please install pip: $PYTHON_CMD -m ensurepip --upgrade"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} pip found:"
$PIP_CMD --version
echo ""

# Create virtual environment
echo -e "${BLUE}[INFO]${NC} Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${BLUE}[INFO]${NC} Virtual environment already exists, skipping creation."
else
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Failed to create virtual environment!"
        echo "Try: sudo apt install python3-venv (on Ubuntu/Debian)"
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Virtual environment created."
fi
echo ""

# Activate virtual environment and install dependencies
echo -e "${BLUE}[INFO]${NC} Installing dependencies..."
source venv/bin/activate

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Failed to install dependencies!"
    exit 1
fi

echo ""
echo -e "${GREEN}[OK]${NC} All dependencies installed successfully!"
echo ""

# Check for browsers
echo -e "${BLUE}[INFO]${NC} Checking for browsers..."

# Check for Firefox
if [ -d "/Applications/Firefox.app" ]; then
    echo -e "${GREEN}[OK]${NC} Firefox found at: /Applications/Firefox.app"
elif command -v firefox &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Firefox found in PATH"
else
    echo -e "${YELLOW}[WARNING]${NC} Firefox not found."
    echo "          Download from: https://www.mozilla.org/firefox/"
fi

# Check for Safari (macOS only)
if [ "$(uname)" == "Darwin" ]; then
    if [ -d "/Applications/Safari.app" ]; then
        echo -e "${GREEN}[OK]${NC} Safari found at: /Applications/Safari.app"
        echo ""
        echo -e "${YELLOW}[NOTE]${NC} To use Safari, enable WebDriver:"
        echo "        Run: safaridriver --enable"
    fi
fi

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To start the bot, run: ./run.sh"
echo "Or: bash run.sh"
echo ""

# Make run.sh executable
chmod +x run.sh 2>/dev/null
