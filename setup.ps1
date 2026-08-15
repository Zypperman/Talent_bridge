# Talent Bridge - one-shot local setup and run via Docker Compose (Windows PowerShell).
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# 1. Docker Compose availability
try {
    docker compose version | Out-Null
} catch {
    throw "Docker (with Compose v2) is required. Install Docker Desktop and try again."
}

# 2. .env
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env (fill in OPENROUTER_KEY, TURSO_DATABASE_URL, TURSO_AUTH_TOKEN before running)..."
    Set-Content -Path ".env" -Value "OPENROUTER_KEY=`nTURSO_DATABASE_URL=`nTURSO_AUTH_TOKEN="
}

# 3. Build and run the gateway (the app talks to a remote Turso database, so
#    there's no local data directory to bind-mount anymore)
Write-Host "Building and starting the gateway..."
Write-Host "Gateway will be available at http://127.0.0.1:8000 once the container is up."

$envContent = Get-Content ".env" -Raw
if ($envContent -notmatch "OPENROUTER_KEY=\S+" -or $envContent -notmatch "TURSO_DATABASE_URL=\S+") {
    Write-Host "Note: OPENROUTER_KEY / TURSO_DATABASE_URL / TURSO_AUTH_TOKEN are not all set in .env yet - the app will fail to start until they are."
}
Write-Host "Once your .env is filled in, seed courses (once) with:"
Write-Host "    python generate_courses.py"

docker compose up --build
