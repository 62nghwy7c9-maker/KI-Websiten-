"""Baut die Firmenseite als eine einzige Datei.

Die Schriften liegen als woff2 im Repo Andrys-Advisory- und werden als
data:-URI eingebettet. Grund: Die Seite soll nichts nachladen — weder von
einem CDN noch von Google Fonts. Das ist Datenschutz, Ladezeit und die
Voraussetzung dafür, dass sie in einer Vorschau genauso aussieht wie später
auf dem eigenen Hosting.

    python3 studie/bauen.py
"""
from __future__ import annotations

import base64
from pathlib import Path

ANDRYS = Path("/workspace/andrys-advisory-")
SCHRIFTEN = ANDRYS / "assets/fonts"
KRISTALL = ANDRYS / "assets/js/crystal.js"
VORLAGE = Path(__file__).parent / "firmenseite-vorlage.html"
ZIEL = Path(__file__).parent / "firmenseite.html"


def als_uri(datei: Path) -> str:
    roh = datei.read_bytes()
    return "data:font/woff2;base64," + base64.b64encode(roh).decode("ascii")


def main() -> None:
    ersetzungen = {
        "__SANS__": als_uri(SCHRIFTEN / "hanken-grotesk-latin-wght-normal.woff2"),
        "__MONO400__": als_uri(SCHRIFTEN / "ibm-plex-mono-latin-400-normal.woff2"),
        "__MONO500__": als_uri(SCHRIFTEN / "ibm-plex-mono-latin-500-normal.woff2"),
        # Unverändert übernommen, nicht nachgebaut: Das ist das gebündelte
        # Three.js samt Szene aus dem eigenen Repo. Three.js steht unter MIT.
        "__KRISTALL__": KRISTALL.read_text(encoding="utf-8"),
    }
    html = VORLAGE.read_text(encoding="utf-8")
    for platzhalter, wert in ersetzungen.items():
        if platzhalter not in html:
            raise SystemExit(f"Platzhalter {platzhalter} fehlt in der Vorlage.")
        html = html.replace(platzhalter, wert)
    ZIEL.write_text(html, encoding="utf-8")
    print(f"{ZIEL} — {len(html) // 1024} KB, Schriften eingebettet")


if __name__ == "__main__":
    main()
