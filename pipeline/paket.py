"""Ein Ordner je Betrieb — alles, was für ein Gespräch gebraucht wird.

    kunden/<slug>/
      befund.md          Zusammenfassung zum Überfliegen, auch auf dem Handy
      check.html         Kundencheck zum Ausdrucken und Übergeben
      dossier.html       interne Übersicht mit allen Prüfpunkten
      anschreiben.md     Entwurf für den Brief, zum Überschreiben
      messung.json       Rohmessung, maschinenlesbar

Der Ordnername folgt `Kandidat.schluessel()` und ist damit derselbe, den auch
das Kontakt-Register benutzt — Ort, Firma und Domain, kleingeschrieben. So
findet man denselben Betrieb in beiden Ablagen wieder.

Warum ein Ordner statt fünf Dateien nebeneinander: Vor einem Besuch braucht man
alles zu *einem* Betrieb. Nach fünfzig Betrieben ist eine flache Ablage
unbrauchbar.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import anschreiben as A
from . import katalog as K
from .befunde import auswaehlen
from .check import Absender
from .check import schreiben as check_schreiben
from .dossier import schreiben as dossier_schreiben
from .farbe import Farbwelt
from .modelle import Pruefbericht

STANDARD_ORDNER = Path("kunden")


@dataclass
class Paket:
    ordner: Path
    dateien: list[Path]
    firma: str
    befunde: int
    qualifiziert: bool


def _befund_md(bericht: Pruefbericht, farbe: Farbwelt) -> str:
    """Die Kurzfassung. Für den Blick aufs Handy kurz vor dem Klingeln."""
    k = bericht.kandidat
    gewaehlt = auswaehlen(bericht.befunde)
    offen = [m for m in bericht.messung if m.ok is None]

    zeilen = [f"# {k.firma}", ""]
    if k.inhaber:
        zeilen.append(f"**Ansprechpartner:** {k.inhaber}  ")
    if k.telefon:
        zeilen.append(f"**Telefon:** {k.telefon}  ")
    if k.kontakt_mail:
        zeilen.append(f"**E-Mail:** {k.kontakt_mail}  ")
    if k.ort:
        zeilen.append(f"**Ort:** {k.ort}  ")
    zeilen += [f"**Website:** {k.url}  ",
               f"**Gemessen am:** {bericht.stand}", ""]

    zeilen.append(
        f"**{len(bericht.befunde)} Befunde belegt.** "
        + ("Qualifiziert allein aus der Automatik."
           if bericht.qualifiziert
           else f"Noch nicht qualifiziert ({K.QUALIFIKATION_AB_BEFUNDEN} nötig) "
                f"— die {len(offen)} offenen Punkte entscheiden."))
    zeilen.append("")

    zeilen.append("## Auf dem Check")
    for i, b in enumerate(gewaehlt, 1):
        zeilen.append(f"{i}. **{b.titel}** — {b.beobachtung}")
        if b.was_es_kostet:
            zeilen.append(f"   *Was es kostet:* {b.was_es_kostet}")
        else:
            zeilen.append("   *(kein Kosten-Satz — Beleg fehlt)*")
    zeilen.append("")

    rest = [b for b in bericht.befunde if b not in gewaehlt]
    if rest:
        zeilen.append("## Belegt, aber nicht auf dem Check")
        zeilen += [f"- {b.titel} — {b.beobachtung}" for b in rest]
        zeilen.append("")

    if bericht.hinweise:
        zeilen.append("## Von Hand nachsehen")
        zeilen += [f"- {h}" for h in bericht.hinweise]
        zeilen.append("")

    zeilen.append("## Gestaltung")
    zeilen.append(f"Akzentfarbe `{farbe.akzent}` — {farbe.herkunft}.")
    zeilen.append("")
    zeilen.append("---")
    zeilen.append("*Erzeugt von der Check-Pipeline. Nichts hiervon ist versendet.*")
    return "\n".join(zeilen) + "\n"


def bauen(bericht: Pruefbericht, absender: Absender, farbe: Farbwelt,
          wurzel: Path = STANDARD_ORDNER) -> Paket:
    """Legt den Ordner für einen Betrieb an und füllt ihn."""
    ordner = Path(wurzel) / bericht.kandidat.schluessel()
    ordner.mkdir(parents=True, exist_ok=True)
    gewaehlt = auswaehlen(bericht.befunde)

    dateien = [
        bericht.speichern(ordner),
        check_schreiben(bericht, absender, ordner, farbe),
        dossier_schreiben(bericht, ordner, farbe.akzent),
        A.schreiben(bericht, absender.name, absender.telefon, gewaehlt, ordner),
    ]
    befund = ordner / "befund.md"
    befund.write_text(_befund_md(bericht, farbe), encoding="utf-8")
    dateien.append(befund)

    # Im Ordner des Betriebs ist der Name schon gesagt: check.html statt
    # check_kerpen_galabau-markus-lindam_lindam-galabau.de.html. Die Schreiber
    # oben kennen den Ordner nicht und benennen nach dem Schlüssel; hier wird
    # gekürzt, damit die Ablage lesbar bleibt.
    schluessel = bericht.kandidat.schluessel()
    for i, pfad in enumerate(dateien):
        kurz = {f"{schluessel}.json": "messung.json",
                f"check_{schluessel}.html": "check.html",
                f"dossier_{schluessel}.html": "dossier.html"}.get(pfad.name)
        if kurz:
            ziel = ordner / kurz
            pfad.replace(ziel)
            dateien[i] = ziel

    return Paket(ordner=ordner, dateien=sorted(dateien),
                 firma=bericht.kandidat.firma,
                 befunde=len(bericht.befunde),
                 qualifiziert=bericht.qualifiziert)
