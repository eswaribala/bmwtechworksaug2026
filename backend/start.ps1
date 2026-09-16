# BMW Data Quality Platform — Start Backend Server (Windows PowerShell)
# Run from project root: .\backend\start.ps1

Write-Host "BMW Data Quality Platform — Backend Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Install dependencies if needed
Write-Host "`nInstalling backend dependencies..." -ForegroundColor Yellow
pip install -r backend\requirements.txt

# Check for .env file
if (Test-Path ".env") {
    Write-Host "`nLoading environment from .env" -ForegroundColor Green
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
} else {
    Write-Host "`n[WARN] No .env found — using local mode (no S3 uploads)" -ForegroundColor Yellow
    Write-Host "       Create .env with: S3_BUCKET=bmw-data-quality-<account-id>" -ForegroundColor Yellow
}

Write-Host "`nStarting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "Docs available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Gray

# Start server
uvicorn backend.app:app --reload --port 8000 --host 0.0.0.0
