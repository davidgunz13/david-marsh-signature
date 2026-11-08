"""Build every image the email signature uses.

    python tools/build_assets.py

Inputs  (tools/source):  signature.png  portrait.jpg
        (tools/icons-src): Simple Icons SVGs (CC0)
Outputs (assets):        portrait.png  signature.gif  signature-static.png
                         signature-blank-start.gif  icons/*.png
"""
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from svg.path import parse_path

from strokes import build as build_chains

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "source"
OUT = ROOT / "assets"

NAVY = (11, 32, 56)          # #0b2038
GOLD_DARK = (150, 106, 32)
GOLD = (201, 149, 45)        # #c9952d
GOLD_LIGHT = (243, 219, 150)


def lerp(a, b, t):
    t = np.clip(t, 0, 1)[..., None]
    return np.array(a) * (1 - t) + np.array(b) * t


def metal(t):
    """Metallic gold ramp: t in 0..1 -> dark, base, light, base, dark."""
    t = np.asarray(t, float)
    w = 0.5 - 0.5 * np.cos(2 * np.pi * t)          # 0 at ends, 1 mid
    low = lerp(GOLD_DARK, GOLD, np.clip(w * 2, 0, 1))
    return np.where((w > 0.5)[..., None], lerp(GOLD, GOLD_LIGHT, (w - 0.5) * 2), low)


# ---------------------------------------------------------------- portrait
def portrait(size=256, ss=4):
    src = Image.open(SRC / "portrait.jpg").convert("RGB")
    cy, cx, r_src = 139, 140, 129          # photo circle inside the old ring
    photo = src.crop((cx - r_src, cy - r_src, cx + r_src, cy + r_src))
    S = size * ss
    c = S / 2
    yy, xx = np.mgrid[0:S, 0:S] + 0.5
    rr = np.hypot(yy - c, xx - c) / ss                  # radius in output px
    ang = np.arctan2(yy - c, xx - c)
    gold = metal((np.cos(ang - np.radians(-135)) * 0.5 + 0.5) * 0.9 + 0.05)
    # rings (output px):  photo <=113, thin ring 115.5-117.5, thick ring 120.5-126.5
    r_photo = 113.0
    ph = photo.resize((int(2 * r_photo * ss), int(2 * r_photo * ss)), Image.LANCZOS)
    canvas = np.zeros((S, S, 4), float)
    off = int(c - r_photo * ss)
    canvas[off:off + ph.height, off:off + ph.width, :3] = np.array(ph)
    canvas[..., 3] = (rr <= r_photo) * 255
    for r0, r1 in [(115.5, 117.5), (120.5, 126.5)]:
        m = (rr >= r0) & (rr <= r1)
        canvas[m, :3] = gold[m]
        canvas[m, 3] = 255
    img = Image.fromarray(canvas.astype(np.uint8), "RGBA").resize((size, size), Image.LANCZOS)
    img.save(OUT / "portrait.png", optimize=True)


# ---------------------------------------------------------------- icons
ICONS = ["instagram", "tiktok", "youtube", "facebook", "venmo", "paypal"]


def venmo_mask(px):
    """Venmo's app mark is a bold italic V (the SVG is a wordmark, unreadable this small)."""
    from PIL import ImageFont
    big = px * 2
    m = Image.new("L", (big, big), 0)
    f = ImageFont.truetype("arialbi.ttf", int(big * 1.05))
    d = ImageDraw.Draw(m)
    l, t, r, b = d.textbbox((0, 0), "V", font=f)
    d.text(((big - (r - l)) / 2 - l, (big - (b - t)) / 2 - t), "V", font=f, fill=255)
    return np.array(m.resize((px, px), Image.LANCZOS)) > 127


def svg_mask(name, px):
    if name == "venmo":
        return venmo_mask(px)
    text = (ROOT / "tools" / "icons-src" / f"{name}.svg").read_text()
    d = re.search(r'\sd="([^"]+)"', text).group(1)
    path = parse_path(d)
    mask = Image.new("1", (px, px), 0)
    k = px / 24.0
    subs, cur = [], []
    for seg in path:
        if seg.__class__.__name__ == "Move":
            if cur:
                subs.append(cur)
            cur = []
            continue
        n = max(2, int(seg.length() * k / 1.5))
        cur += [seg.point(i / n) for i in range(n + 1)]
    if cur:
        subs.append(cur)
    acc = np.zeros((px, px), bool)
    for sp in subs:                                      # even-odd fill
        m = Image.new("1", (px, px), 0)
        ImageDraw.Draw(m).polygon([(p.real * k, p.imag * k) for p in sp], fill=1)
        acc ^= np.array(m)
    return acc


def icon(name, size=56, ss=8):
    S = size * ss
    c = S / 2
    yy, xx = np.mgrid[0:S, 0:S] + 0.5
    rr = np.hypot(yy - c, xx - c)
    R = S / 2 - ss * 0.5
    ring_w = 2.2 * ss
    rgba = np.zeros((S, S, 4), float)
    disc = rr <= R
    rgba[disc, :3] = NAVY
    rgba[disc, 3] = 255
    ring = disc & (rr >= R - ring_w)
    gold_ring = metal(((xx - yy) / (2 * S)) + 0.5)
    rgba[ring, :3] = gold_ring[ring]
    gw = int(S * 0.50)                                   # glyph box
    g = svg_mask(name, gw)
    gold_glyph = metal(np.linspace(0.18, 0.62, gw))[:, None, :].repeat(gw, 1)
    o = (S - gw) // 2
    sub = rgba[o:o + gw, o:o + gw]
    sub[g, :3] = gold_glyph[g]
    img = Image.fromarray(rgba.astype(np.uint8), "RGBA").resize((size, size), Image.LANCZOS)
    img.save(OUT / "icons" / f"{name}.png", optimize=True)


# ---------------------------------------------------------------- handwriting
# Pen order. Each stroke is a pen-down movement; (chain, reversed).
# "J" = jump to the next chain without drawing a connecting line.
STROKES = [
    # D: stem, then the big loop that flows into the crossbar
    [(9, 0), (26, 0), (31, 0)],
    [(1, 0), (20, 1)],
    # a
    [(21, 0), (28, 1), (29, 0), (12, 1)],
    # v i d
    [(16, 0), (14, 1), "J", (25, 0), "J", (7, 0), (27, 0)],
    # i dot
    [(10, 1)],
    # M in one continuous stroke
    [(41, 1), (5, 1), (3, 1), (6, 0), (2, 1), (0, 1), (4, 0), (37, 0)],
    # a r s h
    [(15, 0), (17, 1), (18, 0), (13, 1), (24, 0), (23, 1), (11, 1), (8, 0), (11, 0), (19, 0)],
    # navy swooshes under the name
    [(36, 1), (34, 1), (33, 0)],
    [(40, 1), (39, 1)],
]
PAUSE = 0.07          # pen lift between strokes (s)
T_START = 0.12        # blank lead-in (s)
T_WRITE = 2.30        # all handwriting (s)
T_GOLD = 0.45         # gold underline sweep (s)
FPS = 25
GHOST = 0.20          # opacity of the guide shown in frame 1
PAD_BOTTOM = 26       # room for the gold underline (source px)
GIF_W = 600           # shown at 300px in the email (2x for sharp screens)


def ease_inv(n, a=0.45):
    """Arc-length positions 0..1 -> time 0..1 for a pen that eases in and out."""
    u = np.linspace(0, 1, 400)
    s = (1 - a) * u + a * (3 * u ** 2 - 2 * u ** 3)
    return lambda x: np.interp(x, s, u)


def stroke_points(chains, stroke):
    pts, jumps = [], []
    for tok in stroke:
        if tok == "J":
            jumps.append(len(pts))
            continue
        cid, rev = tok
        p = np.array(chains[cid]["path"], float)
        if rev:
            p = p[::-1]
        if pts and (len(pts) not in jumps):
            a, b = np.array(pts[-1]), p[0]
            n = int(np.hypot(*(b - a)) / 0.5)
            pts += [a + (b - a) * i / n for i in range(1, n)]
        pts += list(p)
    return np.array(pts)


def time_map(alpha):
    chains, _, _ = build_chains(alpha)
    by_id = {c["id"]: c for c in chains}
    strokes = [stroke_points(by_id, s) for s in STROKES]
    lens = [np.r_[0, np.cumsum(np.hypot(*np.diff(s, axis=0).T))] for s in strokes]
    durs = np.array([L[-1] ** 0.72 for L in lens])
    durs *= (T_WRITE - PAUSE * (len(strokes) - 1)) / durs.sum()
    inv = ease_inv(0)
    allp, allt = [], []
    t0 = T_START
    for s, L, d in zip(strokes, lens, durs):
        allp.append(s)
        allt.append(t0 + inv(L / L[-1]) * d)
        t0 += d + PAUSE
    P, T = np.vstack(allp), np.concatenate(allt)
    tree = cKDTree(P)
    ys, xs = np.nonzero(alpha > 0.01)
    q = np.c_[ys, xs].astype(float)
    dist, idx = tree.query(q, k=12)
    near = dist <= dist[:, :1] + 1.6            # earliest stroke passing this pixel
    tpix = np.where(near, T[idx], np.inf).min(1)
    tm = np.full(alpha.shape, np.inf)
    tm[ys, xs] = tpix
    return tm, t0 - PAUSE


def gold_line(W, H, ss=4):
    """Tapered metallic underline. Returns (alpha, rgb, x-progress map)."""
    S = ss
    x0, x1 = 128, 646
    xs = np.linspace(x0, x1, 600)
    u = (xs - x0) / (x1 - x0)
    ys = 202 - 9 * np.sin(np.pi * u) + 6 * u           # gentle arc
    w = 5.2 * np.sin(np.pi * np.clip(u, 0, 1)) ** 0.55 + 0.5
    big = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(big)
    top = [(x * S, (y - wi / 2) * S) for x, y, wi in zip(xs, ys, w)]
    bot = [(x * S, (y + wi / 2) * S) for x, y, wi in zip(xs, ys, w)][::-1]
    d.polygon(top + bot, fill=255)
    a = np.array(big.resize((W, H), Image.LANCZOS), float) / 255
    xx = np.arange(W)[None, :].repeat(H, 0)
    prog = np.clip((xx - x0) / (x1 - x0), 0, 1)
    rgb = metal(np.clip(prog * 1.6 - 0.3, 0, 1) * 0.8 + 0.1)
    return a, rgb, prog


def handwriting():
    src = np.array(Image.open(SRC / "signature.png").convert("RGBA"))
    alpha0 = src[..., 3].astype(float) / 255
    tm0, t_end_write = time_map(alpha0)
    H0, W0 = alpha0.shape
    H, W = H0 + PAD_BOTTOM, W0
    alpha = np.zeros((H, W)); alpha[:H0] = alpha0
    tm = np.full((H, W), np.inf); tm[:H0] = tm0
    ink = np.array(NAVY, float)
    ga, grgb, gprog = gold_line(W, H)
    g_start = t_end_write + 0.05
    total = g_start + T_GOLD

    def frame(t, ghost, bg_white=True):
        vis = np.clip((t - tm) / 0.05 + 1, 0, 1)          # soft pen tip
        a = np.maximum(alpha * vis, alpha * ghost)
        gp = np.clip((t - g_start) / T_GOLD, 0, 1)
        gp = 1 - (1 - gp) ** 2                            # sweep eases out
        gv = np.clip((gp * 1.04 - gprog) / 0.04, 0, 1) if t >= g_start else np.zeros_like(gprog)
        gv = np.maximum(gv, ghost * (ghost > 0))
        g_a = ga * gv
        if bg_white:
            out = np.full((H, W, 3), 255.0)
            out = out * (1 - a[..., None]) + ink * a[..., None]
            out = out * (1 - g_a[..., None]) + grgb * g_a[..., None]
            return Image.fromarray(out.round().astype(np.uint8), "RGB")
        a_tot = 1 - (1 - a) * (1 - g_a)
        rgb = (ink * a[..., None] * (1 - g_a[..., None]) + grgb * g_a[..., None]) / np.maximum(a_tot, 1e-6)[..., None]
        return Image.fromarray(np.dstack([rgb, a_tot * 255]).round().astype(np.uint8), "RGBA")

    # static PNG (transparent, 2x)
    final = frame(1e9, 0, bg_white=False)
    final.resize((GIF_W, round(H * GIF_W / W)), Image.LANCZOS).save(OUT / "signature-static.png", optimize=True)

    size = (GIF_W, round(H * GIF_W / W))
    for name, ghost in [("signature.gif", GHOST), ("signature-blank-start.gif", 0.0)]:
        times = np.arange(0, total + 1e-9, 1 / FPS)
        frames = [frame(t, ghost).resize(size, Image.LANCZOS) for t in times]
        frames.append(frame(1e9, 0).resize(size, Image.LANCZOS))
        pal = Image.new("RGB", (size[0], size[1] * 2))
        pal.paste(frames[-1], (0, 0)); pal.paste(frames[len(frames) // 2], (0, size[1]))
        pal = pal.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        pv = pal.getpalette()[:96 * 3]
        wi = max(range(96), key=lambda i: sum(pv[3 * i:3 * i + 3]))
        pv[3 * wi:3 * wi + 3] = [255, 255, 255]           # background must be pure white
        pal.putpalette(pv)
        q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
        durs = [int(1000 / FPS)] * (len(q) - 1) + [60000]
        durs[0] = 300                                      # hold the first frame briefly
        q[0].save(OUT / name, save_all=True, append_images=q[1:], duration=durs,
                  optimize=True, disposal=1)
        print(name, len(q), "frames", f"{total:.2f}s", (OUT / name).stat().st_size // 1024, "KB")
    print("display size", GIF_W // 2, "x", round(H * GIF_W / W) // 2)


if __name__ == "__main__":
    (OUT / "icons").mkdir(parents=True, exist_ok=True)
    portrait()
    for n in ICONS:
        icon(n)
    handwriting()
