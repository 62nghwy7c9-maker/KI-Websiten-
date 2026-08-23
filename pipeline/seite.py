"""Baut aus Stammdaten und Texten den fertigen webroot des Kunden.

Was hier entsteht, ist genau das, was spaeter auf seinem Webspace liegt:
Startseite, Impressum, Datenschutzerklaerung, Dankeseite, Stil, der
Pflegebereich und eine Installationsanleitung.

Die Arbeitsteilung, an der alles haengt:

  Der Rechner baut alles Mechanische.   Kopf, Fuss, Navigation, Rufnummern,
                                        die beiden Rechtsseiten, das Formular,
                                        der Pflegebereich.
  Der Mensch schreibt die Saetze.       Ueberschriften, Leistungen, der Ton.

Was der Rechner nicht hat, denkt er sich nicht aus. Fehlt ein Pflichtfeld,
bricht der Bau ab und nennt es beim Namen. Es gibt keinen Platzhalter, der
versehentlich live gehen kann.
"""
from __future__ import annotations

import hashlib
import html as H
import shutil
from dataclasses import dataclass
from pathlib import Path

from .stammdaten import Stammdaten
from .texte import Abschnitt, Gruppe, lesen as texte_lesen, offene_stellen
from .vorlagen import fuellen, offene_platzhalter

VORLAGE = Path("studie/pflege/vorlage/seite")
PFLEGE = Path("studie/pflege")

# Abschnitte mit fester Bedeutung. Alles andere wird zu einem gewoehnlichen
# Abschnitt der Seite, in der Reihenfolge aus texte.md.
BESONDERS = ("aufmacher", "band", "kontakt")

# Der Pflegebereich, unveraendert aus der Vorlage. Diese Dateien duerfen sich
# zwischen Kunden nicht unterscheiden, sonst erbt der naechste Kunde einen
# alten Fehler.
PFLEGEDATEIEN = ("index.php", "inhalt.php", ".htaccess")


@dataclass
class Ergebnis:
    webroot: Path
    dateien: list[str]
    warnungen: list[str]


# ── Bausteine der Startseite ─────────────────────────────────────────────

def _band(a: Abschnitt) -> str:
    if not a or not a.zeilen:
        return ""
    # Die Marker heissen wie das, was drinsteht: der Betrieb aendert im
    # Pflegebereich seine Mitarbeiterzahl, nicht "Feld 1".
    namen = a.angaben.get("felder", "").split()
    zeilen = []
    for i, (wert, text) in enumerate(a.zeilen):
        marke = namen[i] if i < len(namen) else ""
        inhalt = (f"<!--wg:{marke}-->{H.escape(wert)}<!--/wg-->"
                  if marke else H.escape(wert))
        zeilen.append(f"      <li><b>{inhalt}</b>"
                      f"<span>{H.escape(text)}</span></li>")
    return ("\n<div class=\"band\">\n  <div class=\"bahn\">\n    <ul>\n"
            + "\n".join(zeilen)
            + "\n    </ul>\n  </div>\n</div>\n")


def _prosa(text: str, daten: Stammdaten) -> str:
    """Macht aus einem geschriebenen Satz sicheres HTML.

    Der Text wird zuerst vollstaendig entschaerft, erst danach duerfen die
    wenigen erlaubten Einsetzungen wieder HTML werden. Andersherum koennte
    ein Text aus texte.md Markup in die Seite schmuggeln.

    Erlaubt sind ``{telefon}``, ``{mail}``, ``{firma}`` und ``{ort}``. Damit
    steht die Rufnummer auch mitten in einem Satz noch als anklickbarer Link
    und traegt denselben Marker wie ueberall sonst -- aendert der Betrieb sie
    im Pflegebereich, aendert sie sich auch hier.
    """
    sicher = H.escape(text)
    tel = (f'<a href="tel:{H.escape(daten.telefon_wahl)}">'
           f'<!--wg:telefon-->{H.escape(daten["telefon"])}<!--/wg--></a>')
    mail = (f'<a href="mailto:{H.escape(daten["mail"])}">'
            f'<!--wg:mail-->{H.escape(daten["mail"])}<!--/wg--></a>')
    for zeichen, ersatz in (("{telefon}", tel), ("{mail}", mail),
                            ("{firma}", H.escape(daten["firma"])),
                            ("{ort}", H.escape(daten["ort"]))):
        sicher = sicher.replace(zeichen, ersatz)
    return sicher


def _gruppen(gruppen: list[Gruppe], daten: Stammdaten) -> str:
    if not gruppen:
        return ""
    stuecke = []
    for g in gruppen:
        punkte = "\n".join(f"          <li>{_prosa(p, daten)}</li>"
                           for p in g.punkte)
        titel = f"        <h3>{H.escape(g.titel)}</h3>\n" if g.titel else ""
        stuecke.append(f"      <div class=\"gruppe\">\n{titel}"
                       f"        <ul>\n{punkte}\n        </ul>\n      </div>")
    return ("\n    <div class=\"leistungen\">\n" + "\n".join(stuecke)
            + "\n    </div>\n")


def _absaetze(a: Abschnitt, pflegefeld: str, daten: Stammdaten) -> str:
    stuecke = []
    for i, (art, text) in enumerate(a.absaetze):
        inhalt = _prosa(text, daten)
        # Genau ein Absatz je Abschnitt kann im Pflegebereich aenderbar sein.
        # Mehr waere unuebersichtlich, weniger nimmt dem Betrieb die
        # Stellenanzeige aus der Hand.
        if pflegefeld and i == 0:
            inhalt = f"<!--wg:{pflegefeld}-->{inhalt}<!--/wg-->"
        if art == "hinweis":
            titel = a["kasten"]
            kopf = f"      <h3>{H.escape(titel)}</h3>\n" if titel else ""
            stuecke.append(f"    <div class=\"kasten\">\n{kopf}"
                           f"      <p>{inhalt}</p>\n    </div>")
        else:
            stuecke.append(f"    <p>{inhalt}</p>")
    return ("\n" + "\n".join(stuecke) + "\n") if stuecke else ""


def _bild(a: Abschnitt, daten: Stammdaten) -> str:
    name = a["bild"]
    if not name:
        return ""
    angabe = daten.bilder.get(name, {})
    datei = angabe.get("datei", f"{name}.jpg")
    alt = angabe.get("alt", "Foto aus dem Betrieb")
    titel = angabe.get("titel", "")
    return (f"\n    <figure>\n      <!--wg:bild:{name}-->\n"
            f"      <img src=\"bilder/{H.escape(datei)}\" "
            f"alt=\"{H.escape(alt)}\">\n"
            f"      <figcaption><!--wg:bildtitel-->{H.escape(titel)}"
            f"<!--/wg--></figcaption>\n    </figure>\n")


def _abschnitt(a: Abschnitt, daten: Stammdaten) -> str:
    kopf = [f"\n<section id=\"{H.escape(a.name)}\">",
            "  <div class=\"bahn\">"]
    if a["marke"]:
        kopf.append(f"    <p class=\"marke\">{H.escape(a['marke'])}</p>")
    if a["h2"]:
        kopf.append(f"    <h2>{H.escape(a['h2'])}</h2>")
    if a["vorspann"]:
        kopf.append(f"    <p class=\"vorspann\">{H.escape(a['vorspann'])}</p>")

    rumpf = (_absaetze(a, a["pflegefeld"], daten)
             + _gruppen(a.gruppen, daten))
    bild = _bild(a, daten)
    if bild:
        # Text links, Bild rechts. Dieselbe Aufteilung wie auf der
        # Referenzseite, damit es auf dem Handy sauber untereinander faellt.
        rumpf = (f"\n    <div class=\"referenz\">\n      <div>{rumpf}"
                 f"      </div>{bild}    </div>\n")

    return "\n".join(kopf) + rumpf + "  </div>\n</section>\n"


def _nav(abschnitte: list[Abschnitt]) -> str:
    glieder = [f"<a href=\"#{H.escape(a.name)}\">{H.escape(a.beschriftung)}</a>"
               for a in abschnitte if a.name not in ("aufmacher", "band")]
    return "\n      ".join(glieder)


# ── Der Bau ──────────────────────────────────────────────────────────────

def _werte(daten: Stammdaten) -> dict[str, str]:
    """Alles, was in jeder Vorlage vorkommen kann."""
    w = {f: daten[f] for f in daten.bestaetigt}
    w.update({
        "telefon_wahl": daten.telefon_wahl,
        "anschrift": daten.anschrift,
        "hinweis": daten["hinweis"] or
                   "Diesen Hinweis ändern Sie selbst, zum Beispiel für "
                   "Betriebsurlaub oder einen Notdienst.",
        # Der Block "Register und Kammern" erscheint nur, wenn wenigstens
        # eine der vier Angaben da ist. Eine leere Ueberschrift auf einem
        # Impressum sieht aus, als fehle etwas.
        "register_block": "".join(daten[f] for f in
                                  ("handwerkskammer", "ihk",
                                   "handelsregister", "ustid")),
        "protokolldauer_offen": "" if daten["protokolldauer"] else "ja",
    })
    return w


def _seiten_kopf(vorlagen: dict[str, str], werte: dict[str, str],
                 titel: str, beschreibung: str, nav: str,
                 noindex: bool = False) -> str:
    return fuellen(vorlagen["_kopf"], {**werte, "titel": titel,
                                       "beschreibung": beschreibung,
                                       "nav": nav,
                                       "nicht_indexieren": "ja" if noindex else ""})


def bauen(ordner: Path, wurzel: Path = Path(".")) -> Ergebnis:
    ordner = Path(ordner)
    daten = Stammdaten.laden(ordner)
    fehlt = daten.fehlend()
    if fehlt:
        raise SystemExit(
            "Der Bau bricht ab, es fehlen bestätigte Angaben:\n  "
            + "\n  ".join(fehlt)
            + "\n\nDiese Angaben kommen vom Betrieb, nicht von uns. "
              "Sie stehen im Fragebogen ERHEBUNG.md.\n"
              "Gibt es eine davon beim Betrieb wirklich nicht, trage "
              "\"entfaellt\" ein.")

    texte_datei = ordner / "texte.md"
    if not texte_datei.is_file():
        raise SystemExit(f"Keine Texte in {texte_datei}.")
    abschnitte = texte_lesen(texte_datei)
    offen = offene_stellen(abschnitte)
    if offen:
        raise SystemExit("In texte.md steht noch Unfertiges:\n  "
                         + "\n  ".join(offen))

    nach_namen = {a.name: a for a in abschnitte}
    if "aufmacher" not in nach_namen:
        raise SystemExit("In texte.md fehlt der Abschnitt \"# aufmacher\".")

    v = {p.stem: p.read_text(encoding="utf-8")
         for p in (wurzel / VORLAGE).glob("*.html")}
    v["stil"] = (wurzel / VORLAGE / "stil.css").read_text(encoding="utf-8")

    werte = _werte(daten)
    webroot = ordner / "webroot"
    webroot.mkdir(parents=True, exist_ok=True)
    (webroot / "pflege").mkdir(exist_ok=True)
    geschrieben: list[str] = []
    warnungen: list[str] = []

    def schreiben(pfad: Path, text: str) -> None:
        rest = offene_platzhalter(text)
        if rest:
            raise SystemExit(f"In {pfad.name} blieben Platzhalter stehen: "
                             + ", ".join(rest))
        pfad.write_text(text, encoding="utf-8")
        geschrieben.append(str(pfad.relative_to(webroot)))

    # ── Startseite ──
    auf = nach_namen["aufmacher"]
    kon = nach_namen.get("kontakt", Abschnitt("kontakt"))
    inhalt = [a for a in abschnitte if a.name not in BESONDERS]

    nav_glieder = [a for a in abschnitte if a.name not in ("aufmacher", "band")]
    if "kontakt" not in nach_namen:
        nav_glieder.append(Abschnitt("kontakt", {"marke": "Kontakt"}))

    seite = fuellen(v["index"], {
        **werte,
        "kopf": _seiten_kopf(
            v, werte,
            f"{daten['firma']} · {auf['titel'] or auf['marke']}",
            auf["beschreibung"],
            _nav(nav_glieder)),
        "fuss": fuellen(v["_fuss"], {**werte, "skript": v["_skript"],
                                     "fussnav": '<a href="impressum.html">Impressum</a> ·\n      '
                                                '<a href="datenschutz.html">Datenschutz</a>'}),
        "aufmacher_marke": auf["marke"],
        "aufmacher_h1": auf["h1"],
        "aufmacher_einleitung": auf["einleitung"],
        "band": _band(nach_namen.get("band")),
        "abschnitte": "".join(_abschnitt(a, daten) for a in inhalt),
        "kontakt_marke": kon["marke"] or "Kontakt",
        "kontakt_h2": kon["h2"] or "Rufen Sie an oder schreiben Sie uns",
        "zeiten_titel": kon["zeiten_titel"] or "Erreichbar",
    })
    schreiben(webroot / "index.html", seite)

    # ── Die beiden Rechtsseiten und die Dankeseite ──
    rechts_fuss = lambda ohne: fuellen(v["_fuss"], {
        **werte, "skript": "",
        "fussnav": " · ".join(
            f'<a href="{z}">{n}</a>' for z, n in
            (("index.html", "Startseite"), ("impressum.html", "Impressum"),
             ("datenschutz.html", "Datenschutz")) if z != ohne)})

    schreiben(webroot / "impressum.html", fuellen(v["impressum"], {
        **werte,
        "kopf": _seiten_kopf(v, werte, f"Impressum · {daten['firma']}",
                             f"Impressum und Anbieterkennzeichnung nach § 5 DDG "
                             f"für {daten['firma']}, {daten.anschrift}.",
                             '<a href="index.html">Startseite</a>\n      '
                             '<a href="datenschutz.html">Datenschutz</a>'),
        "fuss": rechts_fuss("impressum.html")}))

    schreiben(webroot / "datenschutz.html", fuellen(v["datenschutz"], {
        **werte,
        "kopf": _seiten_kopf(v, werte, f"Datenschutz · {daten['firma']}",
                             f"Datenschutzerklärung von {daten['firma']}.",
                             '<a href="index.html">Startseite</a>\n      '
                             '<a href="impressum.html">Impressum</a>'),
        "fuss": rechts_fuss("datenschutz.html")}))

    schreiben(webroot / "danke.html", fuellen(v["danke"], {
        **werte,
        "kopf": _seiten_kopf(v, werte, f"Danke für Ihre Anfrage · {daten['firma']}",
                             "", '<a href="index.html">Startseite</a>\n      '
                                 '<a href="impressum.html">Impressum</a>',
                             noindex=True),
        "fuss": rechts_fuss("danke.html")}))

    # ── Stil ──
    farben = ""
    if daten.farbe and daten.farbe.count("#") == 3:
        a, b, c = [t.strip() for t in daten.farbe.split() if t.strip()][:3]
        farben = ("/* Hausfarbe dieses Betriebs, alle drei Töne festgelegt. */\n"
                  f":root{{--blau:{a};--blau-tief:{b};--blau-hell:{c}}}\n")
    elif daten.farbe:
        warnungen.append(
            "farbe in stammdaten.json ist gesetzt, aber nicht als drei "
            "Hexwerte (Grundton, dunkel, hell). Die Seite bekommt die "
            "Standardfarben. Zwei Töne aus einem auszurechnen ergibt "
            "Kontraste, die niemand geprüft hat.")
    schreiben(webroot / "stil.css", fuellen(v["stil"], {"farbwahl": farben}))

    # ── Pflegebereich: unveraendert, ausser den vier Konstanten ──
    for name in PFLEGEDATEIEN:
        shutil.copy2(wurzel / PFLEGE / name, webroot / "pflege" / name)
        geschrieben.append(f"pflege/{name}")

    formular = (wurzel / PFLEGE / "formular.php").read_text(encoding="utf-8")
    for alt, neu in (
        ("const EMPFAENGER = 'info@musterbetrieb.de';",
         f"const EMPFAENGER = '{daten['mail']}';"),
        ("const BETRIEB = 'Musterbetrieb';",
         f"const BETRIEB = '{daten['firma']}';"),
        # Die Vorlage zeigt auf /danke.html und /kontakt.html. Beides gibt es
        # in dieser Aufteilung nicht: das Formular liegt in pflege/, und der
        # Kontakt ist ein Abschnitt der Startseite.
        ("const ZURUECK = '/danke.html';",
         "const ZURUECK = '../danke.html';"),
        ("const ZURUECK_FEHLER = '/kontakt.html?fehler=1';",
         "const ZURUECK_FEHLER = '../index.html?fehler=1#kontakt';"),
    ):
        if alt not in formular:
            raise SystemExit(f"In der Vorlage formular.php fehlt: {alt}")
        formular = formular.replace(alt, neu)
    (webroot / "pflege" / "formular.php").write_text(formular, encoding="utf-8")
    geschrieben.append("pflege/formular.php")

    # ── Bilder ──
    quelle_bilder = ordner / "bilder"
    if daten.bilder:
        (webroot / "bilder").mkdir(exist_ok=True)
        for name, angabe in daten.bilder.items():
            datei = angabe.get("datei", f"{name}.jpg")
            her = quelle_bilder / datei
            if not her.is_file():
                raise SystemExit(
                    f"Das Bild {datei} fehlt in {quelle_bilder}. "
                    f"Es kommt vom Betrieb. Wir setzen kein fremdes Foto ein.")
            shutil.copy2(her, webroot / "bilder" / datei)
            geschrieben.append(f"bilder/{datei}")
            if her.stat().st_size > 900_000:
                warnungen.append(
                    f"{datei} ist {her.stat().st_size // 1024} KB gross. "
                    f"Auf dem Handy laedt das spuerbar lange. Vor der "
                    f"Uebergabe verkleinern.")

    # ── Installationsanleitung ──
    schreiben(webroot / "INSTALLATION.txt", _installation(daten))

    (ordner / ".gebaut").write_text(_stand(webroot), encoding="utf-8")
    return Ergebnis(webroot, geschrieben, warnungen)


def _installation(daten: Stammdaten) -> str:
    return f"""Website {daten['firma']}
{'=' * (9 + len(daten['firma']))}

So kommt die Seite auf den Webspace:

1. Den gesamten Inhalt dieses Ordners in das Webverzeichnis hochladen.
   Es heisst je nach Anbieter htdocs, www, public_html oder httpdocs.

2. Nichts umbenennen. Der Ordner pflege muss pflege heissen und neben
   index.html liegen.

3. Die Seite im Browser aufrufen. Sie braucht keine Einrichtung, keine
   Datenbank und keine Konfigurationsdatei.

Voraussetzungen beim Anbieter:

  PHP 8 oder neuer
  Der Ordner pflege muss beschreibbar sein
  Mailversand ueber die PHP-Funktion mail()

Kommt keine Mail an, gehen die Anfragen trotzdem nicht verloren: Sie
liegen im Pflegebereich unter {daten['domain']}/pflege/ und werden dort
angezeigt.

Das Passwort fuer den Pflegebereich haben Sie muendlich bekommen. Es steht
in keiner Datei dieses Pakets. Aendern Sie es bei der ersten Anmeldung.
"""


# Diese entstehen erst beim Schnueren des Pakets oder beim Ausprobieren.
# Sie gehoeren nicht zum gebauten Stand.
NICHT_GEBAUT = ("passwort.php", "anfragen.php", "anfragen-neu.php",
                "anfragen.lock", "selbsttest.php")


def _stand(webroot: Path) -> str:
    """Fingerabdruck des gebauten Standes.

    Damit faellt auf, wenn nach dem Bau von Hand nachgebessert wurde -- und
    ein zweiter Bau die Handarbeit sonst stillschweigend ueberschreibt.
    """
    h = hashlib.sha256()
    for pfad in sorted(webroot.rglob("*")):
        if pfad.name in NICHT_GEBAUT or "sicherungen" in pfad.parts:
            continue
        if pfad.is_file():
            h.update(str(pfad.relative_to(webroot)).encode())
            h.update(pfad.read_bytes())
    return h.hexdigest()


def handarbeit_seit_bau(ordner: Path) -> bool:
    merk = Path(ordner) / ".gebaut"
    webroot = Path(ordner) / "webroot"
    if not merk.is_file() or not webroot.is_dir():
        return False
    return merk.read_text(encoding="utf-8").strip() != _stand(webroot)
