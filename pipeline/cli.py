"""Kommandozeile der Check-Pipeline.

    python -m pipeline messen --url gophai-thaiimbiss.metro.bar \\
        --firma "Gophai Thai Imbiss" --ort Kerpen --branche gastro

    python -m pipeline register            # zeigt den Stand des Kontakt-Registers

Erzeugt Entwürfe. Versendet nie etwas.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

from . import finden as F
from . import katalog as K
from .befunde import bilden
from .check import Absender, schreiben
from .dossier import schreiben as dossier_schreiben
from .leads import aus_datei as leads_aus_datei
from .paket import bauen as paket_bauen
from .farbe import Farbwelt, ableiten, stylesheets_von
from .messung import hole, lcp_von_psi, messen
from .modelle import Kandidat, Pruefbericht, ROUTEN
from .register import Register, STANDARD_DATEI


def _kandidat_aus(args) -> Kandidat:
    return Kandidat(
        firma=args.firma or args.url,
        url=args.url,
        branche=args.branche or "",
        ort=args.ort or "",
        kontakt_mail=args.mail or "",
    )


def befehl_messen(args) -> int:
    kandidat = _kandidat_aus(args)
    reg = Register(args.register)

    if reg.bereits_kontaktiert(kandidat) and not args.trotzdem:
        z = reg.finde(kandidat)
        print(f"Übersprungen: {kandidat.firma} steht schon im Register "
              f"(Route {z['route']}, Erstkontakt {z['erstkontakt_am'] or 'offen'}).")
        print("Mit --trotzdem erneut messen.")
        return 0

    lcp = None
    if args.psi:
        lcp, fehler = lcp_von_psi(kandidat.url, args.psi_key)
        if lcp is None:
            print(f"Hinweis: PageSpeed nicht abrufbar ({fehler})", file=sys.stderr)

    print(f"Messe {kandidat.url} …")
    bericht = messen(kandidat, lcp_ms=lcp)

    ausloeser = [m for m in bericht.messung if m.ok is False]
    offen = [m for m in bericht.messung if m.ok is None]

    breite = max(len(m.pruefpunkt) for m in bericht.messung)
    for m in bericht.messung:
        zeichen = {True: "  ok  ", False: " BEFUND", None: "  ??  "}[m.ok]
        print(f"  {zeichen}  {m.pruefpunkt:<{breite}}  {m.wert}")

    bilden(bericht)
    if bericht.befunde:
        gewaehlt = set(bericht.auswahl_fuer_check)
        print("\nBefunde (▶ = kommt auf den Check):")
        for b in sorted(bericht.befunde,
                        key=lambda x: (x.id not in gewaehlt, -x.schweregrad)):
            marke = "▶" if b.id in gewaehlt else " "
            print(f"  {marke} [{b.schweregrad}] {b.titel}")
            print(f"      {b.beobachtung}")
            if b.was_es_kostet:
                print(f"      Was es kostet: {b.was_es_kostet}")
            else:
                print("      (kein Kosten-Satz — Beleg fehlt)")

    # Bewusst kein endgültiges Urteil, solange Sichtprüfungen offen sind: Die
    # automatischen Punkte allein unterschätzen einen Kandidaten regelmäßig. Beim
    # Gophai-Check kamen drei der fünf Befunde erst durch Hinsehen zustande.
    print(f"\n{len(ausloeser)} automatisch belegt, {len(offen)} offen (Sichtprüfung).")
    if len(ausloeser) >= K.QUALIFIKATION_AB_BEFUNDEN:
        print(f"Qualifiziert allein aus der Automatik (≥ {K.QUALIFIKATION_AB_BEFUNDEN}). "
              f"Auf den Check kommen höchstens {K.MAX_BEFUNDE_AUF_CHECK}.")
    elif offen:
        print(f"Noch nicht entschieden: {len(ausloeser)} von "
              f"{K.QUALIFIKATION_AB_BEFUNDEN} nötigen Befunden automatisch belegt, "
              f"{len(offen)} Punkte brauchen einen Blick. Erst danach verwerfen.")
    else:
        print(f"Nicht qualifiziert — unter {K.QUALIFIKATION_AB_BEFUNDEN} Befunden und "
              "nichts mehr offen. Kandidat verwerfen.")

    if bericht.hinweise:
        print("\nVon Hand nachsehen:")
        for h in bericht.hinweise:
            print(f"  - {h}")

    pfad = bericht.speichern(Path(args.out))
    print(f"\nRohmessung: {pfad}")

    reg.eintragen(kandidat, route="pruefung", notiz=f"{len(ausloeser)} Auslöser")
    reg.speichern()
    print(f"Register:   {reg.datei} (Route: pruefung)")
    return 0


def befehl_finden(args) -> int:
    """Stufe 0: Betriebe aus OpenStreetMap holen und als Liste ablegen."""
    ql = (F.abfrage(args.lat, args.lon, args.umkreis, args.branche)
          if args.lat and args.lon
          else F.abfrage_nach_ort(args.ort, args.umkreis, args.branche))

    text = None
    if args.datei:
        text = Path(args.datei).read_text(encoding="utf-8")
        print(f"Gelesen aus {args.datei}")
    elif args.live:
        print("Frage Overpass ab (kann dauern) …")
        text, fehler = F.live_holen(ql)
        if text is None:
            print(f"Overpass nicht erreichbar ({fehler}).\n", file=sys.stderr)
            _turbo_anleitung(ql)
            return 1
    else:
        _turbo_anleitung(ql)
        return 0

    funde = F.aus_json(text, ort_vorgabe=args.ort, branche_vorgabe=args.branche)
    mit, ohne = F.sortieren(funde)
    reg = Register(args.register)

    neu = [f for f in mit if not reg.bereits_kontaktiert(f.als_kandidat())]
    schon = len(mit) - len(neu)

    print(f"\n{len(funde)} Betriebe gefunden.")
    print(f"  {len(mit)} mit eigener Website  → Website-Check"
          + (f" ({schon} davon schon im Register)" if schon else ""))
    print(f"  {len(ohne)} ohne Website         → anderes Gespräch "
          f"(„Sie sind online nicht zu finden\")")

    ziel = Path(args.ziel)
    with ziel.open("w", encoding="utf-8", newline="") as f:
        s = csv.writer(f)
        s.writerow(["firma", "url", "branche", "ort", "strasse", "telefon",
                    "osm_id", "hat_website"])
        for x in neu + ohne:
            s.writerow([x.name, x.url, x.branche, x.ort, x.strasse, x.telefon,
                        x.osm_id, "ja" if x.hat_website else "nein"])
    print(f"\nListe: {ziel}")
    if neu:
        print(f"Weiter mit:  python -m pipeline stapel --liste {ziel}")
    return 0


def _turbo_anleitung(ql: str) -> None:
    print("So kommst du an die Liste:")
    print("  1. https://overpass-turbo.eu öffnen")
    print("  2. Abfrage unten einfügen, auf „Ausführen“ klicken")
    print("  3. „Exportieren“ → „Rohdaten als JSON“ → speichern")
    print("  4. python -m pipeline finden --datei <gespeicherte.json> --ort <Ort>")
    print("\n" + "─" * 68)
    print(ql)
    print("─" * 68)


def befehl_stapel(args) -> int:
    """Misst eine ganze Liste und sortiert nach Anzahl belegter Befunde."""
    zeilen = [z for z in csv.DictReader(
        Path(args.liste).open(encoding="utf-8")) if z.get("hat_website") == "ja"]
    if not zeilen:
        print("Keine Betriebe mit Website in der Liste.")
        return 0

    reg = Register(args.register)
    ergebnisse = []
    print(f"Messe {len(zeilen)} Betriebe (je ~{args.pause}s Pause, "
          f"damit die Server nicht belastet werden) …\n")

    for i, z in enumerate(zeilen, 1):
        kandidat = Kandidat(firma=z["firma"], url=z["url"],
                            branche=z.get("branche", ""), ort=z.get("ort", ""))
        if reg.bereits_kontaktiert(kandidat) and not args.trotzdem:
            print(f"  [{i}/{len(zeilen)}] {z['firma'][:32]:<32} übersprungen "
                  f"(schon im Register)")
            continue
        try:
            bericht = bilden(messen(kandidat))
        except Exception as e:  # eine kaputte Seite darf den Lauf nicht beenden
            print(f"  [{i}/{len(zeilen)}] {z['firma'][:32]:<32} "
                  f"FEHLER {type(e).__name__}")
            continue

        belegt = len(bericht.befunde)
        offen = sum(1 for m in bericht.messung if m.ok is None)
        marke = "QUALIFIZIERT" if bericht.qualifiziert else f"{belegt} Befunde"
        print(f"  [{i}/{len(zeilen)}] {z['firma'][:32]:<32} {marke:<13} "
              f"(+{offen} offen)")
        bericht.speichern(Path(args.out))
        ergebnisse.append(bericht)
        reg.eintragen(kandidat, route="pruefung", notiz=f"{belegt} Befunde")
        if i < len(zeilen):
            time.sleep(args.pause)

    reg.speichern()
    ergebnisse.sort(key=lambda b: len(b.befunde), reverse=True)
    qual = [b for b in ergebnisse if b.qualifiziert]

    print(f"\n{len(qual)} von {len(ergebnisse)} allein aus der Automatik "
          f"qualifiziert (≥ {K.QUALIFIKATION_AB_BEFUNDEN} Befunde).")
    if qual:
        print("\nReihenfolge zum Anschauen:")
        for b in qual:
            titel = ", ".join(x.titel for x in b.befunde[:3])
            print(f"  {len(b.befunde)}  {b.kandidat.firma[:30]:<30} {titel[:58]}")
    rest = [b for b in ergebnisse if not b.qualifiziert]
    if rest:
        print(f"\n{len(rest)} noch nicht entschieden — die Sichtprüfungen "
              f"entscheiden. Nicht vorschnell verwerfen.")
    print(f"\nRohmessungen: {args.out}/")
    return 0


def befehl_check(args) -> int:
    """Stufe 3: aus einer Rohmessung den druckfertigen Check bauen."""
    quelle = Path(args.bericht)
    if not quelle.exists():
        print(f"{quelle} gibt es nicht. Erst messen.", file=sys.stderr)
        return 1

    bericht = Pruefbericht.laden(quelle)
    if not bericht.befunde:
        bilden(bericht)  # ältere Rohmessung ohne Stufe 2
    if not bericht.befunde:
        print("Keine Befunde — für diesen Betrieb gibt es nichts zu zeigen.")
        return 1

    farbe = Farbwelt()
    if not args.neutral:
        abruf = hole(bericht.kandidat.url)
        if abruf.html:
            # Stylesheets mitlesen: Betriebe definieren ihre Farben fast immer
            # dort, nicht im HTML.
            css = stylesheets_von(abruf.html, abruf.endgueltige_url
                                  or bericht.kandidat.url, hole)
            farbe = ableiten(abruf.html, css)
        else:
            print("Hinweis: Seite für die Farbwelt nicht abrufbar, "
                  "neutrale Gestaltung.", file=sys.stderr)

    absender = Absender.laden(args.absender)
    ziel = schreiben(bericht, absender, Path(args.ziel), farbe)
    intern = dossier_schreiben(bericht, Path(args.ziel), farbe.akzent)

    gewaehlt = len(bericht.auswahl_fuer_check) or len(bericht.befunde)
    print(f"Kundencheck:      {ziel}")
    print(f"Interne Übersicht: {intern}")
    print(f"  {gewaehlt} von {len(bericht.befunde)} Befunden auf dem Blatt")
    print(f"  Farbwelt: {farbe.akzent} — {farbe.herkunft}")
    ohne_beleg = sum(1 for b in bericht.befunde if not b.was_es_kostet)
    if ohne_beleg:
        print(f"  {ohne_beleg} Befund(e) ohne Kosten-Satz (kein Beleg hinterlegt)")

    if absender.vollstaendig:
        print("\nIm Browser öffnen, Strg+P, „Als PDF speichern“.")
    else:
        print(f"\nNOCH NICHT VERSANDFERTIG — in {args.absender} fehlen: "
              f"{', '.join(absender.fehlend)}.")
        print("Der Check trägt oben einen roten Sperrbalken, bis das ausgefüllt ist.")
        return 2
    return 0


def befehl_pakete(args) -> int:
    """Nimmt eine Lead-Liste und legt für jeden Betrieb einen Ordner an."""
    e = leads_aus_datei(args.liste, ort_vorgabe=args.ort)
    if not e.leads:
        print(f"Keine Betriebe in {args.liste} erkannt.", file=sys.stderr)
        for u in e.uebersprungen:
            print(f"  - {u}", file=sys.stderr)
        return 1

    print(f"{len(e.leads)} Betriebe aus {args.liste}")
    print("Spalten erkannt: "
          + ", ".join(f"{f} ← „{k}“" for f, k in e.spalten.items()))
    if e.uebersprungen:
        print(f"\n{len(e.uebersprungen)} Zeile(n) übersprungen:")
        for u in e.uebersprungen:
            print(f"  - {u}")

    absender = Absender.laden(args.absender)
    reg = Register(args.register)
    pakete = []
    print()

    for i, lead in enumerate(e.leads, 1):
        kandidat = lead.als_kandidat()
        if reg.bereits_kontaktiert(kandidat) and not args.trotzdem:
            print(f"  [{i}/{len(e.leads)}] {lead.firma[:30]:<30} übersprungen "
                  f"(schon im Register)")
            continue
        try:
            bericht = bilden(messen(kandidat))
            farbe = Farbwelt()
            if not args.neutral:
                abruf = hole(kandidat.url)
                if abruf.html:
                    farbe = ableiten(abruf.html, stylesheets_von(
                        abruf.html, abruf.endgueltige_url or kandidat.url, hole))
            # A/B-Test: jeder zweite Check ohne den Positivteil. Ob
            # Anerkennung mehr Rueckmeldungen bringt oder Druck wegnimmt, ist
            # bei null verschickten Checks nicht zu wissen -- nur zu messen.
            ohne = args.ohne_positives or (args.ab_test and i % 2 == 0)
            p = paket_bauen(bericht, absender, farbe, Path(args.ziel), ohne)
        except Exception as ex:  # ein kaputter Betrieb stoppt den Lauf nicht
            print(f"  [{i}/{len(e.leads)}] {lead.firma[:30]:<30} "
                  f"FEHLER {type(ex).__name__}")
            continue

        marke = "QUALIFIZIERT" if p.qualifiziert else f"{p.befunde} Befunde"
        print(f"  [{i}/{len(e.leads)}] {lead.firma[:30]:<30} {marke:<13} "
              f"→ {p.ordner}")
        pakete.append(p)
        reg.eintragen(kandidat, route="pruefung", notiz=f"{p.befunde} Befunde")
        if i < len(e.leads):
            time.sleep(args.pause)

    reg.speichern()
    pakete.sort(key=lambda p: p.befunde, reverse=True)
    print(f"\n{len(pakete)} Pakete in {args.ziel}/ — je fünf Dateien: "
          f"befund.md, check.html, dossier.html, anschreiben.md, messung.json")
    if pakete:
        print("\nReihenfolge zum Anschauen:")
        for p in pakete:
            print(f"  {p.befunde:>2}  {p.firma[:34]:<34} {p.ordner}")
    if not absender.vollstaendig:
        print(f"\nNOCH NICHT VERSANDFERTIG — in {args.absender} fehlen: "
              f"{', '.join(absender.fehlend)}.")
        print("Jeder Check trägt oben einen roten Sperrbalken, bis das steht.")
        return 2
    return 0


def befehl_register(args) -> int:
    reg = Register(args.register)
    if not reg.zeilen:
        print(f"{reg.datei} ist leer oder existiert noch nicht.")
        return 0
    for route in ROUTEN:
        treffer = reg.nach_route(route)
        if treffer:
            print(f"\n{route.upper()} ({len(treffer)})")
            for z in treffer:
                print(f"  {z['firma']:<34} {z['host']:<30} {z['letzte_aenderung']}")
    print(f"\nGesamt: {len(reg.zeilen)} Betriebe in {reg.datei}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="pipeline", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--register", default=str(STANDARD_DATEI),
                   help="Pfad zum Kontakt-Register (Standard: %(default)s)")
    unter = p.add_subparsers(dest="befehl", required=True)

    m = unter.add_parser("messen", help="Stufe 1: eine Website messen")
    m.add_argument("--url", required=True)
    m.add_argument("--firma", default="")
    m.add_argument("--ort", default="")
    m.add_argument("--branche", default="", choices=["", "gastro", "handwerk", "verein"])
    m.add_argument("--mail", default="")
    m.add_argument("--out", default="out", help="Ordner für die Rohmessung")
    m.add_argument("--psi", action="store_true", help="Ladezeit über PageSpeed messen")
    m.add_argument("--psi-key", default="", help="API-Schlüssel für PageSpeed Insights")
    m.add_argument("--trotzdem", action="store_true",
                   help="auch messen, wenn der Betrieb schon kontaktiert wurde")
    m.set_defaults(func=befehl_messen)

    f = unter.add_parser("finden", help="Stufe 0: Betriebe aus OpenStreetMap holen")
    f.add_argument("--ort", default="", help="z. B. Kerpen")
    f.add_argument("--umkreis", type=float, default=10, help="km (Standard: %(default)s)")
    f.add_argument("--branche", default="gastro",
                   choices=["gastro", "handwerk", "verein", "alle"])
    f.add_argument("--lat", type=float, help="Breitengrad (statt --ort, für --live)")
    f.add_argument("--lon", type=float, help="Längengrad (statt --ort, für --live)")
    f.add_argument("--datei", default="", help="gespeicherte Overpass-Antwort (JSON)")
    f.add_argument("--live", action="store_true",
                   help="Overpass direkt fragen (oft überlastet)")
    f.add_argument("--ziel", default="kandidaten.csv")
    f.set_defaults(func=befehl_finden)

    s = unter.add_parser("stapel", help="eine ganze Liste messen")
    s.add_argument("--liste", default="kandidaten.csv")
    s.add_argument("--out", default="out")
    s.add_argument("--pause", type=float, default=2.0,
                   help="Sekunden zwischen zwei Seiten (Standard: %(default)s)")
    s.add_argument("--trotzdem", action="store_true")
    s.set_defaults(func=befehl_stapel)

    c = unter.add_parser("check", help="Stufe 3: Check als druckfertiges HTML")
    c.add_argument("--bericht", required=True, help="out/<datei>.json aus dem Messen")
    c.add_argument("--absender", default="absender.json")
    c.add_argument("--ziel", default="checks", help="Ordner für die HTML-Datei")
    c.add_argument("--neutral", action="store_true",
                   help="Standardfarben statt Farbwelt des Betriebs")
    c.set_defaults(func=befehl_check)

    pk = unter.add_parser("pakete",
                          help="Lead-Liste → ein fertiger Ordner je Betrieb")
    pk.add_argument("--liste", required=True,
                    help="Lead-Liste als Markdown-Tabelle, CSV oder TSV")
    pk.add_argument("--ziel", default="kunden")
    pk.add_argument("--absender", default="absender.json")
    pk.add_argument("--ort", default="", help="Ort, falls die Liste keinen nennt")
    pk.add_argument("--pause", type=float, default=2.0)
    pk.add_argument("--neutral", action="store_true",
                    help="Standardfarben statt Farbwelt des Betriebs")
    pk.add_argument("--ohne-positives", action="store_true",
                    help="Abschnitt „Was schon gut ist“ weglassen")
    pk.add_argument("--ab-test", action="store_true",
                    help="jeden zweiten Check ohne Positivteil, zum Vergleichen")
    pk.add_argument("--trotzdem", action="store_true")
    pk.set_defaults(func=befehl_pakete)

    r = unter.add_parser("register", help="Stand des Kontakt-Registers zeigen")
    r.set_defaults(func=befehl_register)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
