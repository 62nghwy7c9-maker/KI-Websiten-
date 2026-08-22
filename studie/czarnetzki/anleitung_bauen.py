#!/usr/bin/env python3
"""Macht aus ANLEITUNG.md und LIVEGANG.md druckbare HTML-Seiten.

Kein Markdown-Paket, keine fremden Abrufe: Was gedruckt werden soll, muss
auch dann funktionieren, wenn gerade kein Netz da ist.
"""
import html
import re
from pathlib import Path

HIER = Path(__file__).parent

KOPF = """<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titel}</title>
<style>
:root{{--text:#1a1a1a;--matt:#5a5a5a;--linie:#dcdcdc;--akzent:#B23A0E}}
*{{box-sizing:border-box}}
body{{margin:0;padding:2.5rem 1.5rem 4rem;font:16px/1.65 -apple-system,
  BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  color:var(--text);background:#fff}}
main{{max-width:44rem;margin:0 auto}}
h1{{font-size:clamp(1.6rem,5vw,2.2rem);line-height:1.15;margin:0 0 .3rem;
  letter-spacing:-.02em;hyphens:auto}}
h2{{font-size:1.25rem;margin:2.6rem 0 .6rem;padding-top:1.4rem;
  border-top:1px solid var(--linie);letter-spacing:-.01em}}
h2:first-of-type{{border-top:0;padding-top:0}}
h3{{font-size:1.05rem;margin:1.6rem 0 .4rem}}
p,li{{margin:.6rem 0}}
ul,ol{{padding-left:1.3rem}}
li{{margin:.35rem 0}}
code{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.92em;background:#f3f3f1;padding:.1em .35em;border-radius:3px}}
pre{{background:#f7f7f5;border:1px solid var(--linie);border-radius:6px;
  padding:.9rem 1rem;overflow-x:auto;font-size:.9rem;line-height:1.5}}
pre code{{background:0;padding:0}}
a{{color:var(--akzent);text-decoration:none;font-weight:600;
  overflow-wrap:anywhere}}
a:hover{{text-decoration:underline}}
strong{{font-weight:650}}
hr{{border:0;border-top:1px solid var(--linie);margin:2.2rem 0}}
.vorspann{{color:var(--matt);font-size:1.02rem;margin:0 0 2rem}}
table{{border-collapse:collapse;width:100%;margin:1.1rem 0;font-size:.95rem}}
th,td{{text-align:left;padding:.55rem .7rem;border-bottom:1px solid var(--linie);
  vertical-align:top}}
th{{font-weight:650;border-bottom:2px solid var(--text)}}
.fuss{{margin-top:3rem;padding-top:1.2rem;border-top:2px solid var(--text);
  font-size:.95rem}}
.fuss strong{{color:var(--akzent)}}
ul.haken{{list-style:none;padding-left:0}}
ul.haken>li{{position:relative;padding:.55rem 0 .55rem 2rem;
  border-bottom:1px solid var(--linie)}}
ul.haken>li:last-child{{border-bottom:0}}
ul.haken>li::before{{content:"";position:absolute;left:0;top:.82em;
  width:1.05rem;height:1.05rem;border:2px solid var(--matt);border-radius:3px}}
ul.haken ol{{margin:.5rem 0 0;padding-left:1.2rem}}
ul.haken ol li,ul.haken ul li{{padding:.2rem 0;border:0}}
@media (max-width:34rem){{body{{padding:1.6rem 1.1rem 3rem}}
  table,thead,tbody,th,td,tr{{display:block}}
  thead{{display:none}}
  td{{border:0;padding:.15rem 0}}
  tr{{border-bottom:1px solid var(--linie);padding:.6rem 0}}
  td:first-child{{font-weight:650}}}}
@media print{{
  body{{padding:0;font-size:11pt;line-height:1.5}}
  main{{max-width:none}}
  h1{{font-size:20pt}} h2{{font-size:13pt}} h3{{font-size:11.5pt}}
  h2,h3{{break-after:avoid;page-break-after:avoid}}
  table,pre,ul,ol{{break-inside:avoid;page-break-inside:avoid}}
  tr{{break-inside:avoid;page-break-inside:avoid}}
  a{{color:inherit;text-decoration:none}}
  @page{{margin:18mm 16mm}}
}}
.marke{{display:flex;align-items:center;gap:.55rem;margin:0 0 2.2rem;
  padding-bottom:1rem;border-bottom:1px solid var(--linie)}}
.marke svg{{width:1.3rem;height:1.3rem;flex:none}}
.marke b{{font:700 .95rem/1 "Archivo Narrow",Arial Narrow,sans-serif;
  letter-spacing:.09em;text-transform:uppercase}}
@media print{{.marke{{margin-bottom:1.4rem}}}}
</style></head><body><main>
<p class="marke"><svg viewBox="0 0 48 48" aria-hidden="true">
<g fill="none" stroke="currentColor" stroke-width="4.6" stroke-linecap="square">
<path d="M5 17 V5 H17"/><path d="M31 5 H43 V17"/>
<path d="M43 31 V43 H31"/><path d="M17 43 H5 V31"/></g>
<circle cx="24" cy="24" r="5.4" fill="#B0271C"/></svg><b>Webgewerk</b></p>
"""

FUSS = """</main></body></html>
"""


def zeile(t: str) -> str:
    """Fettdruck und Code innerhalb einer Zeile."""
    t = html.escape(t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    # Verweise der Form [Text](Adresse). Ohne das stuende die Adresse
    # als roher Text auf der Seite und waere nicht anklickbar.
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)',
               r'<a href="\2">\1</a>', t)
    return t


def bauen(md: str) -> str:
    aus = []
    zeilen = md.split('\n')
    i = 0
    liste = None          # 'ul' oder 'ol', wenn eine offen ist

    def liste_schliessen():
        nonlocal liste
        if liste:
            aus.append('</ul>' if liste.startswith('ul') else f'</{liste}>')
            liste = None

    while i < len(zeilen):
        z = zeilen[i]

        # Eingerückter Block als Kasten
        if z.startswith('    ') and z.strip():
            liste_schliessen()
            block = []
            while i < len(zeilen) and (zeilen[i].startswith('    ')
                                       or not zeilen[i].strip()):
                block.append(zeilen[i][4:])
                i += 1
            while block and not block[-1].strip():
                block.pop()
            aus.append('<pre><code>' + html.escape('\n'.join(block))
                       + '</code></pre>')
            continue

        s = z.strip()

        if not s:
            liste_schliessen()
            i += 1
            continue

        if s == '---':
            liste_schliessen()
            i += 1
            continue

        if s.startswith('### '):
            liste_schliessen()
            aus.append(f'<h3>{zeile(s[4:])}</h3>')
        elif s.startswith('## '):
            liste_schliessen()
            aus.append(f'<h2>{zeile(s[3:])}</h2>')
        elif s.startswith('# '):
            liste_schliessen()
            aus.append(f'<h1>{zeile(s[2:])}</h1>')
        elif s.startswith('|'):
            liste_schliessen()
            reihen = []
            while i < len(zeilen) and zeilen[i].strip().startswith('|'):
                reihen.append([f.strip() for f in
                               zeilen[i].strip().strip('|').split('|')])
                i += 1
            reihen = [r for r in reihen
                      if not all(set(f) <= set('-: ') for f in r)]
            if reihen:
                aus.append('<table><thead><tr>' + ''.join(
                    f'<th>{zeile(f)}</th>' for f in reihen[0])
                    + '</tr></thead><tbody>')
                for r in reihen[1:]:
                    aus.append('<tr>' + ''.join(
                        f'<td>{zeile(f)}</td>' for f in r) + '</tr>')
                aus.append('</tbody></table>')
            continue
        elif re.match(r'^\d+\. ', s):
            if liste != 'ol':
                liste_schliessen()
                aus.append('<ol>')
                liste = 'ol'
            # Die Nummer kommt aus der Quelle. Wird eine Aufzaehlung von
            # Unterpunkten unterbrochen, faengt sie sonst wieder bei 1 an,
            # und in einer Anleitung ist die Reihenfolge der Inhalt.
            nummer = int(re.match(r'^(\d+)\. ', s).group(1))
            text = re.sub(r'^\d+\. ', '', s)
            aus.append('<li value="' + str(nummer) + '">' + zeile(text)
                       + '</li>')
        elif s.startswith('- [ ] ') or s.startswith('- [x] '):
            # Zum Abhaken, auf Papier wie am Bildschirm.
            if liste != 'ul-haken':
                liste_schliessen()
                aus.append('<ul class="haken">')
                liste = 'ul-haken'
            aus.append('<li>' + zeile(s[6:]) + '</li>')
        elif s.startswith('- '):
            if liste != 'ul':
                liste_schliessen()
                aus.append('<ul>')
                liste = 'ul'
            aus.append(f'<li>{zeile(s[2:])}</li>')
        else:
            # Fortsetzungszeile eines Listenpunkts
            if liste and aus and aus[-1].endswith('</li>'):
                aus[-1] = aus[-1][:-5] + ' ' + zeile(s) + '</li>'
            else:
                # Aufeinanderfolgende Zeilen sind ein Absatz, kein Absatz
                # je Zeile. Im Druck ist der Unterschied deutlich.
                klasse = ' class="vorspann"' if aus and aus[-1].startswith('<h1') \
                    else ''
                teile = [s]
                while (i + 1 < len(zeilen) and zeilen[i + 1].strip()
                       and not zeilen[i + 1].startswith('    ')
                       and not re.match(r'^([#|-]|\d+\. )',
                                        zeilen[i + 1].strip())
                       and zeilen[i + 1].strip() != '---'):
                    i += 1
                    teile.append(zeilen[i].strip())
                aus.append('<p' + klasse + '>' + zeile(' '.join(teile))
                           + '</p>')
        i += 1

    liste_schliessen()
    return '\n'.join(aus)


for quelle, titel in (('ANLEITUNG.md', 'Ihre Website pflegen'),
                      ('LIVEGANG.md', 'Livegang'),
                      ('CHECKLISTE.md', 'Czarnetzki: Schritt für Schritt')):
    md = (HIER / quelle).read_text(encoding='utf-8')
    ziel = HIER / (Path(quelle).stem + '.html')
    ziel.write_text(KOPF.format(titel=html.escape(titel)) + bauen(md) + FUSS,
                    encoding='utf-8')
    print(f'{ziel} · {ziel.stat().st_size // 1024} KB')
