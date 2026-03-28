@echo off
REM ═══════════════════════════════════════════════════════
REM lora-forge — Phase 5: SDXL LoRA Training (BF16)
REM ═══════════════════════════════════════════════════════
REM CRITICAL: bf16 not fp16. SDXL produces NaN with fp16.
REM CRITICAL: Delete *.npz in dataset folder between attempts.
REM CRITICAL: Kill ComfyUI before training — it holds VRAM.
REM ═══════════════════════════════════════════════════════

set PYTHONIOENCODING=utf-8
chcp 65001 >nul

REM ── CONFIGURE THESE ──────────────────────────────────
set KOHYA_DIR=D:\KOHYA\kohya_ss
set BASE_MODEL=D:\models\Stable-diffusion\sd_xl_base_1.0.safetensors
set DATASET_DIR=D:\lora-forge\dataset
set OUTPUT_DIR=D:\models\Lora
set OUTPUT_NAME=my_lora
set NETWORK_DIM=16
set NETWORK_ALPHA=8
set EPOCHS=8
REM ─────────────────────────────────────────────────────

cd /d %KOHYA_DIR%
call venv\Scripts\activate.bat

accelerate launch --mixed_precision="bf16" --num_cpu_threads_per_process 4 sd-scripts\sdxl_train_network.py ^
  --pretrained_model_name_or_path="%BASE_MODEL%" ^
  --train_data_dir="%DATASET_DIR%" ^
  --output_dir="%OUTPUT_DIR%" ^
  --output_name="%OUTPUT_NAME%" ^
  --save_every_n_epochs=2 ^
  --max_train_epochs=%EPOCHS% ^
  --resolution=1024,1024 ^
  --train_batch_size=1 ^
  --network_module=networks.lora ^
  --network_dim=%NETWORK_DIM% ^
  --network_alpha=%NETWORK_ALPHA% ^
  --learning_rate=1e-4 ^
  --unet_lr=1e-4 ^
  --network_train_unet_only ^
  --lr_scheduler="cosine" ^
  --lr_warmup_steps=100 ^
  --optimizer_type="AdamW8bit" ^
  --mixed_precision="bf16" ^
  --no_half_vae ^
  --cache_latents ^
  --gradient_checkpointing ^
  --max_data_loader_n_workers=2 ^
  --enable_bucket ^
  --min_bucket_reso=256 ^
  --max_bucket_reso=2048 ^
  --bucket_reso_steps=64 ^
  --seed=42 ^
  --caption_extension=".txt" ^
  --shuffle_caption ^
  --keep_tokens=1 ^
  --max_token_length=225 ^
  --sdpa ^
  --save_precision="bf16" ^
  --save_model_as="safetensors" ^
  --logging_dir="%KOHYA_DIR%\logs"

echo.
echo LoRA training complete. Check %OUTPUT_DIR% for %OUTPUT_NAME% files.
pause
