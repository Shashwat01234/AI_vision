# ==============================================================================
# AI-Powered Accessibility Assistant — Full System Verification Script
# ==============================================================================

Write-Host ''
Write-Host '========================================================' -ForegroundColor Cyan
Write-Host '   AI ACCESSIBILITY ASSISTANT — SYSTEM VERIFICATION' -ForegroundColor Cyan
Write-Host '========================================================' -ForegroundColor Cyan
Write-Host ''

# 1. Python Environment Check
Write-Host '[1/5] Checking Python Environment...' -ForegroundColor Yellow
$pyVer = python --version 2>&1
Write-Host "  [OK] Python detected: $pyVer" -ForegroundColor Green

# 2. Pretrained AI Models Check
Write-Host ''
Write-Host '[2/5] Checking AI Model Weights...' -ForegroundColor Yellow
$yoloPretrained = 'models/pretrained/yolo11n.pt'
$yoloCustom = 'models/custom/best.pt'

if (Test-Path $yoloPretrained) {
    $fileItem = Get-Item $yoloPretrained
    $mbSize = [math]::Round($fileItem.Length / 1MB, 2)
    Write-Host "  [OK] Pretrained YOLO model found: $mbSize MB ($yoloPretrained)" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Pretrained YOLO model missing at $yoloPretrained" -ForegroundColor Yellow
}

if (Test-Path $yoloCustom) {
    Write-Host "  [OK] Custom fine-tuned YOLO model found: $yoloCustom" -ForegroundColor Green
} else {
    Write-Host '  [INFO] Custom model not found (defaulting to pretrained YOLO11n backbone)' -ForegroundColor Gray
}

# 3. Database and Storage Check
Write-Host ''
Write-Host '[3/5] Checking Database and Storage Directories...' -ForegroundColor Yellow
$dbPath = 'storage/accessibility.db'
$dirs = @('storage/uploads', 'storage/processed', 'storage/audio')

foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
    }
}
Write-Host '  [OK] Storage directories verified: uploads, processed, audio' -ForegroundColor Green

if (Test-Path $dbPath) {
    Write-Host "  [OK] SQLite database present: $dbPath" -ForegroundColor Green
} else {
    Write-Host '  [INFO] Database will be initialized automatically on first backend launch.' -ForegroundColor Gray
}

# 4. Frontend Assets Check
Write-Host ''
Write-Host '[4/5] Checking Frontend Build...' -ForegroundColor Yellow
if (Test-Path 'frontend/dist/index.html') {
    Write-Host '  [OK] Production frontend build verified in frontend/dist/' -ForegroundColor Green
} else {
    Write-Host '  [INFO] Building production frontend bundle...' -ForegroundColor Gray
    Push-Location frontend
    npm run build
    Pop-Location
    if (Test-Path 'frontend/dist/index.html') {
        Write-Host '  [OK] Frontend successfully built!' -ForegroundColor Green
    }
}

# 5. Execute Full Automated Pytest Suite
Write-Host ''
Write-Host '[5/5] Running Automated Test Suite...' -ForegroundColor Yellow
Write-Host '  NOTE: test_api.py requires the backend server running on :8000' -ForegroundColor Gray
python -m pytest tests -v --tb=short
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host ''
    Write-Host '========================================================' -ForegroundColor Green
    Write-Host '  ALL AUTOMATED TESTS PASSED CLEANLY!' -ForegroundColor Green
    Write-Host '========================================================' -ForegroundColor Green
} else {
    Write-Host ''
    Write-Host '========================================================' -ForegroundColor Red
    Write-Host "  SOME TESTS FAILED - Exit Code: $exitCode" -ForegroundColor Red
    Write-Host '========================================================' -ForegroundColor Red
}

Write-Host ''
Write-Host 'To start the complete application for end-to-end use:' -ForegroundColor Cyan
Write-Host '  1. Backend API:     python backend/run.py' -ForegroundColor White
Write-Host '  2. Frontend UI:     cd frontend; npm run dev' -ForegroundColor White
Write-Host '  3. Open in Browser: http://localhost:5173' -ForegroundColor Yellow
Write-Host '  4. OpenAPI Docs:    http://localhost:8000/api/docs' -ForegroundColor Yellow
Write-Host ''
