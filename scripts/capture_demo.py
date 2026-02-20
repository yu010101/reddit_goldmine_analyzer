"""Capture demo screenshots of the Streamlit app for GIF creation."""
from playwright.sync_api import sync_playwright
import time

URL = "http://localhost:8501"
OUT = "docs"
FRAMES = []


def screenshot(page, name, delay=2):
    time.sleep(delay)
    path = f"{OUT}/demo_{name}.png"
    page.screenshot(path=path)
    FRAMES.append(path)
    print(f"  Captured: {name}")


def click_radio(page, label_text):
    """Click a Streamlit radio button by its label text."""
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.5)
    # Use JavaScript to find and click the radio by label text
    page.evaluate(f"""() => {{
        const labels = document.querySelectorAll('label[data-baseweb="radio"]');
        for (const label of labels) {{
            if (label.textContent.trim() === '{label_text}') {{
                const input = label.querySelector('input[type="radio"]');
                if (input) {{
                    input.click();
                    return;
                }}
                label.click();
                return;
            }}
        }}
    }}""")
    time.sleep(2)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    print("Capturing demo screenshots...")

    # ── Frame 1: Landing page ──
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    screenshot(page, "01_landing", delay=3)

    # ── Frame 2: Scroll down to pain points ──
    page.evaluate("window.scrollBy(0, 600)")
    screenshot(page, "02_painpoints")

    # ── Frame 3: Scroll further ──
    page.evaluate("window.scrollBy(0, 500)")
    screenshot(page, "03_details")

    # ── Frame 4: Switch to Discover tab ──
    click_radio(page, "Discover")
    screenshot(page, "04_discover", delay=2)

    # ── Frame 5: Scroll down in Discover ──
    page.evaluate("window.scrollBy(0, 500)")
    screenshot(page, "05_discover_cards")

    # ── Frame 6: Switch to Japanese ──
    click_radio(page, "日本語")
    screenshot(page, "06_japanese", delay=2)

    browser.close()
    print(f"\nCaptured {len(FRAMES)} frames")

# ── Combine into GIF ──
try:
    from PIL import Image
    import os

    images = [Image.open(f) for f in FRAMES]
    gif_path = f"{OUT}/demo.gif"

    # Optimize: reduce to palette mode for smaller file
    optimized = []
    for img in images:
        optimized.append(img.convert("P", palette=Image.ADAPTIVE, colors=256))

    optimized[0].save(
        gif_path,
        save_all=True,
        append_images=optimized[1:],
        duration=2500,  # 2.5 seconds per frame
        loop=0,
    )

    size_mb = os.path.getsize(gif_path) / (1024 * 1024)
    print(f"GIF saved: {gif_path} ({size_mb:.1f} MB)")

    # Clean up individual frames
    for f in FRAMES:
        os.remove(f)
    # Remove recon screenshot too
    if os.path.exists(f"{OUT}/recon.png"):
        os.remove(f"{OUT}/recon.png")
    print("Cleaned up individual frame files")

except ImportError:
    print("Pillow not installed. Install with: pip install Pillow")
    print(f"Individual frames saved as {OUT}/demo_*.png")
