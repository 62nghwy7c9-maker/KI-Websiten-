"""Die Papiere, die der Betrieb in die Hand bekommt.

Vier Dokumente, alle aus derselben Quelle wie die Website. Damit koennen sie
nicht auseinanderlaufen: Steht im Impressum eine neue Rufnummer, steht sie
auch auf dem Freigabeblatt.

  ANLEITUNG       Wie er seine Seite selbst pflegt. Zum Ausdrucken.
  CHECKLISTE      Unser Ablauf zum Abhaken, von der Datei bis zur Uebergabe.
  LIVEGANG        Die Domainumstellung, Schritt fuer Schritt.
  FREIGABEBLATT   Was er unterschreibt, bevor an der Domain gedreht wird.

Ein fuenftes Papier entsteht hier absichtlich nicht: LIESMICH.md haelt fest,
woher die Inhalte dieses einen Entwurfs stammen und was daran noch offen ist.
Das ist bei jedem Betrieb etwas anderes und laesst sich nicht aus Feldern
zusammensetzen. Es wird von Hand geschrieben, sonst entstuende ein Dokument,
das aussieht wie eine Herkunftsangabe, aber keine ist.

Das Passwort kommt in keinem dieser Papiere vor. Es wird muendlich uebergeben.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .drucken import nach_html
from .stammdaten import Stammdaten
from .vorlagen import fuellen, offene_platzhalter

VORLAGE = Path("studie/pflege/vorlage/papiere")

# Datei, Titel der Druckfassung, und ob eine Druckfassung ueberhaupt sinnvoll
# ist. Die Checkliste arbeiten wir am Bildschirm ab, das Freigabeblatt geht
# als Papier zum Kunden.
PAPIERE = (
    ("ANLEITUNG.md", "Ihre Website pflegen", True),
    ("CHECKLISTE.md", "Schritt für Schritt", True),
    ("LIVEGANG.md", "Livegang", True),
    ("FREIGABEBLATT.md", "Freigabe", True),
)


@dataclass
class Ergebnis:
    dateien: list[Path]
    fehlend: list[str]


def bauen(ordner: Path, wurzel: Path = Path("."), heute: date | None = None) -> Ergebnis:
    ordner = Path(ordner)
    daten = Stammdaten.laden(ordner)
    tag = heute or date.today()

    werte = {f: daten[f] for f in daten.bestaetigt}
    werte.update({
        "kurzname": daten.kurzname,
        "telefon_wahl": daten.telefon_wahl,
        "anschrift": daten.anschrift,
        "stand": tag.strftime("%d.%m.%Y"),
        "stand_iso": tag.isoformat(),
        # Woher die Oeffnungszeiten stammen, wenn nicht von der alten Seite.
        # Steht nichts da, fragt das Freigabeblatt sie einfach ohne Herkunft ab.
        "zeiten_herkunft": daten.bestaetigt.get("zeiten_herkunft", ""),
    })

    gebaut: list[Path] = []
    fehlend: list[str] = []
    for name, titel, drucken in PAPIERE:
        vorlage = wurzel / VORLAGE / name
        if not vorlage.is_file():
            fehlend.append(name)
            continue
        text = fuellen(vorlage.read_text(encoding="utf-8"), werte)
        rest = offene_platzhalter(text)
        if rest:
            raise SystemExit(f"In {name} blieben Platzhalter stehen: "
                             + ", ".join(rest))
        md = ordner / name
        md.write_text(text, encoding="utf-8")
        gebaut.append(md)
        if drucken:
            htm = ordner / (Path(name).stem + ".html")
            htm.write_text(nach_html(text, f"{daten['firma']} · {titel}"),
                           encoding="utf-8")
            gebaut.append(htm)

    return Ergebnis(gebaut, fehlend)
