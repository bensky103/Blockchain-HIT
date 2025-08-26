# Create virtual environment and install dependencies

# Check if venv already exists
if (Test-Path -Path "venv") {
    Write-Host "Virtual environment already exists"
}
else {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate venv
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

Write-Host "Setup complete. Virtual environment is active."
