"""Die Gestaltung eines Betriebs aus seiner Bestandsseite lesen.

`farbe.py` holt die Akzentfarbe. Das reicht nicht: Elf Checks, die sich nur in
einer Farbe unterscheiden, sehen alle gleich aus — und zwar nach Vorlage. Was
ein Dokument einem Betrieb zuordnet, ist vor allem die **Schrift**, danach die
Formensprache (eckig oder rund) und erst dann die Farbe.

Gelesen werden deshalb:

- **Schriftfamilie** — der stärkste Wiedererkennungswert. Ein Betrieb mit
  Serifenschrift und einer mit geometrischer Grotesk wirken vollkommen
  verschieden, selbst bei gleicher Farbe.
- **Rundung** — `border-radius`. Manche Seiten sind durchgehend eckig, andere
  weich. Das prägt den Eindruck mehr als man denkt.
- **Zweitfarbe** — für Linien und Flächen, damit nicht alles in einem Ton liegt.

Weiterhin **nie das Logo** (Konzept, Entscheidung D3).

Grenze der Ehrlichkeit: Eine Webschrift, die der Betrieb nachlädt, lässt sich
auf einem gedruckten Blatt nicht garantieren. Übernommen wird deshalb die
**Kategorie** — Serif bleibt Serif, Grotesk bleibt Grotesk — mit dem
Originalnamen an erster Stelle. Wer die Schrift installiert hat, sieht sie;
alle anderen sehen etwas aus derselben Familie statt etwas Fremdes.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .farbe import (SAETTIGUNG_GEDECKT, SAETTIGUNG_KRAEFTIG, STANDARD_AKZENT,
                    STANDARD_TEXT, Farbwelt, _als_rgb, _helligkeit, _hex,
                    _saettigung)

FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;}{]+)", re.I)
RADIUS = re.compile(r"border-radius\s*:\s*([0-9.]+)(px|rem|em)", re.I)

# Schriften, die nichts über den Betrieb aussagen: Sie stehen in jeder
# Vorlage und in jedem Zurücksetz-Stylesheet.
NICHTSSAGEND = {
    "inherit", "initial", "unset", "sans-serif", "serif", "monospace",
    "system-ui", "-apple-system", "blinkmacsystemfont", "arial", "helvetica",
    "helvetica neue", "segoe ui", "roboto", "ui-sans-serif", "ui-serif",
    "sans", "tahoma", "verdana", "icons", "fontawesome", "font awesome 5 free",
    "glyphicons halflings", "swiper-icons", "revicons", "star", "dashicons",
    "eicons", "elementor-icons", "etmodules", "et-modules", "themify",
    "simple-line-icons", "ionicons", "material icons", "feather",
}

SERIFEN = ("georgia", "times", "garamond", "merriweather", "playfair", "lora",
           "pt serif", "source serif", "crimson", "libre baskerville", "cambria",
           "droid serif", "noto serif", "roboto slab", "rockwell", "slab",
           "book antiqua", "palatino", "spectral", "cormorant", "bitter")

# Druckfeste Stapel je Kategorie. Der Originalname wird davorgesetzt.
STAPEL_SERIF = '"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif'
STAPEL_GROTESK = '"Segoe UI", -apple-system, Roboto, "Helvetica Neue", Arial, sans-serif'


@dataclass(frozen=True)
class Stilprobe:
    """Wie der Betrieb selbst gestaltet — soweit aus seiner Seite ablesbar."""

    akzent: str = STANDARD_AKZENT
    zweit: str = ""
    """Zweite Farbe für Linien und Flächen. Leer = aus dem Akzent ableiten."""
    text: str = STANDARD_TEXT
    schrift: str = STAPEL_GROTESK
    schrift_name: str = ""
    """Der auf der Seite gefundene Name, für die Herkunftsangabe."""
    serif: bool = False
    radius: str = "0"
    herkunft: str = "Standard (auf der Seite nichts Brauchbares gefunden)"

    @property
    def uebernommen(self) -> bool:
        return bool(self.schrift_name) or self.akzent != STANDARD_AKZENT

    @property
    def beschreibung(self) -> str:
        teile = []
        if self.schrift_name:
            teile.append(f"Schrift {self.schrift_name}")
        if self.akzent != STANDARD_AKZENT:
            teile.append(f"Farbe {self.akzent}")
        if self.radius != "0":
            teile.append(f"Rundung {self.radius}")
        return ", ".join(teile) or "keine Vorgaben erkennbar"


VERDAECHTIG = ("font awesome", "fontawesome", "icon", "glyph", "symbol",
               "courier", "consolas", "menlo", "monaco", "mono", "webding",
               "wingding")
"""Namensbestandteile, die eine Schrift als Symbol- oder Codeschrift ausweisen.

Symbolschriften stehen in fast jedem Baukasten-Stylesheet und kommen dort
häufiger vor als die Hausschrift. Courier und Konsorten stammen aus
Code-Bausteinen. Beides als Hausschrift zu übernehmen sähe schlicht falsch aus.
"""


def _schriftname(css: str) -> str | None:
    """Die häufigste aussagekräftige Schriftfamilie im Stylesheet."""
    zaehler: Counter[str] = Counter()
    for treffer in FONT_FAMILY.findall(css):
        for teil in treffer.split(","):
            name = teil.strip().strip("\"'").strip()
            if not name or name.lower() in NICHTSSAGEND:
                continue
            klein = name.lower()
            if name.startswith("var(") or len(name) > 40:
                continue
            if any(v in klein for v in VERDAECHTIG):
                continue
            zaehler[name] += 1
            break  # nur die erste echte Familie je Deklaration
    if not zaehler:
        return None
    name, anzahl = zaehler.most_common(1)[0]
    return name if anzahl >= 2 else None


def _radius(css: str) -> str:
    """Die häufigste Rundung. 50% (Kreise) wird ignoriert — das sind Symbole."""
    zaehler: Counter[str] = Counter()
    for wert, einheit in RADIUS.findall(css):
        try:
            zahl = float(wert)
        except ValueError:
            continue
        if zahl <= 0 or (einheit == "px" and zahl > 24):
            continue
        zaehler[f"{wert.rstrip('.0') or '0'}{einheit}"] += 1
    if not zaehler:
        return "0"
    wert, anzahl = zaehler.most_common(1)[0]
    return wert if anzahl >= 3 else "0"


def _zweitfarbe(text: str, akzent: str) -> str:
    """Eine zweite kräftige Farbe, die sich vom Akzent unterscheidet."""
    von_akzent = _als_rgb(akzent)
    zaehler: Counter[tuple[int, int, int]] = Counter()
    for treffer in re.findall(r"#([0-9a-fA-F]{6})\b", text):
        rgb = _als_rgb("#" + treffer)
        if rgb:
            zaehler[rgb] += 1
    for rgb, anzahl in zaehler.most_common(30):
        if anzahl < 3 or not von_akzent:
            continue
        if _saettigung(rgb) < SAETTIGUNG_GEDECKT or not (25 <= _helligkeit(rgb) <= 210):
            continue
        # Deutlich anders als der Akzent, sonst wirkt es wie ein Zufallston.
        if sum(abs(a - b) for a, b in zip(rgb, von_akzent)) > 120:
            return _hex(rgb)
    return ""


def ableiten(html: str, css: list[str] | None = None) -> Stilprobe:
    """Liest Schrift, Rundung und Farben aus Quelltext und Stylesheets."""
    from .farbe import ableiten as farbe_ableiten

    alles = html + "\n" + "\n".join(css or [])
    farbwelt: Farbwelt = farbe_ableiten(html, css)

    name = _schriftname(alles)
    serif = bool(name and any(s in name.lower() for s in SERIFEN))
    if name:
        stapel = (f'"{name}", ' + (STAPEL_SERIF if serif else STAPEL_GROTESK))
    else:
        stapel = STAPEL_GROTESK

    herkunft = []
    if name:
        herkunft.append(f"Schrift „{name}“ von der Bestandsseite")
    if farbwelt.uebernommen:
        herkunft.append(farbwelt.herkunft)

    return Stilprobe(
        akzent=farbwelt.akzent,
        zweit=_zweitfarbe(alles, farbwelt.akzent),
        text=farbwelt.text,
        schrift=stapel,
        schrift_name=name or "",
        serif=serif,
        radius=_radius(alles),
        herkunft="; ".join(herkunft) or
                 "Standard (auf der Seite nichts Brauchbares gefunden)",
    )
