"""Stufe 2 — aus Rohmessungen werden Befunde.

Zwei Regeln, die im Konzept getrennt sind und hier getrennt bleiben:

- **Qualifikation**: ab QUALIFIKATION_AB_BEFUNDEN belegten Befunden auf der
  vollen Messung lohnt sich der Kandidat.
- **Präsentationsdeckel**: auf den Check kommen höchstens MAX_BEFUNDE_AUF_CHECK.

Und die harte Regel aus dem Konzept: **ohne Beleg kein Kosten-Satz.** Ein Befund
ohne belegte Quelle wird trotzdem gezeigt — aber nur mit der Beobachtung, ohne
die Folgen-Behauptung. Das ist in TEXTE technisch erzwungen: Wo `beleg` leer ist,
wird `was_es_kostet` beim Bauen verworfen.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import katalog as K
from .modelle import Befund, Messwert, Pruefbericht

# ── Belegquellen ─────────────────────────────────────────────────────────────

ABRUF = "eigener Abruf der Seite am {stand}"
"""Für Aussagen, die der Empfänger selbst nachsehen kann. Der stärkste Beleg."""

CWV = ("Google, Core Web Vitals: LCP bis 2,5 s gut, über 4,0 s schlecht "
       "(web.dev/articles/lcp)")
DDG = "§ 5 DDG (Impressumspflicht für geschäftliche Websites)"


@dataclass(frozen=True)
class Text:
    """Die Formulierung eines Befunds für den Check.

    `beobachtung` ist eine neutrale Tatsache — sie steht immer.
    `was_es_kostet` ist die Folge — sie steht nur, wenn `beleg` gefüllt ist.
    """

    titel: str
    beobachtung: str
    was_es_kostet: str = ""
    beleg: str = ""
    behebbarkeit: str = "hoch"


# Anrede: der Check spricht den Inhaber mit „Ihre Seite" an, nicht in Fachsprache.
TEXTE: dict[int, Text] = {
    1: Text(
        "Die Seite ist nicht erreichbar",
        "Beim Aufruf Ihrer Adresse antwortet der Server nicht bzw. mit einer "
        "Fehlermeldung ({wert}).",
        "Wer Ihre Adresse eingibt oder aus Google kommt, landet auf einer "
        "Fehlerseite und ist weg.",
        ABRUF,
    ),
    2: Text(
        "Keine sichere Verbindung",
        "Ihre Seite ist nicht durchgängig verschlüsselt erreichbar ({wert}).",
        "Gängige Browser zeigen davor eine Warnung an. Viele Besucher brechen "
        "an dieser Stelle ab.",
        ABRUF,
    ),
    3: Text(
        "Nicht für Handys eingerichtet",
        "Im Quelltext Ihrer Seite fehlt die Angabe, wie sie auf kleinen "
        "Bildschirmen dargestellt werden soll.",
        "Auf dem Handy erscheint die Seite verkleinert; man muss zoomen und "
        "schieben, um etwas zu lesen.",
        ABRUF,
    ),
    4: Text(
        "Lange Ladezeit auf dem Handy",
        "Der größte sichtbare Bereich Ihrer Seite erscheint auf dem Handy erst "
        "nach {wert}.",
        "Google bewertet alles über 4 Sekunden als schlecht — das wirkt sich auf "
        "die Platzierung in der Trefferliste aus.",
        CWV,
    ),
    5: Text(
        "Telefonnummer nicht antippbar",
        "Ihre Telefonnummer steht als Text auf der Seite, ist aber nicht als "
        "Anruf-Link hinterlegt ({wert}).",
        "Auf dem Handy kann man sie nicht antippen, um anzurufen — die Nummer "
        "muss abgetippt werden.",
        ABRUF,
    ),
    6: Text(
        "Kein klarer Kontaktweg",
        "Auf Ihrer Startseite ist weder ein Formular noch eine E-Mail-Adresse "
        "noch eine anrufbare Nummer hinterlegt.",
        "Wer Sie anfragen möchte, findet auf Anhieb keinen Weg dazu.",
        ABRUF,
    ),
    7: Text(
        "Impressum unvollständig oder widersprüchlich",
        "{wert}.",
        "Ein fehlerhaftes Impressum ist in Deutschland abmahnfähig. Und wer an "
        "die falsche Adresse schreibt, erreicht Sie nicht.",
        DDG,
    ),
    9: Text(
        "Keine Seite für Stellenangebote",
        "Auf Ihrer Website gibt es keinen Bereich für Karriere, Jobs oder "
        "offene Stellen.",
        "Wer bei Ihnen arbeiten möchte, findet keinen Weg, sich zu bewerben.",
        ABRUF,
    ),
    11: Text(
        "Seitentitel fehlt oder ist ein Vorlagenwert",
        "Der Titel Ihrer Seite lautet {wert}.",
        "Genau dieser Text steht als Überschrift in der Google-Trefferliste — "
        "dort sollte Ihr Betriebsname stehen.",
        ABRUF,
    ),
    12: Text(
        "Keine Beschreibung für Google",
        "Ihre Seite hat keine hinterlegte Kurzbeschreibung ({wert}).",
        "",  # bewusst leer: siehe BELEG_OFFEN
        "",
    ),
    13: Text(
        "Fremde Adresse statt eigener Domain",
        "Ihre Seite läuft unter {wert} statt unter einer eigenen Adresse.",
        "",  # bewusst leer: siehe BELEG_OFFEN
        "",
    ),
    15: Text(
        "Vorlagentext auf der Seite",
        "Auf Ihrer Seite steht sichtbar unbearbeiteter Vorlagentext ({wert}).",
        "Das wirkt ungepflegt — Besucher zweifeln an der Sorgfalt, bevor sie "
        "Ihre Arbeit kennen.",
        ABRUF,
    ),
    20: Text(
        "Speisekarte nicht als Text",
        "Ihre Karte ist als Bild bzw. PDF eingebunden, nicht als lesbarer Text "
        "({wert}).",
        "",  # bewusst leer: siehe BELEG_OFFEN
        "",
    ),
    21: Text(
        "Kein Bestell- oder Anfrageweg",
        "Es gibt keinen Weg, eine Bestellung aufzugeben oder eine Anfrage für "
        "Catering zu senden.",
        "Jede Bestellung bindet jemanden am Telefon.",
        ABRUF,
    ),
    22: Text(
        "Kein Bewerbungsweg",
        "Ihre Karriereseite nennt keine Möglichkeit, sich zu bewerben — weder "
        "Formular noch E-Mail-Adresse.",
        "Wer sich bewerben will, muss selbst herausfinden, an wen.",
        ABRUF,
    ),
}

BELEG_OFFEN: dict[int, str] = {
    12: "Dass eine fehlende Beschreibung die Google-Vorschau verschlechtert, ist "
        "plausibel, aber hier nicht gegen eine Primärquelle geprüft. Bis dahin "
        "steht im Check nur die Beobachtung.",
    13: "Dass eine Baukasten-Adresse schlechter rankt oder weniger seriös wirkt, "
        "ist eine verbreitete Behauptung ohne belegte Quelle. Nicht verwenden, "
        "bis geprüft.",
    20: "Dass Google Gerichte aus einem Bild nicht lesen kann, ist technisch "
        "richtig; die Folge für die Auffindbarkeit ist nicht beziffert. "
        "Formulierung erst mit Quelle aufnehmen.",
}
"""Prüfpunkte, deren Kosten-Satz noch keine belegte Quelle hat (D7).

Der Befund erscheint trotzdem auf dem Check — nur ohne den Folgen-Satz. Wer eine
Quelle findet, trägt sie in TEXTE ein und löscht den Eintrag hier.
"""


def _fuellen(vorlage: str, messwert: Messwert, stand: str) -> str:
    return vorlage.format(wert=messwert.wert, stand=stand).replace("  ", " ").strip()


def bilden(bericht: Pruefbericht) -> Pruefbericht:
    """Wandelt die Messwerte des Berichts in Befunde und wählt die für den Check.

    Verändert den Bericht an Ort und Stelle und gibt ihn zurück.
    """
    bericht.befunde = []
    ohne_beleg: list[str] = []

    for mw in bericht.messung:
        if mw.ok is not False:
            continue  # nur echte Auslöser, nie ein Verdacht
        punkt = K.NACH_NR.get(mw.id)
        if punkt is None or not punkt.erzeugt_befund:
            continue
        text = TEXTE.get(mw.id)
        if text is None:
            continue

        hat_beleg = bool(text.beleg)
        if not hat_beleg:
            ohne_beleg.append(punkt.name)

        bericht.befunde.append(Befund(
            id=mw.id,
            titel=text.titel,
            beobachtung=_fuellen(text.beobachtung, mw, bericht.stand),
            # Ohne Beleg kein Satz — hier wird die Regel erzwungen, nicht erinnert.
            was_es_kostet=_fuellen(text.was_es_kostet, mw, bericht.stand)
            if hat_beleg else "",
            beleg=text.beleg.format(stand=bericht.stand) if hat_beleg else "",
            schweregrad=punkt.schweregrad,
            behebbarkeit=text.behebbarkeit,
        ))

    bericht.qualifiziert = len(bericht.befunde) >= K.QUALIFIKATION_AB_BEFUNDEN
    bericht.auswahl_fuer_check = [b.id for b in auswaehlen(bericht.befunde)]

    if ohne_beleg:
        bericht.hinweise.append(
            "Ohne belegten Kosten-Satz und deshalb nur als Beobachtung im Check: "
            + ", ".join(sorted(set(ohne_beleg)))
            + ". Quelle suchen oder so belassen.")
    return bericht


_GEWICHT_BEHEBBARKEIT = {"hoch": 3, "mittel": 2, "niedrig": 1}


def auswaehlen(befunde: list[Befund],
               deckel: int = K.MAX_BEFUNDE_AUF_CHECK) -> list[Befund]:
    """Die stärksten Befunde für den Check, höchstens `deckel` Stück.

    Sortiert nach Schweregrad, bei Gleichstand nach Behebbarkeit — also zuerst
    die Punkte, die das Standardpaket ohnehin löst. Ein Befund mit belegtem
    Kosten-Satz schlägt bei sonst gleichem Rang einen ohne, weil er auf dem
    Check mehr trägt.
    """
    geordnet = sorted(
        befunde,
        key=lambda b: (b.schweregrad,
                       _GEWICHT_BEHEBBARKEIT.get(b.behebbarkeit, 0),
                       bool(b.beleg)),
        reverse=True,
    )
    return geordnet[:deckel]
