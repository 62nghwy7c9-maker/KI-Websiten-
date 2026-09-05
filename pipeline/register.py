"""Kontakt-Register — welcher Betrieb wurde wann über welchen Weg angesprochen.

Struktur aus der Belegpipeline übernommen (Konzept, Abschnitt 13): eine flache
CSV-Datei mit einem `route`-Feld als Zustand. Daraus fällt die Dedup gegen bereits
kontaktierte Betriebe ohne Zusatzarbeit ab.

Bewusst CSV und nicht SQLite: Kira und Yannik müssen die Datei zur Not in Excel
öffnen und von Hand korrigieren können.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from .modelle import Kandidat, ROUTEN

SPALTEN = (
    "schluessel", "firma", "url", "host", "branche", "ort",
    "kontakt_mail", "telefon", "anschrift",
    "route", "kanal", "erstkontakt_am", "letzte_aenderung", "notiz",
    # Wer darf eine Werbemail bekommen, und warum duerfen wir das annehmen.
    # Kalte Werbemails an Betriebe brauchen nach § 7 Abs. 2 Nr. 2 UWG eine
    # Einwilligung, auch im B2B. Im Streitfall muss der Absender beweisen,
    # dass sie vorlag. Ein Gedaechtnis ist kein Beweis, eine Zeile hier schon.
    "einwilligung_am", "einwilligung_durch", "einwilligung_wie",
)

STANDARD_DATEI = Path("register/kontakte.csv")


def slug(text: str) -> str:
    """'Elektro Müller & Söhne GmbH' -> 'elektro-mueller-soehne-gmbh'."""
    text = (text or "").lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(a, b)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "ohne-namen"


def normhost(url: str) -> str:
    """Hostname ohne www und ohne Schema — die Grundlage für Dedup."""
    u = (url or "").strip()
    if u and "//" not in u:
        u = "http://" + u
    host = (urlsplit(u).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


class Register:
    """Liest und schreibt die Kontaktliste. Legt sie an, wenn sie fehlt."""

    def __init__(self, datei: Path | str = STANDARD_DATEI) -> None:
        self.datei = Path(datei)
        self.zeilen: list[dict[str, str]] = []
        self._laden()

    # ── Lesen und Schreiben ──────────────────────────────────────────────────

    def _laden(self) -> None:
        if not self.datei.exists():
            self.zeilen = []
            return
        with self.datei.open(encoding="utf-8-sig", newline="") as f:
            self.zeilen = [
                {s: (r.get(s) or "").strip() for s in SPALTEN}
                for r in csv.DictReader(f, delimiter=";")
            ]

    def speichern(self) -> Path:
        self.datei.parent.mkdir(parents=True, exist_ok=True)
        with self.datei.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=SPALTEN, delimiter=";")
            w.writeheader()
            w.writerows(self.zeilen)
        return self.datei

    # ── Abfragen ─────────────────────────────────────────────────────────────

    def finde(self, kandidat: Kandidat) -> dict[str, str] | None:
        """Treffer über den Hostnamen, ersatzweise über Firma und Ort.

        Der Host ist der verlässlichere Schlüssel: Firmennamen werden
        unterschiedlich geschrieben, die Domain nicht.
        """
        host = normhost(kandidat.url)
        if host:
            for z in self.zeilen:
                if z["host"] == host:
                    return z
        s = kandidat.schluessel()
        for z in self.zeilen:
            if z["schluessel"] == s:
                return z
        return None

    def bereits_kontaktiert(self, kandidat: Kandidat) -> bool:
        """True, sobald ein Check tatsächlich rausgegangen ist.

        'neu' und 'pruefung' zählen nicht — solange nichts versendet wurde,
        darf ein Kandidat neu bewertet werden.
        """
        z = self.finde(kandidat)
        return bool(z and z["route"] in ("versendet", "abgelehnt"))

    def route_von(self, kandidat: Kandidat) -> str | None:
        z = self.finde(kandidat)
        return z["route"] if z else None

    def nach_route(self, route: str) -> list[dict[str, str]]:
        return [z for z in self.zeilen if z["route"] == route]

    def darf_mail(self, schluessel: str) -> bool:
        """Ob an diesen Betrieb eine Werbemail gehen darf.

        Nur wenn eine Einwilligung eingetragen ist und eine Mailadresse
        vorliegt. Fehlt eines von beidem, bleibt der Weg der Brief oder das
        persoenliche Gespraech.
        """
        z = next((x for x in self.zeilen if x["schluessel"] == schluessel), None)
        return bool(z and z.get("einwilligung_am") and z.get("kontakt_mail"))

    def mit_einwilligung(self) -> list[dict[str, str]]:
        return [z for z in self.zeilen
                if z.get("einwilligung_am") and z.get("kontakt_mail")]

    # ── Schreiben ────────────────────────────────────────────────────────────

    def eintragen(self, kandidat: Kandidat, route: str = "neu",
                  kanal: str = "", notiz: str = "") -> dict[str, str]:
        """Legt an oder aktualisiert. Überschreibt nie stillschweigend Daten."""
        if route not in ROUTEN:
            raise ValueError(f"Unbekannte Route {route!r}. Erlaubt: {', '.join(ROUTEN)}")
        heute = date.today().isoformat()
        z = self.finde(kandidat)
        if z is None:
            z = {s: "" for s in SPALTEN}
            z.update(
                schluessel=kandidat.schluessel(),
                firma=kandidat.firma,
                url=kandidat.url,
                host=normhost(kandidat.url),
                branche=kandidat.branche,
                ort=kandidat.ort,
                kontakt_mail=kandidat.kontakt_mail,
                telefon=kandidat.telefon,
                anschrift=kandidat.anschrift,
            )
            self.zeilen.append(z)
        else:
            # Nur leere Felder auffüllen — vorhandene Angaben gewinnen.
            for feld, wert in (
                ("firma", kandidat.firma), ("url", kandidat.url),
                ("branche", kandidat.branche), ("ort", kandidat.ort),
                ("kontakt_mail", kandidat.kontakt_mail),
                ("telefon", kandidat.telefon), ("anschrift", kandidat.anschrift),
            ):
                if wert and not z.get(feld):
                    z[feld] = wert
        z["route"] = route
        if kanal:
            z["kanal"] = kanal
        if notiz:
            z["notiz"] = (z["notiz"] + " | " + notiz).strip(" |") if z["notiz"] else notiz
        if route == "versendet" and not z["erstkontakt_am"]:
            z["erstkontakt_am"] = heute
        z["letzte_aenderung"] = heute
        return z

    def einwilligung(self, schluessel: str, durch: str, wie: str,
                     am: str = "") -> dict[str, str]:
        """Haelt fest, dass der Betrieb einer Zusendung zugestimmt hat.

        ``durch`` ist der Mensch, der gefragt hat, ``wie`` die Gelegenheit
        (Telefonat, Besuch, Messe). Beides gehoert dazu: Im Streitfall zaehlt
        nicht, dass jemand zugestimmt hat, sondern wer das bezeugen kann.
        """
        z = next((x for x in self.zeilen if x["schluessel"] == schluessel), None)
        if z is None:
            raise KeyError(f"Kein Eintrag mit Schluessel {schluessel!r}")
        if not durch.strip() or not wie.strip():
            raise ValueError("Einwilligung ohne Zeugen und Anlass ist keine. "
                             "durch und wie muessen gefuellt sein.")
        z["einwilligung_am"] = am or date.today().isoformat()
        z["einwilligung_durch"] = durch.strip()
        z["einwilligung_wie"] = wie.strip()
        z["letzte_aenderung"] = date.today().isoformat()
        return z
