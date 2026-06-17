#!/usr/bin/env python3
"""
Generate launch assets for Databery:
  - assets/img/og-card.jpg        branded 1200x630 social share image
  - assets/img/apple-touch-icon.png  180x180 home-screen icon
  - re-compresses assets/img/*.jpg (progressive, optimized) to cut bytes

Run:  python make_assets.py
"""
import os, glob
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "assets", "img")
os.makedirs(IMG, exist_ok=True)
FONTS = r"C:\Windows\Fonts"

# brand gradient stops (navy -> royal purple -> electric blue)
STOPS = [(0.0, (28, 27, 78)), (0.52, (99, 36, 196)), (1.0, (63, 94, 251))]

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def grad(t):
    for i in range(len(STOPS) - 1):
        t0, c0 = STOPS[i]; t1, c1 = STOPS[i + 1]
        if t <= t1:
            tt = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return lerp(c0, c1, max(0.0, min(1.0, tt)))
    return STOPS[-1][1]

def hgrad(w, h):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for x in range(w):
        d.line([(x, 0), (x, h)], fill=grad(x / (w - 1)))
    return img

def draw_berry(d, ox, oy, s, node_fill=(255, 255, 255), dot_fill=(178, 200, 255), lw=2):
    P = lambda px, py: (ox + px * s, oy + py * s)
    edges = [((16,18),(24,16)),((16,18),(12,26)),((24,16),(28,24)),((12,26),(20,30)),
             ((28,24),(20,30)),((20,30),(16,38)),((16,38),(26,36)),((28,24),(26,36))]
    for a, b in edges:
        d.line([P(*a), P(*b)], fill=node_fill, width=lw)
    nodes = [((16,18),3),((24,16),3.4),((12,26),3.6),((28,24),3),((20,30),4),((16,38),3.4),((26,36),3)]
    for (px,py), r in nodes:
        cx, cy = P(px, py); rr = r * s
        d.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=node_fill)
    scatter = [((34,20),1.7),((37.5,26),2),((34.5,32),1.6),((31,38),1.3),((38.5,33),1.1)]
    for (px,py), r in scatter:
        cx, cy = P(px, py); rr = r * s
        d.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=dot_fill)

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

# ---------------------------------------------------------------- OG card
def make_og():
    W, H = 1200, 630
    img = hgrad(W, H)
    d = ImageDraw.Draw(img)
    # decorative translucent circles (berry-node motif), top/right
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for cx, cy, r, a in [(1050,110,95,38),(1135,250,58,28),(975,70,40,48),(1160,470,130,24),(1080,560,55,26)]:
        od.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255,255,255,a))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)
    # berry mark
    draw_berry(d, ox=92, oy=70, s=2.5, lw=3)
    # wordmark (two-tone like the logo)
    fb = font("arialbd.ttf", 116)
    x0, y0 = 88, 210
    w1 = d.textlength("Data", font=fb)
    d.text((x0, y0), "Data", font=fb, fill=(255, 255, 255))
    d.text((x0 + w1, y0), "bery", font=fb, fill=(170, 196, 255))
    # tagline
    d.text((x0 + 4, y0 + 165), "Account & Sales Intelligence", font=font("arial.ttf", 42), fill=(226, 226, 242))
    # eyebrow tagline
    d.text((x0 + 4, y0 + 250), "INSIGHTS   ·   INTELLIGENCE   ·   IMPACT",
           font=font("arialbd.ttf", 24), fill=(188, 196, 232))
    out = os.path.join(IMG, "og-card.jpg")
    img.save(out, "JPEG", quality=90, optimize=True, progressive=True)
    return out, os.path.getsize(out)

# ---------------------------------------------------------------- apple touch icon
def make_icon():
    S = 180
    img = hgrad(S, S)
    d = ImageDraw.Draw(img)
    draw_berry(d, ox=44, oy=36, s=2.5, lw=3)
    out = os.path.join(IMG, "apple-touch-icon.png")
    img.save(out, "PNG", optimize=True)
    return out, os.path.getsize(out)

# ---------------------------------------------------------------- recompress photos
def recompress():
    results = []
    for p in sorted(glob.glob(os.path.join(IMG, "*.jpg"))):
        if os.path.basename(p) == "og-card.jpg":
            continue
        before = os.path.getsize(p)
        im = Image.open(p).convert("RGB")
        if im.width > 1600:
            im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
        im.save(p, "JPEG", quality=72, optimize=True, progressive=True)
        after = os.path.getsize(p)
        results.append((os.path.basename(p), before, after))
    return results

if __name__ == "__main__":
    og, ogs = make_og()
    ic, ics = make_icon()
    print("OG card     :", os.path.basename(og), round(ogs/1024), "kb")
    print("Touch icon  :", os.path.basename(ic), round(ics/1024), "kb")
    print("Recompressed:")
    saved = 0
    for name, b, a in recompress():
        saved += (b - a)
        print("  %-26s %5d kb -> %5d kb" % (name, b//1024, a//1024))
    print("Total saved : %d kb" % (saved // 1024))
