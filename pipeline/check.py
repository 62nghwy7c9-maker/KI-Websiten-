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
from .bild import Aufnahme
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


def _css(s: Stilprobe, klassisch: bool = True) -> str:
    """Ein Prüfbericht, kein Werbeblatt.

    Die Zielgruppe sind Handwerksmeister, oft über fünfzig. Was bei ihnen
    Vertrauen erzeugt, ist ein Dokument, das aussieht wie ein Dokument: Antiqua,
    schwarze Schrift auf Weiß, gerade Linien, keine Farbflächen. Wer einen
    Sachverständigenbericht oder eine Abnahme kennt, erkennt die Form wieder.

    Die Farbwelt des Betriebs wird bewusst **nicht** verwendet. Sie gehört in
    den Entwurf der neuen Seite, wo sie ein Argument ist — auf dem Gutachten
    wäre sie Dekoration und würde die Nüchternheit kaputtmachen, die den Wert
    des Blattes ausmacht.

    `klassisch=False` schaltet auf die Gestaltung des Betriebs um, falls sich
    das im Gespräch als besser herausstellt.
    """
    if klassisch:
        schrift = ('"Palatino Linotype", "Book Antiqua", Palatino, '
                   '"Iowan Old Style", Georgia, serif')
        akzent = "#1A1A1A"
        linie = "#B8B5AC"
        grund = "17px"
    else:
        schrift, akzent, linie, grund = s.schrift, s.akzent, "#DAD8D0", "16px"

    return f"""
:root{{--akzent:{akzent};--ink:#12120F;--grau:#4A4842;--linie:{linie};
 --warn:#8A2E20;--schrift:{schrift};}}
*{{box-sizing:border-box}}
body{{margin:0;background:#DEDCD6;color:var(--ink);font-family:var(--schrift);
 font-size:{grund};line-height:1.55}}
.blatt{{max-width:42rem;margin:0 auto;background:#fff;padding:3.6rem 3.2rem 2.8rem}}
.sperre{{border:1px solid var(--warn);color:var(--warn);padding:.7rem .9rem;
 margin:0 0 2.4rem;font-size:.88rem;line-height:1.45}}
.sperre small{{display:block;opacity:.85;margin-top:.25rem}}

h1{{font-size:1.85rem;line-height:1.22;margin:0 0 1rem;font-weight:700;
 max-width:20em}}
.weitere{{display:none}}
.betrieb{{font-size:1rem;margin:0;font-weight:700}}
.geprueft{{margin:.15rem 0 1.6rem;font-size:.86rem;color:var(--grau)}}
.geprueft a{{color:inherit}}
.regel{{border:none;border-top:1.5px solid var(--ink);margin:0 0 1.5rem}}

.aufnahme{{display:flex;gap:1.1rem;align-items:flex-start;margin:0 0 .5rem;
 break-inside:avoid}}
.aufnahme figure{{margin:0}}
.aufnahme img{{display:block;width:100%;height:auto;border:1px solid var(--linie)}}
.aufnahme .hoch{{flex:0 0 32%}}
.aufnahme .quer{{flex:1 1 auto}}
.aufnahme figcaption{{font-size:.78rem;color:var(--grau);margin-top:.3rem}}
.bildquelle{{font-size:.8rem;color:var(--grau);margin:0 0 2rem}}

.hook{{margin:0 0 2.2rem;max-width:33em}}
.bilanz{{margin:0 0 1.4rem;font-size:.9rem;color:var(--grau)}}
.bilanz b{{color:var(--ink);font-weight:700}}
.bilanz .sep{{display:none}}
.abschnitt{{font-size:1rem;font-weight:700;margin:0 0 1.2rem;
 padding-bottom:.35rem;border-bottom:1px solid var(--ink)}}

.befund{{display:grid;grid-template-columns:1.9rem 1fr;gap:0 .8rem;
 padding:0 0 1.3rem;margin:0 0 1.3rem;border-bottom:1px solid var(--linie);
 break-inside:avoid}}
.befund:last-of-type{{border-bottom:none}}
.nr{{font-size:1.05rem;font-weight:700;padding-top:.02rem}}
.befund h2{{font-size:1.06rem;margin:0 0 .35rem;font-weight:700;line-height:1.35}}
.befund p{{margin:0 0 .4rem}}
.kostet{{color:var(--grau)}}
.kostet b{{color:var(--ink);font-weight:700}}
.quelle{{font-size:.82rem;color:var(--grau);margin:.3rem 0 0}}

.gut{{margin:2rem 0;break-inside:avoid}}
.gut h2{{font-size:1rem;font-weight:700;margin:0 0 .35rem}}
.gut ul{{margin:0;padding-left:1.1rem;color:var(--grau)}}

.angebot{{margin:2.4rem 0 0;padding:1.4rem 0 0;border-top:1.5px solid var(--ink);
 break-inside:avoid}}
.angebot h2{{margin:0 0 .5rem;font-size:1.1rem}}
.angebot p{{margin:0 0 .55rem;max-width:32em}}
.rahmen{{font-weight:700;margin:.8rem 0 .3rem}}
.cta{{margin:1rem 0 0}}
.trenner{{display:none}}
.fuss{{border-top:1px solid var(--linie);margin-top:2.4rem;padding-top:.9rem;
 font-size:.8rem;color:var(--grau);line-height:1.55}}
@media print{{
 @page{{margin:20mm 18mm}}
 body{{background:#fff;font-size:11pt}}
 .blatt{{max-width:none;padding:0}}
 .befund,.angebot,.gut,.fuss,.aufnahme{{break-inside:avoid}}
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

ZAHLWORT = {1: "Ein", 2: "Zwei", 3: "Drei", 4: "Vier", 5: "Fünf"}


def _zahlwort(n: int) -> str:
    """Kleine Zahlen ausgeschrieben. „Vier Punkte" liest sich, „4 Punkte" nicht."""
    return ZAHLWORT.get(n, str(n))


MONATE = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember")


def _datum(iso: str) -> str:
    """2026-08-12 → 12. August 2026. Ein Meister liest keine ISO-Daten."""
    try:
        jahr, monat, tag = (int(t) for t in iso.split("-"))
        return f"{tag}. {MONATE[monat - 1]} {jahr}"
    except Exception:
        return iso


def _kurz(url: str) -> str:
    """Adresse ohne Protokoll und ohne Schrägstrich am Ende — so liest sie sich.

    Der Link selbst bleibt vollständig; angezeigt wird die Form, die der
    Inhaber von seiner Visitenkarte kennt.
    """
    return url.split("//")[-1].rstrip("/")


def _aufnahme_block(aufnahme: Aufnahme | None, stand: str) -> str:
    """Die Seite des Betriebs, wie sie heute aussieht.

    Steht bewusst ganz oben, noch vor der Bilanz: Der Empfänger erkennt seine
    eigene Seite und weiß in einer Sekunde, dass dieses Blatt ihn meint und
    nicht irgendwen. Danach liest er weiter.

    Und es ist der Beweis. „Auf dem Handy schwer zu lesen" ist eine Behauptung,
    das Bild derselben Seite auf einem Handy ist keine.
    """
    if not aufnahme or not aufnahme.hat_bild:
        return ""
    bilder = []
    if aufnahme.handy:
        bilder.append(f'<figure class="hoch"><img src="{aufnahme.handy}" '
                      f'alt="Ihre Website auf dem Handy">'
                      f'<figcaption>Auf dem Handy</figcaption></figure>')
    if aufnahme.schreibtisch:
        bilder.append(f'<figure class="quer"><img src="{aufnahme.schreibtisch}" '
                      f'alt="Ihre Website am Bildschirm">'
                      f'<figcaption>Am Bildschirm</figcaption></figure>')
    return (f'<div class="aufnahme">{"".join(bilder)}</div>'
            f'<p class="bildquelle">Ihre Website am {_e(stand)}, aufgenommen '
            f'wie ein Besucher sie sieht.</p>')


def bauen(bericht: Pruefbericht, absender: Absender,
          stil: Stilprobe | None = None, ohne_positives: bool = False,
          aufnahme: Aufnahme | None = None) -> str:
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

    # Kein Etikett „Website-Check" über dem Kopf: Der Empfänger sieht den
    # Betriebsnamen zuerst, dann den Befund. Was das Blatt ist, erklärt der
    # erste Satz — eine Überschrift, die sich selbst benennt, wirkt wie Werbung.
    teile = [sperre,
             f'<p class="betrieb">{_e(k.firma)}</p>',
             (f'<p class="geprueft">{_e(k.ort)}</p>' if k.ort else ''),
             '<hr class="regel">',
             f'<h1>{_e(_kopfzeile(gewaehlt))}</h1>',
             _aufnahme_block(aufnahme, _datum(bericht.stand)),
             # Die Zahl vorweg: Sie zeigt, dass ein Katalog abgearbeitet wurde
             # und nicht vier Dinge aufgefallen sind. Das ist der Unterschied
             # zwischen einer Prüfung und einer Meinung.
             f'<p class="hook">So sieht Ihre Seite heute auf einem Handy aus. '
             f'{_zahlwort(len(gewaehlt))} Punkte sind uns dabei aufgefallen. '
             f'Nachprüfen können Sie jeden selbst.</p>']

    teile.append(f'<p class="bilanz">Wir haben <b>{geprueft} Punkte</b> '
                 f'geprüft. <b>{len(gewaehlt)}</b> davon sollten Sie ändern.</p>')
    teile.append('<p class="abschnitt">Was uns aufgefallen ist</p>')

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
        '<h2>Was sich ändern lässt</h2>',
        '<p>Wir machen Websites für Handwerksbetriebe aus Kerpen und '
        'Umgebung. Auf Wunsch bauen wir Ihnen vorab eine Seite zum Ansehen, '
        'mit Ihren eigenen Texten und Bildern. Das kostet nichts und '
        'verpflichtet zu nichts.</p>',
        # Voreinstellung: kein Preis. Siehe Absender.preis_hinweis.
        (f'<p class="rahmen">{_e(absender.preis_hinweis)}</p>'
         if absender.preis_hinweis else ''),
        f'<p class="cta">Wenn Sie darüber reden wollen: '
        f'{_e(absender.telefon)}. Zehn Minuten genügen.</p>',
        '</div>',
        '<div class="fuss">',
        f'<b>{_e(absender.name)}</b><br>{_e(absender.anschrift)}<br>'
        f'{_e(absender.telefon)} · {_e(absender.mail)}<br><br>',
        f'Geprüft wurde {_e(_kurz(k.url))} am {_e(_datum(bericht.stand))}. '
        f'Alle Punkte ohne eigene Quellenangabe stammen aus diesem Abruf und '
        f'sind dort nachprüfbar. Der Check ist kostenlos und unverbindlich.',
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
              stil: Stilprobe | None = None, ohne_positives: bool = False,
              aufnahme: Aufnahme | None = None) -> Path:
    ordner.mkdir(parents=True, exist_ok=True)
    ziel = ordner / f"check_{bericht.kandidat.schluessel()}.html"
    ziel.write_text(bauen(bericht, absender, stil, ohne_positives, aufnahme),
                    encoding="utf-8")
    return ziel
