<#
.SYNOPSIS
Test the AXIS API endpoints
.DESCRIPTION
Tests report generation, assessments, and AI integration
.EXAMPLE
. .\test_api.ps1
#>

$baseUrl = "http://localhost:8000"

Write-Host "`n" + "="*70 -ForegroundColor Cyan
Write-Host "AXIS API TEST SUITE" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan

# Check for token
if (-not $env:AUTH_TOKEN) {
    Write-Host "`nError: AUTH_TOKEN not set" -ForegroundColor Red
    Write-Host "Run: . .\get_token.ps1`n" -ForegroundColor Yellow
    exit
}

$headers = @{
    "Authorization" = "Bearer $env:AUTH_TOKEN"
    "Content-Type" = "application/json"
}

Write-Host "`nUsing token: " -ForegroundColor Green -NoNewline
Write-Host $env:AUTH_TOKEN.Substring(0, 40) + "..." -ForegroundColor White

# Test 1: Get audits list
Write-Host "`n[1/5] Testing: GET /hospitality/audits" -ForegroundColor Yellow
try {
    $audits = Invoke-RestMethod -Uri "$baseUrl/hospitality/audits" `
        -Headers $headers `
        -ErrorAction Stop

    Write-Host "  Found $($audits.Count) audits" -ForegroundColor Green

    if ($audits.Count -gt 0) {
        $auditId = $audits[0].id
        $auditTitle = $audits[0].title
        Write-Host "  Using: $auditTitle (ID: $auditId)" -ForegroundColor Green
        $auditId | Out-File "audit_id.txt"
    }
}
catch {
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    exit
}

# Test 2: Get audit details
Write-Host "`n[2/5] Testing: GET /hospitality/audits/{id}" -ForegroundColor Yellow
try {
    $audit = Invoke-RestMethod -Uri "$baseUrl/hospitality/audits/$auditId" `
        -Headers $headers `
        -ErrorAction Stop

    Write-Host "  Title: $($audit.title)" -ForegroundColor Green
    Write-Host "  Site: $($audit.site_name)" -ForegroundColor Green
    Write-Host "  Status: $($audit.status)" -ForegroundColor Green
    Write-Host "  Version: $($audit.version)" -ForegroundColor Green
    Write-Host "  Assessments: $($audit.bundle.assessments.Count)" -ForegroundColor Green
    Write-Host "  Evidence: $($audit.bundle.evidence.Count)" -ForegroundColor Green
}
catch {
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Get readiness report
Write-Host "`n[3/5] Testing: GET /hospitality/audits/{id}/readiness" -ForegroundColor Yellow
try {
    $readiness = Invoke-RestMethod -Uri "$baseUrl/hospitality/audits/$auditId/readiness" `
        -Headers $headers `
        -ErrorAction Stop

    Write-Host "  Report title: $($readiness.report.title)" -ForegroundColor Green
    Write-Host "  Hotel: $($readiness.report.hotel)" -ForegroundColor Green
    Write-Host "  Pillars assessed: $($readiness.report.pillars.Count)" -ForegroundColor Green
    Write-Host "  Evidence items: $($readiness.report.evidence_register.Count)" -ForegroundColor Green

    $readiness | ConvertTo-Json -Depth 10 | Out-File "readiness_report.json"
    Write-Host "  Saved to: readiness_report.json" -ForegroundColor Green
}
catch {
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Get JSON report
Write-Host "`n[4/5] Testing: GET /hospitality/audits/{id}/report?format=json" -ForegroundColor Yellow
try {
    $report = Invoke-RestMethod -Uri "$baseUrl/hospitality/audits/$auditId/report?format=json" `
        -Headers $headers `
        -ErrorAction Stop

    Write-Host "  Audit ID: $($report.audit.id)" -ForegroundColor Green
    Write-Host "  Assessments: $($report.assessments.Count)" -ForegroundColor Green
    Write-Host "  Evidence: $($report.evidence.Count)" -ForegroundColor Green

    $report | ConvertTo-Json -Depth 10 | Out-File "audit_report.json"
    Write-Host "  Saved to: audit_report.json" -ForegroundColor Green
}
catch {
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Get Markdown report
Write-Host "`n[5/5] Testing: GET /hospitality/audits/{id}/report?format=markdown" -ForegroundColor Yellow
try {
    $markdown = Invoke-RestMethod -Uri "$baseUrl/hospitality/audits/$auditId/report?format=markdown" `
        -Headers $headers `
        -ErrorAction Stop

    $markdown | Out-File "audit_report.md"
    Write-Host "  Markdown report generated" -ForegroundColor Green
    Write-Host "  Saved to: audit_report.md" -ForegroundColor Green
    Write-Host "  Size: $($markdown.Length) characters" -ForegroundColor Green
}
catch {
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Optional: Test AI integration
Write-Host "`n[Optional] Testing AI integration..." -ForegroundColor Yellow
try {
    Write-Host "  Checking for OpenRouter API configuration..." -ForegroundColor Cyan

    $aiTest = Invoke-RestMethod -Uri "$baseUrl/hospitality/audits/$auditId/readiness/generate-ai" `
        -Headers $headers `
        -Method Post `
        -Body "{}" `
        -ErrorAction Stop

    Write-Host "  AI narrative generated successfully!" -ForegroundColor Green
    Write-Host "  Saved to: ai_narrative.json" -ForegroundColor Green

    $aiTest | ConvertTo-Json -Depth 10 | Out-File "ai_narrative.json"
}
catch {
    if ($_.Exception.Message -match "openrouter_api_key") {
        Write-Host "  AI not configured (requires OPENROUTER_API_KEY)" -ForegroundColor Yellow
        Write-Host "  To enable: Set OPENROUTER_API_KEY in .env and restart API" -ForegroundColor Yellow
    }
    else {
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n" + "="*70 -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan

Write-Host "`nGenerated files:" -ForegroundColor Green
Write-Host "  - readiness_report.json (Readiness assessment)" -ForegroundColor White
Write-Host "  - audit_report.json (Audit data export)" -ForegroundColor White
Write-Host "  - audit_report.md (Markdown summary)" -ForegroundColor White
if (Test-Path "ai_narrative.json") {
    Write-Host "  - ai_narrative.json (AI-generated content)" -ForegroundColor White
}

Write-Host "`nAudit ID saved to: audit_id.txt" -ForegroundColor Green

Write-Host "`nWhat you can do next:" -ForegroundColor Yellow
Write-Host "  1. Review the generated JSON files in VS Code" -ForegroundColor White
Write-Host "  2. Share markdown reports via email" -ForegroundColor White
Write-Host "  3. Convert JSON to Word using python-docx" -ForegroundColor White
Write-Host "  4. Test more endpoints with different assessments" -ForegroundColor White
Write-Host "  5. Set up OpenRouter API for AI-generated narratives" -ForegroundColor White

Write-Host "`n" + "="*70 -ForegroundColor Cyan + "`n"
