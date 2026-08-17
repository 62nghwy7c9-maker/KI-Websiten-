

def _bericht(k):
    from pipeline.modelle import Befund, Pruefbericht
    b = [Befund(id=9, titel="Keine Seite für Stellenangebote",
                beobachtung="Kein Bereich für Karriere.", was_es_kostet="",
                beleg="", schweregrad=2, behebbarkeit="hoch")]
    return Pruefbericht(kandidat=k, stand="17.08.2026", messung=[], befunde=b,
                        qualifiziert=True, auswahl_fuer_check=b, hinweise=[])


def test_offene_stelle_wird_zum_aufhaenger():
    """Ist eine Stelle belegt, führt der Brief damit — als Feststellung."""
    from pipeline.modelle import Kandidat
    from pipeline.anschreiben import bauen
    k = Kandidat(firma="Elektro Müller", url="mueller.de", ort="Kerpen",
                 sucht="einen Elektriker",
                 sucht_beleg="Ihre Anzeige bei Indeed vom 4. August")
    t = bauen(_bericht(k), "Yannik Dettmer", "0162 3242260",
              _bericht(k).auswahl_fuer_check)
    assert "Sie suchen einen Elektriker" in t
    assert "Ihre Anzeige bei Indeed vom 4. August" in t
    # Feststellung, keine Verkaufsfrage
    assert "Suchen Sie Personal?" not in t


def test_ohne_beleg_keine_behauptung():
    """Ohne Beleg wird nichts über offene Stellen behauptet."""
    from pipeline.modelle import Kandidat
    from pipeline.anschreiben import bauen
    k = Kandidat(firma="Elektro Müller", url="mueller.de", ort="Kerpen",
                 sucht="einen Elektriker")           # Beleg fehlt absichtlich
    t = bauen(_bericht(k), "Yannik Dettmer", "0162 3242260",
              _bericht(k).auswahl_fuer_check)
    brief = t[t.index("Sehr geehrte"):t.index("---", t.index("Sehr geehrte"))]
    assert "Sie suchen" not in brief
    assert "Keine offene Stelle belegt" in t


def test_drei_fragen_nur_in_der_notiz():
    """Die drei Fragen stehen in der Gesprächsnotiz, nie im Brief."""
    from pipeline.modelle import Kandidat
    from pipeline.anschreiben import bauen
    k = Kandidat(firma="Elektro Müller", url="mueller.de", ort="Kerpen")
    t = bauen(_bericht(k), "Yannik Dettmer", "0162 3242260",
              _bericht(k).auswahl_fuer_check)
    frage = "Wie lange suchen Sie schon jemanden?"
    brief = t[t.index("Sehr geehrte"):t.index("---", t.index("Sehr geehrte"))]
    assert frage not in brief
    assert frage in t
