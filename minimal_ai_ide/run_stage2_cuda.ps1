# ============================================
# STAGE 2 CUDA TRAINING LAUNCH SCRIPT (PowerShell)
# ============================================
#
# Purpose: Launch Stage 2 CUDA-optimized LoRA training
# Environment: CUDA 12.1, PyTorch 2.5.1+cu121, Python 3.11.9
# GPU: NVIDIA GeForce RTX 4050 Laptop GPU (6GB VRAM)
#
# ============================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "STAGE 2 CUDA TRAINING LAUNCH" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "lora_dataset\popperian_examples.json")) {
    Write-Host "ERROR: Dataset not found!" -ForegroundColor Red
    Write-Host "Expected: lora_dataset\popperian_examples.json" -ForegroundColor Yellow
    Write-Host "Current directory: $PWD" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if CUDA virtual environment exists
if (-not (Test-Path "venv_cuda\Scripts\python.exe")) {
    Write-Host "ERROR: CUDA virtual environment not found!" -ForegroundColor Red
    Write-Host "Expected: venv_cuda\Scripts\python.exe" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please ensure you have:" -ForegroundColor Yellow
    Write-Host "1. Python 3.11.9 installed" -ForegroundColor Yellow
    Write-Host "2. CUDA-enabled PyTorch in venv_cuda" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Verify CUDA is available
Write-Host "Verifying CUDA configuration..." -ForegroundColor Green
try {
    $cudaCheck = & "venv_cuda\Scripts\python.exe" -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
    Write-Host $cudaCheck -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to verify CUDA!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "TRAINING CONFIGURATION" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Model: distilgpt2" -ForegroundColor White
Write-Host "Dataset: 50 Popperian examples" -ForegroundColor White
Write-Host "Output: trained_lora_stage2_cuda" -ForegroundColor White
Write-Host "Batch Size: 4" -ForegroundColor White
Write-Host "Epochs: 5" -ForegroundColor White
Write-Host "Learning Rate: 5e-5" -ForegroundColor White
Write-Host "Mixed Precision: FP16 enabled" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Start Stage 2 CUDA training? (Y/N)"
if ($confirmation -notmatch '^[Yy]$') {
    Write-Host "Training cancelled." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "STARTING STAGE 2 CUDA TRAINING" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Run Stage 2 training
$startTime = Get-Date
Write-Host "Starting training at: $startTime" -ForegroundColor Green
Write-Host ""

try {
    & "venv_cuda\Scripts\python.exe" lora\stage2_cuda_training.py `
        --dataset lora_dataset\popperian_examples.json `
        --output trained_lora_stage2_cuda `
        --model distilgpt2

    $trainingResult = $LASTEXITCODE
} catch {
    Write-Host "ERROR: Failed to start training!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Yellow
    $trainingResult = 1
}

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "TRAINING COMPLETE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Finished at: $endTime" -ForegroundColor Green
Write-Host "Duration: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Green
Write-Host ""

if ($trainingResult -eq 0) {
    Write-Host "✅ TRAINING SUCCESSFUL" -ForegroundColor Green
    Write-Host ""
    Write-Host "Model saved to: trained_lora_stage2_cuda" -ForegroundColor White
    Write-Host "Training results: trained_lora_stage2_cuda\training_result.json" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Test the model: test_trained_model.py --model trained_lora_stage2_cuda" -ForegroundColor White
    Write-Host "2. Check Christ score in training_result.json" -ForegroundColor White
    Write-Host "3. Verify governance compliance" -ForegroundColor White
} else {
    Write-Host "❌ TRAINING FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error messages above." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Cyan
    Write-Host "1. Verify GPU memory is available" -ForegroundColor White
    Write-Host "2. Check dataset format" -ForegroundColor White
    Write-Host "3. Run test: python lora\test_stage2_cuda.py" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to exit"
