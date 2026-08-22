#!/usr/bin/env python3
"""Baut aus webroot/ eine einzelne Datei zum Anschauen.

Die ausgelieferte Website besteht aus vier Seiten und lädt Schriften und
Bilder als eigene Dateien. Eine Vorschau muss eine einzige Datei sein.
Deshalb: alles einbetten, die vier Seiten untereinander legen und oben
eine Leiste zum Umschalten. Was hier dazukommt, ist ausdrücklich nicht
Teil des Produkts.
"""
import base64
import re
from pathlib import Path

HIER = Path(__file__).parent
WEB = HIER / "webroot"
SEITEN = [("start", "index.html", "Startseite"),
          ("impressum", "impressum.html", "Impressum"),
          ("datenschutz", "datenschutz.html", "Datenschutz"),
          ("danke", "danke.html", "Danke-Seite")]

TYP = {".woff2": "font/woff2", ".png": "image/png", ".jpg": "image/jpeg",
       ".svg": "image/svg+xml", ".webp": "image/webp"}


def datenadresse(pfad: Path) -> str:
    typ = TYP[pfad.suffix.lower()]
    return f"data:{typ};base64," + base64.b64encode(pfad.read_bytes()).decode()


def stil() -> str:
    css = (WEB / "stil.css").read_text(encoding="utf-8")
    for treffer in sorted(set(re.findall(r'url\("([^"]+\.woff2)"\)', css))):
        css = css.replace(f'url("{treffer}")', f'url("{datenadresse(WEB / treffer)}")')
    return css


def koerper(datei: str) -> str:
    s = (WEB / datei).read_text(encoding="utf-8")
    m = re.search(r"<body[^>]*>(.*)</body>", s, re.S)
    inhalt = m.group(1)
    # Bilder einbetten
    for bild in sorted(set(re.findall(r'src="(bilder/[^"]+)"', inhalt))):
        inhalt = inhalt.replace(f'src="{bild}"', f'src="{datenadresse(WEB / bild)}"')
    # Verweise zwischen den Seiten schalten die Vorschau um
    for name, seitendatei, _ in SEITEN:
        inhalt = inhalt.replace(f'href="{seitendatei}"', f'href="#" data-seite="{name}"')
    # Das Formular kann hier nichts versenden
    inhalt = inhalt.replace('<form class="anfrage" action="formular.php" method="post">',
                            '<form class="anfrage" data-vorschau>')
    return inhalt


LEISTE = """<div class="wg-leiste">
  <span class="wg-hinweis">Vorschau. Die ausgelieferte Website besteht aus vier
  Dateien und verschickt echte Anfragen.</span>
  <span class="wg-knoepfe">{knoepfe}</span>
</div>"""

ZUSATZ = """
/* ---- Nur für die Vorschau, nicht Teil der ausgelieferten Website ---- */
.wg-leiste { position: sticky; top: 0; z-index: 60; display: flex; flex-wrap: wrap;
  gap: .4rem 1.2rem; align-items: center; justify-content: space-between;
  background: var(--tinte); color: #C9D3CF; padding: .5rem clamp(1rem, 4vw, 3rem);
  font: 400 12px/1.4 var(--mono); }
.wg-knoepfe { display: flex; flex-wrap: wrap; gap: .3rem; }
.wg-leiste button { font: 500 12px/1 var(--mono); letter-spacing: .05em;
  padding: .42rem .8rem; border: 1px solid #3E4C47; background: transparent;
  color: #C9D3CF; cursor: pointer; }
.wg-leiste button:hover { border-color: #6C7A75; }
.wg-leiste button[aria-pressed="true"] { background: var(--blatt); color: var(--tinte);
  border-color: var(--blatt); }
.wg-leiste + .wg-seite .kopf { top: 2.4rem; }
"""

SKRIPT = """
/* Zwei Dinge, die es auf dem echten Hosting nicht braucht: das Umschalten
   zwischen den Seiten und ein Formular, das nichts verschickt. */
(function () {
  "use strict";
  var leiste = document.querySelector(".wg-leiste");
  function zeige(name) {
    document.querySelectorAll(".wg-seite").forEach(function (s) {
      s.hidden = s.dataset.name !== name;
    });
    leiste.querySelectorAll("button[data-seite]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.seite === name));
    });
    window.scrollTo(0, 0);
  }
  document.addEventListener("click", function (e) {
    var z = e.target.closest("[data-seite]");
    if (!z) { return; }
    e.preventDefault();
    zeige(z.dataset.seite);
  });
  document.addEventListener("submit", function (e) {
    if (!e.target.matches("[data-vorschau]")) { return; }
    e.preventDefault();
    var k = e.target.querySelector("button[type=submit]");
    if (k) { k.textContent = "In der Vorschau wird nichts verschickt"; k.disabled = true; }
  });
  zeige("start");
})();
"""


def bauen() -> Path:
    knoepfe = "".join(
        f'<button type="button" data-seite="{n}" aria-pressed="{"true" if n == "start" else "false"}">{t}</button>'
        for n, _, t in SEITEN)
    seiten = "".join(
        f'<div class="wg-seite" data-name="{n}"{"" if n == "start" else " hidden"}>{koerper(d)}</div>\n'
        for n, d, _ in SEITEN)
    kopf = (WEB / "index.html").read_text(encoding="utf-8")
    titel = re.search(r"<title>(.*?)</title>", kopf, re.S).group(1)
    beschreibung = re.search(r'name="description" content="([^"]*)"', kopf).group(1)

    seite = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titel}</title>
<meta name="description" content="{beschreibung}">
<style>
{stil()}
{ZUSATZ}</style>
</head>
<body>
{LEISTE.format(knoepfe=knoepfe)}
{seiten}<script>{SKRIPT}</script>
</body>
</html>
"""
    ziel = HIER / "vorschau.html"
    ziel.write_text(seite, encoding="utf-8")
    return ziel


if __name__ == "__main__":
    z = bauen()
    print(f"{z} · {z.stat().st_size // 1024} KB")
