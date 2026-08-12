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
from .stil import Stilprobe
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


def _css(s: Stilprobe) -> str:
    """Das Blatt in der Gestaltung des Betriebs.

    Bewusst vermieden werden die Merkmale, an denen ein automatisch erzeugtes
    Dokument sofort zu erkennen ist: runde Nummernkreise, gesperrte
    Versal-Etiketten, überall dieselbe Systemschrift, Kästen um jeden Abschnitt.
    Stattdessen ein ruhiger Satzspiegel mit Haarlinien, großen Ziffern in der
    Marginalspalte und der Schrift des Betriebs.
    """
    zweit = s.zweit or s.akzent
    # Serifenschrift braucht mehr Durchschuss und verträgt größere Grade.
    grund = "17px" if s.serif else "16px"
    h1 = "2.45rem" if s.serif else "2.25rem"
    return f"""
:root{{--akzent:{s.akzent};--zweit:{zweit};--ink:{s.text};--papier:#fff;
 --grau:#57564F;--linie:#DAD8D0;--warn:#8A3324;--radius:{s.radius};
 --schrift:{s.schrift};}}
*{{box-sizing:border-box}}
body{{margin:0;background:#E9E8E3;color:var(--ink);font-family:var(--schrift);
 font-size:{grund};line-height:1.62;-webkit-font-smoothing:antialiased}}
.blatt{{max-width:44rem;margin:0 auto;background:var(--papier);
 padding:4rem 3.4rem 3rem}}
.sperre{{background:var(--warn);color:#fff;padding:.9rem 1.2rem;margin:0 0 2.6rem;
 font-weight:600;line-height:1.45;border-radius:var(--radius)}}
.sperre small{{display:block;font-weight:400;opacity:.9;margin-top:.3rem}}

.marke{{font-size:.82rem;color:var(--grau);margin:0 0 2.2rem;
 padding-bottom:.6rem;border-bottom:1px solid var(--linie)}}
h1{{font-size:{h1};line-height:1.16;margin:0 0 .7rem;font-weight:700;
 letter-spacing:-.015em;max-width:19em}}
.weitere{{font-size:1.05rem;color:var(--grau);margin:0 0 1.6rem}}
.betrieb{{font-size:1rem;margin:0;font-weight:600}}
.geprueft{{margin:.25rem 0 0;font-size:.85rem;color:var(--grau)}}
.geprueft a{{color:var(--akzent);overflow-wrap:anywhere}}

.bilanz{{margin:2.4rem 0 2.2rem;padding:1rem 0;font-size:.92rem;
 color:var(--grau);border-top:2px solid var(--akzent);
 border-bottom:1px solid var(--linie)}}
.bilanz b{{color:var(--ink);font-size:1.1rem}}
.bilanz .sep{{margin:0 .8rem;color:var(--linie)}}
.hook{{margin:0 0 3rem;font-size:1.03rem;max-width:34em}}

.abschnitt{{font-size:.95rem;font-weight:700;color:var(--akzent);
 margin:0 0 1.6rem;padding-bottom:.4rem;border-bottom:1px solid var(--linie)}}

.befund{{display:grid;grid-template-columns:2.8rem 1fr;gap:0 1rem;
 padding:0 0 1.6rem;margin:0 0 1.6rem;border-bottom:1px solid var(--linie);
 break-inside:avoid}}
.befund:last-of-type{{border-bottom:none}}
.nr{{font-size:1.9rem;line-height:1;font-weight:700;color:var(--zweit);
 opacity:.75;padding-top:.05rem}}
.befund h2{{font-size:1.14rem;margin:0 0 .45rem;font-weight:700;line-height:1.32}}
.befund p{{margin:0 0 .5rem}}
.kostet{{color:var(--grau)}}
.kostet b{{color:var(--ink);font-weight:600}}
.quelle{{font-size:.79rem;color:var(--grau);margin:.4rem 0 0}}

.gut{{margin:2.6rem 0;padding-left:1.2rem;border-left:3px solid var(--zweit);
 break-inside:avoid}}
.gut h2{{font-size:.95rem;font-weight:700;margin:0 0 .4rem}}
.gut ul{{margin:0;padding-left:1.1rem;color:var(--grau)}}

.angebot{{margin:2.8rem 0 0;padding:1.7rem 1.9rem;background:#F5F4EF;
 border-radius:var(--radius);break-inside:avoid}}
.angebot h2{{margin:0 0 .6rem;font-size:1.2rem}}
.angebot p{{margin:0 0 .6rem;max-width:32em}}
.rahmen{{font-size:1.25rem;font-weight:700;color:var(--akzent);margin:1rem 0 .3rem}}
.cta{{margin:1.3rem 0 0;font-weight:600}}
.trenner{{display:none}}
.fuss{{border-top:1px solid var(--linie);margin-top:2.8rem;padding-top:1.1rem;
 font-size:.79rem;color:var(--grau);line-height:1.6}}
@media print{{
 @page{{margin:17mm 16mm}}
 body{{background:#fff;font-size:10.5pt}}
 .blatt{{max-width:none;padding:0}}
 .sperre{{border:2pt solid var(--warn)}}
 .befund,.angebot,.gut,.fuss{{break-inside:avoid}}
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
          stil: Stilprobe | None = None, ohne_positives: bool = False) -> str:
    """Baut den Check als HTML. Nimmt höchstens MAX_BEFUNDE_AUF_CHECK Befunde."""
    stil = stil or Stilprobe()
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
             '<p class="marke">Kostenloser Website-Check</p>',
             f'<h1>{_e(_kopfzeile(gewaehlt))}</h1>',
             (f'<p class="weitere">— und {len(gewaehlt) - 1} weitere '
              f'{"Punkt" if len(gewaehlt) == 2 else "Punkte"}</p>'
              if len(gewaehlt) > 1 else ''),
             f'<p class="betrieb">{_e(k.firma)}'
             + (f', {_e(k.ort)}' if k.ort else '') + '</p>',
             f'<p class="geprueft">Geprüft wurde <a href="{_e(k.url)}">'
             f'{_e(_kurz(k.url))}</a> am {_e(bericht.stand)}.</p>',
             # Die Zahl vorweg: Sie zeigt, dass ein Katalog abgearbeitet wurde
             # und nicht vier Dinge aufgefallen sind. Das ist der Unterschied
             # zwischen einer Prüfung und einer Meinung.
             f'<p class="bilanz"><b>{geprueft}</b> Punkte geprüft'
             f'<span class="sep">|</span><b>{len(gewaehlt)}</b> davon mit '
             f'Handlungsbedarf</p>',
             '<p class="hook">Ich prüfe jede Seite nach demselben Katalog. '
             'Was dabei herauskommt, schicke ich Ihnen kostenlos und ohne '
             'Verpflichtung — <b>jeder Punkt ist heute selbst nachprüfbar.</b></p>']

    teile.append('<p class="abschnitt">Was ich ändern würde</p>')

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
        teile += ['<div class="gut"><h2>Was schon gut ist</h2><ul>',
                  "".join(f'<li>{_e(z)}</li>' for z in gut[:2]),
                  '</ul></div>']

    teile += [
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
         f'({_e(stil.herkunft)}).' if stil.uebernommen else ''),
        '</div>',
    ]

    titel = f"Website-Check {k.firma}"
    return (f'<!doctype html><html lang="de"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{_e(titel)}</title><style>{_css(stil)}</style></head>'
            f'<body><div class="blatt">{"".join(teile)}</div></body></html>')


def schreiben(bericht: Pruefbericht, absender: Absender, ordner: Path,
              stil: Stilprobe | None = None, ohne_positives: bool = False) -> Path:
    ordner.mkdir(parents=True, exist_ok=True)
    ziel = ordner / f"check_{bericht.kandidat.schluessel()}.html"
    ziel.write_text(bauen(bericht, absender, stil, ohne_positives),
                    encoding="utf-8")
    return ziel
