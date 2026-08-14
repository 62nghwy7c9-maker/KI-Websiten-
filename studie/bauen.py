"""Baut die Firmenseite als eine einzige Datei.

Die Schriften liegen als woff2 im Repo Andrys-Advisory- und werden als
data:-URI eingebettet. Grund: Die Seite soll nichts nachladen — weder von
einem CDN noch von Google Fonts. Das ist Datenschutz, Ladezeit und die
Voraussetzung dafür, dass sie in einer Vorschau genauso aussieht wie später
auf dem eigenen Hosting.

Die Kristallszene kommt aus demselben Repo. Geometrie, Bewegung und
Scrollkopplung bleiben unangetastet — geändert werden **nur die fünf
Farbstellen**, die im Original kühles Schiefergrau sind. Auf dem warmen
Ocker-Grundton der Seite wirkt dieses Blaugrau fremd; das Regelwerk vom
13.08.2026 schließt Türkis-Grau ausdrücklich aus. Jede Ersetzung wird
unten benannt und beim Bauen geprüft: Fehlt eine Stelle, bricht der Bau ab,
statt still das Original durchzureichen.

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

# Kühles Schiefergrau raus, warmes Ocker rein. Links das Original, rechts
# unsere Fassung — jeweils mit dem, was die Stelle im Bild tut.
KRISTALL_FARBEN: dict[str, str] = {
    # Körper des Kristalls im Licht: helles Blaugrau → gebranntes Ocker
    'uBase:{value:new De("#dfe3ea")}': 'uBase:{value:new De("#D08F3A")}',
    # Körper im Schatten: Schiefer → tiefes Röstbraun
    'uDeep:{value:new De("#8f95a5")}': 'uDeep:{value:new De("#6B3F12")}',
    # Kantenlicht: kaltes Weiß → warmes Cremeweiß
    'uRim:{value:new De("#f7f9fb")}': 'uRim:{value:new De("#FBE6C4")}',
    # Die beiden Drahtgitter-Hüllen: 0x383E4E → 0x8A6A3A (Bronze)
    "color:3685966": "color:9071162",
    # Staubpunkte, die nach oben treiben: blaugrau → warmes Licht
    "vec4(0.714, 0.729, 0.773, a)": "vec4(0.92, 0.80, 0.58, a)",
}


def als_uri(datei: Path) -> str:
    roh = datei.read_bytes()
    return "data:font/woff2;base64," + base64.b64encode(roh).decode("ascii")


def kristall_warm(js: str) -> str:
    """Färbt die Szene um. Bricht ab, wenn eine Stelle fehlt.

    Ohne diese Prüfung würde eine neue Fassung von crystal.js im anderen
    Repo dazu führen, dass wieder das kalte Original ausgeliefert wird —
    und niemand würde es merken, bis es jemand ansieht.
    """
    for alt, neu in KRISTALL_FARBEN.items():
        anzahl = js.count(alt)
        if anzahl == 0:
            raise SystemExit(
                f"Farbstelle nicht gefunden: {alt}\n"
                "crystal.js hat sich geändert — Farben von Hand nachziehen.")
        js = js.replace(alt, neu)
    return js


def main() -> None:
    ersetzungen = {
        "__SANS__": als_uri(SCHRIFTEN / "hanken-grotesk-latin-wght-normal.woff2"),
        "__MONO400__": als_uri(SCHRIFTEN / "ibm-plex-mono-latin-400-normal.woff2"),
        "__MONO500__": als_uri(SCHRIFTEN / "ibm-plex-mono-latin-500-normal.woff2"),
        # Three.js steht unter MIT. Übernommen wird das gebündelte Skript,
        # umgefärbt werden nur die Stellen aus KRISTALL_FARBEN.
        "__KRISTALL__": kristall_warm(KRISTALL.read_text(encoding="utf-8")),
    }
    html = VORLAGE.read_text(encoding="utf-8")
    for platzhalter, wert in ersetzungen.items():
        if platzhalter not in html:
            raise SystemExit(f"Platzhalter {platzhalter} fehlt in der Vorlage.")
        html = html.replace(platzhalter, wert)
    ZIEL.write_text(html, encoding="utf-8")
    print(f"{ZIEL} — {len(html) // 1024} KB, Schriften eingebettet, "
          f"{len(KRISTALL_FARBEN)} Farbstellen umgefärbt")


if __name__ == "__main__":
    main()
