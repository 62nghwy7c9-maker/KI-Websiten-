"""Was stimmen muss, bevor ein Paket den Rechner verlaesst.

Jede Pruefung hier steht wegen eines Fehlers, der einmal wirklich passiert
ist. Keiner davon fiel beim Lesen des Codes auf; alle fielen auf, als jemand
nachgesehen hat. Also sieht jetzt jedes Mal jemand nach, und zwar der Rechner.

Der Pruefstand sagt nur, was er nachgemessen hat. Vier Dinge kann er nicht,
und die stehen am Ende jedes Berichts, damit sie niemand fuer erledigt haelt:
ob eine Mail wirklich ankommt, wie die Seite auf einem echten Handy aussieht,
ob die Angaben des Betriebs stimmen, und ob der Text gut ist.
"""
from __future__ import annotations

import html.parser
import re
from dataclasses import dataclass
from pathlib import Path

from .seite import PFLEGE, PFLEGEDATEIEN, handarbeit_seit_bau
from .stammdaten import Stammdaten

SEITEN = ("index.html", "impressum.html", "datenschutz.html", "danke.html")

# Der Pruefstand misst nicht alles. Was er nicht kann, sagt er.
NICHT_MESSBAR = (
    "Ob eine Mail wirklich im Postfach des Betriebs ankommt. Das geht erst "
    "auf seinem Hosting.",
    "Wie die Seite auf einem echten Handy aussieht.",
    "Ob die Angaben des Betriebs stimmen. Das bestaetigt er auf dem "
    "Freigabeblatt, nicht wir.",
    "Ob die Texte gut sind.",
)


@dataclass
class Befund:
    ok: bool
    titel: str
    detail: str


class _Links(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.href: list[str] = []
        self.src: list[str] = []
        self.ereignisse: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        for name, wert in attrs:
            if name == "href":
                self.href.append(wert or "")
            elif name in ("src", "action"):
                self.src.append(wert or "")
            elif name.startswith("on"):
                # Ein Ereignis-Attribut im erzeugten HTML hiesse, dass Text
                # aus texte.md als Markup durchgekommen ist.
                self.ereignisse.append(f"{tag}[{name}]")


def _lesen(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _flach(text: str) -> str:
    """Alle Folgen von Leerraum auf ein Leerzeichen.

    HTML bricht Zeilen, wo sie zu lang werden. Eine Textpruefung, die daran
    scheitert, misst die Zeilenbreite statt des Inhalts.
    """
    return " ".join(text.split())


def pruefen(ordner: Path, wurzel: Path = Path(".")) -> list[Befund]:
    ordner = Path(ordner)
    webroot = ordner / "webroot"
    b: list[Befund] = []

    def sagen(ok: bool, titel: str, detail: str) -> None:
        b.append(Befund(ok, titel, detail))

    if not webroot.is_dir():
        return [Befund(False, "Es gibt einen gebauten Stand",
                       f"{webroot} fehlt. Erst bauen.")]

    daten = Stammdaten.laden(ordner)

    # 1 Alle vom Betrieb bestaetigten Angaben liegen vor.
    fehlt = daten.fehlend()
    sagen(not fehlt, "Alle Pflichtangaben sind bestaetigt",
          "vollstaendig" if not fehlt else "es fehlen: " + ", ".join(fehlt))

    # 2 Die Seiten sind da.
    da = [s for s in SEITEN if (webroot / s).is_file()]
    sagen(len(da) == len(SEITEN), "Alle vier Seiten liegen im Paket",
          ", ".join(da) if len(da) == len(SEITEN)
          else "es fehlen: " + ", ".join(set(SEITEN) - set(da)))

    texte = {s: _lesen(webroot / s) for s in SEITEN}
    alles = "\n".join(texte.values())

    # 3 Kein Platzhalter ist stehengeblieben.
    reste = sorted(set(re.findall(r"\{\{[#/&]?[a-z0-9_]+\}\}", alles)))
    sagen(not reste, "Keine Platzhalter mehr in den Seiten",
          "keine" if not reste else ", ".join(reste))

    # 4 Jede Rufnummer ist dieselbe. Eine alte Nummer auf einer Unterseite
    #   faellt niemandem auf, ausser dem Anrufer.
    tel = sorted({h for t in texte.values()
                  for h in re.findall(r'href="tel:([^"]+)"', t)})
    sagen(tel == [daten.telefon_wahl],
          "Ueberall dieselbe Rufnummer",
          f"{daten.telefon_wahl} auf allen Seiten" if tel == [daten.telefon_wahl]
          else f"gefunden: {', '.join(tel) or 'keine'}, erwartet {daten.telefon_wahl}")

    mails = sorted({h for t in texte.values()
                    for h in re.findall(r'href="mailto:([^"]+)"', t)})
    sagen(mails in ([daten["mail"]], []), "Ueberall dieselbe Mailadresse",
          ", ".join(mails) or "keine Mailadresse verlinkt")

    # 5 Die Marker sind paarweise geschlossen. Ein offener Marker frisst beim
    #   Speichern im Pflegebereich den Rest der Seite.
    kaputt = []
    for name, t in texte.items():
        if t.count("<!--wg:") != t.count("<!--/wg-->") + len(
                re.findall(r"<!--wg:bild:[a-z0-9_-]+-->", t)):
            kaputt.append(name)
    sagen(not kaputt, "Alle Pflege-Marker sind geschlossen",
          "in Ordnung" if not kaputt else "offen in: " + ", ".join(kaputt))

    # 6 Impressum und Datenschutz sind von jeder Seite erreichbar.
    ohne = []
    for name, t in texte.items():
        soll = {"index.html", "impressum.html", "datenschutz.html"} - {name}
        fehlt_hier = [z for z in sorted(soll) if f'href="{z}"' not in t]
        if fehlt_hier:
            ohne.append(f"{name} ohne {', '.join(fehlt_hier)}")
    sagen(not ohne,
          "Startseite, Impressum und Datenschutz sind gegenseitig verlinkt",
          "alle vier Seiten" if not ohne else "; ".join(ohne))

    # 7 Nichts wird von fremden Servern nachgeladen. Sonst stimmt die
    #   Datenschutzerklaerung nicht mehr, die genau das verneint.
    fremd = []
    for name, t in texte.items():
        p = _Links()
        p.feed(t)
        fremd += [f"{name}: {u}" for u in p.href + p.src
                  if u.startswith(("http://", "https://", "//"))
                  and "hwk-" not in u and not u.startswith("https://" + daten["domain"])]
    # Der Verweis auf die Kammer im Impressum ist ein Link, kein Nachladen.
    fremd = [f for f in fremd if "impressum" not in f]
    sagen(not fremd, "Nichts wird von fremden Servern geladen",
          "keine fremden Quellen" if not fremd else ", ".join(fremd))

    # 8 Kein Ereignis-Attribut. Waere ein Zeichen, dass Text als Markup
    #   durchgeschlagen ist.
    ereignisse = []
    for name, t in texte.items():
        p = _Links()
        p.feed(t)
        ereignisse += [f"{name}: {e}" for e in p.ereignisse]
    sagen(not ereignisse, "Kein Text ist als Markup durchgeschlagen",
          "sauber" if not ereignisse else ", ".join(ereignisse))

    # 9 Das Formular schickt an den Betrieb, nicht an uns.
    formular = _lesen(webroot / "pflege" / "formular.php")
    empf = re.search(r"const EMPFAENGER = '([^']+)';", formular)
    betrieb = re.search(r"const BETRIEB = '([^']+)';", formular)
    sagen(bool(empf) and empf.group(1) == daten["mail"],
          "Das Formular schickt an die Adresse des Betriebs",
          (empf.group(1) if empf else "keine Adresse gefunden"))
    sagen(bool(betrieb) and betrieb.group(1) == daten["firma"],
          "Der Betriebsname im Formular stimmt",
          (betrieb.group(1) if betrieb else "kein Name gefunden"))

    # 10 Der Rueckweg des Formulars zeigt auf Seiten, die es gibt.
    wege = re.findall(r"const ZURUECK(?:_FEHLER)? = '([^']+)';", formular)
    tot = [w for w in wege
           if not (webroot / w.split("?")[0].split("#")[0].lstrip("./")).is_file()]
    sagen(not tot, "Der Rueckweg des Formulars fuehrt auf vorhandene Seiten",
          ", ".join(wege) if not tot else "zeigt ins Leere: " + ", ".join(tot))

    # 11 Die Datenschutzerklaerung beschreibt, was der Code tut. Das ist der
    #    Fehler, der am leisesten passiert: Code aendern, Text vergessen.
    ds = texte["datenschutz.html"]
    speichert = "const ABLAGE" in formular
    grenze = re.search(r"const ABLAGE_HOECHSTENS = (\d+);", formular)
    stimmig = (not speichert) or ("auf dem Server" in _flach(ds)
                                  and "Datei" in ds)
    sagen(stimmig, "Die Datenschutzerklaerung beschreibt das Speichern",
          "Formular speichert und die Erklaerung sagt es"
          if speichert and stimmig else
          ("Formular speichert, die Erklaerung sagt es nicht" if speichert
           else "Formular speichert nicht"))
    if grenze:
        sagen(grenze.group(1) in ds,
              "Die genannte Obergrenze stimmt mit dem Code",
              f"Code: {grenze.group(1)}, in der Erklaerung "
              + ("genannt" if grenze.group(1) in ds else "NICHT genannt"))

    sagen(bool(daten["aufsichtsbehoerde"])
          and _flach(daten["aufsichtsbehoerde"]) in _flach(ds),
          "Die zustaendige Aufsichtsbehoerde steht in der Erklaerung",
          daten["aufsichtsbehoerde"] or "nicht hinterlegt")

    # 12 Der Pflegebereich ist der aus der Vorlage. Driftet er auseinander,
    #    erbt der naechste Kunde einen alten Fehler.
    abweichung = [n for n in PFLEGEDATEIEN
                  if _lesen(webroot / "pflege" / n)
                  != _lesen(wurzel / PFLEGE / n)]
    sagen(not abweichung, "Der Pflegebereich entspricht der Vorlage",
          "byteweise gleich" if not abweichung
          else "abweichend: " + ", ".join(abweichung))

    # 13 Kein Werkzeug und keine Reste im Paket.
    verboten = [str(p.relative_to(webroot)) for p in webroot.rglob("*")
                if p.name in ("selbsttest.php", "pruefung.php", "anfragen.php",
                              "anfragen-neu.php", "anfragen.lock")
                or p.name == "sicherungen"]
    sagen(not verboten, "Kein Werkzeug und keine Reste im Paket",
          "sauber" if not verboten else ", ".join(verboten))

    # 14 Jedes eingebundene Bild liegt auch dabei.
    fehlende_bilder = []
    for t in texte.values():
        for quelle in re.findall(r'<img src="([^"]+)"', t):
            if not (webroot / quelle).is_file():
                fehlende_bilder.append(quelle)
    sagen(not fehlende_bilder, "Jedes eingebundene Bild liegt im Paket",
          "vollstaendig" if not fehlende_bilder else ", ".join(fehlende_bilder))

    # 15 Keine Gedankenstriche.
    # Der Gedankenstrich als Zeichen, nicht als Text: sonst faende diese
    # Pruefung sich selbst.
    striche = [n for n, t in texte.items() if "\u2014" in t]
    sagen(not striche, "Keine Gedankenstriche in den Seiten",
          "keine" if not striche else ", ".join(striche))

    # 16 Nach dem Bau wurde nicht von Hand nachgebessert. Sonst baut der
    #    naechste Lauf die Handarbeit weg.
    hand = handarbeit_seit_bau(ordner)
    vermerkt = (ordner / ".gebaut").is_file()
    sagen(not hand, "Der gebaute Stand ist unveraendert",
          ("unveraendert seit dem Bau" if vermerkt
           else "von Hand gebaut, es gibt keinen Bau zum Vergleichen")
          if not hand
          else "seit dem Bau von Hand geaendert. Entweder die Aenderung nach "
               "texte.md oder stammdaten.json zurueckholen, oder neu bauen.")

    return b


def bericht(befunde: list[Befund]) -> str:
    gut = sum(1 for x in befunde if x.ok)
    zeilen = [f"{gut} von {len(befunde)} bestanden", ""]
    for x in befunde:
        zeilen.append(f"  {'ok  ' if x.ok else 'NEIN'}  {x.titel}")
        zeilen.append(f"        {x.detail}")
    zeilen += ["", "  Was der Pruefstand nicht messen kann:"]
    zeilen += [f"    - {z}" for z in NICHT_MESSBAR]
    return "\n".join(zeilen)
