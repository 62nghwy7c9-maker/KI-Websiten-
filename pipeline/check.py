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
from dataclasses import asdict, dataclass
from pathlib import Path

from . import katalog as K
from .befunde import auswaehlen
from .farbe import Farbwelt
from .modelle import Pruefbericht

PREIS_AB = 990
WOCHEN = 3

STANDARD_ABSENDER = Path("absender.json")


@dataclass
class Absender:
    """Wer den Check überreicht. Ohne vollständige Angaben kein Versand."""

    name: str = "PLATZHALTER — Name eintragen"
    anschrift: str = "PLATZHALTER — Straße, PLZ Ort eintragen"
    telefon: str = "PLATZHALTER — Telefonnummer eintragen"
    mail: str = "PLATZHALTER — geschäftliche E-Mail eintragen"

    @property
    def vollstaendig(self) -> bool:
        return not any("PLATZHALTER" in str(w) for w in asdict(self).values())

    @property
    def fehlend(self) -> list[str]:
        return [f for f, w in asdict(self).items() if "PLATZHALTER" in str(w)]

    @staticmethod
    def laden(pfad: Path | str = STANDARD_ABSENDER) -> "Absender":
        p = Path(pfad)
        if not p.exists():
            a = Absender()
            p.write_text(json.dumps(asdict(a), ensure_ascii=False, indent=2),
                         encoding="utf-8")
            return a
        return Absender(**json.loads(p.read_text(encoding="utf-8")))


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
.kopf{{border-bottom:3px solid var(--akzent);padding-bottom:1.4rem;margin-bottom:2.5rem}}
.eyebrow{{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;
 color:var(--akzent);font-weight:600;margin:0 0 .7rem}}
h1{{font-size:1.9rem;line-height:1.2;margin:0 0 .6rem;font-weight:700}}
.betrieb{{font-size:1.05rem;color:var(--grau);margin:0}}
.hook{{margin:0 0 2.5rem;font-size:1.02rem}}
.befund{{display:grid;grid-template-columns:2.6rem 1fr;gap:0 1.1rem;
 margin:0 0 2rem;break-inside:avoid}}
.nr{{background:var(--akzent);color:#fff;width:2.2rem;height:2.2rem;border-radius:50%;
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


def bauen(bericht: Pruefbericht, absender: Absender,
          farbe: Farbwelt | None = None) -> str:
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

    teile = [sperre,
             '<div class="kopf">',
             '<p class="eyebrow">Kostenloser Website-Check</p>',
             f'<h1>{len(gewaehlt)} Punkte, die auf Ihrer Seite '
             f'{"Gäste" if k.branche == "gastro" else "Kunden"} kosten</h1>',
             f'<p class="betrieb">{_e(k.firma)}'
             + (f' · {_e(k.ort)}' if k.ort else '')
             + f' · {_e(k.url)}</p>',
             '</div>',
             '<p class="hook">Dieser Check ist ein Geschenk, ganz ohne '
             'Verpflichtung. Ich habe mir Ihre Seite angesehen und '
             f'aufgeschrieben, was aus meiner Sicht gerade am meisten kostet. '
             f'<b>Alles hier ist heute live nachprüfbar.</b></p>']

    for i, b in enumerate(gewaehlt, 1):
        teile.append(f'<div class="befund"><div class="nr">{i}</div><div>')
        teile.append(f'<h2>{_e(b.titel)}</h2>')
        teile.append(f'<p>{_e(b.beobachtung)}</p>')
        if b.was_es_kostet:
            teile.append(f'<p class="kostet"><b>Was es kostet:</b> '
                         f'{_e(b.was_es_kostet)}</p>')
            teile.append(f'<p class="quelle">Grundlage: {_e(b.beleg)}</p>')
        teile.append('</div></div>')

    teile += [
        '<hr class="trenner">',
        '<div class="angebot">',
        '<h2>Der gute Teil: alles behebbar.</h2>',
        '<p>Diese Punkte lassen sich zusammen in einer modernen, mobilen '
        'Website lösen — mit Ihren Inhalten, Ihren Farben und Ihrem Namen.</p>',
        f'<p class="rahmen">Festpreis ab {PREIS_AB} €, fertig in {WOCHEN} Wochen</p>',
        '<p style="margin:0;font-size:.86rem;color:var(--grau)">Was es genau '
        'kostet, hängt vom Umfang ab. Das klären wir im Gespräch.</p>',
        f'<p class="cta">Unverbindlich sprechen? {_e(absender.telefon)}</p>',
        '</div>',
        '<div class="fuss">',
        f'<b>{_e(absender.name)}</b><br>{_e(absender.anschrift)}<br>'
        f'{_e(absender.telefon)} · {_e(absender.mail)}<br><br>',
        f'Erstellt auf Basis der öffentlich einsehbaren Website, '
        f'Stand {_e(bericht.stand)}. Dieser Check ist kostenlos und '
        f'unverbindlich.',
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
              farbe: Farbwelt | None = None) -> Path:
    ordner.mkdir(parents=True, exist_ok=True)
    ziel = ordner / f"check_{bericht.kandidat.schluessel()}.html"
    ziel.write_text(bauen(bericht, absender, farbe), encoding="utf-8")
    return ziel
