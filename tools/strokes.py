"""Turn the signature artwork into ordered pen strokes.

Skeletonize the ink, merge crossing points into junction nodes, split the
rest into chains, then save chains + a labelled debug image.
"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.measure import label
from skimage.morphology import skeletonize
from scipy import ndimage as ndi

N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def load(src):
    im = np.array(Image.open(src).convert("RGBA"))
    alpha = im[..., 3].astype(float) / 255
    return im, alpha


def build(alpha):
    ink = alpha > 0.16
    comp = label(ink, connectivity=2)
    skel = skeletonize(ndi.gaussian_filter(alpha, 0.8) > 0.3)
    H, W = skel.shape
    k = np.ones((3, 3), int)
    deg = ndi.convolve(skel.astype(int), k, mode="constant") - 1
    deg[~skel] = 0
    junc = skel & (deg >= 3)
    # merge nearby junction pixels into one node
    jgrow = ndi.binary_dilation(junc, iterations=3) & skel
    jlab, nj = label(jgrow, connectivity=2, return_num=True)
    rest = skel & (jlab == 0)
    clab, nc = label(rest, connectivity=2, return_num=True)
    chains = []
    for c in range(1, nc + 1):
        pts = list(zip(*np.nonzero(clab == c)))
        ptset = set(pts)
        def nb(p):
            return [(p[0] + dy, p[1] + dx) for dy, dx in N8 if (p[0] + dy, p[1] + dx) in ptset]
        ends = [p for p in pts if len(nb(p)) <= 1]
        start = ends[0] if ends else pts[0]
        # walk the chain
        order, seen, cur = [start], {start}, start
        while True:
            nx = [q for q in nb(cur) if q not in seen]
            if not nx:
                break
            nx.sort(key=lambda q: abs(q[0] - cur[0]) + abs(q[1] - cur[1]))
            cur = nx[0]; seen.add(cur); order.append(cur)
        if len(order) < len(pts) * 0.8:
            continue
        def node_at(p):
            y, x = p
            win = jlab[max(0, y - 2):y + 3, max(0, x - 2):x + 3]
            v = win[win > 0]
            return int(v[0]) if len(v) else 0
        chains.append({
            "path": [[int(y), int(x)] for y, x in order],
            "na": node_at(order[0]), "nb": node_at(order[-1]),
            "comp": int(comp[order[len(order) // 2]]),
            "closed": not ends,
        })
    # drop little spurs hanging off junctions
    chains = [c for c in chains if not (len(c["path"]) < 7 and (c["na"] == 0 or c["nb"] == 0))]
    for i, c in enumerate(chains):
        c["id"] = i
    nodes = {}
    for j in range(1, nj + 1):
        ys, xs = np.nonzero(jlab == j)
        nodes[j] = {"pix": [[int(y), int(x)] for y, x in zip(ys, xs)],
                    "c": [float(ys.mean()), float(xs.mean())]}
    return chains, nodes, comp


def debug(alpha, chains, out):
    H, W = alpha.shape
    S = 3
    dbg = Image.new("RGB", (W * S, H * S), "white")
    a_img = Image.fromarray((alpha * 70).astype(np.uint8)).resize((W * S, H * S))
    dbg.paste(Image.new("RGB", dbg.size, (150, 150, 150)), mask=a_img)
    d = ImageDraw.Draw(dbg)
    rng = np.random.default_rng(5)
    font = ImageFont.truetype("arialbd.ttf", 18)
    for c in chains:
        col = tuple(int(v) for v in rng.integers(0, 190, 3))
        p = [(x * S, y * S) for y, x in c["path"]]
        d.line(p, fill=col, width=3)
        d.ellipse([p[0][0] - 4, p[0][1] - 4, p[0][0] + 4, p[0][1] + 4], fill=col)
        my, mx = c["path"][len(c["path"]) // 2]
        d.text((mx * S + 5, my * S - 10), str(c["id"]), fill=col, font=font)
    dbg.save(out)


if __name__ == "__main__":
    _, alpha = load(sys.argv[1])
    chains, nodes, _ = build(alpha)
    json.dump({"chains": chains, "nodes": nodes}, open(sys.argv[2] + ".json", "w"))
    debug(alpha, chains, sys.argv[2] + ".png")
    for c in chains:
        print(c["id"], "comp", c["comp"], "len", len(c["path"]), "nodes", c["na"], c["nb"],
              "from", c["path"][0], "to", c["path"][-1], "closed" if c["closed"] else "")
