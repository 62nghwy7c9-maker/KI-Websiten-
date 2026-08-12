"""Stufe 0 — Betriebe finden.

Quelle ist OpenStreetMap. Kein Konto, keine Kosten, keine Nutzungsgebühr, und
die Daten enthalten genau die zwei Felder, auf die es ankommt: Branche und
Website (oder eben keine).

Zwei Wege, bewusst in dieser Reihenfolge:

1. **Über die Datei.** `abfrage()` baut die fertige Overpass-Abfrage. Die kommt
   nach https://overpass-turbo.eu, wird dort ausgeführt und als GeoJSON/JSON
   gespeichert. `aus_datei()` liest sie ein. Das funktioniert immer.
2. **Live.** `live_holen()` fragt die Overpass-API direkt. Bequemer, aber die
   öffentlichen Server sind oft überlastet oder drosseln nach IP. Deshalb nur
   Kür, nie Voraussetzung.

Zwei Sorten Fund, beide brauchbar:
  - Betrieb **mit** Website  → Kandidat für den Website-Check.
  - Betrieb **ohne** Website → anderes Gespräch („Sie sind online nicht zu
    finden"), oft der leichtere Abschluss. Wird mitgeführt, nicht weggeworfen.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .modelle import Kandidat

SPIEGEL = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
)

KOPF = {"User-Agent": "website-check/0.1 (OSM-Abfrage, geringe Frequenz)"}

# OSM-Merkmale je Branche. Bewusst knapp gehalten: lieber wenige, sichere
# Kategorien als eine breite Abfrage, die halb Kerpen zurückgibt.
BRANCHEN: dict[str, tuple[str, ...]] = {
    "gastro": (
        '["amenity"~"^(restaurant|fast_food|cafe|bar|pub|biergarten|ice_cream)$"]',
    ),
    "handwerk": (
        '["craft"]',
        '["shop"~"^(car_repair|hairdresser|bakery|butcher|florist|optician)$"]',
    ),
    "verein": (
        '["office"="association"]',
        '["club"]',
    ),
}

WEBSITE_FELDER = ("website", "contact:website", "url", "contact:url")


@dataclass(frozen=True)
class Fund:
    """Ein Betrieb aus OpenStreetMap, noch ungemessen."""

    name: str
    url: str
    branche: str
    ort: str
    strasse: str = ""
    telefon: str = ""
    osm_id: str = ""

    @property
    def hat_website(self) -> bool:
        return bool(self.url)

    def als_kandidat(self) -> Kandidat:
        return Kandidat(firma=self.name, url=self.url, branche=self.branche,
                        ort=self.ort, kontakt_mail="")


def abfrage(lat: float, lon: float, umkreis_km: float = 10,
            branche: str = "gastro") -> str:
    """Baut die Overpass-Abfrage. Direkt in overpass-turbo.eu einfügbar."""
    merkmale = BRANCHEN.get(branche) or tuple(
        m for gruppe in BRANCHEN.values() for m in gruppe)
    radius = int(umkreis_km * 1000)
    zeilen = []
    for m in merkmale:
        for art in ("node", "way"):
            zeilen.append(f'  {art}{m}(around:{radius},{lat},{lon});')
    return ("[out:json][timeout:90];\n(\n" + "\n".join(zeilen) +
            "\n);\nout center tags;")


def abfrage_nach_ort(ort: str, umkreis_km: float = 10,
                     branche: str = "gastro") -> str:
    """Variante für overpass-turbo: dort löst {{geocodeArea}} den Ortsnamen auf.

    Über die API funktioniert das *nicht* — dafür braucht es `abfrage()` mit
    Koordinaten.
    """
    merkmale = BRANCHEN.get(branche) or tuple(
        m for gruppe in BRANCHEN.values() for m in gruppe)
    zeilen = []
    for m in merkmale:
        for art in ("node", "way"):
            zeilen.append(f'  {art}{m}(area.suchgebiet);')
    return (f'[out:json][timeout:90];\n'
            f'{{{{geocodeArea:{ort}}}}}->.suchgebiet;\n(\n'
            + "\n".join(zeilen) + "\n);\nout center tags;")


def _ort_aus(tags: dict, vorgabe: str) -> str:
    return (tags.get("addr:city") or tags.get("addr:town")
            or tags.get("addr:village") or vorgabe)


def _branche_aus(tags: dict, vorgabe: str) -> str:
    if tags.get("amenity") in {"restaurant", "fast_food", "cafe", "bar", "pub",
                               "biergarten", "ice_cream"}:
        return "gastro"
    if tags.get("craft") or tags.get("shop") in {"car_repair", "hairdresser",
                                                 "bakery", "butcher"}:
        return "handwerk"
    if tags.get("club") or tags.get("office") == "association":
        return "verein"
    return vorgabe


def _saeubern(roh: str) -> str:
    """Macht aus einem OSM-Website-Wert eine brauchbare Adresse — oder nichts.

    OSM enthält viel Unsauberes: Facebook-Seiten, Instagram-Profile, leere
    Werte, Mehrfachangaben mit Semikolon. Ein Facebook-Auftritt ist kein
    Kandidat für einen Website-Check, sondern ein Betrieb *ohne* Website.
    """
    wert = (roh or "").split(";")[0].strip()
    if not wert or wert.lower() in {"no", "none", "-"}:
        return ""
    ohne = wert.split("//")[-1].lower()
    fremd = ("facebook.", "instagram.", "linktr.ee", "wa.me", "tiktok.",
             "google.com/maps", "goo.gl", "lieferando.", "wolt.", "ubereats.")
    if any(f in ohne for f in fremd):
        return ""
    return wert


def aus_json(text: str, ort_vorgabe: str = "",
             branche_vorgabe: str = "") -> list[Fund]:
    """Liest eine Overpass-Antwort (JSON) und macht Funde daraus.

    Verträgt beide Formen, die overpass-turbo speichert: die rohe API-Antwort
    mit `elements` und das exportierte GeoJSON mit `features`.
    """
    daten = json.loads(text)
    roh = daten.get("elements")
    if roh is None:
        roh = [{"tags": f.get("properties", {}), "id": f.get("id", "")}
               for f in daten.get("features", [])]

    funde: list[Fund] = []
    gesehen: set[str] = set()
    for e in roh:
        tags = e.get("tags") or {}
        name = (tags.get("name") or "").strip()
        if not name:
            continue  # ohne Namen kein Anschreiben
        schluessel = name.lower() + "|" + (tags.get("addr:street") or "")
        if schluessel in gesehen:
            continue
        gesehen.add(schluessel)

        url = ""
        for feld in WEBSITE_FELDER:
            url = _saeubern(tags.get(feld, ""))
            if url:
                break

        hausnr = tags.get("addr:housenumber", "")
        strasse = " ".join(x for x in (tags.get("addr:street", ""), hausnr) if x)
        funde.append(Fund(
            name=name,
            url=url,
            branche=_branche_aus(tags, branche_vorgabe),
            ort=_ort_aus(tags, ort_vorgabe),
            strasse=strasse,
            telefon=tags.get("phone") or tags.get("contact:phone") or "",
            osm_id=str(e.get("id", "")),
        ))
    return funde


def aus_datei(pfad: Path | str, ort_vorgabe: str = "",
              branche_vorgabe: str = "") -> list[Fund]:
    return aus_json(Path(pfad).read_text(encoding="utf-8"),
                    ort_vorgabe, branche_vorgabe)


def live_holen(ql: str, versuche: int = 3) -> tuple[str | None, str]:
    """Fragt die Overpass-API. Gibt (Antworttext, Fehlermeldung) zurück.

    Die öffentlichen Server sind Gemeingut: bei 429 wird gewartet, nicht
    schneller nachgefragt. Schlägt alles fehl, ist das kein Programmfehler —
    dann gilt der Weg über overpass-turbo.
    """
    letzter = ""
    for i in range(versuche):
        for basis in SPIEGEL:
            try:
                anfrage = urllib.request.Request(
                    basis, data=urllib.parse.urlencode({"data": ql}).encode(),
                    headers=KOPF)
                with urllib.request.urlopen(anfrage, timeout=90) as antwort:
                    return antwort.read().decode("utf-8", "replace"), ""
            except urllib.error.HTTPError as e:
                letzter = f"{basis.split('/')[2]}: HTTP {e.code}"
                if e.code == 429:
                    time.sleep(5 * (i + 1))
            except Exception as e:  # Netzfehler, Zeitüberschreitung
                letzter = f"{basis.split('/')[2]}: {type(e).__name__}"
        time.sleep(2 ** i)
    return None, letzter or "kein Server erreichbar"


def sortieren(funde: list[Fund]) -> tuple[list[Fund], list[Fund]]:
    """Trennt in „hat Website" (Check-Kandidaten) und „hat keine" (anderes Gespräch)."""
    mit = sorted((f for f in funde if f.hat_website), key=lambda f: f.name)
    ohne = sorted((f for f in funde if not f.hat_website), key=lambda f: f.name)
    return mit, ohne
