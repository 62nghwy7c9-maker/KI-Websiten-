"""Lead-Listen einlesen — egal in welcher Form sie ankommen.

Listen entstehen unterwegs: als Markdown-Tabelle in einer Notiz, als CSV aus
einem Export, als Semikolon-Datei aus Excel. Dieses Modul erkennt die Form
selbst und ordnet die Spalten über Namensvarianten zu, damit niemand vorher
Kopfzeilen umbenennen muss.

Was nicht erkannt wird, wird gemeldet — nicht stillschweigend verworfen. Eine
Lead-Liste, aus der beim Einlesen unbemerkt drei Betriebe verschwinden, ist
schlimmer als gar keine.
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from pathlib import Path

from .finden import _saeubern
from .modelle import Kandidat

# Spaltennamen, wie sie in echten Listen vorkommen. Kleingeschrieben verglichen,
# Umlaute und Bindestriche vorher entfernt.
SPALTEN: dict[str, tuple[str, ...]] = {
    "firma": ("betrieb", "firma", "name", "unternehmen", "company", "kunde"),
    "url": ("website", "url", "webseite", "homepage", "internet", "seite",
            "domain"),
    "branche": ("gewerk", "branche", "kategorie", "sparte", "art"),
    "ort": ("ort", "stadt", "standort", "sitz", "plz ort"),
    "telefon": ("telefon", "tel", "telefonnummer", "phone", "rufnummer"),
    "mail": ("email", "e mail", "mail", "kontakt mail", "emailadresse"),
    "inhaber": ("inhaber", "ansprechpartner", "geschaeftsfuehrer", "kontakt",
                "person"),
    "notiz": ("begruendung", "notiz", "bemerkung", "befund", "kommentar",
              "eignung"),
}

# Gewerke aus der Liste auf die drei Branchen des Prüfkatalogs abbilden.
GEWERKE_HANDWERK = (
    "elektro", "shk", "sanitaer", "heizung", "klima", "maler", "galabau",
    "garten", "dachdecker", "dach", "zimmer", "tischler", "schreiner",
    "fenster", "tueren", "bau", "installateur", "metall", "fliesen",
    "trockenbau", "geruest", "stuck", "schlosser", "estrich",
)
GEWERKE_GASTRO = ("gastro", "restaurant", "imbiss", "cafe", "baeckerei", "hotel")


def _norm(text: str) -> str:
    """Kopfzeilen vergleichbar machen: klein, ohne Umlaute, ohne Sonderzeichen."""
    t = (text or "").strip().lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9 ]+", " ", t).strip()


def _branche_aus_gewerk(gewerk: str) -> str:
    g = _norm(gewerk)
    if any(w in g for w in GEWERKE_HANDWERK):
        return "handwerk"
    if any(w in g for w in GEWERKE_GASTRO):
        return "gastro"
    if "verein" in g or "club" in g:
        return "verein"
    return ""


def _zuordnen(kopf: list[str]) -> dict[str, int]:
    """Ordnet Spaltenüberschriften den bekannten Feldern zu.

    Erst exakt, dann als Teilwort — damit „PLZ / Ort" und „E-Mail (Inhaber)"
    ebenfalls greifen.
    """
    normiert = [_norm(k) for k in kopf]
    treffer: dict[str, int] = {}
    for feld, namen in SPALTEN.items():
        for i, k in enumerate(normiert):
            if i in treffer.values():
                continue
            if k in namen:
                treffer[feld] = i
                break
        if feld not in treffer:
            for i, k in enumerate(normiert):
                if i in treffer.values() or not k:
                    continue
                if any(n in k or k in n for n in namen):
                    treffer[feld] = i
                    break
    return treffer


@dataclass
class Lead:
    firma: str
    url: str
    branche: str = ""
    ort: str = ""
    telefon: str = ""
    mail: str = ""
    inhaber: str = ""
    notiz: str = ""

    @property
    def hat_website(self) -> bool:
        return bool(self.url)

    def als_kandidat(self) -> Kandidat:
        return Kandidat(firma=self.firma, url=self.url, branche=self.branche,
                        ort=self.ort, kontakt_mail=self.mail,
                        telefon=self.telefon, inhaber=self.inhaber)


@dataclass
class Einlesen:
    """Ergebnis eines Imports — samt allem, was nicht geklappt hat."""

    leads: list[Lead] = field(default_factory=list)
    uebersprungen: list[str] = field(default_factory=list)
    """Zeilen ohne Firmennamen oder ohne brauchbare Adresse, mit Begründung."""
    spalten: dict[str, str] = field(default_factory=dict)
    """Welche Kopfzeile auf welches Feld gelegt wurde — zum Nachprüfen."""


def _zeilen_aus_markdown(text: str) -> list[list[str]]:
    """Zieht alle Zeilen aus allen Markdown-Tabellen des Dokuments.

    Mehrere Tabellen (etwa „Gruppe 1" und „Gruppe 2") werden zusammengefasst;
    jede bringt ihre eigene Kopfzeile mit, deshalb wird je Tabelle zugeordnet.
    """
    blöcke: list[list[list[str]]] = []
    aktuell: list[list[str]] = []
    for zeile in text.splitlines():
        s = zeile.strip()
        if s.startswith("|") and s.endswith("|") and s.count("|") >= 3:
            felder = [f.strip() for f in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", f or "-") for f in felder):
                continue  # Trennzeile ---|---
            aktuell.append(felder)
        elif aktuell:
            blöcke.append(aktuell)
            aktuell = []
    if aktuell:
        blöcke.append(aktuell)
    return [b for b in blöcke if len(b) >= 2]  # type: ignore[misc]


def _zeilen_aus_tabelle(text: str) -> list[list[str]]:
    """CSV oder TSV, Trennzeichen wird geraten."""
    probe = text[:4000]
    try:
        dialekt = csv.Sniffer().sniff(probe, delimiters=";,\t|")
    except csv.Error:
        dialekt = csv.excel
        dialekt.delimiter = ";" if probe.count(";") > probe.count(",") else ","
    return [z for z in csv.reader(io.StringIO(text), dialekt) if any(z)]


def einlesen(text: str, ort_vorgabe: str = "",
             branche_vorgabe: str = "") -> Einlesen:
    """Liest eine Lead-Liste. Erkennt Markdown-Tabelle, CSV und TSV selbst."""
    ergebnis = Einlesen()
    tabellen: list[list[list[str]]]
    if "|" in text and re.search(r"^\s*\|.*\|\s*$", text, re.M):
        tabellen = _zeilen_aus_markdown(text)  # type: ignore[assignment]
    else:
        tabellen = [_zeilen_aus_tabelle(text)]

    gesehen: set[str] = set()
    for tabelle in tabellen:
        if len(tabelle) < 2:
            continue
        kopf, *zeilen = tabelle
        felder = _zuordnen(kopf)
        if "firma" not in felder or "url" not in felder:
            ergebnis.uebersprungen.append(
                f"Tabelle mit Kopfzeile „{' | '.join(kopf[:4])}…“ übersprungen: "
                f"keine Spalte für Betrieb bzw. Website erkennbar.")
            continue
        for feld, i in felder.items():
            ergebnis.spalten.setdefault(feld, kopf[i])

        def hol(z: list[str], feld: str) -> str:
            i = felder.get(feld)
            return z[i].strip() if i is not None and i < len(z) else ""

        for z in zeilen:
            firma = hol(z, "firma")
            if not firma:
                continue
            roh_url = hol(z, "url")
            url = _saeubern(re.sub(r"^\[|\]\(.*$", "", roh_url))
            if not url:
                ergebnis.uebersprungen.append(
                    f"{firma}: keine eigene Website in der Liste"
                    + (f" (eingetragen: {roh_url})" if roh_url else ""))
                continue
            schluessel = _norm(firma)
            if schluessel in gesehen:
                ergebnis.uebersprungen.append(f"{firma}: Dublette")
                continue
            gesehen.add(schluessel)

            gewerk = hol(z, "branche")
            ergebnis.leads.append(Lead(
                firma=firma,
                url=url,
                branche=_branche_aus_gewerk(gewerk) or branche_vorgabe,
                ort=hol(z, "ort") or ort_vorgabe,
                telefon=hol(z, "telefon"),
                mail=hol(z, "mail"),
                inhaber=hol(z, "inhaber"),
                notiz=hol(z, "notiz")[:200],
            ))
    return ergebnis


def aus_datei(pfad: Path | str, ort_vorgabe: str = "",
              branche_vorgabe: str = "") -> Einlesen:
    p = Path(pfad)
    if p.suffix.lower() in {".xlsx", ".xls"}:
        raise SystemExit(
            f"{p.name} ist eine Excel-Datei. In Excel „Speichern unter“ → "
            f"„CSV UTF-8“ wählen und die CSV übergeben.")
    return einlesen(p.read_text(encoding="utf-8-sig"), ort_vorgabe, branche_vorgabe)
