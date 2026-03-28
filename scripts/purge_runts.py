"""
lora-forge — Phase 2b: Purge Runts
Removes downloaded images under a size threshold (usually thumbnails or 403 stubs).

Usage: python purge_runts.py image_dir/ [min_kb]
"""
import os, sys

def purge(img_dir, min_kb=50):
    exts = ('.jpg', '.jpeg', '.png', '.webp')
    files = [f for f in os.listdir(img_dir) if f.lower().endswith(exts)]
    total = len(files)
    removed = 0
    sizes = []

    for f in files:
        fp = os.path.join(img_dir, f)
        sz = os.path.getsize(fp)
        sizes.append(sz)
        if sz < min_kb * 1024:
            print(f'  PURGE {f}: {sz // 1024} KB')
            os.remove(fp)
            removed += 1

    remaining = total - removed
    avg = sum(sizes) // len(sizes) // 1024 if sizes else 0
    print(f'\nTotal: {total}, Purged: {removed}, Surviving: {remaining}, Avg size: {avg} KB')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python purge_runts.py <image_dir> [min_kb]')
        sys.exit(1)
    min_kb = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    purge(sys.argv[1], min_kb)
