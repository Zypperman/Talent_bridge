# Talent Bridge - one-shot local setup and run (Windows PowerShell).
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# 1. Virtual environment
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

$venvPy = ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    throw "Could not find a python executable inside .venv"
}

# 2. Dependencies
Write-Host "Installing dependencies..."
& $venvPy -m pip install --quiet --upgrade pip
& $venvPy -m pip install --quiet -r requirements.txt

# 3. .env
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env (fill in ANTHROPIC_API_KEY before chatting or seeding courses)..."
    Set-Content -Path ".env" -Value "ANTHROPIC_API_KEY="
}

# 4. Local DB path for dev (production still defaults to /opt/talentbridge/data/talentbridge.db)
$env:TALENTBRIDGE_DB_PATH = Join-Path (Get-Location) "data\talentbridge.db"
New-Item -ItemType Directory -Force -Path "data" | Out-Null

# 5. Schema
if (-not (Test-Path $env:TALENTBRIDGE_DB_PATH)) {
    Write-Host "Initializing database schema at $($env:TALENTBRIDGE_DB_PATH)..."
    & $venvPy -c "import os, sqlite3; conn = sqlite3.connect(os.environ['TALENTBRIDGE_DB_PATH']); conn.executescript(open('schema.sql').read()); conn.commit()"
}

# 6. Seed courses if the table is empty
$courseCount = (& $venvPy -c "import os, sqlite3; conn = sqlite3.connect(os.environ['TALENTBRIDGE_DB_PATH']); print(conn.execute('SELECT COUNT(*) FROM courses').fetchone()[0])").Trim()
if ($courseCount -eq "0") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "ANTHROPIC_API_KEY=\S+") {
        Write-Host "Seeding courses (this calls the Anthropic API)..."
        & $venvPy generate_courses.py
    } else {
        Write-Host "Skipping course seeding: set ANTHROPIC_API_KEY in .env, then run '$venvPy generate_courses.py' manually."
    }
}

# 7. Run
Write-Host "Starting server at http://127.0.0.1:8000 ..."
& $venvPy -m uvicorn main:app --reload
