"""Stufe 4 — der Anschreiben-Entwurf.

Vorgabe aus CLAUDE.md, Abschnitt 5: kurz, konkreter Bezug zum Betrieb, Check als
Beilage, **genau ein** Handlungsaufruf, neutraler Ton, kein Umsatzversprechen,
kein Preis.

Zwei Dinge, die dieses Modul bewusst *nicht* tut:

- **Es versendet nichts.** Es schreibt eine Datei. Der Freigabe-Gate ist, dass
  ein Mensch sie liest, bevor irgendetwas passiert.
- **Es formuliert keine E-Mail für den Erstkontakt.** Kalte Werbemails an
  Betriebe brauchen nach § 7 Abs. 2 Nr. 2 UWG eine Einwilligung, auch im B2B
  (Konzept, Abschnitt 12). Der Entwurf ist ein **Brief**. Die Mailfassung
  entsteht erst nach einem Telefonat und steht deshalb hier nur als kurzer
  Baustein, ausdrücklich als Antwort gekennzeichnet.

Der Entwurf ist Markdown und zum Überschreiben gedacht. Ein Anschreiben, das
klingt wie von einem Programm erzeugt, ist schlechter als drei handgeschriebene
Sätze — die Vorlage nimmt nur die leere Seite weg.
"""
from __future__ import annotations

from pathlib import Path

from .modelle import Befund, Pruefbericht

# Der Aufhänger: ein Satz, der zeigt, dass jemand hingesehen hat. Er wird aus
# dem stärksten Befund gebildet, weil genau der den Betrieb betrifft — nicht aus
# einer Floskel, die für jeden Betrieb gleich klingt.
HOOKS: dict[int, str] = {
    1: "Ihre Website war bei meinem Aufruf nicht erreichbar",
    2: "Ihre Website öffnet sich derzeit mit einer Sicherheitswarnung",
    3: "Ihre Website ist auf dem Handy schwer zu lesen",
    4: "Ihre Website braucht auf dem Handy auffällig lange zum Laden",
    5: "Ihre Telefonnummer lässt sich auf dem Handy nicht antippen",
    6: "auf Ihrer Startseite habe ich keinen direkten Weg gefunden, Sie zu erreichen",
    7: "in Ihrem Impressum ist mir eine Kleinigkeit aufgefallen, die Ärger machen kann",
    8: "die jüngste Spur auf Ihrer Website stammt aus {jahr}",
    9: "auf Ihrer Website habe ich keine Seite für offene Stellen gefunden",
    10: "auf Ihrer Website gibt es kein Formular für Anfragen",
    11: "in der Google-Trefferliste steht bei Ihnen nicht Ihr Betriebsname",
    12: "Google zeigt zu Ihrer Website keine Beschreibung an",
    13: "Ihre Website läuft nicht unter einer eigenen Adresse",
    15: "auf Ihrer Website steht noch unbearbeiteter Vorlagentext",
}

STANDARD_HOOK = "mir sind ein paar Dinge an Ihrer Website aufgefallen"


def _hook(befunde: list[Befund], sucht: str = "") -> str:
    """Der erste Satz. Eine belegte offene Stelle schlägt jeden Mangel.

    Ein technischer Mangel interessiert einen Meister mäßig — er hat seit
    Jahren damit gelebt. Eine unbesetzte Stelle kostet ihn jeden Monat Geld,
    und das weiß er. Wenn wir belegen können, dass er sucht, ist das der
    einzige Satz, der ihn beim ersten Blick auf das Blatt hält.

    Entscheidend ist die Form: **Feststellung, keine Frage.** „Sie suchen
    einen Elektriker" ist etwas, das wir gesehen haben und zeigen können.
    „Suchen Sie Personal?" wäre eine Verkaufsfrage — und die erkennt jeder,
    der schon einmal Post von einer Agentur bekommen hat.
    """
    if sucht.strip():
        return f"Sie suchen {sucht.strip()}"
    for b in befunde:
        if b.id in HOOKS:
            jahr = b.beobachtung.split()[-1].rstrip(".")
            return HOOKS[b.id].format(jahr=jahr)
    return STANDARD_HOOK


GESPRAECHSFRAGEN = (
    ("Wie lange suchen Sie schon jemanden?",
     "Monate mal Deckungsbeitrag eines Gesellen. Die Zahl kennt er, wir nicht."),
    ("Wie viele Anfragen lehnen Sie im Monat ab, weil Leute fehlen?",
     "Macht die unbesetzte Stelle in Aufträgen sichtbar."),
    ("Woher kam Ihr letzter Bewerber?",
     "Meist über Bekannte. Dann ist die Frage, was passiert, wenn dieser "
     "Kanal versiegt."),
)
"""Die drei Fragen aus Konzept 3.1 — bewusst **nicht** im Anschreiben.

Ihr ganzer Wert liegt darin, dass der Betrieb selbst rechnet: Er nennt die
Monate, er kennt den Deckungsbeitrag, die Zahl ist am Ende seine. Auf Papier
kann er nicht antworten. Dort wird aus jeder Frage eine rhetorische, und
rhetorische Fragen in kalter Post liest jeder als das, was sie sind.

Sie stehen deshalb unten in der Gesprächsnotiz — damit sie beim Telefonat
und im Vorgespräch auf dem Tisch liegen, wo sie wirken.
"""


def _anrede(inhaber: str) -> str:
    """Persönliche Anrede nur, wenn der Name belegt ist.

    Geraten wird nicht: Ein falsch angesprochener Inhaber ist schlimmer als
    eine neutrale Anrede. Die Anrede selbst bleibt bewusst offen — ob „Herr"
    oder „Frau" passt, entscheidet der Mensch beim Durchsehen, nicht das
    Programm anhand des Vornamens.
    """
    if not inhaber.strip():
        return "Sehr geehrte Damen und Herren,"
    nachname = inhaber.strip().split()[-1]
    return f"Sehr geehrte/r Frau/Herr {nachname},   ← Anrede prüfen"


def _stellennotiz(k) -> str:
    """Zeile über die belegte offene Stelle — oder der Hinweis, dass sie fehlt.

    Steht in der internen Notiz, nie auf dem Check. Fehlt der Beleg, sagt die
    Notiz das offen: Dann darf im Gespräch auch nicht behauptet werden, der
    Betrieb suche jemanden.
    """
    if k.sucht.strip() and k.sucht_beleg.strip():
        return (f"\n**Belegte offene Stelle:** {k.sucht.strip()} "
                f"— gefunden über {k.sucht_beleg.strip()}. "
                "Damit beginnt das Anschreiben.\n")
    return ("\n**Keine offene Stelle belegt.** Vor dem Anruf zwei Minuten "
            "suchen: Google, Indeed, Handwerkskammer, Fahrzeugbeschriftung. "
            "Wird etwas gefunden, `sucht` und `sucht_beleg` eintragen und den "
            "Brief neu erzeugen — der Aufhänger wird dadurch deutlich "
            "stärker. Ohne Fund wird nichts behauptet.\n")


def _einstieg(k, gewaehlt: list[Befund], punkte: str) -> str:
    """Die beiden ersten Sätze. Zwei Fassungen, je nach Beleglage.

    Mit belegter offener Stelle führt der Brief damit — und stellt die
    Verbindung zur Website her, statt sie zu behaupten. Ohne Beleg bleibt es
    beim Mangel als Aufhänger.
    """
    if k.sucht.strip() and k.sucht_beleg.strip():
        return (
            f"Sie suchen {k.sucht.strip()} — das habe ich gesehen "
            f"({k.sucht_beleg.strip()}). Auf Ihrer Website findet ein "
            "Bewerber davon nichts.\n\n"
            "Ich habe mir die Seite deshalb einmal angesehen und "
            f"{punkte} aufgeschrieben, die einem Bewerber im Weg stehen. "
            "Der Check liegt bei; jeden Punkt können Sie selbst nachprüfen."
        )
    return (
        f"ich habe mir Ihre Website angesehen — {_hook(gewaehlt)}.\n\n"
        "Weil das schnell behoben ist und Sie vermutlich Wichtigeres zu tun "
        f"haben, habe ich {punkte} aufgeschrieben und lege Ihnen den Check "
        "bei. Jeden Punkt können Sie selbst nachprüfen."
    )


def bauen(bericht: Pruefbericht, absender_name: str, absender_telefon: str,
          gewaehlt: list[Befund]) -> str:
    k = bericht.kandidat
    anzahl = len(gewaehlt)
    punkte = "einen Punkt" if anzahl == 1 else f"{anzahl} Punkte"

    return f"""# Anschreiben-Entwurf — {k.firma}

> **Entwurf. Nichts ist versendet.** Vor dem Verschicken lesen und in eigene
> Worte bringen. Als **Brief**, nicht als E-Mail (§ 7 Abs. 2 Nr. 2 UWG,
> Konzept Abschnitt 12).

**An:** {k.firma}{f", {k.inhaber}" if k.inhaber else ""}{f" · {k.ort}" if k.ort else ""}
**Beilage:** Website-Check, {anzahl} {'Punkt' if anzahl == 1 else 'Punkte'}
**Geprüfte Seite:** {k.url}

---

{_anrede(k.inhaber)}

{_einstieg(k, gewaehlt, punkte)}

Falls Sie darüber sprechen möchten: {absender_telefon}. Zehn Minuten reichen.

Mit freundlichen Grüßen
{absender_name}

---

## Wenn er sich meldet — Kurzfassung für die Antwortmail

*Erst nach einem Telefonat oder einer Rückmeldung verwenden. Nicht für den
Erstkontakt.*

> Guten Tag {k.inhaber.split()[-1] if k.inhaber else ""},
>
> wie besprochen im Anhang der Website-Check für {k.firma}.
> Bei Fragen erreichen Sie mich unter {absender_telefon}.

## Notiz für das Gespräch

Diese Punkte stehen auf dem Check:

{chr(10).join(f"{i}. **{b.titel}** — {b.beobachtung}" for i, b in enumerate(gewaehlt, 1))}
{_stellennotiz(k)}
### Die drei Fragen — im Gespräch stellen, nicht auf Papier

Sie gehören nicht ins Anschreiben. Ihr Wert liegt darin, dass der Betrieb
selbst rechnet: Er nennt die Monate, er kennt den Deckungsbeitrag, die Zahl
ist am Ende **seine**. Auf Papier kann er nicht antworten — dort wird aus
jeder Frage eine rhetorische.

{chr(10).join(f'{i}. **„{f}"** — {w}' for i, (f, w) in enumerate(GESPRAECHSFRAGEN, 1))}

Nicht abhaken wie einen Fragebogen. Eine Frage stellen, zuhören, die Zahl
stehen lassen. Wer selbst ausrechnet, dass ihn eine unbesetzte Stelle im Jahr
fünfstellig kostet, braucht kein Verkaufsargument mehr.

Kein Preis auf dem Check und kein Preis im ersten Satz. Erst fragen, wie viele
Mitarbeiter der Betrieb hat — danach eine Zahl nennen (Konzept, Abschnitt 4).
"""


def schreiben(bericht: Pruefbericht, absender_name: str, absender_telefon: str,
              gewaehlt: list[Befund], ordner: Path) -> Path:
    ordner.mkdir(parents=True, exist_ok=True)
    ziel = ordner / "anschreiben.md"
    ziel.write_text(
        bauen(bericht, absender_name, absender_telefon, gewaehlt),
        encoding="utf-8")
    return ziel
