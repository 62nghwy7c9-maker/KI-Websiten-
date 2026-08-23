"""Macht aus einer gebauten Kundenseite zwei fertige Pakete.

    python -m pipeline kunde packen czarnetzki

Erzeugt neben dem Kundenordner:

    <kunde>-website.zip        die Auslieferfassung, geht an den Kunden
    <kunde>-TEST.zip           dieselbe Seite fuer unser Testgeraet

Warum zwei Pakete: Die Auslieferfassung traegt die echte Adresse des Betriebs
als Empfaenger des Formulars. Wer damit auf einem Testserver herumklickt,
schickt Testanfragen an einen echten Kunden. Die Testfassung leitet stattdessen
an uns und steht auf "nicht indexieren", damit eine Kopie der Kundenseite nicht
neben dem Original in der Suchmaschine auftaucht.

Nebenbei erledigt das Skript, was sonst jedes Mal von Hand geschieht und jedes
Mal vergessen werden kann:

  * ein neues Passwort wuerfeln und nur seinen Hash ablegen
  * einen neuen Schluessel fuer den Selbsttest setzen
  * die Sicherungen und die Anfragen des letzten Kunden herauswerfen

Das Passwort erscheint genau einmal, hier auf dem Bildschirm. Es steht in
keiner Datei und laesst sich nicht nachschlagen.
"""
from __future__ import annotations

import argparse
import json
import re
import secrets
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RIEGEL = "<?php http_response_code(404); exit; ?>\n"

# Was aus dem letzten Einsatz stammt und nie mitgeliefert werden darf.
FLUECHTIG = ("anfragen.php", "anfragen-neu.php", "anfragen.lock", "sicherungen")


def wuerfeln() -> str:
    """Ein Passwort, das man am Telefon durchgeben kann.

    Keine Zeichen, die sich beim Vorlesen verwechseln lassen: kein l und I,
    kein O und 0. Der Betrieb tippt es genau einmal und aendert es dann.
    """
    zeichen = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(zeichen) for _ in range(14))


def hash_erzeugen(passwort: str) -> str:
    """Laesst PHP den Hash rechnen, damit er zu password_verify passt."""
    fertig = subprocess.run(
        ["php", "-r", "echo password_hash($argv[1], PASSWORD_DEFAULT);", "--", passwort],
        capture_output=True, text=True, check=True,
    )
    hash_wert = fertig.stdout.strip()
    if not hash_wert.startswith("$2y$"):
        raise SystemExit("PHP hat keinen brauchbaren Hash geliefert: " + hash_wert)
    return hash_wert


def leeren(webroot: Path) -> None:
    """Wirft heraus, was vom Ausprobieren uebrig ist."""
    pflege = webroot / "pflege"
    for name in FLUECHTIG:
        pfad = pflege / name
        if pfad.is_dir():
            shutil.rmtree(pfad)
        elif pfad.exists():
            pfad.unlink()


def ersetzen(pfad: Path, alt: str, neu: str, pflicht: bool = True) -> bool:
    text = pfad.read_text(encoding="utf-8")
    if alt not in text:
        if pflicht:
            raise SystemExit(f"In {pfad.name} nicht gefunden: {alt[:60]}")
        return False
    pfad.write_text(text.replace(alt, neu), encoding="utf-8")
    return True


def empfaenger_lesen(webroot: Path) -> str:
    """Die Adresse, die im Formular als Empfaenger eingetragen ist."""
    text = (webroot / "pflege" / "formular.php").read_text(encoding="utf-8")
    treffer = re.search(r"const EMPFAENGER = '([^']+)';", text)
    if not treffer:
        raise SystemExit("In formular.php steht kein EMPFAENGER.")
    return treffer.group(1)


def testfassung(quelle: Path, ziel: Path, unsere_adresse: str) -> None:
    """Dieselbe Seite, aber ungefaehrlich fuer den Kunden."""
    if ziel.exists():
        shutil.rmtree(ziel)
    shutil.copytree(quelle, ziel)
    echte = empfaenger_lesen(quelle)

    ersetzen(ziel / "pflege" / "formular.php",
             f"const EMPFAENGER = '{echte}';",
             f"const EMPFAENGER = '{unsere_adresse}';   // TESTFASSUNG, nicht ausliefern")

    for seite in ziel.rglob("*.html"):
        text = seite.read_text(encoding="utf-8")
        vorher = text
        text = text.replace(echte, unsere_adresse)
        if '<meta name="robots"' not in text:
            text = text.replace('<meta name="viewport"',
                                '<meta name="robots" content="noindex, nofollow">\n'
                                '<meta name="viewport"', 1)
        if text != vorher:
            seite.write_text(text, encoding="utf-8")

    # Auch in Beipackzetteln. Dort loest die Adresse zwar keine Mail aus, aber
    # wer beim Testen darin nachschlaegt, schreibt sonst den echten Kunden an.
    for zettel in list(ziel.rglob("*.txt")) + list(ziel.rglob("*.md")):
        text = zettel.read_text(encoding="utf-8")
        if echte in text:
            zettel.write_text(text.replace(echte, unsere_adresse), encoding="utf-8")

    # Letzte Kontrolle: nirgends im Testpaket darf die Kundenadresse stehen.
    uebrig = [d.relative_to(ziel) for d in ziel.rglob("*") if d.is_file()
              and echte in d.read_text(encoding="utf-8", errors="ignore")]
    if uebrig:
        raise SystemExit("Kundenadresse noch in der Testfassung: "
                         + ", ".join(str(d) for d in uebrig))


def packen(quelle: Path, ziel: Path) -> int:
    if ziel.exists():
        ziel.unlink()
    anzahl = 0
    with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as z:
        for pfad in sorted(quelle.rglob("*")):
            if pfad.is_file():
                z.write(pfad, pfad.relative_to(quelle))
                anzahl += 1
    return anzahl


def schnueren(kunde: Path, unsere_adresse: str | None = None,
              wurzel: Path = Path("."), leise: bool = False) -> tuple[str, str]:
    """Baut beide Pakete und gibt Passwort und Selbsttestschluessel zurueck.

    Beides erscheint genau einmal, naemlich beim Aufrufer. Nichts davon wird
    irgendwo abgelegt, und nichts davon laesst sich nachschlagen.
    """
    kunde = Path(kunde)
    webroot = kunde / "webroot"
    if not (webroot / "pflege" / "formular.php").is_file():
        raise SystemExit(f"Kein Kundenpaket in {webroot}")

    unsere = unsere_adresse
    if unsere is None:
        absender = wurzel / "absender.json"
        if absender.is_file():
            unsere = json.loads(absender.read_text(encoding="utf-8")).get("mail")
    if not unsere:
        raise SystemExit("Keine eigene Adresse. Entweder --unsere-adresse "
                         "setzen oder absender.json anlegen.")

    def sagen(text: str) -> None:
        if not leise:
            print(text)

    sagen(f"Kunde:            {kunde}")
    sagen(f"Echter Empfaenger: {empfaenger_lesen(webroot)}")

    leeren(webroot)
    sagen("Reste vom Ausprobieren: entfernt")

    passwort = wuerfeln()
    (webroot / "pflege" / "passwort.php").write_text(
        RIEGEL + hash_erzeugen(passwort) + "\n", encoding="utf-8")
    sagen("Neues Passwort:   gesetzt, nur als Hash abgelegt")

    # Die Auslieferfassung zuerst, und zwar ohne Werkzeug darin. Der
    # Selbsttest veraendert Inhalte, um sie zu pruefen. So etwas gehoert in
    # unser Testpaket, nie in das, was der Kunde bekommt.
    lieferung = kunde / f"{kunde.name}-website.zip"
    n1 = packen(webroot, lieferung)

    test_ordner = kunde / ".testfassung"
    testfassung(webroot, test_ordner, unsere)

    schluessel = ""
    vorlage = wurzel / "studie/pflege/selbsttest.php"
    if vorlage.is_file():
        schluessel = secrets.token_hex(8)
        text = re.sub(r"const SCHLUESSEL = '[0-9a-f]+';",
                      f"const SCHLUESSEL = '{schluessel}';",
                      vorlage.read_text(encoding="utf-8"), count=1)
        (test_ordner / "pflege" / "selbsttest.php").write_text(
            text, encoding="utf-8")
        sagen("Selbsttest:       nur im Testpaket, neuer Schluessel")

    test_zip = kunde / f"{kunde.name}-TEST.zip"
    n2 = packen(test_ordner, test_zip)
    shutil.rmtree(test_ordner)

    sagen("")
    sagen(f"  {lieferung}  ({n1} Dateien)")
    sagen(f"  {test_zip}  ({n2} Dateien)")
    return passwort, schluessel


def anzeigen(passwort: str, schluessel: str) -> None:
    """Das Einzige, was nirgends sonst zu sehen sein wird."""
    print()
    print("  " + "=" * 62)
    print(f"  Passwort fuer den Pflegebereich:  {passwort}")
    print("  Jetzt notieren. Es steht in keiner Datei und ist nicht")
    print("  wiederherstellbar. Der Betrieb aendert es bei der Uebergabe.")
    if schluessel:
        print()
        print(f"  Selbsttest aufrufen:  .../pflege/selbsttest.php?s={schluessel}")
    print("  " + "=" * 62)


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("kunde", type=Path,
                   help="Ordner des Kunden, darin liegt webroot/")
    p.add_argument("--unsere-adresse", default=None,
                   help="Empfaenger der Testfassung (Vorgabe aus absender.json)")
    args = p.parse_args()
    anzeigen(*schnueren(args.kunde, args.unsere_adresse))
    return 0


if __name__ == "__main__":
    sys.exit(main())
