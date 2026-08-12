"""Screenshots der Bestandsseite — der Beweis, den niemand bestreiten kann.

„Ihre Seite ist auf dem Handy schwer zu lesen" ist eine Behauptung. Ein Bild
derselben Seite auf einem Handy daneben ist keine. Deshalb steht der
Handy-Screenshot direkt unter der Überschrift des Checks.

Das Bild wird als data:-URI eingebettet, nicht verlinkt. Der Check bleibt damit
eine einzige Datei, die sich verschicken, ausdrucken und in zwei Jahren noch
öffnen lässt — auch dann, wenn der Betrieb seine Seite längst geändert hat.
Genau das ist der Punkt: Der Check dokumentiert einen Stand.

Braucht Playwright und einen Chromium. Fehlt beides, entsteht der Check ohne
Bild und sagt das im Dossier. Ein fehlender Screenshot darf keinen Lauf
anhalten.
"""
from __future__ import annotations

import base64
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

HANDY = {"width": 390, "height": 844}
"""Größe eines iPhone 14/15. Nicht die kleinste, sondern die häufigste."""

SCHREIBTISCH = {"width": 1280, "height": 800}

# Wie weit unter dem Seitenanfang abgeschnitten wird. Mehr als eine
# Bildschirmhöhe zeigt niemand auf einem A4-Blatt.
HOEHE_HANDY = 844
HOEHE_SCHREIBTISCH = 720


@dataclass
class Aufnahme:
    handy: str = ""
    """data:-URI oder leer."""
    schreibtisch: str = ""
    fehler: str = ""

    @property
    def hat_bild(self) -> bool:
        return bool(self.handy or self.schreibtisch)


def _chromium() -> str | None:
    """Findet einen Chromium, ohne einen herunterzuladen."""
    if pfad := os.environ.get("CHROMIUM_PFAD"):
        return pfad if Path(pfad).exists() else None
    ordner = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"))
    if ordner.exists():
        for kandidat in sorted(ordner.glob("chromium-*/chrome-linux/chrome")):
            return str(kandidat)
    for name in ("chromium", "chromium-browser", "google-chrome"):
        if gefunden := shutil.which(name):
            return gefunden
    return None  # Playwright sucht dann selbst


def _als_uri(rohdaten: bytes) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(rohdaten).decode("ascii")


def aufnehmen(url: str, warten_ms: int = 2500) -> Aufnahme:
    """Nimmt die Seite auf einem Handy und auf einem Bildschirm auf.

    Wirft nie. Was nicht geht, steht in `fehler` und bleibt leer.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return Aufnahme(fehler="Playwright ist nicht installiert "
                               "(pip install playwright)")

    aufnahme = Aufnahme()
    argumente = ["--no-sandbox", "--disable-quic", "--hide-scrollbars"]
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=_chromium(), args=argumente,
                proxy={"server": proxy} if proxy else None)
            try:
                for name, groesse, hoehe in (
                        ("handy", HANDY, HOEHE_HANDY),
                        ("schreibtisch", SCHREIBTISCH, HOEHE_SCHREIBTISCH)):
                    seite = browser.new_page(viewport=groesse,
                                             device_scale_factor=2)
                    try:
                        seite.goto(url, wait_until="domcontentloaded",
                                   timeout=30000)
                        seite.wait_for_timeout(warten_ms)
                        rohdaten = seite.screenshot(
                            type="jpeg", quality=72,
                            clip={"x": 0, "y": 0,
                                  "width": groesse["width"], "height": hoehe})
                        setattr(aufnahme, name, _als_uri(rohdaten))
                    except Exception as e:
                        aufnahme.fehler = f"{type(e).__name__}: {e}".splitlines()[0]
                    finally:
                        seite.close()
            finally:
                browser.close()
    except Exception as e:
        aufnahme.fehler = f"{type(e).__name__}: {e}".splitlines()[0]
    return aufnahme
