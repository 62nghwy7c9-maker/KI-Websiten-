"""Liest die Prosa der Kundenseite aus einer schlichten Textdatei.

Die Fakten stehen in ``stammdaten.json``, die Saetze in ``texte.md``. Die
Trennung ist keine Schoenheit, sondern eine Frage der Herkunft: Fakten kommen
vom Betrieb und muessen stimmen, Saetze schreiben wir und muessen zum Betrieb
passen. Beides in einer Datei zu mischen fuehrt dazu, dass beim Umformulieren
eine Rufnummer verrutscht.

Das Format ist absichtlich klein genug, dass Kira es lesen und aendern kann,
ohne HTML zu koennen:

    # aufmacher
    marke: Elektro- und Gebaeudesystemtechnik . Bergheim
    h1: Elektroinstallation fuer Gewerbe, Kommunen und Privat.
    einleitung: Acht Mitarbeiter, die gesamte Breite der Technik.

    # band
    8 | Mitarbeiter im Betrieb
    Nachts und am Wochenende | Wartung ohne Betriebsstillstand

    # leistungen
    marke: Leistungen
    h2: Die gesamte Breite der Elektroinstallation
    vorspann: Was hier nicht steht, fragen Sie einfach.

    ## Gebaeude und Anlagen
    - Schaltschrankbau
    - SPS-Steuerungen

    # echeck
    marke: E-Check
    h2: Die Pruefung, die Ihre Versicherung anerkennt

    Ein gewoehnlicher Absatz.

    ! Ein Absatz, der hervorgehoben wird.

``# aufmacher``, ``# band`` und ``# kontakt`` haben eine feste Bedeutung.
Jeder andere Abschnitt wird zu einem Abschnitt der Seite, in der Reihenfolge,
in der er hier steht. Die Navigation im Kopf entsteht daraus.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Zeilen mit dieser Form sind Angaben, keine Prosa: ``marke: Leistungen``.
ANGABE = re.compile(r"^([a-z][a-z0-9_]*)\s*:\s*(.*)$")


@dataclass
class Gruppe:
    """Eine Ueberschrift mit einer Liste darunter, etwa eine Leistungsgruppe."""
    titel: str
    punkte: list[str] = field(default_factory=list)


@dataclass
class Abschnitt:
    name: str
    angaben: dict[str, str] = field(default_factory=dict)
    absaetze: list[tuple[str, str]] = field(default_factory=list)  # (art, text)
    gruppen: list[Gruppe] = field(default_factory=list)
    zeilen: list[tuple[str, str]] = field(default_factory=list)    # fuer das Band

    def __getitem__(self, feld: str) -> str:
        return self.angaben.get(feld, "")

    @property
    def beschriftung(self) -> str:
        """Was im Menue steht. ``nav:`` schlaegt ``marke:``."""
        return self["nav"] or self["marke"] or self.name.capitalize()


def lesen(pfad: Path) -> list[Abschnitt]:
    text = Path(pfad).read_text(encoding="utf-8")
    abschnitte: list[Abschnitt] = []
    jetzt: Abschnitt | None = None
    gruppe: Gruppe | None = None
    sammler: list[str] = []
    art = "absatz"

    def absatz_schliessen() -> None:
        nonlocal sammler, art
        if sammler and jetzt is not None:
            jetzt.absaetze.append((art, " ".join(sammler).strip()))
        sammler = []
        art = "absatz"

    for roh in text.splitlines():
        zeile = roh.rstrip()

        if zeile.startswith("# "):
            absatz_schliessen()
            jetzt = Abschnitt(name=zeile[2:].strip().lower())
            abschnitte.append(jetzt)
            gruppe = None
            continue

        if jetzt is None:
            continue  # alles vor dem ersten Abschnitt ist Notiz

        if zeile.startswith("## "):
            absatz_schliessen()
            gruppe = Gruppe(titel=zeile[3:].strip())
            jetzt.gruppen.append(gruppe)
            continue

        if zeile.startswith("- "):
            absatz_schliessen()
            punkt = zeile[2:].strip()
            if gruppe is None:
                gruppe = Gruppe(titel="")
                jetzt.gruppen.append(gruppe)
            gruppe.punkte.append(punkt)
            continue

        if not zeile.strip():
            absatz_schliessen()
            continue

        if "|" in zeile and jetzt.name == "band":
            links, rechts = zeile.split("|", 1)
            jetzt.zeilen.append((links.strip(), rechts.strip()))
            continue

        treffer = ANGABE.match(zeile)
        if treffer and not sammler:
            absatz_schliessen()
            jetzt.angaben[treffer.group(1)] = treffer.group(2).strip()
            continue

        if zeile.startswith("! "):
            absatz_schliessen()
            art = "hinweis"
            sammler.append(zeile[2:].strip())
            continue

        sammler.append(zeile.strip())

    absatz_schliessen()
    return abschnitte


def offene_stellen(abschnitte: list[Abschnitt]) -> list[str]:
    """Sucht, was beim Schreiben stehengeblieben ist.

    Ein ``TODO`` oder eine eckige Klammer im Text ist der haeufigste Weg, auf
    dem ein Entwurf versehentlich live geht. Der Bau bricht daran ab.
    """
    verdaechtig = []
    marken = ("TODO", "TBD", "XXX", "Platzhalter", "Lorem", "...ergaenzen")
    for a in abschnitte:
        stuecke = list(a.angaben.values()) + [t for _, t in a.absaetze]
        stuecke += [g.titel for g in a.gruppen]
        stuecke += [p for g in a.gruppen for p in g.punkte]
        stuecke += [x for paar in a.zeilen for x in paar]
        for s in stuecke:
            if any(m.lower() in s.lower() for m in marken) or re.search(r"\[[^\]]{3,}\]", s):
                verdaechtig.append(f"{a.name}: {s[:60]}")
    return verdaechtig
