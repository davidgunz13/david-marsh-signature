# David Marsh — Email Signature

Premium navy-and-gold email signature for **Sigma Cash Offer**, hosted on GitHub Pages so
Outlook can load the images from public HTTPS URLs.

- Preview + copy button: https://davidgunz13.github.io/david-marsh-signature/
- Signature only: https://davidgunz13.github.io/david-marsh-signature/outlook-signature.html

## What's here

| File | What it is |
|---|---|
| `index.html` | Preview page with a **Copy signature** button |
| `outlook-signature.html` | The signature alone (tables + inline CSS, no scripts) |
| `assets/signature.gif` | Handwriting animation, ~3 s, plays once, 600×194 (shown at 300×97) |
| `assets/signature-blank-start.gif` | Same animation starting from a blank frame (alternative) |
| `assets/signature-static.png` | Finished signature, transparent background |
| `assets/portrait.png` | Circular headshot with gold double ring (shown at 120×120) |
| `assets/icons/*.png` | Instagram, TikTok, YouTube, Facebook, Venmo, PayPal |
| `tools/` | Scripts and source art that rebuild everything above |

## How the animation works

`tools/strokes.py` thins the handwriting artwork down to its centre lines and splits them into
pen strokes. `tools/build_assets.py` plays those strokes back in writing order (D, avid, M, arsh,
the navy swooshes, then the gold underline) and saves the frames as a GIF.

The first frame shows a light "guide" of the whole signature. Clients that don't animate GIFs
(older desktop Outlook 2007–2013) show only the first frame, so they still display the name.
Modern clients play the pen writing over the guide. `signature-blank-start.gif` is the purer
version with an empty first frame, if you prefer that look.

## Rebuild after a change

```bash
pip install pillow numpy scipy scikit-image svg.path
python tools/build_assets.py
python tools/build_html.py
```

When an image changes, bump `VERSION` in `tools/build_html.py` so email clients fetch the new copy,
then commit and push. GitHub Pages republishes in about a minute.

Icons: [Simple Icons](https://simpleicons.org) (CC0), recoloured. Brand names belong to their owners.
