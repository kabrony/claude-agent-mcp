#!/bin/bash

echo "Installing Claude Agent dependencies..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed! Please install Python 3.8 or newer."
    echo "You can install it with: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "Dependencies installed successfully!"
echo ""
echo "To use the Claude Agent, run:"
echo "  source venv/bin/activate"
echo "  python agent.py --query \"Your query here\""
echo ""

# Make this script executable
chmod +x install_dependencies.sh
