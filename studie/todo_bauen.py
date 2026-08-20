"""Erzeugt studie/todo.html aus studie/aufgaben.json.

Word-Fassung und HTML-Fassung lesen dieselbe Datei. Zwei Listen, die
auseinanderlaufen, waren im Konzept-Check schon einmal der Grund für drei
verschiedene Prüfkataloge — das passiert hier nicht noch einmal.

    python3 studie/todo_bauen.py
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DATEN = HIER / "aufgaben.json"
KOPF = HIER / "todo-kopf.html"
ZIEL = HIER / "todo.html"

KLASSE = {"K": "w-k", "Y": "w-y", "C": "w-c", "K+Y": "w-b"}


def hervorheben(text: str) -> str:
    """Setzt den ersten Halbsatz fett — das ist der Teil, den man überfliegt."""
    sicher = html.escape(text)
    treffer = re.match(r"^(.{12,72}?)(:| —|, | \(| und | über )(.*)$", sicher)
    if treffer:
        return f"<strong>{treffer.group(1)}</strong>{treffer.group(2)}{treffer.group(3)}"
    return f"<strong>{sicher}</strong>"


def zeile(wer: str, frist: str, was: str, grund: str, farbe: str,
          konzept: str = "") -> str:
    """Eine Aufgabenzeile. `konzept` ist der Abschnitt im Unternehmenskonzept,
    an dem derselbe Punkt steht — vorhanden nur bei den Zeilen, die dort in der
    Übersicht der offenen Punkte auftauchen."""
    klasse = KLASSE.get(wer, "w-b")
    wichtig = ' class="wichtig"' if farbe == "R" else ""
    notiz = f"\n      <em>{html.escape(grund)}</em>" if grund else ""
    return (f'    <li{wichtig}><span class="kasten"></span>'
            f'<span class="wer {klasse}">{html.escape(wer)}</span>'
            f'<span class="frist">{html.escape(frist)}</span>\n'
            f'      <span class="was">{hervorheben(was)}{notiz}</span></li>')


def bauen() -> str:
    d = json.loads(DATEN.read_text(encoding="utf-8"))
    teile = [KOPF.read_text(encoding="utf-8")]

    teile.append(f"""
<header>
  <div class="bahn">
    <p class="marke">Aufgabenliste</p>
    <h1>Was zu tun ist</h1>
    <p class="unter">
      Stand {d['stand']} · zusammengeführt aus der Aufgabenliste vom 17.08.
      und der Terminliste aus dem Konzept. Diese Fassung ersetzt beide.<br>
      Jede Zeile hat einen Verantwortlichen und eine Frist. Was beides nicht
      hat, steht nicht drin.
    </p>
    <div class="legende">
      <span class="w-k">■ K — Kira</span>
      <span class="w-y">■ Y — Yannik</span>
      <span class="w-b">■ K+Y — beide</span>
      <span class="w-c">■ C — Claude</span>
    </div>
    <div class="sperrblock">
      <b>Der Anker: Tag 1</b>
      <p>Tag 1 ist der Tag, an dem der erste Check übergeben wird.
      Vorgeschlagen: <strong>{d['anker']['tag1']}</strong>, Tag 90 ist dann
      {d['anker']['tag90']}. Alle Fristen im Vorlauf hängen daran — wird das
      Datum verschoben, verschieben sich alle mit. Zweiter Anker ist die
      Gewerbeanmeldung ({d['anker']['gruendung']}): An ihr hängen die
      ELSTER-Frist und der Befreiungsantrag bei der Rentenversicherung.</p>
    </div>
  </div>
</header>

<main class="bahn">""")

    for block in d["bloecke"]:
        titel, _, wann = block["titel"].partition(" — ")
        teile.append('\n<section>')
        teile.append(f'  <div class="phase"><h2>{html.escape(titel)}</h2>'
                     f'<span class="wann">{html.escape(wann)}</span></div>')
        if block.get("vorspann"):
            teile.append(f'  <p class="hinweis">{html.escape(block["vorspann"])}</p>')
        teile.append('  <ul class="liste">')
        for z in block["zeilen"]:
            teile.append(zeile(*z))
        teile.append('  </ul>\n</section>')

    teile.append('\n<section>')
    teile.append('  <div class="phase"><h2>Aus der älteren Liste herausgefallen</h2>'
                 '<span class="wann">und warum</span></div>')
    teile.append('  <ul class="liste">')
    for was, warum, wann in d["gestrichen"]:
        teile.append(f'    <li><span class="kasten haken">✓</span>'
                     f'<span class="wer w-c">—</span>'
                     f'<span class="frist">{html.escape(wann)}</span>\n'
                     f'      <span class="was">{hervorheben(was)}\n'
                     f'      <em>{html.escape(warum)}</em></span></li>')
    teile.append('  </ul>\n</section>')

    teile.append('\n<section class="fertig">\n  <h2>Erledigt</h2>\n  <ul>')
    for e in d["erledigt"]:
        teile.append(f'    <li>{html.escape(e)}</li>')
    teile.append('  </ul>\n</section>\n\n</main>')

    teile.append("""
<footer><div class="bahn">
  K&amp;D Webdesign · Kira Moewes und Yannik Dettmer · Kerpen<br>
  Erzeugt aus studie/aufgaben.json — nicht von Hand ändern, sonst läuft die
  Word-Fassung auseinander.
</div></footer>""")

    return "\n".join(teile) + "\n"


if __name__ == "__main__":
    text = bauen()
    ZIEL.write_text(text, encoding="utf-8")
    anzahl = sum(len(b["zeilen"])
                 for b in json.loads(DATEN.read_text(encoding="utf-8"))["bloecke"])
    print(f"{ZIEL} · {anzahl} Aufgaben · {len(text) // 1024} KB")
