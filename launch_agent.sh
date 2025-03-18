#!/bin/bash

# Set title (works in most terminals)
echo -e "\033]0;OrganiX Claude Agent Launcher\007"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed!"
    echo "Please install Python 3.8 or newer."
    echo "You can install it with: sudo apt-get install python3 python3-pip python3-venv"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Setting up..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    read -p "Press Enter to exit..."
    exit 1
fi

# Check for dependencies
pip show rich &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies."
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Clear the screen
clear

# Display menu
echo
echo "==================================="
echo "    OrganiX Claude Agent Launcher"
echo "==================================="
echo
echo "Select an option:"
echo "1. Launch Terminal Dashboard"
echo "2. Launch Web Dashboard"
echo "3. Launch CLI Agent"
echo "4. Manage Environment"
echo "5. Run Memory Maintenance"
echo "6. Install/Update Dependencies"
echo "7. Exit"
echo

# Get user input
read -p "Enter your choice (1-7): " choice

# Process choice
case $choice in
    1)
        clear
        echo "Launching Terminal Dashboard..."
        python dashboard.py
        ;;
    2)
        clear
        echo "Launching Web Dashboard..."
        echo "This will start a web server on http://localhost:8080"
        echo "Press Ctrl+C to stop the server."
        echo
        python web_server.py
        ;;
    3)
        clear
        echo "Launching CLI Agent..."
        echo "Type your query after the prompt."
        echo "Press Ctrl+C to exit."
        echo
        python agent.py
        ;;
    4)
        clear
        echo "Environment Management"
        python model_manager.py interactive
        # Return to this menu after exiting model manager
        exec $0
        ;;
    5)
        clear
        echo "Running Memory Maintenance..."
        python agent.py --maintenance
        read -p "Press Enter to continue..."
        # Return to this menu
        exec $0
        ;;
    6)
        clear
        echo "Installing/Updating Dependencies..."
        pip install -r requirements.txt
        echo
        echo "Dependencies installed/updated."
        read -p "Press Enter to continue..."
        # Return to this menu
        exec $0
        ;;
    7)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Please try again."
        read -p "Press Enter to continue..."
        # Return to this menu
        exec $0
        ;;
esac

# Make the script executable when created
chmod +x launch_agent.sh
