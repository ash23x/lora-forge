"""
lora-forge — Phase 4: Dataset Preparer
Builds the Kohya-compatible folder structure from captioned images.

Usage: python prepare_dataset.py image_dir/ dataset_dir/ token [repeats]

Creates: dataset_dir/{repeats}_{token}/ with paired .jpg/.txt files
"""
import os, sys, shutil

def prepare(img_dir, dataset_dir, token, repeats=5):
    exts = ('.jpg', '.jpeg', '.png', '.webp')
    target = os.path.join(dataset_dir, f'{repeats}_{token}')
    os.makedirs(target, exist_ok=True)

    images = sorted([f for f in os.listdir(img_dir) if f.lower().endswith(exts)])
    paired = 0
    orphan_img = 0

    for fname in images:
        stem = os.path.splitext(fname)[0]
        txt = stem + '.txt'
        img_path = os.path.join(img_dir, fname)
        txt_path = os.path.join(img_dir, txt)

        if not os.path.exists(txt_path):
            print(f'  SKIP {fname} (no caption file)')
            orphan_img += 1
            continue

        shutil.copy2(img_path, os.path.join(target, fname))
        shutil.copy2(txt_path, os.path.join(target, txt))
        paired += 1

    print(f'\nDataset ready: {target}')
    print(f'  Paired: {paired} image+caption sets')
    print(f'  Orphans: {orphan_img} (no caption)')
    print(f'  Repeats: {repeats}x per epoch')
    print(f'  Token: "{token}"')
    print(f'\nTotal steps per epoch: {paired * repeats}')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python prepare_dataset.py <image_dir> <dataset_dir> <token> [repeats]')
        print('Example: python prepare_dataset.py raw_images/ dataset/ mybrand 5')
        sys.exit(1)
    repeats = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    prepare(sys.argv[1], sys.argv[2], sys.argv[3], repeats)
