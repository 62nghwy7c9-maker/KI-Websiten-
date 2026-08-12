"""Datenmodell der Pipeline — der Vertrag zwischen den Stufen.

Das Format ist eingefroren (CLAUDE.md, Abschnitt 5). Wer es ändert, ändert alle
Stufen. `schemas/befund.schema.json` beschreibt dieselbe Struktur maschinenlesbar.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

ROUTEN = ("neu", "pruefung", "freigabe", "versendet", "abgelehnt")
"""Zustände eines Kandidaten. Entspricht dem route-Feld der Belegpipeline."""


@dataclass
class Kandidat:
    firma: str
    url: str
    branche: str = ""
    ort: str = ""
    kontakt_mail: str = ""
    telefon: str = ""
    anschrift: str = ""
    inhaber: str = ""
    """Ansprechpartner aus der Lead-Liste. Nachträglich ergänzt, deshalb optional —
    ältere Rohmessungen bleiben lesbar."""
    gewerk: str = ""
    """Das Gewerk im Wortlaut der Lead-Liste — „Elektro", „SHK", „GaLaBau".

    `branche` fasst alles zu „handwerk" zusammen, weil der Prüfkatalog nicht
    feiner unterscheidet. Für die Gestaltung ist der Unterschied aber
    entscheidend: Ein Elektrobetrieb und ein Gartenbaubetrieb treten
    grundverschieden auf."""

    def schluessel(self) -> str:
        """Stabiler Schlüssel für Dedup und Dateinamen."""
        from .register import normhost, slug
        return f"{slug(self.ort)}_{slug(self.firma)}_{normhost(self.url)}"


@dataclass
class Messwert:
    """Eine Rohmessung. Enthält keine Bewertung — nur, was gemessen wurde."""

    id: int
    pruefpunkt: str
    wert: str
    """Menschenlesbar, so wie es später im Check zitiert werden könnte."""
    quelle: str
    """Womit gemessen: 'HTTP', 'HTML', 'TLS', 'PageSpeed Insights', 'manuell'."""
    auto: bool = True
    ok: bool | None = None
    """True = unauffällig, False = Auslöser erfüllt, None = nicht bestimmbar."""
    roh: dict = field(default_factory=dict)
    """Rohdaten für Nachvollzug und spätere Regeln. Nie im Check verwenden."""


@dataclass
class Befund:
    """Ein belegter Mangel. Entsteht in Stufe 2 aus Messwerten."""

    id: int
    titel: str
    beobachtung: str
    """Neutrale Tatsache. Keine Wertung."""
    was_es_kostet: str = ""
    """Konsequenz. Nur mit `beleg` befüllen — ohne Beleg kein Satz."""
    beleg: str = ""
    schweregrad: int = 1
    behebbarkeit: str = "hoch"


@dataclass
class Pruefbericht:
    """Ausgabe von Stufe 1 und 2. Ein Bericht je Kandidat."""

    kandidat: Kandidat
    stand: str = field(default_factory=lambda: date.today().isoformat())
    messung: list[Messwert] = field(default_factory=list)
    befunde: list[Befund] = field(default_factory=list)
    qualifiziert: bool = False
    auswahl_fuer_check: list[int] = field(default_factory=list)
    hinweise: list[str] = field(default_factory=list)
    """Was nicht gemessen werden konnte und warum. Wird nie verschwiegen."""

    def als_dict(self) -> dict:
        return asdict(self)

    def speichern(self, ordner: Path) -> Path:
        ordner.mkdir(parents=True, exist_ok=True)
        ziel = ordner / f"{self.kandidat.schluessel()}.json"
        ziel.write_text(
            json.dumps(self.als_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return ziel

    @staticmethod
    def laden(pfad: Path) -> "Pruefbericht":
        d = json.loads(Path(pfad).read_text(encoding="utf-8"))
        return Pruefbericht(
            kandidat=Kandidat(**d["kandidat"]),
            stand=d.get("stand", ""),
            messung=[Messwert(**m) for m in d.get("messung", [])],
            befunde=[Befund(**b) for b in d.get("befunde", [])],
            qualifiziert=d.get("qualifiziert", False),
            auswahl_fuer_check=d.get("auswahl_fuer_check", []),
            hinweise=d.get("hinweise", []),
        )
