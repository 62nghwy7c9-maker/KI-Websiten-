"""Tests fuer den Weg vom zugesagten Kunden bis zum Paket.

Laufen ohne Netz und ohne PHP. Alles, was sie brauchen, bauen sie sich in
einem eigenen Ordner auf.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline import papiere, seite
from pipeline.pruefstand import pruefen
from pipeline.stammdaten import ENTFAELLT, Stammdaten, waehlbar
from pipeline.texte import lesen, offene_stellen
from pipeline.vorlagen import fuellen, offene_platzhalter

WURZEL = Path(__file__).parent.parent
ECHT = WURZEL / "studie" / "czarnetzki"


# ── Rufnummern ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("roh, erwartet", [
    ("02271 45550", "+49227145550"),
    ("+49 2271 45550", "+49227145550"),
    ("0049 2271 45550", "+49227145550"),
    ("02271/455-50", "+49227145550"),
    ("45550", ""),          # ohne Vorwahl waere jede Ergaenzung geraten
    ("", ""),
])
def test_waehlbar(roh, erwartet):
    assert waehlbar(roh) == erwartet


# ── Stammdaten ───────────────────────────────────────────────────────────

def test_entfaellt_ist_beantwortet_aber_leer():
    """`entfaellt` heisst gefragt und gibt es nicht. Leer heisst nicht gefragt."""
    s = Stammdaten("probe", bestaetigt={"fax": ENTFAELLT, "ustid": ""})
    assert s["fax"] == ""            # steht nicht auf der Seite
    assert not s.hat("fax")
    assert "fax" not in s.fehlend()  # aber es blockiert den Bau nicht
    assert "ustid" in s.fehlend()    # ungefragt schon


def test_fehlende_pflichtangabe_blockiert():
    s = Stammdaten.laden(ECHT)
    s.bestaetigt["telefon"] = ""
    assert "telefon" in s.fehlend()
    assert not s.baubereit()


def test_czarnetzki_ist_vollstaendig():
    assert Stammdaten.laden(ECHT).fehlend() == []


# ── Vorlagen ─────────────────────────────────────────────────────────────

def test_leerer_block_verschwindet():
    v = "A{{#fax}} Fax {{fax}}{{/fax}}B"
    assert fuellen(v, {"fax": ""}) == "AB"
    assert fuellen(v, {"fax": "1"}) == "A Fax 1B"


def test_werte_werden_entschaerft():
    aus = fuellen("{{firma}}", {"firma": '<script>x</script>'})
    assert "<script>" not in aus


def test_offene_platzhalter_werden_gefunden():
    assert offene_platzhalter("{{a}} und {{&b}}") == ["a", "b"]


# ── Texte ────────────────────────────────────────────────────────────────

def test_texte_lesen():
    a = {x.name: x for x in lesen(ECHT / "texte.md")}
    assert a["aufmacher"]["h1"]
    assert len(a["band"].zeilen) == 4
    assert a["leistungen"].gruppen
    assert a["referenz"].beschriftung == "Bauvorhaben"   # nav schlaegt marke


def test_unfertige_stellen_fallen_auf():
    p = Path(__file__).parent / "daten" / "_probe_texte.md"
    p.parent.mkdir(exist_ok=True)
    p.write_text("# a\nh2: TODO Ueberschrift\n", encoding="utf-8")
    try:
        assert offene_stellen(lesen(p))
    finally:
        p.unlink()


# ── Bauen ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def gebaut(tmp_path_factory):
    ordner = tmp_path_factory.mktemp("kunde")
    for name in ("stammdaten.json", "texte.md"):
        (ordner / name).write_text((ECHT / name).read_text(encoding="utf-8"),
                                   encoding="utf-8")
    (ordner / "bilder").mkdir()
    (ordner / "bilder" / "betrieb.jpg").write_bytes(
        (ECHT / "bilder" / "betrieb.jpg").read_bytes())
    seite.bauen(ordner, WURZEL)
    papiere.bauen(ordner, WURZEL)
    return ordner


def test_gebauter_stand_besteht_den_pruefstand(gebaut):
    schlecht = [b for b in pruefen(gebaut, WURZEL) if not b.ok]
    assert not schlecht, [f"{b.titel}: {b.detail}" for b in schlecht]


def test_kein_passwort_im_paket(gebaut):
    assert not (gebaut / "webroot" / "pflege" / "passwort.php").exists()


def test_kein_passwort_in_den_papieren(gebaut):
    for p in gebaut.glob("*.md"):
        assert "Heerstrasse15A" not in p.read_text(encoding="utf-8")


def test_formular_zeigt_auf_den_betrieb(gebaut):
    t = (gebaut / "webroot" / "pflege" / "formular.php").read_text(encoding="utf-8")
    assert "const EMPFAENGER = 'info@pcelektro.de';" in t
    assert "musterbetrieb" not in t


def test_bau_bricht_ohne_pflichtangabe_ab(tmp_path):
    daten = json.loads((ECHT / "stammdaten.json").read_text(encoding="utf-8"))
    daten["bestaetigt"]["strasse"] = ""
    (tmp_path / "stammdaten.json").write_text(json.dumps(daten), encoding="utf-8")
    (tmp_path / "texte.md").write_text(
        (ECHT / "texte.md").read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(SystemExit, match="strasse"):
        seite.bauen(tmp_path, WURZEL)


def test_fehlendes_bild_bricht_ab(tmp_path):
    for name in ("stammdaten.json", "texte.md"):
        (tmp_path / name).write_text((ECHT / name).read_text(encoding="utf-8"),
                                     encoding="utf-8")
    with pytest.raises(SystemExit, match="betrieb.jpg"):
        seite.bauen(tmp_path, WURZEL)


def test_handarbeit_faellt_auf(gebaut):
    ziel = gebaut / "webroot" / "index.html"
    urzustand = ziel.read_text(encoding="utf-8")
    ziel.write_text(urzustand + "\n<!-- von Hand -->", encoding="utf-8")
    try:
        assert seite.handarbeit_seit_bau(gebaut)
    finally:
        ziel.write_text(urzustand, encoding="utf-8")
    assert not seite.handarbeit_seit_bau(gebaut)


# ── Einwilligung fuer Werbemails ─────────────────────────────────────────

def test_einwilligung_braucht_zeugen_und_anlass(tmp_path):
    """Eine Einwilligung ohne Herkunft ist im Streitfall wertlos."""
    from pipeline.modelle import Kandidat
    from pipeline.register import Register

    reg = Register(tmp_path / "k.csv")
    k = Kandidat(firma="Elektro Muster", url="https://muster.de",
                 kontakt_mail="info@muster.de")
    z = reg.eintragen(k)
    assert not reg.darf_mail(z["schluessel"])

    for durch, wie in (("", "Besuch"), ("Vater", ""), ("  ", "  ")):
        with pytest.raises(ValueError):
            reg.einwilligung(z["schluessel"], durch, wie)

    reg.einwilligung(z["schluessel"], "Vater", "Besuch im Betrieb")
    assert reg.darf_mail(z["schluessel"])
    assert reg.mit_einwilligung() == [z]


def test_einwilligung_ohne_mailadresse_erlaubt_nichts(tmp_path):
    from pipeline.modelle import Kandidat
    from pipeline.register import Register

    reg = Register(tmp_path / "k.csv")
    z = reg.eintragen(Kandidat(firma="Ohne Mail", url="https://ohne.de"))
    reg.einwilligung(z["schluessel"], "Vater", "Besuch")
    assert not reg.darf_mail(z["schluessel"])
