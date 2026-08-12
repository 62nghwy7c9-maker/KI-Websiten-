"""Prüfkatalog — die Schwellwerte und Texte, nach denen gemessen und bewertet wird.

Die Werte hier sind Startwerte, keine Festlegung (siehe Konzept, Abschnitt 3).
Korrekturen gehören ins Lernprotokoll KORREKTUREN-GELERNT.md und von dort hierher.

Der Katalog ist bewusst reine Datenstruktur ohne Logik: Er wird von der Messung
gelesen (welche Werte hole ich?) und von der Befundbildung (ab wann ist es ein
Befund?). Wer eine Schwelle ändert, ändert nur diese Datei.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# ── Grenzwerte ───────────────────────────────────────────────────────────────

TIMEOUT_SEKUNDEN = 15
"""Ab hier gilt eine Seite als nicht erreichbar (Prüfpunkt 1)."""

LCP_SCHLECHT_MS = 4000
"""Google Core Web Vitals: über 4,0 s gilt als schlecht. Erzeugt einen Befund."""

LCP_MITTEL_MS = 2500
"""Bis 2,5 s gilt als gut. Zwischen 2500 und 4000 nur nennen, wenn sonst zu wenig
Befunde vorliegen — siehe NUR_BEI_ZU_WENIG_BEFUNDEN."""

BESCHREIBUNG_MIN_ZEICHEN = 50
BESCHREIBUNG_MAX_ZEICHEN = 160

MOBIL_BREITE_PX = 390
"""Referenzbreite für den Test auf horizontales Scrollen (Prüfpunkt 3)."""

QUALIFIKATION_AB_BEFUNDEN = 3
"""Ab so vielen belegten Befunden lohnt sich der Kandidat."""

MAX_BEFUNDE_AUF_CHECK = 4
"""Präsentationsdeckel. Auch wenn mehr belegt sind."""

# Titel, die ein unbearbeiteter Baukasten hinterlässt (Prüfpunkt 11).
TITEL_VORLAGENWERTE = {
    "startseite", "home", "willkommen", "start", "unbenannt", "neue seite",
    "untitled", "my site", "meine website", "website", "homepage",
    "index", "new page", "seite ohne titel",
}

# Baukasten-Hosts (Prüfpunkt 13). Liste wächst über das Lernprotokoll.
BAUKASTEN_HOSTS = (
    "wixsite.com", "wix.com", "jimdosite.com", "jimdo.com", "jimdofree.com",
    "business.site", "metro.bar", "weebly.com", "webnode.", "beepworld.de",
    "npage.de", "jouwweb.", "strikingly.com", "square.site", "godaddysites.com",
    "myshopify.com", "wordpress.com", "blogspot.", "webflow.io", "netlify.app",
    "vercel.app", "github.io", "site123.me", "ionos.space", "1and1-editor.",
)

# Hinweise auf unbearbeiteten Vorlagentext (Prüfpunkt 15).
PLATZHALTER_MUSTER = (
    "lorem ipsum", "your text here", "beispieltext", "mustertext",
    "hier steht ihr text", "platzhalter", "dummy text", "text hier einfügen",
    "insert your text", "example.com", "max mustermann", "musterstadt",
    "ihr text hier", "lorem", "tempor incididunt",
)

# Linktexte, die auf eine Karriereseite zeigen (Prüfpunkt 9).
KARRIERE_WOERTER = ("karriere", "jobs", "stellen", "stellenangebot", "wir suchen",
                    "arbeiten bei", "bewerbung", "mitarbeiter gesucht", "team werden")

# Linktexte/Pfade, die auf ein Impressum zeigen (Prüfpunkt 7).
IMPRESSUM_WOERTER = ("impressum", "anbieterkennzeichnung", "legal-notice")


@dataclass(frozen=True)
class Pruefpunkt:
    """Ein Eintrag des Prüfkatalogs."""

    nr: int
    name: str
    """Bezeichnung, wie sie im Befund und im Check erscheint."""
    schweregrad: int
    """1 bis 3. Bestimmt die Sortierung der vier Befunde auf dem Check."""
    automatisch: bool
    """False = braucht eine Sichtprüfung durch einen Menschen."""
    ausloeser: str
    """Wann ein Befund entsteht — in einem Satz, für die Nachvollziehbarkeit."""
    branche: str | None = None
    """None = branchenübergreifend. Sonst 'gastro', 'handwerk', 'verein'."""
    erzeugt_befund: bool = True
    """False = wird gemessen, ist aber nie allein ein Befund (8, 10)."""
    nur_bei_zu_wenig_befunden: bool = False
    """True = nur aufnehmen, wenn sonst weniger als MAX_BEFUNDE_AUF_CHECK vorliegen."""


KATALOG: tuple[Pruefpunkt, ...] = (
    Pruefpunkt(1, "Erreichbarkeit", 3, True,
               f"HTTP-Status 4xx/5xx oder keine Antwort binnen {TIMEOUT_SEKUNDEN} s"),
    Pruefpunkt(2, "HTTPS", 3, True,
               "kein HTTPS, ungültiges oder abgelaufenes Zertifikat, "
               "oder keine Weiterleitung von http auf https"),
    Pruefpunkt(3, "Mobiltauglichkeit", 3, True,
               f"viewport-Angabe fehlt oder die Seite scrollt bei "
               f"{MOBIL_BREITE_PX} px horizontal"),
    Pruefpunkt(4, "Ladezeit mobil", 2, True,
               f"LCP über {LCP_SCHLECHT_MS / 1000:.1f} s (Google: schlecht)"),
    Pruefpunkt(5, "Klickbare Telefonnummer", 2, True,
               "eine Telefonnummer ist sichtbar, aber es gibt keinen tel:-Link"),
    Pruefpunkt(6, "Kontaktweg", 3, True,
               "weder Formular noch mailto: noch tel: in zwei Klicks erreichbar"),
    Pruefpunkt(7, "Impressum", 3, True,
               "Impressumsseite fehlt oder Name, Anschrift oder Kontaktweg fehlt"),
    Pruefpunkt(8, "Aktualität", 1, False,
               "nicht objektiv messbar — nur als Zusatz zu einem anderen Befund",
               erzeugt_befund=False),
    Pruefpunkt(9, "Karriereseite", 2, True,
               "kein Link auf Karriere, Jobs oder Stellen", branche="handwerk"),
    Pruefpunkt(10, "Formular", 1, True,
               "weder Formular noch mailto: vorhanden — sonst kein eigener Befund",
               erzeugt_befund=False),
    Pruefpunkt(11, "Seitentitel", 2, True,
               "title fehlt, ist leer oder trägt einen Vorlagenwert"),
    Pruefpunkt(12, "Meta-Description", 2, True,
               f"fehlt oder kürzer als {BESCHREIBUNG_MIN_ZEICHEN} Zeichen"),
    Pruefpunkt(13, "Eigene Domain", 3, True,
               "die Seite läuft auf einer Baukasten-Adresse statt auf eigener Domain"),
    Pruefpunkt(14, "Google-Unternehmensprofil", 3, False,
               "kein Profil, oder Adresse und Telefon weichen von der Website ab"),
    Pruefpunkt(15, "Platzhalter- und Fremdtext", 2, False,
               "sichtbarer Vorlagen- oder fremdsprachiger Text auf der Seite"),
    Pruefpunkt(20, "Speisekarte als Text", 3, False,
               "die Karte ist nur als Bild oder PDF eingebunden", branche="gastro"),
    Pruefpunkt(21, "Bestell- oder Anfrageweg", 2, True,
               "kein Weg, eine Bestellung oder Catering-Anfrage zu senden",
               branche="gastro"),
    Pruefpunkt(22, "Bewerbungsweg", 2, True,
               "Karriereseite vorhanden, aber kein Formular und keine Mailadresse",
               branche="handwerk"),
    Pruefpunkt(23, "Weg zur Mitgliedschaft", 2, False,
               "weder Formular noch benannter Ansprechpartner", branche="verein"),
)

NACH_NR: dict[int, Pruefpunkt] = {p.nr: p for p in KATALOG}


def fuer_branche(branche: str | None) -> tuple[Pruefpunkt, ...]:
    """Kernpunkte plus die Zusatzpunkte der angegebenen Branche."""
    b = (branche or "").strip().lower()
    return tuple(p for p in KATALOG if p.branche is None or p.branche == b)
