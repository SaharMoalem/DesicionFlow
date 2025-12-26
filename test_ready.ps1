# Quick test script for /ready endpoint

$baseUrl = "http://localhost:8000"

Write-Host "`n=== Testing DecisionFlow Endpoints ===" -ForegroundColor Cyan

# Test /health
Write-Host "`n1. Testing /health endpoint..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -ErrorAction Stop
    Write-Host "   Status: $($healthResponse.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($healthResponse.Content)" -ForegroundColor White
} catch {
    Write-Host "   ERROR: App is not running or not accessible" -ForegroundColor Red
    Write-Host "   Make sure you started the app with: uvicorn app.main:app --reload" -ForegroundColor Yellow
    exit 1
}

# Test /ready
Write-Host "`n2. Testing /ready endpoint..." -ForegroundColor Yellow
try {
    $readyResponse = Invoke-WebRequest -Uri "$baseUrl/ready" -Method GET -ErrorAction Stop
    Write-Host "   Status: $($readyResponse.StatusCode)" -ForegroundColor Green
    $content = $readyResponse.Content | ConvertFrom-Json
    Write-Host "   Status: $($content.status)" -ForegroundColor White
    Write-Host "   Checks:" -ForegroundColor White
    Write-Host "     - Redis: $($content.checks.redis)" -ForegroundColor $(if ($content.checks.redis) { "Green" } else { "Red" })
    Write-Host "     - OpenAI: $($content.checks.openai)" -ForegroundColor $(if ($content.checks.openai) { "Green" } else { "Red" })
} catch {
    if ($_.Exception.Response.StatusCode -eq 503) {
        $errorContent = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "   Status: 503 Service Unavailable" -ForegroundColor Red
        Write-Host "   Status: $($errorContent.detail.status)" -ForegroundColor Yellow
        Write-Host "   Checks:" -ForegroundColor White
        Write-Host "     - Redis: $($errorContent.detail.checks.redis)" -ForegroundColor $(if ($errorContent.detail.checks.redis) { "Green" } else { "Red" })
        Write-Host "     - OpenAI: $($errorContent.detail.checks.openai)" -ForegroundColor $(if ($errorContent.detail.checks.openai) { "Green" } else { "Red" })
        Write-Host "`n   Note: Some dependencies are unavailable. This is OK for testing." -ForegroundColor Yellow
    } else {
        Write-Host "   ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test root endpoint
Write-Host "`n3. Testing root endpoint..." -ForegroundColor Yellow
try {
    $rootResponse = Invoke-WebRequest -Uri "$baseUrl/" -Method GET -ErrorAction Stop
    Write-Host "   Status: $($rootResponse.StatusCode)" -ForegroundColor Green
    $content = $rootResponse.Content | ConvertFrom-Json
    Write-Host "   Service: $($content.service)" -ForegroundColor White
    Write-Host "   Version: $($content.version)" -ForegroundColor White
    Write-Host "   Status: $($content.status)" -ForegroundColor White
} catch {
    Write-Host "   ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "`nAPI Documentation: http://localhost:8000/docs" -ForegroundColor Green

