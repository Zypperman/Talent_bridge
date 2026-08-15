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
    Write-Host "Creating .env (fill in ANTHROPIC_API_KEY before chatting or seeding courses)..."
    Set-Content -Path ".env" -Value "ANTHROPIC_API_KEY="
}

# 3. Data directory (bind-mounted into the gateway/auth-service/teaching-service containers)
New-Item -ItemType Directory -Force -Path "data" | Out-Null

# 4. Build and run every service (gateway, auth-service, teaching-service, redis)
Write-Host "Building and starting services..."
Write-Host "Gateway will be available at http://127.0.0.1:8000 once containers are up."

$envContent = Get-Content ".env" -Raw
if ($envContent -notmatch "ANTHROPIC_API_KEY=\S+") {
    Write-Host "Note: ANTHROPIC_API_KEY is not set in .env yet, so teaching-service will fail to answer chats/evaluations until you set it and restart."
}
Write-Host "Once ANTHROPIC_API_KEY is set and containers are running, seed courses (once) with:"
Write-Host "    docker compose run --rm teaching-service python generate_courses.py"

docker compose up --build
