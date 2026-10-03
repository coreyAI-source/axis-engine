#Requires -Version 5.1
<#
.SYNOPSIS
One-click setup to run the full API with test audit data
.DESCRIPTION
Starts Docker services, creates test data, and runs the API
.EXAMPLE
.\setup_and_run.ps1
#>

param(
    [switch]$SkipDocker,
    [switch]$SkipDatabase
)

$ErrorActionPreference = "Stop"

Write-Host "`n" + "="*70 -ForegroundColor Cyan
Write-Host "AXIS ENGINE - FULL SETUP" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan

# Step 1: Fix dependencies
Write-Host "`n[1/5] Fixing dependencies..." -ForegroundColor Yellow
pip install --upgrade pydantic pydantic-settings -q 2>&1 | Select-String "Successfully" -ErrorAction SilentlyContinue
Write-Host "  Done: Dependencies upgraded" -ForegroundColor Green

# Step 2: Start Docker (optional)
if (-not $SkipDocker) {
    Write-Host "`n[2/5] Starting Docker services..." -ForegroundColor Yellow
    $currentDir = Get-Location
    try {
        Set-Location infra
        Write-Host "  Running: docker compose up -d"
        docker compose up -d 2>&1 | Where-Object {$_ -match "(Starting|Created)"}
        Write-Host "  Waiting for database to be healthy..." -ForegroundColor Cyan
        $attempts = 0
        while ($attempts -lt 30) {
            $status = docker compose ps db 2>&1 | Select-String "healthy"
            if ($status) {
                Write-Host "  Database is healthy!" -ForegroundColor Green
                break
            }
            Start-Sleep -Seconds 1
            $attempts++
        }
        if ($attempts -eq 30) {
            Write-Host "  Warning: Database may not be fully ready yet" -ForegroundColor Yellow
        }
    }
    finally {
        Set-Location $currentDir
    }
} else {
    Write-Host "`n[2/5] Skipping Docker (using existing services)" -ForegroundColor Yellow
}

# Step 3: Create test audit data
if (-not $SkipDatabase) {
    Write-Host "`n[3/5] Creating test audit data..." -ForegroundColor Yellow
    Write-Host "  Running: python setup_test_audit.py"
    python setup_test_audit.py 2>&1 | Select-String "(complete|Audit ID|Error)" -ErrorAction SilentlyContinue
    $auditOutput = python setup_test_audit.py 2>&1
    if ($auditOutput -match "Audit ID: ([a-f0-9\-]+)") {
        $auditId = $matches[1]
        Write-Host "  Created audit: $auditId" -ForegroundColor Green
        $auditId | Out-File "AUDIT_ID.txt"
        Write-Host "  Saved to: AUDIT_ID.txt" -ForegroundColor Green
    }
    else {
        Write-Host "  Done: Test data created" -ForegroundColor Green
    }
} else {
    Write-Host "`n[3/5] Skipping database setup" -ForegroundColor Yellow
}

# Step 4: Show API startup info
Write-Host "`n[4/5] Preparing API startup..." -ForegroundColor Yellow

Write-Host "`n" + "="*70 -ForegroundColor Green
Write-Host "READY TO START API" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Green

Write-Host "`n[5/5] Next step: Start the API" -ForegroundColor Yellow

Write-Host "`nRun this command in a new PowerShell window:`n" -ForegroundColor Cyan
Write-Host "  cd services\api" -ForegroundColor White
Write-Host "  uvicorn app.main:app --reload --port 8000" -ForegroundColor White

Write-Host "`nThen in another window, get your auth token:`n" -ForegroundColor Cyan
Write-Host "  . ..\get_token.ps1" -ForegroundColor White

Write-Host "`nAPI will run at: http://localhost:8000" -ForegroundColor Green
Write-Host "Web UI at: http://localhost:3000 (after running npm run dev in apps\web)" -ForegroundColor Green

Write-Host "`nTest user credentials:" -ForegroundColor Cyan
Write-Host "  Email: auditor@test.local" -ForegroundColor White
Write-Host "  Password: TestPassword123!" -ForegroundColor White

Write-Host "`nFor AI integration, set OPENROUTER_API_KEY in .env" -ForegroundColor Cyan

Write-Host "`n" + "="*70 -ForegroundColor Cyan
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Cyan + "`n"
