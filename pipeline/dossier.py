"""Interne Übersicht zu einem Betrieb — das Arbeitsblatt, nicht das Geschenk.

Klare Trennung zum Kundencheck (`check.py`):

| | Dossier (hier) | Kundencheck |
|---|---|---|
| Empfänger | Kira | der Betrieb |
| Zeigt | **alles**: jeden Messwert, auch die unauffälligen und die offenen | höchstens vier Befunde |
| Gestaltung | dicht, sachlich, zum Überfliegen | Farbwelt des Betriebs, großzügig |
| Enthält | Kontaktdaten, Notiz aus der Lead-Liste, offene Sichtprüfungen | nichts davon |

Der Grund für die Trennung: Ein Dokument, das beides versucht, wird für beide
Zwecke schlechter. Der Kunde soll vier Punkte begreifen, nicht 19 Messwerte
sehen — und Kira braucht genau die 19, bevor sie hinfährt.
"""
from __future__ import annotations

import html
from pathlib import Path

from . import katalog as K
from .farbe import STANDARD_AKZENT
from .modelle import Pruefbericht

# Der Platzhalter wird ersetzt, nicht formatiert: CSS enthält "100%" und
# "%s"-Formatierung würde daran scheitern.
STIL = """
:root{--akzent:__AKZENT__;--ink:#16150F;--grau:#5B5A52;--linie:#DDDCD6;
 --ok:#3E6B47;--befund:#8A3324;--offen:#8A6D3B;
 --sans:"Segoe UI",-apple-system,Roboto,Helvetica,Arial,sans-serif;}
*{box-sizing:border-box}
body{margin:0;background:#EDEDEA;color:var(--ink);font-family:var(--sans);
 font-size:15px;line-height:1.5}
.blatt{max-width:56rem;margin:0 auto;background:#fff;padding:2.5rem 2.5rem 3rem}
.kopf{display:flex;justify-content:space-between;align-items:baseline;
 gap:1rem;border-bottom:3px solid var(--akzent);padding-bottom:.9rem}
h1{font-size:1.5rem;margin:0}
.marke{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;
 color:var(--grau);white-space:nowrap}
.urteil{margin:1.2rem 0 1.8rem;padding:.9rem 1.1rem;background:#F6F6F3;
 border-left:4px solid var(--akzent);font-weight:600}
h2{font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;
 color:var(--grau);margin:2rem 0 .7rem;font-weight:600}
dl.daten{display:grid;grid-template-columns:auto 1fr;gap:.3rem 1.2rem;margin:0}
dl.daten dt{color:var(--grau)}
dl.daten dd{margin:0;overflow-wrap:anywhere}
table{width:100%;border-collapse:collapse;font-size:.87rem}
th{text-align:left;color:var(--grau);font-weight:600;padding:.35rem .5rem;
 border-bottom:1px solid var(--linie);font-size:.78rem;text-transform:uppercase;
 letter-spacing:.06em}
td{padding:.4rem .5rem;border-bottom:1px solid var(--linie);vertical-align:top}
td.nr{color:var(--grau);width:2.2rem}
.z{font-weight:700;white-space:nowrap;width:5.5rem}
.z.b{color:var(--befund)} .z.o{color:var(--offen)} .z.g{color:var(--ok)}
.auf-check{background:#FBF7E8}
.marker{display:inline-block;background:var(--akzent);color:#fff;
 border-radius:2px;padding:0 .35rem;font-size:.72rem;margin-left:.4rem}
ul.hinweise{margin:0;padding-left:1.1rem}
ul.hinweise li{margin-bottom:.4rem}
.fuss{margin-top:2.5rem;padding-top:.9rem;border-top:1px solid var(--linie);
 font-size:.78rem;color:var(--grau)}
@media print{@page{margin:14mm}body{background:#fff;font-size:9.5pt}
 .blatt{max-width:none;padding:0}tr{break-inside:avoid}}
"""


def _e(t: str) -> str:
    return html.escape(t or "", quote=False)

def _argumente(bericht: Pruefbericht) -> list[tuple[str, str, str]]:
    """Welches Verkaufsargument bei diesem Betrieb trägt — vor dem Gespräch.

    Drei Fragen, die im Gespräch über den Einstieg entscheiden und sich aus der
    Messung beantworten lassen. Sie stehen hier, damit vor dem Klingeln klar
    ist, worüber geredet wird — nicht erst an der Tür.
    """
    w = {m.id: m for m in bericht.messung}

    def stand(nr: int, wenn_befund: str, wenn_ok: str,
              wenn_offen: str = "nicht geprüft") -> str:
        m = w.get(nr)
        if m is None or m.ok is None:
            return wenn_offen
        return wenn_befund if m.ok is False else wenn_ok

    return [
        ("Karriereseite",
         stand(9, "fehlt", "vorhanden"),
         "Praktikanten und Azubis — bei ausgelasteten Betrieben das stärkere "
         "Argument als Kundengewinnung"),
        ("Anfrageformular",
         stand(10, "fehlt", "vorhanden"),
         "Ohne Formular bewirbt sich niemand vom Handy aus"),
        ("Eigene Domain",
         stand(13, "nein, Baukasten", "ja"),
         "Bei „ja“ gibt es kein Baukasten-Abo zu kündigen — dann im Gespräch "
         "fragen, was er heute für Hosting zahlt"),
    ]


def bauen(bericht: Pruefbericht, akzent: str = STANDARD_AKZENT) -> str:
    k = bericht.kandidat
    auf_check = set(bericht.auswahl_fuer_check)
    befund_ids = {b.id for b in bericht.befunde}

    ausloeser = [m for m in bericht.messung if m.ok is False]
    offen = [m for m in bericht.messung if m.ok is None]

    urteil = (f"{len(ausloeser)} Auslöser belegt, {len(offen)} Punkte offen. "
              + ("Qualifiziert allein aus der Automatik."
                 if bericht.qualifiziert else
                 f"Noch nicht qualifiziert — {K.QUALIFIKATION_AB_BEFUNDEN} Befunde "
                 f"nötig. Die offenen Punkte entscheiden, nicht vorschnell verwerfen."))

    daten = [("Betrieb", _e(k.firma))]
    for name, wert in (("Ansprechpartner", k.inhaber), ("Ort", k.ort),
                       ("Gewerk", k.branche), ("Telefon", k.telefon),
                       ("E-Mail", k.kontakt_mail)):
        if wert:
            daten.append((name, _e(wert)))
    daten.append(("Website", f'<a href="{_e(k.url)}">{_e(k.url)}</a>'))
    daten.append(("Stand", _e(bericht.stand)))

    zeilen = []
    for m in sorted(bericht.messung, key=lambda x: x.id):
        klasse, wort = {True: ("g", "unauffällig"), False: ("b", "BEFUND"),
                        None: ("o", "offen")}[m.ok]
        marker = ""
        if m.id in auf_check:
            marker = '<span class="marker">auf dem Check</span>'
        elif m.id in befund_ids:
            marker = '<span class="marker" style="background:#9A9A92">Befund, nicht gewählt</span>'
        quelle = "" if m.auto else " · Sichtprüfung"
        zeilen.append(
            f'<tr class="{"auf-check" if m.id in auf_check else ""}">'
            f'<td class="nr">{m.id}</td>'
            f'<td class="z {klasse}">{wort}</td>'
            f'<td><b>{_e(m.pruefpunkt)}</b>{marker}<br>{_e(m.wert)}'
            f'<span style="color:var(--grau)"> — {_e(m.quelle)}{quelle}</span></td></tr>')

    formulierungen = "".join(
        f'<tr><td class="nr">{b.id}</td><td><b>{_e(b.titel)}</b><br>'
        f'{_e(b.beobachtung)}<br>'
        + (f'<i>Was es kostet:</i> {_e(b.was_es_kostet)}<br>'
           f'<span style="color:var(--grau)">Beleg: {_e(b.beleg)}</span>'
           if b.was_es_kostet else
           '<span style="color:var(--befund)">kein Kosten-Satz — Beleg fehlt</span>')
        + '</td></tr>'
        for b in bericht.befunde)

    hinweise = "".join(f"<li>{_e(h)}</li>" for h in bericht.hinweise)

    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dossier {_e(k.firma)}</title><style>{STIL.replace('__AKZENT__', akzent)}</style></head><body>
<div class="blatt">
<div class="kopf"><h1>{_e(k.firma)}</h1>
<span class="marke">Interne Übersicht · nicht für den Kunden</span></div>
<p class="urteil">{_e(urteil)}</p>

<h2>Betrieb</h2>
<dl class="daten">{''.join(f'<dt>{n}</dt><dd>{w}</dd>' for n, w in daten)}</dl>

<h2>Womit ins Gespräch</h2>
<table><tbody>{''.join(
    f'<tr><td style="width:11rem"><b>{_e(n)}</b></td>'
    f'<td style="width:9rem">{_e(wert)}</td>'
    f'<td style="color:var(--grau)">{_e(warum)}</td></tr>'
    for n, wert, warum in _argumente(bericht))}</tbody></table>

<h2>Alle Prüfpunkte</h2>
<table><thead><tr><th></th><th>Ergebnis</th><th>Prüfpunkt und Messwert</th>
</tr></thead><tbody>{''.join(zeilen)}</tbody></table>

<h2>Formulierungen für den Check</h2>
<table><tbody>{formulierungen or '<tr><td>keine Befunde</td></tr>'}</tbody></table>

{'<h2>Von Hand nachsehen</h2><ul class="hinweise">' + hinweise + '</ul>' if hinweise else ''}

<p class="fuss">Erzeugt aus der Rohmessung vom {_e(bericht.stand)}.
Gelb hinterlegt: kommt auf den Kundencheck.</p>
</div></body></html>"""


def schreiben(bericht: Pruefbericht, ordner: Path,
              akzent: str = STANDARD_AKZENT) -> Path:
    ordner.mkdir(parents=True, exist_ok=True)
    ziel = ordner / f"dossier_{bericht.kandidat.schluessel()}.html"
    ziel.write_text(bauen(bericht, akzent), encoding="utf-8")
    return ziel
