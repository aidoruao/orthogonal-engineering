# MINIMAL AI IDE - PowerShell Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MINIMAL AI IDE - PowerShell Edition" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your local AI IDE with guaranteed execution" -ForegroundColor Green
Write-Host "Model: llama3.2 via Ollama" -ForegroundColor Green
Write-Host ""
Write-Host "Starting interactive chat..." -ForegroundColor Yellow
Write-Host "Type 'exit' or 'quit' to end" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location -Path 

# Check Python
try {
     = python --version 2>&1
    Write-Host "✅ Python found: " -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host "Install Python or add it to PATH" -ForegroundColor Red
    pause
    exit 1
}

# Run the chat mode
python cli.py chat

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI session ended." -ForegroundColor Yellow
Write-Host "Press any key to exit..." -ForegroundColor Gray
 = .UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
