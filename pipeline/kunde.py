"""Der Weg eines Kunden, von der Messung bis zur eigenen Domain.

Ein Betrieb durchlaeuft immer dieselben Stufen. Dieses Modul weiss, auf
welcher er gerade steht, und sagt, was als Naechstes dran ist -- fuer jeden
Betrieb einzeln, mit dem fertigen Befehl zum Kopieren.

Der Zustand wird **abgelesen, nicht gefuehrt**. Es gibt keine Datei, in der
steht "freigegeben: ja". Solche Dateien luegen irgendwann, weil jemand
vergisst, sie zu aendern. Stattdessen zaehlt, was auf der Platte liegt: gibt
es einen gebauten Stand, laeuft der Pruefstand durch, sind die Pakete neuer
als der Bau.

Zwei Dinge kann man nicht ablesen, weil sie ausserhalb des Rechners
passieren: dass der Betrieb zugesagt hat und dass er das Freigabeblatt
unterschrieben hat. Beides steht darum mit Datum in ``verlauf`` und wird von
Hand eingetragen. Genau diese zwei, kein drittes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from . import papiere, seite
from .pruefstand import pruefen
from .stammdaten import (ENTFAELLT, GEFRAGT, PFLICHT, Stammdaten, VOM_HOSTER,
                         aus_messung)
from .texte import lesen as texte_lesen, offene_stellen

STUDIE = Path("studie")

# Ordner in studie/, die keine Kunden sind.
KEINE_KUNDEN = {"pflege", "marke", "word", "eigene-website"}


@dataclass
class Lage:
    kurzname: str
    ordner: Path
    stufe: str
    erledigt: list[str]
    naechstes: str
    befehl: str
    offen_beim_menschen: list[str]

    @property
    def bereit_fuer_die_domain(self) -> bool:
        """Ob an der Domain gedreht werden darf.

        Zwei Unterschriften fehlen dafuer nie: die Zusage und das
        Freigabeblatt. Beim Umstellen kann die Firmenpost des Betriebs
        ausfallen, deshalb ist das kein Formfehler, sondern die Bremse.
        """
        return not self.offen_beim_menschen


def _kunden(wurzel: Path) -> list[Path]:
    return sorted(p for p in (wurzel / STUDIE).iterdir()
                  if p.is_dir() and p.name not in KEINE_KUNDEN
                  and not p.name.startswith("."))


def lage(ordner: Path, wurzel: Path = Path(".")) -> Lage:
    ordner = Path(ordner)
    name = ordner.name
    erledigt: list[str] = []

    menschlich: list[str] = []

    def fertig(stufe: str, naechstes: str, befehl: str) -> Lage:
        return Lage(name, ordner, stufe, erledigt, naechstes, befehl,
                    menschlich)

    if not (ordner / "stammdaten.json").is_file():
        return fertig("kein Kunde", "Anlegen, sobald der Betrieb zusagt.",
                      f"python -m pipeline kunde anlegen <messung-slug> "
                      f"--kurzname {name}")
    erledigt.append("angelegt")
    daten = Stammdaten.laden(ordner)
    if daten.verlauf.get("zugesagt_am"):
        erledigt.append("zugesagt")
    else:
        menschlich.append(
            "Der Betrieb hat noch nicht zugesagt. Sobald er es tut, das "
            "Datum in stammdaten.json unter verlauf.zugesagt_am eintragen.")
    if not daten.verlauf.get("freigabe_am"):
        menschlich.append(
            "Das Freigabeblatt ist nicht unterschrieben zurueck. Ohne "
            "Unterschrift wird an keiner Domain gedreht.")

    fehlt = daten.fehlend()
    if fehlt:
        return fertig("Angaben unvollstaendig",
                      f"{len(fehlt)} Angaben fehlen, sie kommen vom Betrieb: "
                      + ", ".join(fehlt[:5])
                      + (" ..." if len(fehlt) > 5 else ""),
                      f"python -m pipeline kunde erhebung {name}")
    erledigt.append("erhoben")

    if not (ordner / "texte.md").is_file():
        return fertig("Texte fehlen",
                      "Die Saetze der Seite schreiben. Fakten stehen in "
                      "stammdaten.json, hier gehoert die Prosa hin.",
                      f"{ordner}/texte.md anlegen")
    offen = offene_stellen(texte_lesen(ordner / "texte.md"))
    if offen:
        return fertig("Texte unfertig",
                      f"{len(offen)} Stellen sind noch Entwurf: {offen[0][:50]}",
                      f"{ordner}/texte.md")
    erledigt.append("getextet")

    if not (ordner / "webroot" / "index.html").is_file():
        return fertig("nicht gebaut", "Seite und Papiere bauen.",
                      f"python -m pipeline kunde bauen {name}")
    if seite.handarbeit_seit_bau(ordner):
        return fertig("von Hand geaendert",
                      "Seit dem Bau wurde im webroot von Hand geaendert. "
                      "Entweder die Aenderung nach texte.md zurueckholen "
                      "oder neu bauen.",
                      f"python -m pipeline kunde bauen {name}")
    erledigt.append("gebaut")

    befunde = pruefen(ordner, wurzel)
    schlecht = [b for b in befunde if not b.ok]
    if schlecht:
        return fertig("Pruefstand rot",
                      f"{len(schlecht)} Punkte offen: {schlecht[0].titel}",
                      f"python -m pipeline kunde pruefen {name}")
    erledigt.append("geprueft")

    if not (ordner / "FREIGABEBLATT.md").is_file():
        return fertig("Papiere fehlen", "Die vier Papiere bauen.",
                      f"python -m pipeline kunde bauen {name}")
    erledigt.append("papiere")

    zips = sorted(ordner.glob("*-website.zip")) + sorted(ordner.glob("*-TEST.zip"))
    gebaut_am = (ordner / "webroot" / "index.html").stat().st_mtime
    aktuell = [z for z in zips if z.stat().st_mtime >= gebaut_am]
    if len(aktuell) < 2:
        return fertig("nicht gepackt",
                      "Die beiden Pakete schnueren. Dabei wird ein neues "
                      "Passwort gewuerfelt und genau einmal angezeigt.",
                      f"python -m pipeline kunde packen {name}")
    erledigt.append("gepackt")

    if not daten.verlauf.get("freigabe_am"):
        return fertig("gepackt, wartet auf Freigabe",
                      "FREIGABEBLATT.md ausgedruckt zum Betrieb, "
                      "unterschrieben zurueck. Ohne Unterschrift wird an "
                      "keiner Domain gedreht: beim Umstellen kann seine "
                      "Firmenpost ausfallen. Danach Datum unter "
                      "verlauf.freigabe_am eintragen.",
                      "")
    erledigt.append("freigegeben")

    if not daten.verlauf.get("live_seit"):
        return fertig("bereit fuer den Livegang",
                      "LIVEGANG.md Abschnitt 4 und 5 abarbeiten. Danach "
                      "Datum unter verlauf.live_seit eintragen.",
                      f"{ordner}/LIVEGANG.md")
    erledigt.append("live")
    return fertig("live", "Fertig. Uebergabe nach ANLEITUNG.html.", "")


# ── Fragebogen ───────────────────────────────────────────────────────────

FRAGEN = {
    "firma": "Wie heisst der Betrieb genau, so wie er im Impressum stehen soll?",
    "inhaber": "Wer ist der Inhaber?",
    "strasse": "Strasse und Hausnummer",
    "plz": "Postleitzahl",
    "ort": "Ort",
    "telefon": "Telefonnummer, so geschrieben wie sie auf der Seite stehen soll",
    "mail": "E-Mail-Adresse fuer Anfragen",
    "domain": "Die Internetadresse ohne www, zum Beispiel musterbetrieb.de",
    "gewerk": "Das Gewerk, zum Beispiel Elektro, Heizung und Sanitaer, Maler",
    "untertitel": "Eine Zeile unter dem Firmennamen, zum Beispiel "
                  "\"Elektrotechnik und mehr . Bergheim\"",
    "einzugsgebiet": "Wo arbeitet der Betrieb, zum Beispiel "
                     "\"Bergheim und der Rhein-Erft-Kreis\"",
    "aufsichtsbehoerde": "Zustaendige Datenschutz-Aufsichtsbehoerde. In "
                         "Nordrhein-Westfalen: der Landesbeauftragten fuer "
                         "Datenschutz und Informationsfreiheit "
                         "Nordrhein-Westfalen",
    "fax": "Faxnummer",
    "ustid": "Umsatzsteuer-Identifikationsnummer",
    "handelsregister": "Handelsregister, zum Beispiel "
                       "\"Amtsgericht Koeln, HRA 12345\"",
    "handwerkskammer": "Handwerkskammer und Nummer",
    "ihk": "Industrie- und Handelskammer und Nummer",
    "berufsbezeichnung": "Berufsbezeichnung, zum Beispiel "
                         "\"Elektrotechnikerhandwerk\"",
    "kammer_aufsicht": "Welche Kammer fuehrt die Aufsicht?",
    "kammer_link": "Internetadresse dieser Kammer",
    "rechtsform": "Rechtsform, falls im Namen nicht schon enthalten",
    "mitarbeiter": "Wie viele Mitarbeiter?",
    "oeffnungszeiten": "Wann ist das Buero erreichbar?",
    "einsatzzeiten": "Arbeitet der Betrieb auch abends oder am Wochenende?",
    "anfahrt": "Woran erkennt man die kurze Anfahrt, zum Beispiel "
               "\"A61 . B477\"",
    "gegruendet": "Seit wann gibt es den Betrieb?",
    "hinweis": "Ein aktueller Hinweis, zum Beispiel Betriebsurlaub. Kann "
               "spaeter im Pflegebereich geaendert werden",
    "stellenanzeige": "Wird jemand gesucht? Sonst: sind Initiativbewerbungen "
                      "willkommen?",
    "hoster": "Bei wem liegt die Website heute?",
    "avv": "Gibt es mit dem Hoster einen Vertrag zur Auftragsverarbeitung "
           "nach Art. 28 DSGVO?",
    "protokolldauer": "Wie lange bewahrt der Hoster seine Protokolle auf?",
}


def erhebung(ordner: Path) -> Path:
    """Der Fragebogen fuer den Termin beim Betrieb.

    Vorbefuellt mit dem, was beim Messen seiner alten Seite gefunden wurde --
    aber als Vorschlag zum Abhaken, nie als Tatsache. Was er nicht bestaetigt,
    kommt nicht auf die Seite.
    """
    ordner = Path(ordner)
    daten = Stammdaten.laden(ordner)

    def block(titel: str, felder, erklaerung: str) -> list[str]:
        z = [f"## {titel}", "", erklaerung, ""]
        for f in felder:
            frage = FRAGEN.get(f, f)
            vorschlag = daten.bestaetigt.get(f, "") or daten.vermutet.get(f, "")
            woher = ("bereits bestaetigt" if daten.bestaetigt.get(f)
                     else "von der alten Seite, ungeprueft" if daten.vermutet.get(f)
                     else "")
            z.append(f"**{f}** - {frage}")
            z.append("")
            z.append(f"    {vorschlag}" if vorschlag else "    ")
            if woher:
                z.append(f"    ({woher})")
            z.append("")
        return z

    zeilen = [
        f"# Angaben fuer die Website: {daten.bestaetigt.get('firma') or daten.vermutet.get('firma') or daten.kurzname}",
        "",
        f"Stand {date.today().strftime('%d.%m.%Y')}. Zum Termin mitnehmen.",
        "",
        "Alles, was hier eingetragen wird, steht spaeter woertlich auf der",
        "Seite oder im Impressum. Was hier leer bleibt, bleibt auch dort leer:",
        "Der Bau bricht ab, statt sich etwas auszudenken.",
        "",
        f"Gibt es eine Angabe beim Betrieb wirklich nicht, kommt `{ENTFAELLT}`",
        "hinein. Das ist ein Unterschied mit Gewicht: leer heisst \"noch nicht",
        f"gefragt\", `{ENTFAELLT}` heisst \"gefragt, gibt es nicht\".",
        "",
        "Die Antworten danach nach `stammdaten.json` unter `bestaetigt`",
        "uebertragen.",
        "",
        "---",
        "",
    ]
    zeilen += block("Muss der Betrieb beantworten", PFLICHT,
                    "Ohne diese Angaben gibt es keine Seite.")
    zeilen += block("Muss gefragt werden, darf \"" + ENTFAELLT + "\" sein",
                    GEFRAGT,
                    "Diese Angaben braucht ein Impressum nur, wenn es sie "
                    "gibt. Weglassen ohne zu fragen waere ein Fehler.")
    zeilen += block("Kann der Betrieb beantworten", 
                    ("rechtsform", "mitarbeiter", "oeffnungszeiten",
                     "einsatzzeiten", "anfahrt", "gegruendet", "hinweis",
                     "stellenanzeige"),
                    "Schmueckt die Seite, blockiert sie aber nicht.")
    zeilen += block("Weiss nur sein Hostinganbieter", VOM_HOSTER,
                    "Solange das offen ist, steht dazu nichts in seiner "
                    "Datenschutzerklaerung. Lieber nichts als etwas Falsches.")
    zeilen += [
        "---",
        "",
        "## Fotos",
        "",
        "Fotos kommen vom Betrieb. Wir setzen kein gekauftes Bild ein, auf dem",
        "Menschen zu sehen sind, die nicht er ist, und wir verwenden sein Logo",
        "nicht.",
        "",
        "- [ ] Fotos erhalten, Anzahl: ____",
        "- [ ] Er darf sie verwenden (selbst gemacht oder Rechte vorhanden)",
        "",
    ]
    ziel = ordner / "ERHEBUNG.md"
    ziel.write_text("\n".join(zeilen), encoding="utf-8")
    return ziel
