"""
lora-forge — Phase 3b: Caption Cleaner
Fixes LLaVA's tag repetition loops and caps tag count.

Usage: python clean_captions.py image_dir/
"""
import os, sys

def clean(img_dir, max_tags=25):
    files = sorted([f for f in os.listdir(img_dir) if f.endswith('.txt')])
    clean_count = loop_count = 0

    for fname in files:
        fpath = os.path.join(img_dir, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            raw = f.read().strip()
        tags = [t.strip() for t in raw.split(',') if t.strip()]
        seen = set()
        unique = []
        for tag in tags:
            key = tag.lower()
            if key not in seen:
                seen.add(key)
                unique.append(tag)
        was_looping = len(tags) > len(unique) * 1.5
        if was_looping:
            loop_count += 1
            print(f'  CLEANED {fname}: {len(tags)} tags -> {len(unique)} unique')
        unique = unique[:max_tags]
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(', '.join(unique))
        clean_count += 1

    print(f'\nProcessed: {clean_count} captions, fixed loops in: {loop_count}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python clean_captions.py <image_dir>')
        sys.exit(1)
    clean(sys.argv[1])
