"""Stufe 3 — der Website-Check als druckfertige HTML-Seite.

Aufbau nach Konzept, Abschnitt 9:
  Seite 1–2  Kopf, Hook, bis zu vier Befunde. Neutral. **Kein Preis.**
  Seite 3    Ausblick, Preisrahmen, genau ein Handlungsaufruf.

Ausgabe ist HTML mit Druck-Stylesheet. Im Browser öffnen, Strg+P, als PDF
speichern — kein zusätzliches Werkzeug nötig, und was am Bildschirm steht, steht
auch auf dem Papier.

Solange die Absenderangaben Platzhalter enthalten, trägt der Check oben einen
roten Sperrbalken. Er lässt sich ansehen, aber nicht versehentlich übergeben.
"""
from __future__ import annotations

import html
import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from . import katalog as K
from .befunde import auswaehlen, positives
from .farbe import Farbwelt
from .modelle import Pruefbericht

STANDARD_ABSENDER = Path("absender.json")


@dataclass
class Absender:
    """Wer den Check überreicht. Ohne vollständige Angaben kein Versand."""

    name: str = "PLATZHALTER — Name eintragen"
    anschrift: str = "PLATZHALTER — Straße, PLZ Ort eintragen"
    telefon: str = "PLATZHALTER — Telefonnummer eintragen"
    mail: str = "PLATZHALTER — geschäftliche E-Mail eintragen"
    preis_hinweis: str = ""
    """Leer lassen = kein Preis auf dem Check. Das ist die Voreinstellung.

    Ein Preis auf einem kalt zugestellten Blatt deckelt, was danach im Gespräch
    noch verlangt werden kann — und zwar bei jedem Betrieb gleich, egal ob er
    zwei oder zwanzig Mitarbeiter hat. Wer hier etwas einträgt, sollte wissen,
    warum. Der Platzhalter-Prüfung unterliegt dieses Feld bewusst nicht.
    """

    @property
    def vollstaendig(self) -> bool:
        return not self.fehlend

    @property
    def fehlend(self) -> list[str]:
        return [f for f, w in asdict(self).items()
                if f != "preis_hinweis" and "PLATZHALTER" in str(w)]

    @staticmethod
    def laden(pfad: Path | str = STANDARD_ABSENDER) -> "Absender":
        p = Path(pfad)
        if not p.exists():
            a = Absender()
            p.write_text(json.dumps(asdict(a), ensure_ascii=False, indent=2),
                         encoding="utf-8")
            return a
        d = json.loads(p.read_text(encoding="utf-8"))
        bekannt = {f.name for f in fields(Absender)}
        return Absender(**{k: v for k, v in d.items() if k in bekannt})


def _e(text: str) -> str:
    return html.escape(text or "", quote=False)


def _stil(farbe: Farbwelt) -> str:
    return f"""
:root{{--akzent:{farbe.akzent};--ink:{farbe.text};--papier:#fff;
 --grau:#5B5A52;--linie:rgba(0,0,0,.14);--warn:#8A3324;
 --sans:"Segoe UI",-apple-system,Roboto,Helvetica,Arial,sans-serif;}}
*{{box-sizing:border-box}}
body{{margin:0;background:#EDEDEA;color:var(--ink);font-family:var(--sans);
 font-size:16px;line-height:1.6}}
.blatt{{max-width:46rem;margin:0 auto;background:var(--papier);
 padding:3.5rem 3rem 3rem;min-height:100vh}}
.sperre{{background:var(--warn);color:#fff;padding:.9rem 1.2rem;margin:0 0 2.5rem;
 font-weight:600;line-height:1.45}}
.sperre small{{display:block;font-weight:400;opacity:.9;margin-top:.3rem}}
.kopf{{border-bottom:4px solid var(--akzent);padding-bottom:1.5rem;margin-bottom:2.2rem}}
.eyebrow{{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;
 color:var(--akzent);font-weight:600;margin:0 0 .7rem}}
h1{{font-size:2.15rem;line-height:1.18;margin:0 0 .55rem;font-weight:700;
 letter-spacing:-.01em}}
.betrieb{{font-size:1.05rem;color:var(--ink);margin:.9rem 0 0;font-weight:600}}
.weitere{{font-size:1.15rem;color:var(--grau);margin:.3rem 0 0}}
.hook{{margin:0 0 2.5rem;font-size:1.02rem}}
.geprueft{{margin:.5rem 0 0;font-size:.86rem;color:var(--grau)}}
.geprueft a{{color:var(--akzent);overflow-wrap:anywhere}}
.bilanz{{margin:0 0 1.6rem;padding:.8rem 0;border-bottom:1px solid var(--linie);
 color:var(--grau);font-size:.95rem}}
.bilanz .zahl{{font-size:1.35rem;font-weight:700;color:var(--ink);
 margin-right:.35rem}}
.bilanz .zahl.akzent{{color:var(--akzent)}}
.bilanz .trenn{{margin:0 .9rem;opacity:.5}}
.gut{{background:#F6F6F3;padding:1.1rem 1.4rem;margin:0 0 2.2rem;
 break-inside:avoid}}
.gut h2{{font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;
 color:var(--grau);margin:0 0 .5rem;font-weight:600}}
.gut ul{{margin:0;padding-left:1.1rem}}
.gut li{{margin-bottom:.2rem}}
h2.abschnitt{{font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;
 color:var(--grau);margin:0 0 1.3rem;font-weight:600}}
.befund{{display:grid;grid-template-columns:2.6rem 1fr;gap:0 1.1rem;
 margin:0 0 2rem;break-inside:avoid}}
.nr{{background:var(--akzent);color:#fff;width:2.3rem;height:2.3rem;border-radius:50%;
 display:flex;align-items:center;justify-content:center;font-weight:700;
 font-size:1.05rem}}
.befund h2{{font-size:1.12rem;margin:.15rem 0 .5rem;font-weight:700;line-height:1.3}}
.befund p{{margin:0 0 .55rem}}
.kostet{{color:var(--grau)}}
.kostet b{{color:var(--ink);font-weight:600}}
.quelle{{font-size:.78rem;color:var(--grau);margin:.35rem 0 0}}
.trenner{{border:none;border-top:1px solid var(--linie);margin:3rem 0 2.2rem}}
.angebot{{background:#F6F6F3;border-left:4px solid var(--akzent);
 padding:1.6rem 1.8rem;margin:0 0 2rem;break-inside:avoid}}
.angebot h2{{margin:0 0 .7rem;font-size:1.25rem}}
.rahmen{{font-size:1.3rem;font-weight:700;color:var(--akzent);margin:1rem 0 .3rem}}
.cta{{margin:1.6rem 0 0;font-weight:600}}
.fuss{{border-top:1px solid var(--linie);margin-top:2.5rem;padding-top:1.1rem;
 font-size:.78rem;color:var(--grau);line-height:1.55}}
@media print{{
 @page{{margin:16mm 15mm}}
 body{{background:#fff;font-size:10.5pt}}
 .blatt{{max-width:none;padding:0;min-height:0}}
 .sperre{{border:2pt solid var(--warn)}}
 .befund,.angebot,.fuss{{break-inside:avoid}}
 .seitenumbruch{{break-before:page}}
}}"""


KOPFZEILEN: dict[int, str] = {
    1: "Ihre Website war beim Aufruf nicht erreichbar",
    2: "Ihre Website öffnet sich mit einer Sicherheitswarnung",
    3: "Ihre Website ist auf dem Handy schwer zu lesen",
    4: "Ihre Website lädt auf dem Handy auffällig langsam",
    5: "Ihre Telefonnummer lässt sich auf dem Handy nicht antippen",
    6: "Auf Ihrer Startseite steht kein Weg, Sie zu erreichen",
    7: "Ihr Impressum ist unvollständig",
    8: "Ihre Website ist seit Jahren unverändert",
    9: "Ihre Website hat keine Seite für offene Stellen",
    10: "Ihre Website hat kein Formular für Anfragen",
    11: "In der Google-Trefferliste steht nicht Ihr Betriebsname",
    12: "Google zeigt zu Ihrer Website keine Beschreibung",
    13: "Ihre Website läuft nicht unter einer eigenen Adresse",
    14: "Ihr Google-Profil und Ihre Website widersprechen sich",
    15: "Auf Ihrer Website steht unbearbeiteter Vorlagentext",
    20: "Ihre Speisekarte ist für Google nicht lesbar",
    21: "Es gibt keinen Weg, bei Ihnen zu bestellen",
    22: "Auf Ihrer Karriereseite fehlt der Bewerbungsweg",
}
"""Der stärkste Befund als Überschrift — je Betrieb ein anderer.

Bewusst **keine** Überschrift wie „4 Punkte, die Sie Kunden kosten". Die bricht
die Belegregel des Konzepts: Jeder Kosten-Satz im Check hat eine Quelle, und
ausgerechnet in der größten Schrift stünde dann die eine Behauptung, die sich
nicht belegen lässt — dass dieser Betrieb Kunden verliert. Ein ausgelasteter
Meister liest das als „der kennt meinen Betrieb nicht" und legt das Blatt weg.

Ein einzelner konkreter Befund lässt sich dagegen nicht bestreiten. Er holt das
Handy heraus und sieht es in fünf Sekunden — und dann ist der Check gelesen.
"""

STANDARD_KOPFZEILE = "Mir sind ein paar Dinge an Ihrer Website aufgefallen"


def _kopfzeile(gewaehlt: list) -> str:
    for b in gewaehlt:
        if b.id in KOPFZEILEN:
            return KOPFZEILEN[b.id]
    return STANDARD_KOPFZEILE


def _kurz(url: str) -> str:
    """Adresse ohne Protokoll und ohne Schrägstrich am Ende — so liest sie sich.

    Der Link selbst bleibt vollständig; angezeigt wird die Form, die der
    Inhaber von seiner Visitenkarte kennt.
    """
    return url.split("//")[-1].rstrip("/")


def bauen(bericht: Pruefbericht, absender: Absender,
          farbe: Farbwelt | None = None, ohne_positives: bool = False) -> str:
    """Baut den Check als HTML. Nimmt höchstens MAX_BEFUNDE_AUF_CHECK Befunde."""
    farbe = farbe or Farbwelt()
    k = bericht.kandidat
    gewaehlt = auswaehlen(bericht.befunde)

    sperre = ""
    if not absender.vollstaendig:
        sperre = (
            '<div class="sperre">Noch nicht versandfertig — Absenderangaben fehlen.'
            f'<small>Offen: {", ".join(absender.fehlend)}. '
            'In absender.json eintragen, dann neu erzeugen.</small></div>')

    geprueft = len(bericht.messung)
    gut = positives(bericht)

    teile = [sperre,
             '<div class="kopf">',
             '<p class="eyebrow">Kostenloser Website-Check</p>',
             f'<h1>{_e(_kopfzeile(gewaehlt))}</h1>',
             (f'<p class="weitere">— und {len(gewaehlt) - 1} weitere '
              f'{"Punkt" if len(gewaehlt) == 2 else "Punkte"}</p>'
              if len(gewaehlt) > 1 else ''),
             f'<p class="betrieb">{_e(k.firma)}'
             + (f', {_e(k.ort)}' if k.ort else '') + '</p>',
             f'<p class="geprueft">Geprüft wurde <a href="{_e(k.url)}">'
             f'{_e(_kurz(k.url))}</a> am {_e(bericht.stand)}.</p>',
             '</div>',
             # Die Zahl vorweg: Sie zeigt, dass ein Katalog abgearbeitet wurde
             # und nicht vier Dinge aufgefallen sind. Das ist der Unterschied
             # zwischen einer Prüfung und einer Meinung.
             '<div class="bilanz">',
             f'<span class="zahl">{geprueft}</span> Punkte geprüft'
             f'<span class="trenn">·</span>'
             f'<span class="zahl akzent">{len(gewaehlt)}</span> mit '
             f'Handlungsbedarf</div>',
             '<p class="hook">Ich prüfe jede Seite nach demselben Katalog. '
             'Was dabei herauskommt, schicke ich Ihnen kostenlos und ohne '
             'Verpflichtung — <b>jeder Punkt ist heute selbst nachprüfbar.</b></p>']

    teile.append('<h2 class="abschnitt">Was ich ändern würde</h2>')

    for i, b in enumerate(gewaehlt, 1):
        teile.append(f'<div class="befund"><div class="nr">{i}</div><div>')
        teile.append(f'<h2>{_e(b.titel)}</h2>')
        teile.append(f'<p>{_e(b.beobachtung)}</p>')
        if b.was_es_kostet:
            teile.append(f'<p class="kostet"><b>Was es kostet:</b> '
                         f'{_e(b.was_es_kostet)}</p>')
            # Der eigene Abruf steht gesammelt in der Fußzeile. Dreimal
            # „Grundlage: eigener Abruf" untereinander liest niemand — eine
            # fremde Quelle dagegen traegt und gehoert direkt an den Satz.
            if not b.beleg.startswith("eigener Abruf"):
                teile.append(f'<p class="quelle">Grundlage: {_e(b.beleg)}</p>')
        teile.append('</div></div>')

    # Der Positivteil steht bewusst *nach* den Mängeln: Das Problem soll zuerst
    # landen. Am Ende belegt er, dass wirklich geprüft wurde, und nimmt dem
    # Blatt den Ton eines Angriffs — ohne den Mängeln Druck zu nehmen.
    if gut and not ohne_positives:
        teile += ['<hr class="trenner">',
                  '<div class="gut"><h2>Was schon gut ist</h2><ul>',
                  "".join(f'<li>{_e(z)}</li>' for z in gut[:2]),
                  '</ul></div>']

    teile += [
        '<hr class="trenner">' if (ohne_positives or not gut) else '',
        '<div class="angebot">',
        '<h2>Der gute Teil: alles behebbar.</h2>',
        '<p>Diese Punkte lassen sich zusammen in einer modernen, mobilen '
        'Website lösen — mit Ihren Inhalten, Ihren Farben und Ihrem Namen.</p>',
        # Voreinstellung: kein Preis. Siehe Absender.preis_hinweis.
        (f'<p class="rahmen">{_e(absender.preis_hinweis)}</p>'
         if absender.preis_hinweis else ''),
        f'<p class="cta">Was das für Ihren Betrieb bedeutet, bespreche ich gern '
        f'in zehn Minuten am Telefon: {_e(absender.telefon)}</p>',
        '</div>',
        '<div class="fuss">',
        f'<b>{_e(absender.name)}</b><br>{_e(absender.anschrift)}<br>'
        f'{_e(absender.telefon)} · {_e(absender.mail)}<br><br>',
        f'Alle Punkte ohne eigene Quellenangabe stammen aus dem Abruf Ihrer '
        f'Website am {_e(bericht.stand)} und sind dort nachprüfbar. '
        f'Dieser Check ist kostenlos und unverbindlich.',
        ('<br>Gestaltung an die Farbwelt des Betriebs angelehnt '
         f'({_e(farbe.herkunft)}).' if farbe.uebernommen else ''),
        '</div>',
    ]

    titel = f"Website-Check {k.firma}"
    return (f'<!doctype html><html lang="de"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{_e(titel)}</title><style>{_stil(farbe)}</style></head>'
            f'<body><div class="blatt">{"".join(teile)}</div></body></html>')


def schreiben(bericht: Pruefbericht, absender: Absender, ordner: Path,
              farbe: Farbwelt | None = None, ohne_positives: bool = False) -> Path:
    ordner.mkdir(parents=True, exist_ok=True)
    ziel = ordner / f"check_{bericht.kandidat.schluessel()}.html"
    ziel.write_text(bauen(bericht, absender, farbe, ohne_positives),
                    encoding="utf-8")
    return ziel
