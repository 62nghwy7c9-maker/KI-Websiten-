"""Farbwelt des Kunden aus seiner Bestandsseite ableiten.

Entscheidung aus dem Konzept: Der Check nimmt Farbe und Anmutung des Betriebs
auf, **aber nie dessen Logo**. Damit wirkt er zugeschnitten, ohne die rechtlich
heikelste Frage zu berühren.

Gesucht werden zwei Farben — eine kräftige Akzentfarbe und eine dunkle für
Text. Wenn nichts Brauchbares zu finden ist, bleibt es beim neutralen Standard;
geraten wird nicht.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from urllib.parse import urljoin

HEX3 = re.compile(r"#([0-9a-fA-F]{3})\b")
HEX6 = re.compile(r"#([0-9a-fA-F]{6})\b")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})")
THEME = re.compile(
    r"""<meta[^>]+name=["']theme-color["'][^>]+content=["']([^"']+)""", re.I)

SAETTIGUNG_KRAEFTIG = 40
"""Ab hier gilt eine Farbe als Markenfarbe."""
SAETTIGUNG_GEDECKT = 15
"""Ab hier noch als gedeckte Hausfarbe brauchbar — Schiefergrau, Graublau."""

STANDARD_AKZENT = "#4F5F3E"
"""Neutraler Standard, wenn die Seite nichts hergibt."""
STANDARD_TEXT = "#16150F"


@dataclass(frozen=True)
class Farbwelt:
    akzent: str = STANDARD_AKZENT
    text: str = STANDARD_TEXT
    herkunft: str = "Standard (auf der Seite nichts Brauchbares gefunden)"

    @property
    def uebernommen(self) -> bool:
        return self.akzent != STANDARD_AKZENT


def _als_rgb(wert: str) -> tuple[int, int, int] | None:
    w = wert.strip()
    if m := HEX6.fullmatch(w) or HEX6.match(w):
        h = m.group(1)
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    if m := HEX3.fullmatch(w) or HEX3.match(w):
        h = m.group(1)
        return tuple(int(c * 2, 16) for c in h)  # type: ignore[return-value]
    if m := RGB.match(w):
        r, g, b = (min(255, int(x)) for x in m.groups())
        return r, g, b
    return None


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def _helligkeit(rgb: tuple[int, int, int]) -> float:
    """Wahrgenommene Helligkeit 0..255 (Rec. 601)."""
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def _saettigung(rgb: tuple[int, int, int]) -> int:
    return max(rgb) - min(rgb)


def _taugt_als_akzent(rgb: tuple[int, int, int]) -> bool:
    """Kräftig genug, um als Akzent zu tragen, und dunkel genug für weiße Schrift.

    Grau, Weiß und Schwarz fallen raus — sie sagen nichts über die Marke aus.
    Sehr helle Farben ebenfalls: Auf dem gedruckten Check muss weiße Schrift
    darauf lesbar bleiben.
    """
    return (_saettigung(rgb) >= SAETTIGUNG_KRAEFTIG
            and 25 <= _helligkeit(rgb) <= 190)


STYLESHEET = re.compile(
    r"""<link[^>]+rel=["']?stylesheet["']?[^>]*>""", re.I)
HREF = re.compile(r"""href=["']([^"']+)["']""", re.I)


def stylesheets_von(html: str, basis_url: str, hole, grenze: int = 3) -> list[str]:
    """Lädt die verlinkten Stylesheets einer Seite.

    Ohne sie findet die Farbsuche fast nichts: Betriebsseiten definieren ihre
    Farben so gut wie immer in einer eigenen CSS-Datei, nicht im HTML. `hole`
    wird übergeben statt importiert, damit dieses Modul netzfrei testbar bleibt.
    """
    texte: list[str] = []
    for tag in STYLESHEET.findall(html)[:grenze]:
        m = HREF.search(tag)
        if not m:
            continue
        try:
            abruf = hole(urljoin(basis_url, m.group(1)))
        except Exception:
            continue
        if getattr(abruf, "html", ""):
            texte.append(abruf.html)
    return texte


def ableiten(html: str, css: list[str] | None = None) -> Farbwelt:
    """Zieht die Farbwelt aus Quelltext und Stylesheets der Bestandsseite."""
    if css:
        html = html + "\n" + "\n".join(css)
    if m := THEME.search(html):
        rgb = _als_rgb(m.group(1))
        if rgb and _taugt_als_akzent(rgb):
            return Farbwelt(_hex(rgb), STANDARD_TEXT,
                            "theme-color der Bestandsseite")

    zaehler: Counter[tuple[int, int, int]] = Counter()
    for treffer in HEX6.findall(html):
        rgb = _als_rgb("#" + treffer)
        if rgb:
            zaehler[rgb] += 1
    for treffer in HEX3.findall(html):
        rgb = _als_rgb("#" + treffer)
        if rgb:
            zaehler[rgb] += 1
    for r, g, b in RGB.findall(html):
        zaehler[(min(255, int(r)), min(255, int(g)), min(255, int(b)))] += 1

    def beste(mindest_saettigung: int) -> tuple[int, tuple[int, int, int]] | None:
        kandidaten = [(n, rgb) for rgb, n in zaehler.items()
                      if _saettigung(rgb) >= mindest_saettigung
                      and 25 <= _helligkeit(rgb) <= 190]
        if not kandidaten:
            return None
        # Häufigkeit entscheidet, bei Gleichstand die kräftigere Farbe.
        kandidaten.sort(key=lambda t: (t[0], _saettigung(t[1])), reverse=True)
        # Ein einzelnes Vorkommen ist Zufall, keine Markenfarbe.
        return kandidaten[0] if kandidaten[0][0] >= 3 else None

    if treffer := beste(SAETTIGUNG_KRAEFTIG):
        anzahl, akzent = treffer
        return Farbwelt(_hex(akzent), STANDARD_TEXT,
                        f"häufigste kräftige Farbe der Bestandsseite ({anzahl}×)")

    # Zweite Stufe: Viele Handwerksseiten haben gar keine kräftige Hausfarbe,
    # sondern ein gedecktes Grau-Blau. Das ist trotzdem ihre Anmutung — näher
    # dran als der neutrale Standard, der von einem fremden Betrieb stammt.
    if treffer := beste(SAETTIGUNG_GEDECKT):
        anzahl, akzent = treffer
        return Farbwelt(_hex(akzent), STANDARD_TEXT,
                        f"gedeckte Hausfarbe der Bestandsseite ({anzahl}×)")

    return Farbwelt()
