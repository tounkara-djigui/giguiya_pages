"""Genera Giguiya_Documentazione.pdf da DOCUMENTAZIONE.md (richiede: pip install markdown, Chrome/Chromium)."""
import base64
import pathlib
import re
import subprocess
import sys

import markdown

DOCS = pathlib.Path(__file__).resolve().parent
ROOT = DOCS.parent
src = (DOCS / 'DOCUMENTAZIONE.md').read_text(encoding='utf-8')
body_md = src.split('\n---\n', 1)[1].lstrip()
body_md = re.sub(r'^## Indice\n.*?\n---\n', '', body_md, count=1, flags=re.S)

LIST = re.compile(r'^(\s*)([-*]|\d+\.)\s')
out, fence, prev = [], False, ''
for line in body_md.split('\n'):
    is_fence = line.strip().startswith('```')
    if is_fence:
        fence = not fence
    elif not fence:
        m = LIST.match(line)
        if m:
            if 0 < len(m.group(1)) < 4:
                line = '    ' + line.lstrip()
            if prev.strip() and not LIST.match(prev) and not prev.startswith('    '):
                out.append('')
    out.append(line)
    prev = line
html_body = markdown.markdown('\n'.join(out), extensions=['tables', 'fenced_code', 'sane_lists'], lazy_ol=False)

toc = ''.join(f'<li><span class="n">{n}</span><span class="t">{t}</span></li>'
              for n, t in re.findall(r'^## (\d+)\. (.+)$', src, flags=re.M))
logo = base64.b64encode((ROOT / 'frontend/public/images/logo-emblem.png').read_bytes()).decode()
version = re.search(r'Versione del documento: (.+)', src).group(1)

css = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm;
  @bottom-right { content: counter(page); font-size: 8pt; color: #8a7a5a; } }
@page :first { margin: 0; @bottom-right { content: none; } }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'DejaVu Sans', 'Liberation Sans', Arial, sans-serif; color: #1d1a16; font-size: 10pt; line-height: 1.5; }
.cover { height: 296mm; display: flex; flex-direction: column; justify-content: space-between; background: #12100d; color: #f3ead7; padding: 26mm 22mm; page-break-after: always; }
.cover img { width: 34mm; border-radius: 2mm; }
.cover .kicker { color: #c9a24a; letter-spacing: .25em; text-transform: uppercase; font-size: 9pt; }
.cover h1 { font-size: 30pt; line-height: 1.15; margin: 6mm 0 4mm; color: #f3ead7; }
.cover .sub { font-size: 12pt; color: #d8cbb0; max-width: 140mm; }
.cover .bar { height: 2px; width: 40mm; background: #c9a24a; margin: 8mm 0; }
.cover .meta { font-size: 9pt; color: #b9ab8f; border-top: 1px solid #3a332a; padding-top: 5mm; }
.toc { page-break-after: always; }
.toc ol { list-style: none; padding: 0; }
.toc li { display: flex; gap: 6mm; padding: 2.2mm 0; border-bottom: 1px dotted #cbbf9f; font-size: 10.5pt; }
.toc .n { color: #a8842f; font-weight: bold; width: 8mm; }
h2 { font-size: 16pt; color: #12100d; border-bottom: 2px solid #c9a24a; padding-bottom: 2mm; margin: 0 0 4mm; page-break-after: avoid; }
.content h2 { page-break-before: always; }
h3 { font-size: 12pt; color: #7a5e1f; margin: 6mm 0 2mm; page-break-after: avoid; }
ul, ol { padding-left: 6mm; margin: 2mm 0 3mm; }
li { margin: 1mm 0; }
p, li { orphans: 3; widows: 3; }
hr { display: none; }
table { width: 100%; border-collapse: collapse; margin: 3mm 0 5mm; font-size: 8.6pt; }
tr { page-break-inside: avoid; }
th { background: #12100d; color: #f3ead7; text-align: left; padding: 2mm 2.5mm; }
td { padding: 1.8mm 2.5mm; border-bottom: 1px solid #e4dcc8; vertical-align: top; word-break: break-word; }
tr:nth-child(even) td { background: #faf6ec; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.3pt; background: #f3eddd; padding: .3mm 1mm; border-radius: 1mm; word-break: break-all; }
pre { background: #1b1813; color: #efe3c6; padding: 3.5mm 4mm; border-radius: 2mm; border-left: 3px solid #c9a24a; font-size: 8pt; line-height: 1.45; white-space: pre-wrap; word-break: break-all; page-break-inside: avoid; }
pre code { background: none; color: inherit; padding: 0; }
blockquote { margin: 4mm 0; padding: 3mm 4mm; background: #fbf3dc; border-left: 4px solid #c9a24a; }
blockquote p { margin: 0; }
a { color: #7a5e1f; text-decoration: none; }
"""

html = f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Giguiya – Documentazione</title><style>{css}</style></head><body>
<section class="cover">
  <div><img src="data:image/png;base64,{logo}" alt=""></div>
  <div>
    <div class="kicker">Associazione Giguiya · Torino</div>
    <h1>Documentazione tecnica<br>e operativa del sito</h1>
    <div class="bar"></div>
    <div class="sub">Architettura, codice, configurazione di GitHub, Render, MongoDB Atlas e DNS Aruba, sviluppo locale su Windows, manutenzione e risoluzione dei problemi.</div>
  </div>
  <div class="meta">giguiya.it · Versione {version}<br>Documento interno – non contiene password</div>
</section>
<section class="toc"><h2>Indice</h2><ol>{toc}</ol></section>
<section class="content">{html_body}</section>
</body></html>"""

html_file = DOCS / '_build.html'
html_file.write_text(html, encoding='utf-8')
browser = sys.argv[1] if len(sys.argv) > 1 else 'chromium'
subprocess.run([browser, '--headless=new', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                f'--print-to-pdf={DOCS / "Giguiya_Documentazione.pdf"}', html_file.as_uri()], check=True)
html_file.unlink()
print('PDF creato:', DOCS / 'Giguiya_Documentazione.pdf')
