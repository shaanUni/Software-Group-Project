Write-Host "Starting Windows environment setup..." -ForegroundColor Cyan

# Create Virtual Environment
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
} else {
    Write-Host "Virtual environment already exists."
}

# Activate Virtual Environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install Dependencies
$REQ_FILE = Get-ChildItem -Recurse -Filter "requirements.txt" | Select-Object -First 1

if ($REQ_FILE) {
    Write-Host "Installing dependencies from $($REQ_FILE.FullName)..."
    pip install -r $REQ_FILE.FullName
} else {
    Write-Host "No requirements.txt found. Installing Django manually..." -ForegroundColor Yellow
    pip install django
    pip freeze > requirements.txt
}

# Run Migrations
$MANAGE_PY = Get-ChildItem -Recurse -Filter "manage.py" | Select-Object -First 1

if ($MANAGE_PY) {
    Write-Host " Running database migrations..."
    python $MANAGE_PY.FullName migrate
    Write-Host " Setup Complete!" -ForegroundColor Green
    Write-Host "Starting server..."
    python $($MANAGE_PY.FullName) runserver
} else {
    Write-Host "Error: Could not find manage.py." -ForegroundColor Red
}