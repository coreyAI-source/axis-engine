<#
.SYNOPSIS
Get authentication token for API testing
.DESCRIPTION
Retrieves JWT token for API calls
.EXAMPLE
. .\get_token.ps1
#>

$baseUrl = "http://localhost:8000"
$username = "auditor@test.local"
$password = "TestPassword123!"

Write-Host "Requesting token from $baseUrl..." -ForegroundColor Cyan

try {
    $body = @{
        username = $username
        password = $password
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/auth/token" `
        -Method Post `
        -ContentType "application/x-www-form-urlencoded" `
        -Body "username=$username&password=$password" `
        -ErrorAction Stop

    $token = $response.access_token
    $env:AUTH_TOKEN = $token

    Write-Host "`nToken obtained successfully!`n" -ForegroundColor Green
    Write-Host "Token: " -ForegroundColor Cyan -NoNewline
    Write-Host $token.Substring(0, 50) + "..." -ForegroundColor White
    Write-Host "`nStored in: `$env:AUTH_TOKEN" -ForegroundColor Green

    Write-Host "`nTest it with:`n" -ForegroundColor Yellow
    Write-Host "`$headers = @{ 'Authorization' = 'Bearer `$env:AUTH_TOKEN' }" -ForegroundColor White
    Write-Host "`nInvoke-RestMethod -Uri 'http://localhost:8000/hospitality/audits' -Headers `$headers" -ForegroundColor White

    Write-Host "`nTo save token to file:`n" -ForegroundColor Yellow
    Write-Host "`$env:AUTH_TOKEN | Out-File token.txt" -ForegroundColor White
}
catch {
    Write-Host "Error getting token:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "`nMake sure:" -ForegroundColor Yellow
    Write-Host "  1. API is running (uvicorn app.main:app --reload)" -ForegroundColor White
    Write-Host "  2. Database is running (docker compose up -d in infra/)" -ForegroundColor White
    Write-Host "  3. Test data was created (python setup_test_audit.py)" -ForegroundColor White
}
