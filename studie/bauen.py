"""Baut aus der Startseite eine einzelne Datei für die Vorschau.

Die echte Website liegt in `studie/seite/` und besteht aus drei Seiten mit
einem gemeinsamen Stylesheet — so wie sie später auf dem Hosting liegt. Der
Stil steht damit einmal da, nicht dreimal.

Eine Vorschau kann aber nur eine einzige Datei zeigen. Deshalb erzeugt
dieses Skript `studie/firmenseite.html`: dieselbe Startseite, nur mit dem
Stylesheet hineinkopiert. Diese Datei wird **nicht** von Hand bearbeitet —
Änderungen gehören nach `studie/seite/`.

    python3 studie/bauen.py
"""
from __future__ import annotations

from pathlib import Path

SEITE = Path(__file__).parent / "seite"
QUELLE = SEITE / "index.html"
STIL = SEITE / "stil.css"
ZIEL = Path(__file__).parent / "firmenseite.html"

VERWEIS = '<link rel="stylesheet" href="stil.css">'

WARNUNG = """<!-- ERZEUGT — NICHT BEARBEITEN.
     Diese Datei entsteht aus studie/seite/index.html und studie/seite/stil.css
     durch `python3 studie/bauen.py`. Jede Änderung hier ist beim nächsten Bau
     wieder weg. Sie existiert nur, damit die Vorschau eine einzelne Datei
     laden kann. -->
"""


def main() -> None:
    html = QUELLE.read_text(encoding="utf-8")
    if VERWEIS not in html:
        raise SystemExit(f"{VERWEIS} fehlt in {QUELLE.name}.")

    # Die Verweise auf die Nachbarseiten zeigen im Einzeldatei-Bau ins Leere.
    # Das ist gewollt und sichtbar: Die Vorschau ist die Startseite, nicht
    # die ganze Website.
    stil = STIL.read_text(encoding="utf-8")
    html = html.replace(VERWEIS, f"<style>\n{stil}</style>")
    ZIEL.write_text(WARNUNG + html, encoding="utf-8")

    print(f"{ZIEL.name} — {len(WARNUNG + html) // 1024} KB "
          f"(Startseite {QUELLE.stat().st_size // 1024} KB "
          f"+ Stil {STIL.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
