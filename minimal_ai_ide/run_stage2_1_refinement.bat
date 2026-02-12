@echo off
REM ============================================================================
REM STAGE 2.1 REFINEMENT TRAINING BATCH SCRIPT
REM ============================================================================
REM
REM Purpose: Run Stage 2.1 refinement training with proper CUDA environment
REM Fixes Stage 2 issues:
REM 1. Gradient calculation bug (gradient norms = 0.0)
REM 2. Poor learning effectiveness (loss reduction only 0.41)
REM 3. Small dataset (20 → 100+ examples)
REM 4. Low GPU utilization (17.8% → target > 50%)
REM
REM ============================================================================

echo.
echo ========================================
echo STAGE 2.1 REFINEMENT TRAINING
echo ========================================
echo.

REM Check if CUDA environment exists
if not exist "venv_cuda\Scripts\python.exe" (
    echo ERROR: CUDA environment not found!
    echo Please run: python -m venv venv_cuda
    echo Then install requirements: venv_cuda\Scripts\pip install -r requirements_v57_lora.txt
    pause
    exit /b 1
)

REM Activate CUDA environment
call venv_cuda\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate CUDA environment
    pause
    exit /b 1
)

echo CUDA environment activated
echo.

REM Check Python version
python --version
echo.

REM Check CUDA availability
echo Checking CUDA availability...
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); if torch.cuda.is_available(): print(f'GPU: {torch.cuda.get_device_name(0)}'); print(f'CUDA version: {torch.version.cuda}')"
echo.

REM Create output directory
if not exist "trained_lora_stage2_1_refinement" (
    mkdir "trained_lora_stage2_1_refinement"
    echo Created output directory: trained_lora_stage2_1_refinement
)

echo.
echo ========================================
echo STARTING STAGE 2.1 REFINEMENT TRAINING
echo ========================================
echo.

REM Run Stage 2.1 refinement training
echo Running refinement training...
echo Parameters:
echo   - Dataset: lora_dataset\validated_popperian.json
echo   - Model: distilgpt2
echo   - Output: trained_lora_stage2_1_refinement
echo   - Epochs: 10
echo   - Batch size: 8
echo   - Learning rate: 3e-4
echo.

python lora\stage2_1_refinement.py ^
    --dataset "lora_dataset\validated_popperian.json" ^
    --output "trained_lora_stage2_1_refinement" ^
    --model "distilgpt2"

set TRAINING_RESULT=%errorlevel%

echo.
echo ========================================
echo TRAINING COMPLETE
echo ========================================
echo.

if %TRAINING_RESULT% EQU 0 (
    echo ✅ Stage 2.1 refinement training SUCCESSFUL
    echo.

    REM Display results
    if exist "trained_lora_stage2_1_refinement\refinement_result.json" (
        echo Training Results:
        python -c "
import json
try:
    with open('trained_lora_stage2_1_refinement/refinement_result.json', 'r') as f:
        data = json.load(f)

    print(f'  Christ Score: {data[\"christ_score\"]:.3f}')
    print(f'  Loss Reduction: {data[\"loss_reduction\"]:.4f}')
    print(f'  Training Time: {data[\"training_minutes\"]:.2f} minutes')
    print(f'  NaN Events: {data[\"nan_events\"]}')

    if data[\"metrics_history\"]:
        grad_norms = [m[\"gradient_norm\"] for m in data[\"metrics_history\"]]
        avg_grad = sum(grad_norms) / len(grad_norms)
        print(f'  Avg Gradient Norm: {avg_grad:.4f}')
        print(f'  Min Gradient Norm: {min(grad_norms):.4f}')
        print(f'  Max Gradient Norm: {max(grad_norms):.4f}')

    print(f'  GPU Memory Used: {data[\"gpu_info\"].get(\"memory_allocated_gb\", 0):.2f} GB')
    print(f'  GPU Utilization: {data[\"gpu_info\"].get(\"utilization_percent\", 0):.1f}%')

except Exception as e:
    print(f'  Error reading results: {e}')
"
    )

    echo.
    echo Model saved to: trained_lora_stage2_1_refinement
    echo.
    echo Next steps:
    echo 1. Test the refined model: python test_trained_model.py --model trained_lora_stage2_1_refinement
    echo 2. Analyze diagnostics: python -c "import json; data=json.load(open('trained_lora_stage2_1_refinement/refinement_result.json')); print(json.dumps(data['diagnostics'], indent=2))"
    echo 3. Proceed to Stage 3 if Christ Score > 0.6
    echo.

) else (
    echo ❌ Stage 2.1 refinement training FAILED
    echo.
    echo Check the error messages above.
    echo.
    echo Troubleshooting steps:
    echo 1. Verify CUDA installation: python -c "import torch; print(torch.cuda.is_available())"
    echo 2. Check GPU memory: python -c "import torch; print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB')"
    echo 3. Reduce batch size in lora\stage2_1_refinement.py if out of memory
    echo 4. Check dataset: python -c "import json; data=json.load(open('lora_dataset/validated_popperian.json')); print(f'Dataset size: {len(data)}')"
    echo.
)

REM Deactivate environment
call venv_cuda\Scripts\deactivate.bat

echo.
echo ========================================
echo SCRIPT COMPLETE
echo ========================================
echo.

if %TRAINING_RESULT% EQU 0 (
    echo Press any key to exit...
    pause > nul
) else (
    echo Press any key to exit...
    pause > nul
    exit /b 1
)
