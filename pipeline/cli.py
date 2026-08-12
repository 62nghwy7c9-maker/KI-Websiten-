"""Kommandozeile der Check-Pipeline.

    python -m pipeline messen --url gophai-thaiimbiss.metro.bar \\
        --firma "Gophai Thai Imbiss" --ort Kerpen --branche gastro

    python -m pipeline register            # zeigt den Stand des Kontakt-Registers

Erzeugt Entwürfe. Versendet nie etwas.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import katalog as K
from .messung import lcp_von_psi, messen
from .modelle import Kandidat, ROUTEN
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

    # Bewusst kein Urteil, solange Sichtprüfungen offen sind: Die automatischen
    # Punkte allein unterschätzen einen Kandidaten regelmäßig. Beim Gophai-Check
    # kamen drei der fünf Befunde erst durch Hinsehen zustande.
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

    r = unter.add_parser("register", help="Stand des Kontakt-Registers zeigen")
    r.set_defaults(func=befehl_register)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
