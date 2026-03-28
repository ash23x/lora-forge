# lora-forge

**The complete sovereign LoRA pipeline. From a sentence describing what you want, to a trained SDXL LoRA generating images — on your own GPU, with zero cloud APIs.**

Find images that match your vision. Extract them. Caption them automatically. Train a LoRA. Generate 100 images in your new style. Total human effort: describe the aesthetic. Total machine effort: everything else.

---

## What This Actually Does

You say: *"I want watercolour celestial illustrations with gold ink on dark navy, crescent moons, botanical frames, ornate filigree."*

lora-forge turns that sentence into a trained neural network that generates unlimited images in exactly that style. The entire pipeline runs on a single consumer GPU. No cloud. No subscription. No data leaving your box.

```
Pinterest search → Image extraction → Auto-captioning → LoRA training → Image generation
    (10 min)         (2 min)           (15 min)          (90 min)         (seconds)
```

Total time: ~2 hours. Total cost: electricity.

---

## The Pipeline

### Phase 1: Source Images

You need 50-100 reference images that define your target aesthetic. Two extraction methods:

**Method A: RAM RAID (PowerPoint)**
The fastest, most reliable method. Drag images from any browser onto PowerPoint slides — no extensions, no APIs, no CORS, no CSP blocking. PowerPoint embeds a full copy of every image you drag onto it.

Then run the RAM RAID VBA macro (`scripts/ram_raid.bas`): it exports every image from every slide as a 1024×1024 PNG. The `.Export` method forces the GPU render buffer to materialise the actual pixel data, not the compressed XML thumbnails PowerPoint stores internally.

```
1. Open PowerPoint
2. Browse Pinterest/Instagram/anywhere — drag images onto slides
3. Alt+F11 → Insert Module → paste ram_raid.bas → F5
4. All images exported as PNGs
```

**Method B: Pinterest URL Extraction (Browser Console)**
Paste `scripts/pinterest_extract.js` into the browser console on a Pinterest search results page. It scrolls to load images, extracts high-res original URLs, and copies them to your clipboard. Save to a `.txt` file, then download with the Python script:

```bash
python scripts/download.py urls.txt raw_images/
```

### Phase 2: Clean Up

Purge thumbnails and failed downloads (anything under 50KB is probably garbage):

```bash
python scripts/purge_runts.py raw_images/
```

### Phase 3: Auto-Caption

LLaVA (running locally via Ollama) examines each image and writes a comma-separated tag description. No cloud API — your images never leave your machine:

```bash
python scripts/caption.py raw_images/
python scripts/clean_captions.py raw_images/
```

The clean step is essential: LLaVA 7B frequently enters tag repetition loops, producing 50+ tags where 30+ are duplicates. The cleaner deduplicates and caps at 25 tags.

### Phase 4: Build Dataset

Kohya expects a specific folder structure: `{repeats}_{token}/` containing paired `.jpg` + `.txt` files:

```bash
python scripts/prepare_dataset.py raw_images/ dataset/ mybrand 5
```

This creates `dataset/5_mybrand/` with all paired image+caption files. The `5` means each image is seen 5 times per epoch. The `mybrand` becomes your trigger token in prompts.

### Phase 5: Train

Edit `scripts/train.bat` with your paths, then run it:

```bash
scripts\train.bat
```

Training takes ~60-90 minutes on an RTX 4070 (12GB). The script handles all the critical settings — bf16 precision, gradient checkpointing, SDPA attention, cosine scheduler. LoRA checkpoints are saved every 2 epochs.

### Phase 6: Generate

Load the `.safetensors` file in ComfyUI and use your trigger token:

```
a mybrand style illustration, golden celestial design, ornate botanical frame
```

That's it. You have a trained LoRA that generates images in your exact aesthetic.

---

## The Six Gotchas

These will bite anyone who tries to build this pipeline from scratch. We've already been bitten so you don't have to.

### 1. Python Can't Resolve Pinterest CDN via IPv6

`i.pinimg.com` returns IPv6 addresses. Python's `urllib` on Windows with network security tools (Portmaster, AdGuard, corporate firewalls) silently fails on IPv6. The first image downloads (DNS cache), the rest timeout.

**Fix:** The downloader monkey-patches `socket.getaddrinfo` to force IPv4. Do not remove this.

### 2. Pinterest CSP Blocks Script Injection

Pinterest's Content Security Policy blocks loading external scripts via `createElement('script')`. You cannot use JSZip or any CDN library on Pinterest pages. The extraction script uses only vanilla JS for this reason.

### 3. SDXL Training Produces NaN with FP16

This is the big one. SDXL LoRA training on fp16 mixed precision produces `avr_loss=nan` on step 1, regardless of learning rate, optimizer, or attention mechanism. The internet will tell you to lower the learning rate. That does not work.

**Fix:** Use bf16 everywhere. RTX 30xx/40xx cards support bf16 natively. BF16 has an 8-bit exponent (same dynamic range as fp32) vs fp16's 5-bit exponent. The training script is already configured for bf16.

### 4. Cached Latents Poison Subsequent Runs

Failed training runs cache `.npz` latent files in the dataset folder. If you change precision settings and re-run, Kohya loads the old (corrupted) cache instead of re-encoding. You'll see suspiciously fast iteration (500+ it/s instead of ~2 it/s).

**Fix:** Always delete `*.npz` from the dataset folder between training attempts:
```bash
del dataset\5_mybrand\*.npz
```

### 5. Kohya's Japanese Logs Crash Windows

Kohya sd-scripts outputs Japanese text in its logging. Windows console (cp1252) crashes on these characters.

**Fix:** The training script sets `PYTHONIOENCODING=utf-8` and `chcp 65001` before launch.

### 6. LLaVA Enters Tag Repetition Loops

LLaVA 7B frequently produces captions like: `"celestial, fantasy, digital painting, celestial, fantasy, digital painting, celestial..."` — 50+ tags where 30+ are duplicates.

**Fix:** Run `clean_captions.py` after captioning. It deduplicates preserving order and caps at 25 tags.

---

## Prerequisites

| Tool | What For | Install |
|------|----------|---------|
| **Python 3.10+** | Scripts | [python.org](https://python.org) |
| **Ollama** | LLaVA captioning | [ollama.ai](https://ollama.ai), then `ollama pull llava` |
| **Kohya sd-scripts** | LoRA training | [github.com/kohya-ss/sd-scripts](https://github.com/kohya-ss/sd-scripts) |
| **ComfyUI** | Image generation | [github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) |
| **SDXL base model** | Training foundation | `sd_xl_base_1.0.safetensors` from HuggingFace |
| **PowerPoint** | RAM RAID extraction | Any version with VBA (Office 2016+) |
| **NVIDIA GPU 8GB+** | Training + inference | RTX 3060+ recommended, 4070 ideal |

No Python packages to install. The scripts use only standard library (`urllib`, `socket`, `json`, `base64`, `os`, `shutil`). Ollama provides LLaVA. Kohya provides training. ComfyUI provides generation.

---

## VRAM Budget (RTX 4070, 12GB)

| Component | VRAM |
|-----------|------|
| Windows desktop | ~3.8 GB |
| SDXL UNet (bf16) | ~5 GB |
| LoRA weights + optimizer | ~1.5 GB |
| Gradient checkpointing saves | ~2 GB |
| **Total** | **~10.3 GB** |
| Headroom | ~1.7 GB |

**Kill ComfyUI before training** — it holds VRAM even when idle.

---

## Training Parameters Explained

| Parameter | Value | Why |
|-----------|-------|-----|
| `--mixed_precision="bf16"` | bf16 | Prevents NaN (see Gotcha #3) |
| `--no_half_vae` | enabled | VAE encodes in fp32, prevents latent corruption |
| `--network_dim=16` | 16 | LoRA rank. Higher = more capacity, more VRAM. 16 is good for style |
| `--network_alpha=8` | dim/2 | Scaling factor. Rule of thumb: half of dim |
| `--network_train_unet_only` | enabled | Skip text encoders. More stable, less VRAM |
| `--optimizer_type="AdamW8bit"` | 8-bit Adam | Saves ~2GB VRAM vs full Adam |
| `--gradient_checkpointing` | enabled | Essential for 12GB cards |
| `--sdpa` | enabled | PyTorch native attention (faster than xformers on Ada GPUs) |
| `--enable_bucket` | enabled | Handles mixed aspect ratios without resizing |
| `--cache_latents` | enabled | Caches VAE encodings in RAM (not disk — see Gotcha #4) |

### Healthy Loss Curve

```
Step  1: ~0.007 (near zero, initial)
Step  5: ~0.19  (ramping as gradients propagate)
Step 10: ~0.15  (settling)
Step 20: ~0.13  (converging — this is healthy)
```

If you see `avr_loss=nan` → STOP. See Gotcha #3 and #4.

---

## Project Structure

```
lora-forge/
├── scripts/
│   ├── ram_raid.bas          # VBA: PowerPoint → 1024px PNGs
│   ├── pinterest_extract.js  # Browser console: Pinterest → URL list
│   ├── download.py           # Python: URL list → images (IPv4 forced)
│   ├── purge_runts.py        # Python: remove thumbnails/stubs
│   ├── caption.py            # Python: LLaVA auto-captioning via Ollama
│   ├── clean_captions.py     # Python: deduplicate tag loops
│   ├── prepare_dataset.py    # Python: build Kohya folder structure
│   └── train.bat             # Batch: Kohya SDXL bf16 training config
├── raw_images/               # Your extracted images go here
├── dataset/                  # Kohya-formatted training data
├── LICENSE                   # MIT
└── README.md                 # You are here
```

---

## FAQ

**Why PowerPoint?**
Because it's the most reliable cross-platform visual clipboard in existence. Drag from any browser, any app, any source — no scraping libraries, no API keys, no CORS, no CSP blocking. If you can see it on screen, you can drag it onto a slide.

**Why not use a web scraper?**
Pinterest's CSP blocks external scripts. Their API requires OAuth. Chrome extensions break on updates. `selenium` and `playwright` require headless browser setup. PowerPoint just... works.

**Why local captioning?**
Your training images are your competitive advantage. Sending them to a cloud API means they're logged, cached, and potentially used to train someone else's model. LLaVA via Ollama runs entirely on your GPU.

**Can I use this for SD 1.5 instead of SDXL?**
Yes. Change `sd_xl_base_1.0.safetensors` to your SD 1.5 checkpoint, set resolution to 512×512, and you can use fp16 (the NaN issue is SDXL-specific). Everything else is the same.

**How many images do I need?**
50-100 for style LoRAs. 15-20 for character LoRAs (with consistent subject). Quality matters more than quantity — 50 perfect images beat 200 inconsistent ones.

**Which epoch is best?**
Usually epoch 4 of 8. Test all checkpoints: epoch 2 (underbaked, flexible), epoch 4 (usually the sweet spot), epoch 6 (stronger style lock), epoch 8 (risk of overfit). Compare the same prompt + seed across all four.

---

## License

MIT — see [LICENSE](LICENSE).

Built by [Ontos Labs Ltd](https://github.com/ash23x).
