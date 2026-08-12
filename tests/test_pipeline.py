"""Tests für Stufe 0 und 1. Laufen ohne Netz — die Gophai-Seite liegt als Fixture."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline import katalog as K
from pipeline.messung import (
    _Seite, _ist_baukasten, _mailadressen, _telefonnummer_sichtbar,
    _verwechselbare_mails,
)
from pipeline.modelle import Kandidat, Pruefbericht
from pipeline.register import Register, normhost, slug

FIXTURE = Path(__file__).parent.parent / "fixtures" / "gophai" / "startseite.html"


@pytest.fixture(scope="module")
def gophai() -> _Seite:
    s = _Seite()
    s.feed(FIXTURE.read_text(encoding="utf-8"))
    return s


# ── Register ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("roh, erwartet", [
    ("Elektro Müller & Söhne GmbH", "elektro-mueller-soehne-gmbh"),
    ("Gophai Thai Imbiss", "gophai-thai-imbiss"),
    ("  ", "ohne-namen"),
    ("Straßenbau Weiß", "strassenbau-weiss"),
])
def test_slug(roh, erwartet):
    assert slug(roh) == erwartet


@pytest.mark.parametrize("roh, erwartet", [
    ("https://www.beispiel.de/pfad", "beispiel.de"),
    ("beispiel.de", "beispiel.de"),
    ("http://WWW.Beispiel.DE", "beispiel.de"),
    ("gophai-thaiimbiss.metro.bar", "gophai-thaiimbiss.metro.bar"),
    ("", ""),
])
def test_normhost(roh, erwartet):
    assert normhost(roh) == erwartet


def test_register_legt_an_und_dedupliziert(tmp_path):
    datei = tmp_path / "kontakte.csv"
    reg = Register(datei)
    k = Kandidat(firma="Elektro Müller", url="https://elektro-mueller.de", ort="Kerpen")

    reg.eintragen(k, route="pruefung")
    reg.speichern()
    assert len(Register(datei).zeilen) == 1

    # Dieselbe Firma über eine andere Schreibweise der URL: kein zweiter Eintrag.
    reg2 = Register(datei)
    reg2.eintragen(Kandidat(firma="Elektro Mueller GmbH",
                            url="http://www.elektro-mueller.de/kontakt",
                            ort="Kerpen"), route="pruefung")
    reg2.speichern()
    assert len(Register(datei).zeilen) == 1


def test_bereits_kontaktiert_erst_ab_versendet(tmp_path):
    datei = tmp_path / "kontakte.csv"
    reg = Register(datei)
    k = Kandidat(firma="Sanitär Weber", url="https://weber-sanitaer.de")

    reg.eintragen(k, route="pruefung")
    assert reg.bereits_kontaktiert(k) is False, "vor dem Versand darf neu bewertet werden"

    reg.eintragen(k, route="versendet", kanal="post")
    assert reg.bereits_kontaktiert(k) is True
    assert reg.finde(k)["erstkontakt_am"], "Erstkontakt-Datum muss gesetzt sein"


def test_register_ueberschreibt_vorhandene_angaben_nicht(tmp_path):
    datei = tmp_path / "kontakte.csv"
    reg = Register(datei)
    reg.eintragen(Kandidat(firma="Dachbau Klein", url="https://dachbau-klein.de",
                           telefon="02237 123456"), route="pruefung")
    reg.eintragen(Kandidat(firma="Dachbau Klein", url="https://dachbau-klein.de",
                           telefon=""), route="pruefung")
    assert reg.finde(Kandidat(firma="", url="https://dachbau-klein.de"))["telefon"] \
        == "02237 123456"


def test_unbekannte_route_wird_abgelehnt(tmp_path):
    reg = Register(tmp_path / "k.csv")
    with pytest.raises(ValueError):
        reg.eintragen(Kandidat(firma="X", url="https://x.de"), route="erledigt")


# ── Katalog ──────────────────────────────────────────────────────────────────

def test_branchenpunkte_gelten_nur_in_ihrer_branche():
    gastro = {p.nr for p in K.fuer_branche("gastro")}
    handwerk = {p.nr for p in K.fuer_branche("handwerk")}
    assert 20 in gastro and 20 not in handwerk, "Speisekarte ist Gastro"
    assert 9 in handwerk and 9 not in gastro, "Karriereseite ist Handwerk"
    assert 1 in gastro and 1 in handwerk, "Kernpunkte gelten überall"


def test_katalog_nummern_sind_eindeutig():
    nummern = [p.nr for p in K.KATALOG]
    assert len(nummern) == len(set(nummern))


# ── HTML-Auswertung ──────────────────────────────────────────────────────────

def test_titel_nimmt_nur_das_erste_element():
    s = _Seite()
    s.feed("<html><head><title>Echter Titel</title></head>"
           "<body><svg><title>Twitter_Logo_Blue</title></svg></body></html>")
    assert s.titel == "Echter Titel"


def test_skripte_zaehlen_nicht_zum_sichtbaren_text():
    s = _Seite()
    s.feed("<body><script>var lorem ipsum = 1;</script><p>Guten Tag</p></body>")
    assert "lorem ipsum" not in s.sichtbarer_text.lower()
    assert "Guten Tag" in s.sichtbarer_text


@pytest.mark.parametrize("host, treffer", [
    ("gophai-thaiimbiss.metro.bar", True),
    ("meinbetrieb.wixsite.com", True),
    ("projekt.vercel.app", True),
    ("elektro-mueller.de", False),
    ("andrys-advisory.de", False),
])
def test_baukasten_erkennung(host, treffer):
    assert (_ist_baukasten(host) is not None) is treffer


@pytest.mark.parametrize("text, gefunden", [
    ("Rufen Sie an: 02237 / 60 36 457", True),
    ("Mobil +49 152 01560006", True),
    ("Gegründet 1998, 12 Mitarbeiter", False),
])
def test_telefonnummer_im_text(text, gefunden):
    assert (_telefonnummer_sichtbar(text) is not None) is gefunden


def test_verwechselbare_mails_trennt_tippfehler_von_zweitpostfach():
    # Der Gophai-Fall: derselbe Empfänger, zwei Schreibweisen.
    paare = _verwechselbare_mails({"gophai-thai@web.de", "gophaithai@web.de"})
    assert paare == [("gophai-thai@web.de", "gophaithai@web.de")]

    # Zwei echte Postfächer sind kein Fehler und dürfen nicht anschlagen.
    assert _verwechselbare_mails({"info@firma.de", "jobs@firma.de"}) == []
    assert _verwechselbare_mails({"info@firma.de"}) == []
    # Gleiche Schreibweise, andere Domain: kein Widerspruch.
    assert _verwechselbare_mails({"info@firma.de", "info@firma.com"}) == []


# ── Gegen die echte Gophai-Seite ─────────────────────────────────────────────

def test_gophai_hat_keine_meta_description(gophai):
    assert not (gophai.beschreibung or "").strip()


def test_gophai_titel_ist_sauber(gophai):
    assert gophai.titel and "Gophai" in gophai.titel
    assert "Twitter" not in gophai.titel


def test_gophai_traegt_beide_mailschreibweisen(gophai):
    mails = _mailadressen(gophai)
    assert {"gophai-thai@web.de", "gophaithai@web.de"} <= mails
    assert _verwechselbare_mails(mails), "der Widerspruch muss auffallen"


def test_gophai_laeuft_auf_baukasten_adresse():
    assert _ist_baukasten("gophai-thaiimbiss.metro.bar") == "metro.bar"


# ── Bericht ──────────────────────────────────────────────────────────────────

def test_bericht_rundlauf(tmp_path):
    b = Pruefbericht(kandidat=Kandidat(firma="Test GmbH", url="https://test.de",
                                       ort="Kerpen"))
    pfad = b.speichern(tmp_path)
    wieder = Pruefbericht.laden(pfad)
    assert wieder.kandidat.firma == "Test GmbH"
    assert wieder.stand == b.stand


def test_bericht_entspricht_dem_schema(tmp_path):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((Path(__file__).parent.parent / "schemas"
                         / "befund.schema.json").read_text(encoding="utf-8"))
    b = Pruefbericht(kandidat=Kandidat(firma="Test GmbH", url="https://test.de",
                                       branche="gastro"))
    jsonschema.validate(b.als_dict(), schema)


def test_schema_verbietet_kostensatz_ohne_beleg():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((Path(__file__).parent.parent / "schemas"
                         / "befund.schema.json").read_text(encoding="utf-8"))
    bericht = {
        "kandidat": {"firma": "T", "url": "https://t.de"},
        "stand": "2026-08-11", "messung": [], "qualifiziert": True,
        "befunde": [{"id": 12, "titel": "Meta-Description fehlt",
                     "beobachtung": "Keine Beschreibung hinterlegt.",
                     "was_es_kostet": "Die Google-Vorschau bleibt leer.",
                     "beleg": "", "schweregrad": 2}],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bericht, schema)
