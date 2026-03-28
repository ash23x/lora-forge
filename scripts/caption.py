"""
lora-forge — Phase 3: LLaVA Auto-Captioner
Generates training captions for images using LLaVA via Ollama.

Usage: python caption.py image_dir/

Prerequisites:
  - Ollama running: http://localhost:11434
  - LLaVA model pulled: ollama pull llava

GOTCHA: LLaVA 7B frequently enters tag repetition loops, producing 50+ tags
where 30+ are duplicates. Run clean_captions.py after this script to fix.
"""
import os, json, base64, urllib.request, time, sys

OLLAMA = 'http://localhost:11434/api/generate'
MODEL = 'llava'

CAPTION_PROMPT = """Describe this image in detail for SDXL LoRA training. Focus on:
- Art style and medium (watercolor, ink, digital painting, etc.)
- Color palette (specific colors and their relationships)
- Composition and layout
- Key visual elements and motifs
- Line quality (ornate, loose, geometric, etc.)
- Mood and atmosphere
- Background treatment

Write as a flat comma-separated tag list, no sentences. Example:
celestial watercolor illustration, gold ink on dark navy background, crescent moon, ornate filigree border, mystical feminine aesthetic, ethereal dreamy mood"""

def caption_image(img_path):
    with open(img_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    payload = json.dumps({
        'model': MODEL, 'prompt': CAPTION_PROMPT, 'images': [b64],
        'stream': False, 'options': {'temperature': 0.3, 'num_predict': 200}
    }).encode()
    req = urllib.request.Request(OLLAMA, data=payload, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read()).get('response', '').strip()

def caption_dir(img_dir, force=False):
    exts = ('.jpg', '.jpeg', '.png', '.webp')
    files = sorted([f for f in os.listdir(img_dir) if f.lower().endswith(exts)])
    print(f'Captioning {len(files)} images with LLaVA...\n')

    for i, fname in enumerate(files, 1):
        img_path = os.path.join(img_dir, fname)
        txt_name = os.path.splitext(fname)[0] + '.txt'
        txt_path = os.path.join(img_dir, txt_name)

        if os.path.exists(txt_path) and not force:
            print(f'  [{i:03d}/{len(files)}] SKIP {fname} (caption exists)')
            continue
        try:
            t0 = time.time()
            caption = caption_image(img_path)
            dt = time.time() - t0
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(caption)
            preview = caption[:80] + '...' if len(caption) > 80 else caption
            print(f'  [{i:03d}/{len(files)}] {fname} ({dt:.1f}s) -> {preview}')
        except Exception as e:
            print(f'  [{i:03d}/{len(files)}] FAIL {fname}: {e}')

    done = len([f for f in os.listdir(img_dir) if f.endswith('.txt')])
    print(f'\nDone: {done}/{len(files)} captions written')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python caption.py <image_dir> [--force]')
        sys.exit(1)
    caption_dir(sys.argv[1], force='--force' in sys.argv)
