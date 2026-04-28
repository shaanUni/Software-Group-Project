#!/bin/bash

echo "Starting environment setup..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Dependencies
# This searches for requirements.txt even if it's in a subfolder
REQUIREMENT_FILE=$(find . -name "requirements.txt" | head -n 1)

if [ -f "$REQUIREMENT_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENT_FILE..."
    pip install -r "$REQUIREMENT_FILE"
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

# 5. Run Migrations
MANAGE_PY=$(find . -name "manage.py" | head -n 1)
if [ -f "$MANAGE_PY" ]; then
    echo "🗄️ Running database migrations..."
    python3 "$MANAGE_PY" migrate
    echo "Starting server..."
    python3 "$MANAGE_PY" runserver
else
    echo "manage.py not found. You might need to navigate to the app folder manually."
fi