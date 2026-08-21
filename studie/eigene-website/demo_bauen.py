"""Baut aus der eigenen Website eine Fassung fürs Browserfenster.

Die ausgelieferte Seite besteht aus vier Dateien und einem PHP-Endpunkt für
das Kontaktformular. Zum Ansehen steht kein Hosting zur Verfügung, deshalb
diese Fassung: dieselben Dateien in einer, die Verweise zwischen den Seiten
werden zu Schaltern, und das Formular zeigt die Mail, die sonst rausginge.

Die Skripte der echten Seite bleiben unverändert drin. Was hier läuft, ist
also genau das, was ausgeliefert wird: der Prüfvorgang, das gestaffelte
Einblenden, die Zahlen und die Kopfleiste.

Diese Seite hat keinen Pflegebereich. Wir pflegen sie selbst.

    python3 studie/eigene-website/demo_bauen.py
"""
from __future__ import annotations

import base64
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
SEITE = HIER / "webroot"
ZIEL = HIER / "demo.html"


def hauptteil(html: str) -> str:
    """Alles zwischen <body> und </body>, samt Skripten."""
    treffer = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
    if not treffer:
        raise SystemExit("kein <body> gefunden")
    return treffer.group(1).strip()


def bild_als_datenadresse(pfad: Path) -> str:
    art = "png" if pfad.suffix == ".png" else "jpeg"
    roh = base64.b64encode(pfad.read_bytes()).decode("ascii")
    return f"data:image/{art};base64,{roh}"


def bauen() -> str:
    stil = (SEITE / "stil.css").read_text(encoding="utf-8")
    seiten = {
        "start": hauptteil((SEITE / "index.html").read_text(encoding="utf-8")),
        "impressum": hauptteil((SEITE / "impressum.html").read_text(encoding="utf-8")),
        "datenschutz": hauptteil((SEITE / "datenschutz.html").read_text(encoding="utf-8")),
    }

    bild = bild_als_datenadresse(SEITE / "bilder" / "pflegebereich.png")
    for name in seiten:
        seiten[name] = seiten[name].replace(
            'src="bilder/pflegebereich.png"', f'src="{bild}"')
        for datei, ziel in (("index.html", "start"),
                            ("impressum.html", "impressum"),
                            ("datenschutz.html", "datenschutz")):
            seiten[name] = seiten[name].replace(
                f'href="{datei}"', f'href="#" data-seite="{ziel}"')
        # Sprungmarken auf die Startseite von den Rechtsseiten aus
        seiten[name] = seiten[name].replace(
            'href="#" data-seite="start"#', 'href="#" data-seite="start" data-anker="#')

    teile = [KOPF.replace("/*STIL*/", stil)]
    for name, inhalt in seiten.items():
        sichtbar = "" if name == "start" else " hidden"
        teile.append(f'<div class="wg-seite" data-name="{name}"{sichtbar}>\n{inhalt}\n</div>')
    teile.append(SKRIPT)
    return "\n\n".join(teile) + "\n"


KOPF = """<title>Moewes &amp; Dettmer</title>

<style>
/*STIL*/

/* ---- Nur für die Vorschau, nicht Teil der ausgelieferten Website ---- */
.wg-leiste{position:sticky;top:0;z-index:60;display:flex;flex-wrap:wrap;
 gap:.4rem 1rem;align-items:center;justify-content:space-between;
 background:#111110;color:#E9E7E1;padding:.55rem clamp(1rem,4vw,3rem);
 font:600 13px/1.4 var(--sans)}
.wg-leiste .wg-hinweis{font-weight:400;color:#93908A;font-size:12px}
.wg-leiste .wg-knoepfe{display:flex;flex-wrap:wrap;gap:.35rem}
.wg-leiste button{font:inherit;font-size:12.5px;padding:.38rem .85rem;border:0;
 border-radius:100px;background:#2B2A27;color:#E9E7E1;cursor:pointer}
.wg-leiste button:hover{background:#3C3A36}
.wg-leiste button[aria-pressed=true]{background:#F2F0EB;color:#111110}
/* Die Kopfleiste der Seite klebt unter der Vorschauleiste. */
header.kopf{top:2.4rem}
@media print{.wg-leiste{display:none}header.kopf{top:0}}
</style>

<div class="wg-leiste">
  <div>
    <span>Entwurf Moewes &amp; Dettmer</span>
    <span class="wg-hinweis">· Probefassung im Browser. Am Rechner scrollen, dann läuft der Prüfvorgang.</span>
  </div>
  <div class="wg-knoepfe">
    <button type="button" data-seite="start" aria-pressed="true">Startseite</button>
    <button type="button" data-seite="impressum" aria-pressed="false">Impressum</button>
    <button type="button" data-seite="datenschutz" aria-pressed="false">Datenschutz</button>
  </div>
</div>"""


SKRIPT = r"""<script>
/* Nur zwei Dinge, die es auf dem echten Hosting nicht braucht:
   das Umschalten zwischen den drei Seiten und ein Formular, das die Mail
   anzeigt, statt sie zu verschicken. */
(function () {
  'use strict';

  var leiste = document.querySelector('.wg-leiste');

  function zeigeSeite(name) {
    document.querySelectorAll('.wg-seite').forEach(function (s) {
      s.hidden = s.dataset.name !== name;
    });
    leiste.querySelectorAll('button[data-seite]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.seite === name));
    });
    window.scrollTo(0, 0);
    window.dispatchEvent(new Event('resize'));   // Prüfvorgang neu rechnen
  }

  leiste.addEventListener('click', function (e) {
    var b = e.target.closest('button[data-seite]');
    if (b) { zeigeSeite(b.dataset.seite); }
  });

  document.body.addEventListener('click', function (e) {
    var a = e.target.closest('a[data-seite]');
    if (!a) { return; }
    e.preventDefault();
    zeigeSeite(a.dataset.seite);
    var anker = a.dataset.anker;
    if (anker) {
      var ziel = document.querySelector('.wg-seite:not([hidden]) ' + anker);
      if (ziel) { ziel.scrollIntoView(); }
    }
  });

  /* Das Kontaktformular. Auf dem Hosting nimmt formular.php die Anfrage
     entgegen und schickt sie ins Postfach. Hier wird sie nur gezeigt. */
  var geladen = Math.floor(Date.now() / 1000);
  var anfrage = document.querySelector('form.anfrage');
  if (!anfrage) { return; }

  anfrage.addEventListener('submit', function (e) {
    e.preventDefault();
    var fehler = document.getElementById('fehler');
    var falle = anfrage.querySelector('[name=website]').value;
    var schnell = (Math.floor(Date.now() / 1000) - geladen) < 3;
    var name = anfrage.querySelector('[name=name]').value.trim();
    var mail = anfrage.querySelector('[name=mail]').value.trim();
    var tel = anfrage.querySelector('[name=telefon]').value.trim();
    var text = anfrage.querySelector('[name=nachricht]').value.trim();

    if (falle || schnell) {          // wie formular.php: still schlucken
      zeigeDanke('Von einem Programm. In Wirklichkeit passiert hier nichts.');
      return;
    }
    if (!name || !text || (!mail && !tel)) {
      fehler.hidden = false;
      fehler.textContent = 'Bitte Name, Nachricht und einen Rückweg angeben.';
      return;
    }
    zeigeDanke('An hallo@moewes-dettmer.de:\n\nName: ' + name +
      '\nE-Mail: ' + (mail || '-') + '\nTelefon: ' + (tel || '-') +
      '\n\n' + text);
    anfrage.reset();
    geladen = Math.floor(Date.now() / 1000);
  });

  function zeigeDanke(inhalt) {
    var kasten = document.getElementById('wg-danke');
    if (!kasten) {
      kasten = document.createElement('div');
      kasten.id = 'wg-danke';
      kasten.className = 'kasten';
      anfrage.parentNode.appendChild(kasten);
    }
    kasten.innerHTML = '<h3>Anfrage angekommen</h3>' +
      '<p class="klein">Auf dem Hosting geht jetzt genau diese E-Mail raus, ' +
      'nichts wird gespeichert. Hier wird sie nur angezeigt.</p>' +
      '<pre style="white-space:pre-wrap;font:13px/1.6 var(--mono);margin:0;' +
      'color:var(--tinte)"></pre>';
    kasten.querySelector('pre').textContent = inhalt;
    kasten.scrollIntoView({block: 'center'});
  }
})();
</script>"""


if __name__ == "__main__":
    text = bauen()
    ZIEL.write_text(text, encoding="utf-8")
    print(f"{ZIEL} · {len(text) // 1024} KB")
