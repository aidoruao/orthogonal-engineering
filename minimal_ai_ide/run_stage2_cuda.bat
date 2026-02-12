@echo off
REM ============================================
REM STAGE 2 CUDA TRAINING LAUNCH SCRIPT
REM ============================================
REM
REM Purpose: Launch Stage 2 CUDA-optimized LoRA training
REM Environment: CUDA 12.1, PyTorch 2.5.1+cu121, Python 3.11.9
REM GPU: NVIDIA GeForce RTX 4050 Laptop GPU (6GB VRAM)
REM
REM ============================================

echo.
echo ============================================
echo STAGE 2 CUDA TRAINING LAUNCH
echo ============================================
echo.

REM Check if we're in the right directory
if not exist "lora_dataset\popperian_examples.json" (
    echo ERROR: Dataset not found!
    echo Expected: lora_dataset\popperian_examples.json
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Check if CUDA virtual environment exists
if not exist "venv_cuda\Scripts\python.exe" (
    echo ERROR: CUDA virtual environment not found!
    echo Expected: venv_cuda\Scripts\python.exe
    echo.
    echo Please ensure you have:
    echo 1. Python 3.11.9 installed
    echo 2. CUDA-enabled PyTorch in venv_cuda
    echo.
    pause
    exit /b 1
)

REM Verify CUDA is available
echo Verifying CUDA configuration...
call "venv_cuda\Scripts\python.exe" -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
if errorlevel 1 (
    echo ERROR: Failed to verify CUDA!
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo TRAINING CONFIGURATION
echo ============================================
echo Model: distilgpt2
echo Dataset: 50 Popperian examples
echo Output: trained_lora_stage2_cuda
echo Batch Size: 4
echo Epochs: 5
echo Learning Rate: 5e-5
echo Mixed Precision: FP16 enabled
echo ============================================
echo.

REM Ask for confirmation
set /p confirm="Start Stage 2 CUDA training? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Training cancelled.
    pause
    exit /b 0
)

echo.
echo ============================================
echo STARTING STAGE 2 CUDA TRAINING
echo ============================================
echo.

REM Run Stage 2 training
echo Starting training at: %date% %time%
echo.

call "venv_cuda\Scripts\python.exe" lora\stage2_cuda_training.py ^
  --dataset lora_dataset\popperian_examples.json ^
  --output trained_lora_stage2_cuda ^
  --model distilgpt2

set training_result=%errorlevel%

echo.
echo ============================================
echo TRAINING COMPLETE
echo ============================================
echo Finished at: %date% %time%
echo.

if %training_result% equ 0 (
    echo ✅ TRAINING SUCCESSFUL
    echo.
    echo Model saved to: trained_lora_stage2_cuda
    echo Training results: trained_lora_stage2_cuda\training_result.json
    echo.
    echo Next steps:
    echo 1. Test the model: test_trained_model.py --model trained_lora_stage2_cuda
    echo 2. Check Christ score in training_result.json
    echo 3. Verify governance compliance
) else (
    echo ❌ TRAINING FAILED
    echo.
    echo Check the error messages above.
    echo.
    echo Troubleshooting:
    echo 1. Verify GPU memory is available
    echo 2. Check dataset format
    echo 3. Run test: python lora\test_stage2_cuda.py
)

echo.
pause
