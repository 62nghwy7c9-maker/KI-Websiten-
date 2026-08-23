"""Ein sehr kleiner Vorlagenfueller.

Absichtlich klein: Die Vorlagen sollen echte HTML-Dateien bleiben, die man im
Browser oeffnen und im Editor lesen kann. Ein grosses Vorlagen-Paket wuerde
daraus eine eigene Sprache machen, die ausser dem Rechner niemand liest.

Es gibt genau drei Formen:

    {{feld}}          wird durch den Wert ersetzt, HTML-sicher
    {{&feld}}         wird durch fertiges HTML ersetzt, ungefiltert
    {{#feld}}…{{/feld}}   bleibt nur stehen, wenn das Feld einen Wert hat

Mehr braucht keine der Seiten. Was mehr braucht, gehoert in den Bauer.
"""
from __future__ import annotations

import html
import re

BLOCK = re.compile(r"\{\{#([a-z0-9_]+)\}\}(.*?)\{\{/\1\}\}", re.S)
ROH = re.compile(r"\{\{&([a-z0-9_]+)\}\}")
FELD = re.compile(r"\{\{([a-z0-9_]+)\}\}")


def fuellen(vorlage: str, werte: dict[str, str]) -> str:
    def block(t: re.Match) -> str:
        return t.group(2) if str(werte.get(t.group(1), "")).strip() else ""

    text = vorlage
    # Bloecke koennen ineinander liegen, deshalb bis zur Ruhe wiederholen.
    for _ in range(5):
        neu = BLOCK.sub(block, text)
        if neu == text:
            break
        text = neu

    text = ROH.sub(lambda t: str(werte.get(t.group(1), "")), text)
    text = FELD.sub(lambda t: html.escape(str(werte.get(t.group(1), "")), quote=True), text)
    return text


def offene_platzhalter(text: str) -> list[str]:
    """Was der Fueller nicht kannte. Darf nie in einer fertigen Datei stehen."""
    return sorted(set(FELD.findall(text)) | set(ROH.findall(text)))
