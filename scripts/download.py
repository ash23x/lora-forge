"""
lora-forge — Phase 2: Image Downloader
Downloads images from a URL list with IPv4 forcing and retry logic.

Usage: python download.py urls.txt output_dir/

CRITICAL: Python's default DNS resolver often returns IPv6 for CDNs like
i.pinimg.com. Many Windows network stacks (Portmaster, AdGuard, corporate
firewalls) silently fail on IPv6 from Python. The monkey-patch below forces
IPv4 resolution — this is not optional, it is the difference between
downloading 80 images and downloading 1.
"""
import urllib.request, socket, os, time, ssl, sys

# ═══════════════════════════════════════════════════════
# IPv4 FORCE — DO NOT REMOVE THIS
# ═══════════════════════════════════════════════════════
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_only(*args, **kwargs):
    return _orig_getaddrinfo(args[0], args[1], socket.AF_INET, *args[3:], **kwargs)
socket.getaddrinfo = _ipv4_only

def download(url_file, out_dir, min_size_kb=50):
    os.makedirs(out_dir, exist_ok=True)

    with open(url_file) as f:
        raw = f.read()

    # Handle concatenated URLs (common when pasting from JS console)
    parts = raw.split('https://')
    urls = ['https://' + p.strip() for p in parts if p.strip()]
    urls = list(dict.fromkeys(urls))  # dedupe preserving order

    print(f'Downloading {len(urls)} unique images to {out_dir}')
    ok = fail = 0
    ctx = ssl.create_default_context()

    for i, url in enumerate(urls, 1):
        ext = url.split('.')[-1][:4]
        fname = f'img_{i:03d}.{ext}'
        fpath = os.path.join(out_dir, fname)

        if os.path.exists(fpath) and os.path.getsize(fpath) > min_size_kb * 1024:
            print(f'  [{i:03d}/{len(urls)}] SKIP {fname} (exists)')
            ok += 1
            continue

        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://uk.pinterest.com/',
                    'Accept': 'image/webp,image/apng,image/*,*/*'
                })
                data = urllib.request.urlopen(req, timeout=20, context=ctx).read()
                with open(fpath, 'wb') as out:
                    out.write(data)
                sz = len(data) / 1024
                print(f'  [{i:03d}/{len(urls)}] {fname} ({sz:.0f} KB)')
                ok += 1
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                    continue
                print(f'  [{i:03d}/{len(urls)}] FAIL {fname}: {e}')
                fail += 1

        time.sleep(0.3)  # be nice to the CDN

    print(f'\nDone: {ok} downloaded, {fail} failed')
    return ok, fail

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python download.py <url_file> <output_dir>')
        print('Example: python download.py urls.txt raw_images/')
        sys.exit(1)
    download(sys.argv[1], sys.argv[2])
