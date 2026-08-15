"""Baut aus den drei Seiten eine einzelne Datei für die Vorschau.

Die echte Website liegt in `studie/seite/` und besteht aus drei Seiten mit
einem gemeinsamen Stylesheet — so wie sie später auf dem Hosting liegt. Der
Stil steht damit einmal da, nicht dreimal.

Eine Vorschau kann aber nur **eine** Datei zeigen. Dieses Skript setzt
deshalb `studie/firmenseite.html` zusammen: Stylesheet hineinkopiert, die
beiden Rechtsseiten unten angehängt, und die Verweise in der Fußzeile auf
Sprungmarken innerhalb derselben Datei umgebogen. Dadurch funktioniert in
der Vorschau alles, was auf der echten Website auch funktioniert.

Die erzeugte Datei wird **nicht** von Hand bearbeitet — Änderungen gehören
nach `studie/seite/`.

    python3 studie/bauen.py
"""
from __future__ import annotations

import re
from pathlib import Path

SEITE = Path(__file__).parent / "seite"
START = SEITE / "index.html"
STIL = SEITE / "stil.css"
ZIEL = Path(__file__).parent / "firmenseite.html"

# Anhängen in dieser Reihenfolge: Datei, Sprungmarke, Beschriftung im Trenner.
RECHTSSEITEN = [
    (SEITE / "impressum.html", "impressum", "Zweite Seite"),
    (SEITE / "datenschutz.html", "datenschutz", "Dritte Seite"),
]

VERWEIS = '<link rel="stylesheet" href="stil.css">'

WARNUNG = """<!-- ERZEUGT — NICHT BEARBEITEN.
     Diese Datei entsteht aus studie/seite/ durch `python3 studie/bauen.py`.
     Jede Änderung hier ist beim nächsten Bau wieder weg. Sie existiert nur,
     damit eine Vorschau alle drei Seiten in einer einzigen Datei zeigen
     kann. Auf dem Hosting liegen sie getrennt. -->
"""

TRENNER = """
<div class="vorschau-trenner" id="{marke}">
  <span>{beschriftung} · <b>{titel}</b></span>
  <span>Auf dem Hosting eine eigene Adresse: <code>{datei}</code></span>
</div>
"""

# Nur für die Vorschau: der Streifen zwischen den angehängten Seiten und
# die Sprungmarken-Korrektur. Auf der echten Website gibt es beides nicht.
VORSCHAU_STIL = """
<style>
.vorschau-trenner{display:flex;flex-wrap:wrap;gap:.4rem 1.5rem;
 justify-content:space-between;align-items:baseline;
 background:var(--band-2);color:var(--band-gedaempft);
 font-family:var(--mono);font-size:11px;letter-spacing:.08em;
 text-transform:uppercase;padding:1rem var(--rand);
 border-top:2px solid var(--signal);scroll-margin-top:var(--kopf-h)}
.vorschau-trenner b{color:var(--signal)}
.vorschau-trenner code{text-transform:none;letter-spacing:0}
@media print{.vorschau-trenner{break-before:page;background:#fff;color:#000}}
</style>
"""


def hauptteil(html: str) -> str:
    """Holt <main>…</main> aus einer Seite. Kopf und Fuß fallen weg."""
    treffer = re.search(r"<main\b.*?</main>", html, re.S)
    if not treffer:
        raise SystemExit("Kein <main> gefunden — Seitengerüst geändert?")
    return treffer.group(0)


def titel(html: str) -> str:
    treffer = re.search(r"<title>(.*?)</title>", html, re.S)
    return treffer.group(1).split("·")[0].strip() if treffer else "Seite"


def main() -> None:
    html = START.read_text(encoding="utf-8")
    if VERWEIS not in html:
        raise SystemExit(f"{VERWEIS} fehlt in {START.name}.")

    stil = STIL.read_text(encoding="utf-8")
    html = html.replace(VERWEIS, f"<style>\n{stil}</style>" + VORSCHAU_STIL)

    # Die beiden Rechtsseiten vor die Fußzeile hängen.
    anhang = ""
    for datei, marke, beschriftung in RECHTSSEITEN:
        roh = datei.read_text(encoding="utf-8")
        anhang += TRENNER.format(marke=marke, beschriftung=beschriftung,
                                 titel=titel(roh), datei=datei.name)
        anhang += hauptteil(roh) + "\n"

    fuss = html.index('<footer class="fuss">')
    html = html[:fuss] + anhang + "\n" + html[fuss:]

    # In der Vorschau liegt alles in einer Datei, also führen die Verweise
    # auf Sprungmarken statt auf Dateien.
    for datei, marke, _ in RECHTSSEITEN:
        html = html.replace(f'href="{datei.name}"', f'href="#{marke}"')
    html = html.replace('href="index.html#', 'href="#')
    html = html.replace('href="index.html"', 'href="#oben"')

    ZIEL.write_text(WARNUNG + html, encoding="utf-8")
    print(f"{ZIEL.name} — {len(WARNUNG + html) // 1024} KB, "
          f"{1 + len(RECHTSSEITEN)} Seiten in einer Datei")


if __name__ == "__main__":
    main()
