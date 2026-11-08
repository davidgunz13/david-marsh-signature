"""Write outlook-signature.html and index.html from one signature template.

    python tools/build_html.py

Bump VERSION after changing any image so email clients fetch the new copy.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://davidgunz13.github.io/david-marsh-signature/assets"
VERSION = "1"

NAVY = "#0b2038"
GOLD = "#b8862b"       # text gold (a touch darker than the art for contrast)
GOLD_BTN = "#c9952d"

SOCIAL = [
    ("instagram", "Instagram", "https://www.instagram.com/davidgunz13/"),
    ("tiktok", "TikTok", "https://www.tiktok.com/@davidgunz13"),
    ("youtube", "YouTube", "https://www.youtube.com/@davidgunz13"),
    ("facebook", "Facebook", "https://www.facebook.com/davidgunz13"),
    ("venmo", "Venmo", "https://venmo.com/u/davidgunz13"),
    ("paypal", "PayPal", "https://paypal.me/davidgunz13"),
]
BLINQ = "https://blinq.me/cm8zf569s0051s60laa8pd2d9?bs=db"


def img(path):
    return f"{BASE}/{path}?v={VERSION}"


def icons():
    cells = []
    for i, (key, label, url) in enumerate(SOCIAL):
        pad = "0" if i == len(SOCIAL) - 1 else "0 6px 0 0"
        cells.append(
            f'<td style="padding:{pad};"><a href="{url}" target="_blank" title="{label}" '
            f'style="text-decoration:none;"><img src="{img(f"icons/{key}.png")}" width="26" height="26" '
            f'alt="{label}" style="display:block;width:26px;height:26px;border:0;"></a></td>'
        )
    return "".join(cells)


TEXT = f"font-family:Arial,Helvetica,sans-serif;color:{NAVY};"

SIGNATURE = f"""<table cellpadding="0" cellspacing="0" border="0" role="presentation" style="border-collapse:collapse;{TEXT}">
<tr>
<td valign="middle" style="padding:0 18px 0 0;vertical-align:middle;">
<a href="{BLINQ}" target="_blank" style="text-decoration:none;"><img src="{img("portrait.png")}" width="120" height="120" alt="David Marsh" style="display:block;width:120px;height:120px;border:0;"></a>
</td>
<td valign="middle" style="padding:2px 0 2px 18px;vertical-align:middle;border-left:2px solid {GOLD_BTN};">
<table cellpadding="0" cellspacing="0" border="0" role="presentation" style="border-collapse:collapse;">
<tr><td style="padding:0;"><img src="{img("signature.gif")}" width="300" height="97" alt="David Marsh" style="display:block;width:300px;height:97px;border:0;"></td></tr>
<tr><td style="padding:5px 0 0 0;{TEXT}font-size:11px;line-height:14px;font-weight:bold;letter-spacing:1.8px;white-space:nowrap;">REAL ESTATE INVESTOR&nbsp;&nbsp;<span style="color:{GOLD};">|</span>&nbsp;&nbsp;DEAL ARCHITECT</td></tr>
<tr><td style="padding:7px 0 0 0;{TEXT}font-size:16px;line-height:20px;font-weight:bold;letter-spacing:2px;white-space:nowrap;"><span style="font-family:Georgia,'Times New Roman',serif;color:{GOLD};font-size:19px;">&Sigma;</span>&nbsp;&nbsp;SIGMA CASH OFFER</td></tr>
<tr><td style="padding:7px 0 0 0;{TEXT}font-size:13px;line-height:17px;white-space:nowrap;"><a href="tel:+17274735227" style="color:{NAVY};text-decoration:none;">+1 (727) 473-5227</a>&nbsp;&nbsp;<span style="color:{GOLD};">|</span>&nbsp;&nbsp;<a href="mailto:dave@buymyflhome.com" style="color:{NAVY};text-decoration:none;">dave@buymyflhome.com</a></td></tr>
<tr><td style="padding:10px 0 0 0;">
<table cellpadding="0" cellspacing="0" border="0" role="presentation" style="border-collapse:collapse;"><tr>
{icons()}
<td style="padding:0 0 0 14px;"><table cellpadding="0" cellspacing="0" border="0" role="presentation" style="border-collapse:separate;"><tr><td bgcolor="{GOLD_BTN}" style="background-color:{GOLD_BTN};border-radius:4px;padding:6px 14px;"><a href="{BLINQ}" target="_blank" style="font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:14px;font-weight:bold;letter-spacing:0.5px;color:{NAVY};text-decoration:none;white-space:nowrap;">Save Contact</a></td></tr></table></td>
</tr></table>
</td></tr>
</table>
</td>
</tr>
</table>"""

OUTLOOK = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>David Marsh - Outlook signature</title>
</head>
<body style="margin:0;padding:16px;background:#ffffff;">
<!-- signature start -->
{SIGNATURE}
<!-- signature end -->
</body>
</html>
"""

INDEX = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>David Marsh Signature</title>
<style>
  :root {{ --navy:{NAVY}; --gold:{GOLD_BTN}; --bg:#f4f1ea; --card:#ffffff; --muted:#5b6575; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--navy); font:15px/1.55 Arial,Helvetica,sans-serif; }}
  main {{ max-width:760px; margin:0 auto; padding:32px 16px 48px; }}
  h1 {{ font-size:20px; letter-spacing:2px; text-transform:uppercase; margin:0 0 4px; }}
  .sub {{ color:var(--muted); margin:0 0 24px; }}
  .card {{ background:var(--card); border:1px solid #e3dccb; border-radius:10px; padding:28px 24px; overflow-x:auto; }}
  .actions {{ display:flex; flex-wrap:wrap; gap:10px; margin:18px 0 28px; }}
  button {{ font:inherit; font-weight:bold; border:0; border-radius:6px; padding:10px 18px; cursor:pointer; background:var(--navy); color:#fff; }}
  button.alt {{ background:var(--gold); color:var(--navy); }}
  #status {{ align-self:center; color:var(--muted); }}
  h2 {{ font-size:15px; letter-spacing:1.5px; text-transform:uppercase; margin:28px 0 8px; }}
  ol {{ padding-left:20px; }} li {{ margin:4px 0; }}
  code {{ background:#ebe5d6; padding:1px 5px; border-radius:4px; font-size:13px; }}
  a {{ color:var(--navy); }}
</style>
</head>
<body>
<main>
<h1>David Marsh &mdash; Email Signature</h1>
<p class="sub">Sigma Cash Offer &middot; hosted on GitHub Pages for Outlook</p>
<div class="card"><div id="sig">
{SIGNATURE}
</div></div>
<div class="actions">
  <button id="copy">Copy signature</button>
  <button class="alt" id="replay">Replay animation</button>
  <span id="status" role="status"></span>
</div>

<h2>Install in New Outlook / Outlook on the web</h2>
<ol>
  <li>Click <b>Copy signature</b> above.</li>
  <li>In Outlook open <b>Settings &rarr; Accounts &rarr; Signatures</b>.</li>
  <li>Pick <b>David Marsh Premium</b>, click in the editor, select anything already there and press <b>Ctrl+V</b>.</li>
  <li>Click <b>Save</b>. Leave the default boxes as they are until testing is done.</li>
</ol>

<h2>Files</h2>
<p><a href="outlook-signature.html">outlook-signature.html</a> &middot;
<a href="assets/signature.gif">signature.gif</a> &middot;
<a href="assets/signature-static.png">signature-static.png</a> &middot;
<a href="assets/portrait.png">portrait.png</a></p>
</main>
<script>
const sig = document.getElementById('sig');
const status = document.getElementById('status');
document.getElementById('copy').addEventListener('click', async () => {{
  const html = sig.innerHTML.trim();
  try {{
    await navigator.clipboard.write([new ClipboardItem({{
      'text/html': new Blob([html], {{type: 'text/html'}}),
      'text/plain': new Blob([sig.innerText], {{type: 'text/plain'}})
    }})]);
  }} catch (e) {{
    const r = document.createRange(); r.selectNodeContents(sig);
    const s = getSelection(); s.removeAllRanges(); s.addRange(r);
    document.execCommand('copy'); s.removeAllRanges();
  }}
  status.textContent = 'Copied. Paste it into the Outlook signature editor.';
}});
document.getElementById('replay').addEventListener('click', () => {{
  const g = sig.querySelector('img[src*="signature.gif"]');
  const src = g.src.split('&r=')[0];
  g.src = src + '&r=' + Date.now();
}});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    (ROOT / "outlook-signature.html").write_text(OUTLOOK, encoding="utf-8")
    (ROOT / "index.html").write_text(INDEX, encoding="utf-8")
    print("wrote outlook-signature.html and index.html")
