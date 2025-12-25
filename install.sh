#!/bin/bash
# Installation script for Bird Detection and Tracking System

echo "========================================="
echo "Bird Detection System - Installation"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo ""
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping creation..."
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Create .env file if not exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your camera credentials"
fi

# Download YOLO model
echo ""
echo "Downloading YOLO11 model..."
python3 -c "from ultralytics import YOLO; model = YOLO('yolo11n.pt')"

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your camera credentials"
echo "2. Edit config.yaml to customize settings"
echo "3. Run: python main.py"
echo ""
echo "To activate the virtual environment later:"
echo "  source venv/bin/activate"
echo ""
