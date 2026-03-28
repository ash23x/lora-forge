// ═══════════════════════════════════════════════════════
// lora-forge — Phase 1b: Pinterest URL Extractor
// ═══════════════════════════════════════════════════════
// Paste this into the browser console (F12 → Console)
// while on a Pinterest search results page.
//
// It scrolls down to load more images, then extracts
// high-resolution original URLs from all loaded images.
//
// Copy the output and save to a .txt file (one URL per line).
// Then run: python download.py urls.txt raw_images/
// ═══════════════════════════════════════════════════════

(async () => {
  // Scroll to load more images (adjust count for more/fewer)
  const SCROLL_COUNT = 15;
  for (let i = 0; i < SCROLL_COUNT; i++) {
    window.scrollBy(0, 3000);
    await new Promise(r => setTimeout(r, 1200));
  }

  // Extract and upgrade to original resolution
  const imgs = document.querySelectorAll('img[src*="i.pinimg.com"]');
  const urls = new Set();
  imgs.forEach(img => {
    let src = img.src
      .replace(/\/\d+x\d*\//, '/originals/')
      .replace(/\/\d+x\//, '/originals/');
    if (src.includes('/originals/') && !src.includes('user') && !src.includes('avatar'))
      urls.add(src);
  });

  const result = [...urls];
  console.log(`Found ${result.length} unique high-res images`);

  // Copy to clipboard
  const text = result.join('\n');
  await navigator.clipboard.writeText(text);
  console.log('URLs copied to clipboard! Paste into a .txt file.');

  // Also log them for manual copy
  console.log(text);
})();
