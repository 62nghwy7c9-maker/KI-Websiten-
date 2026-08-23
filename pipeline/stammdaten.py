"""Die Fakten eines Kundenbetriebs, an einer Stelle.

Alles, was auf der fertigen Website steht und nicht Prosa ist, kommt aus
dieser Datei: Anschrift fuers Impressum, Telefonnummer fuer die Ruf-Leiste,
Kammernummern, Oeffnungszeiten. Aus derselben Datei entstehen auch die fuenf
Papiere, die der Betrieb bekommt.

Zwei Bloecke, und der Unterschied zwischen ihnen ist der Kern des Ganzen:

  vermutet     Was wir beim Messen seiner alten Seite gefunden haben.
               Ungeprueft. Wird nur benutzt, um den Fragebogen vorzubefuellen,
               damit Kira im Termin nicht alles abtippt.
  bestaetigt   Was der Betrieb selbst gesagt hat. Nur das kommt auf die Seite.

Ein leeres Pflichtfeld laesst den Bau scheitern. Es gibt keinen Platzhalter,
der aus Versehen live gehen kann, und keine Zahl, die wir uns ausdenken.

Fuer Felder, die es beim Betrieb wirklich nicht gibt, steht ``entfaellt``.
Das ist ein Unterschied mit Gewicht: leer heisst "noch nicht gefragt",
``entfaellt`` heisst "gefragt, gibt es nicht". Ein Impressum ohne
Umsatzsteuer-ID kann richtig sein. Ein Impressum, bei dem niemand gefragt
hat, ist es nie.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

ENTFAELLT = "entfaellt"

# Ohne diese Felder gibt es keine Seite. Jedes steht entweder im Impressum
# (dann verlangt es § 5 DDG) oder im Kopf jeder Seite (dann faellt es sofort
# auf, wenn es fehlt).
PFLICHT = (
    "firma", "inhaber", "strasse", "plz", "ort",
    "telefon", "mail", "domain", "gewerk", "untertitel", "einzugsgebiet",
    # Die zustaendige Aufsichtsbehoerde haengt am Bundesland und steht in der
    # Datenschutzerklaerung. Sie laesst sich nicht aus der Anschrift ableiten,
    # ohne sie nachzuschlagen -- also wird sie gefragt.
    "aufsichtsbehoerde",
)

# Diese darf der Betrieb mit ``entfaellt`` beantworten, leer aber nicht.
# Es sind genau die Angaben, die ein Impressum nur dann braucht, wenn es sie
# gibt -- und bei denen das Weglassen ohne Nachfrage ein Fehler waere.
GEFRAGT = (
    "fax", "ustid", "handelsregister", "handwerkskammer", "ihk",
    "berufsbezeichnung", "kammer_aufsicht", "kammer_link",
)

# Der Rest: schmueckt die Seite, blockiert sie aber nicht.
FREIWILLIG = (
    "rechtsform", "mitarbeiter", "oeffnungszeiten", "einsatzzeiten",
    "anfahrt", "gegruendet", "hinweis", "stellenanzeige",
)

# Was erst der Hoster des Betriebs beantworten kann. Solange es fehlt, steht
# dazu nichts in seiner Datenschutzerklaerung. Lieber nichts als etwas
# Falsches.
VOM_HOSTER = ("hoster", "avv", "protokolldauer")

ALLE_FELDER = PFLICHT + GEFRAGT + FREIWILLIG + VOM_HOSTER


def waehlbar(telefon: str) -> str:
    """Macht aus einer geschriebenen Nummer die Fassung fuer ``tel:``.

    ``02271 45550`` wird zu ``+492271455 50``, ohne Leerzeichen. Klappt das
    nicht sicher, kommt ein leerer Text zurueck und der Bau fragt nach,
    statt zu raten. Eine falsche Rufnummer auf einer Handwerkerseite ist
    schlimmer als gar keine.
    """
    roh = re.sub(r"[^\d+]", "", telefon or "")
    if roh.startswith("+49") and len(roh) >= 9:
        return roh
    if roh.startswith("0049"):
        roh = "+49" + roh[4:]
        return roh if len(roh) >= 9 else ""
    if roh.startswith("0") and len(roh) >= 8:
        return "+49" + roh[1:]
    return ""


@dataclass
class Stammdaten:
    kurzname: str
    bestaetigt: dict[str, str] = field(default_factory=dict)
    vermutet: dict[str, str] = field(default_factory=dict)
    farbe: str = ""
    bilder: dict[str, dict[str, str]] = field(default_factory=dict)
    verlauf: dict[str, str] = field(default_factory=dict)
    quelle: str = ""

    # ── Lesen und Schreiben ──────────────────────────────────────────────

    @classmethod
    def laden(cls, ordner: Path) -> "Stammdaten":
        datei = Path(ordner) / "stammdaten.json"
        if not datei.is_file():
            raise SystemExit(f"Keine Stammdaten in {ordner}. "
                             f"Erst anlegen: python -m pipeline kunde anlegen ...")
        d = json.loads(datei.read_text(encoding="utf-8"))
        return cls(
            kurzname=d.get("kurzname", Path(ordner).name),
            bestaetigt={k: str(v) for k, v in d.get("bestaetigt", {}).items()},
            vermutet={k: str(v) for k, v in d.get("vermutet", {}).items()},
            farbe=d.get("farbe", ""),
            bilder=d.get("bilder", {}),
            verlauf=d.get("verlauf", {}),
            quelle=d.get("quelle", ""),
        )

    def speichern(self, ordner: Path) -> Path:
        datei = Path(ordner) / "stammdaten.json"
        inhalt = {
            "kurzname": self.kurzname,
            "quelle": self.quelle,
            "farbe": self.farbe,
            "bestaetigt": {k: self.bestaetigt.get(k, "") for k in ALLE_FELDER},
            "vermutet": {k: v for k, v in self.vermutet.items() if v},
            "bilder": self.bilder,
            "verlauf": self.verlauf,
        }
        datei.write_text(
            json.dumps(inhalt, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        return datei

    # ── Zugriff ──────────────────────────────────────────────────────────

    def __getitem__(self, feld: str) -> str:
        """Der bestaetigte Wert. ``entfaellt`` wird zu leer, denn auf der
        Seite soll dann nichts stehen, nicht das Wort."""
        wert = self.bestaetigt.get(feld, "").strip()
        return "" if wert == ENTFAELLT else wert

    def hat(self, feld: str) -> bool:
        return bool(self[feld])

    @property
    def anschrift(self) -> str:
        return f"{self['strasse']}, {self['plz']} {self['ort']}"

    @property
    def telefon_wahl(self) -> str:
        eigen = self.bestaetigt.get("telefon_wahl", "").strip()
        return eigen or waehlbar(self["telefon"])

    # ── Pruefung ─────────────────────────────────────────────────────────

    def fehlend(self) -> list[str]:
        """Was den Bau blockiert, in der Reihenfolge zum Nachfragen."""
        offen = [f for f in PFLICHT if not self.bestaetigt.get(f, "").strip()]
        offen += [f for f in GEFRAGT if not self.bestaetigt.get(f, "").strip()]
        if not self.telefon_wahl and self.bestaetigt.get("telefon", "").strip():
            offen.append("telefon_wahl")
        return offen

    def baubereit(self) -> bool:
        return not self.fehlend()


def aus_messung(pfad: Path, kurzname: str) -> Stammdaten:
    """Zieht aus der Messung seiner alten Seite, was als Vermutung taugt.

    Nichts davon geht ungeprueft auf die neue Seite. Der Fragebogen zeigt es
    dem Betrieb zum Bestaetigen oder Korrigieren, und mehr soll es auch nicht
    leisten: es nimmt das Abtippen ab, nicht das Nachfragen.
    """
    d = json.loads(Path(pfad).read_text(encoding="utf-8"))
    k = d.get("kandidat", {})
    host = re.sub(r"^https?://(www\.)?", "", k.get("url", "")).strip("/")

    vermutet = {
        "firma": k.get("firma", ""),
        "inhaber": k.get("inhaber", ""),
        "ort": k.get("ort", ""),
        "telefon": k.get("telefon", ""),
        "mail": k.get("kontakt_mail", ""),
        "domain": host.split("/")[0],
        "gewerk": k.get("gewerk", ""),
    }
    anschrift = k.get("anschrift", "")
    if anschrift:
        vermutet["strasse"] = anschrift

    s = Stammdaten(kurzname=kurzname, quelle=str(Path(pfad).parent))
    s.vermutet = {a: b for a, b in vermutet.items() if b}
    return s
