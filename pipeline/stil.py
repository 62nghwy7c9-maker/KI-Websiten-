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


# ── Intuition, wenn die Bestandsseite nichts hergibt ─────────────────────────
#
# Fünf der elf geprüften Betriebe haben schlicht keine Hausschrift — ihre Seiten
# benutzen Arial. Dann bleibt die Wahl zwischen einem neutralen Standard, der
# für alle gleich aussieht, und einer begründeten Annahme. Diese Tabelle ist die
# Annahme, und sie ist als solche gekennzeichnet: `herkunft` sagt es, und
# befund.md zeigt es an.
#
# Alle Schriften sind auf Windows und macOS vorhanden. Eine schöne Webschrift
# nützt nichts, wenn das Blatt beim Ausdrucken auf Arial zurückfällt.

@dataclass(frozen=True)
class Anmutung:
    schrift: str
    akzent: str
    serif: bool
    radius: str
    begruendung: str


GEWERKE_ANMUTUNG: tuple[tuple[tuple[str, ...], Anmutung], ...] = (
    (("elektro", "elektrik", "elektrotechnik"), Anmutung(
        '"Corbel", "Franklin Gothic Book", "Segoe UI", sans-serif',
        "#1F3A5F", False, "0",
        "Elektro: technisch und präzise — schmale, sachliche Grotesk, "
        "eckige Kanten, tiefes Blau")),
    (("shk", "sanitär", "sanitaer", "heizung", "klima", "installat"), Anmutung(
        '"Candara", "Corbel", "Segoe UI", sans-serif',
        "#17607A", False, "3px",
        "SHK: solide und zugewandt — humanistische Grotesk, leicht gerundet, "
        "Stahlblau")),
    (("galabau", "garten", "landschaft"), Anmutung(
        '"Constantia", "Cambria", Georgia, serif',
        "#3E6B47", True, "4px",
        "Garten- und Landschaftsbau: gewachsen statt technisch — Serifenschrift, "
        "weiche Ecken, Grün")),
    (("maler", "lackier", "stuck", "raumaus"), Anmutung(
        '"Century Gothic", "Questrial", "Segoe UI", sans-serif',
        "#A65A2E", False, "0",
        "Maler: gestalterisches Gewerk — geometrische Grotesk, Terrakotta")),
    (("fenster", "tür", "tuer", "bau", "zimmer", "dach", "tischler",
      "schreiner"), Anmutung(
        '"Rockwell", "Cambria", Georgia, serif',
        "#5A5148", True, "0",
        "Bau und Ausbau: handfest — Slab-Serif mit kräftigen Strichen, "
        "warmes Braungrau")),
)

TRADITION = Anmutung(
    '"Palatino Linotype", "Book Antiqua", Georgia, serif',
    "#3C4A3E", True, "0",
    "Traditionsbetrieb: die Bestandsseite ist erkennbar alt, der Betrieb "
    "besteht lange — ruhige Antiqua statt moderner Grotesk")

STANDARD_ANMUTUNG = Anmutung(
    STAPEL_GROTESK, STANDARD_AKZENT, False, "0",
    "Gewerk nicht zuzuordnen — neutraler Standard")


def _anmutung(gewerk: str, konservativ: bool) -> Anmutung:
    """Wählt eine Anmutung aus Gewerk und Alter des Auftritts."""
    g = (gewerk or "").lower()
    for woerter, anmutung in GEWERKE_ANMUTUNG:
        if any(w in g for w in woerter):
            if konservativ:
                # Das Gewerk gibt die Farbe, das Alter die Schrift: Ein
                # jahrzehntealter Betrieb mit Frameset-Seite wirkt mit
                # geometrischer Grotesk verkleidet, nicht getroffen.
                return Anmutung(TRADITION.schrift, anmutung.akzent, True,
                                "0", f"{anmutung.begruendung}; "
                                     f"Auftritt wirkt alteingesessen, deshalb Antiqua")
            return anmutung
    return TRADITION if konservativ else STANDARD_ANMUTUNG


def wirkt_konservativ(bericht) -> bool:
    """Deutet die Messung auf einen alteingesessenen, ruhigen Betrieb hin?

    Bedingung ist eine belegt alte Seite (Prüfpunkt 8); dazu muss mindestens
    ein zweites Merkmal kommen — fehlende Verschlüsselung oder fehlende
    Handytauglichkeit. Zusammen beschreibt das einen Betrieb, der seinen
    Auftritt einmal gemacht und danach gearbeitet hat.
    """
    alt = any(m.id == 8 and m.ok is False for m in bericht.messung)
    if not alt:
        # Ohne belegtes Alter keine Aussage über den Charakter. Eine Seite ohne
        # Verschlüsselung kann auch schlicht schlecht gemacht sein — das sagt
        # nichts darüber, wie der Betrieb auftreten möchte.
        return False
    weiteres = sum(1 for m in bericht.messung
                   if m.id in (2, 3) and m.ok is False)
    return weiteres >= 1


def ergaenzen(probe: Stilprobe, kandidat, bericht) -> Stilprobe:
    """Füllt auf, was die Bestandsseite nicht hergab.

    Ergänzt wird jedes Merkmal einzeln: Wer eine Hausfarbe hat, aber keine
    Hausschrift, behält seine Farbe und bekommt nur die Schrift dazu. Was
    gemessen wurde, hat immer Vorrang vor der Annahme.
    """
    konservativ = wirkt_konservativ(bericht)
    a = _anmutung(kandidat.gewerk or kandidat.branche, konservativ)

    schrift = probe.schrift
    serif = probe.serif
    herkunft = [probe.herkunft] if probe.uebernommen else []

    if not probe.schrift_name:
        schrift, serif = a.schrift, a.serif
        herkunft.append(f"Schrift abgeleitet — {a.begruendung}")

    akzent = probe.akzent
    if akzent == STANDARD_AKZENT:
        akzent = a.akzent
        if probe.schrift_name:  # Begründung stand sonst schon oben
            herkunft.append(f"Farbe abgeleitet — {a.begruendung}")

    return Stilprobe(
        akzent=akzent,
        zweit=probe.zweit,
        text=probe.text,
        schrift=schrift,
        schrift_name=probe.schrift_name,
        serif=serif,
        radius=probe.radius if probe.radius != "0" else a.radius,
        herkunft="; ".join(herkunft) or a.begruendung,
    )
