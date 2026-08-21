"""Baut aus der echten Website eine Fassung, die im Browser läuft.

Die ausgelieferte Website braucht PHP auf dem Hosting des Kunden. Zum
Ausprobieren steht aber kein Hosting zur Verfügung — deshalb diese Fassung:
dieselben Dateien, dieselben Markierungen, dieselben Feldnamen, nur dass
der Pflegebereich in JavaScript nachgebaut ist und im Browser speichert.

Wichtig: Der Inhalt wird **nicht** abgeschrieben, sondern aus
seite/index.html gelesen. Was hier zu sehen ist, ist die echte Seite.

    python3 studie/czarnetzki/demo_bauen.py
"""
from __future__ import annotations

import base64
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
SEITE = HIER / "webroot"
ZIEL = HIER / "demo.html"


def hauptteil(html: str) -> str:
    """Alles zwischen <body> und </body>, ohne das abschließende Skript."""
    treffer = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
    if not treffer:
        raise SystemExit("kein <body> gefunden")
    koerper = treffer.group(1)
    return re.sub(r"<script>.*?</script>", "", koerper, flags=re.S).strip()


def bild_als_datenadresse(pfad: Path) -> str:
    roh = base64.b64encode(pfad.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{roh}"


def bauen() -> str:
    stil = (SEITE / "stil.css").read_text(encoding="utf-8")
    seiten = {
        "start": hauptteil((SEITE / "index.html").read_text(encoding="utf-8")),
        "impressum": hauptteil((SEITE / "impressum.html").read_text(encoding="utf-8")),
        "datenschutz": hauptteil((SEITE / "datenschutz.html").read_text(encoding="utf-8")),
    }

    # Das Platzhalterbild wandert als Datenadresse in die Datei — die Seite
    # muss ohne einen einzigen fremden Abruf funktionieren.
    bild = bild_als_datenadresse(SEITE / "bilder" / "betrieb.jpg")
    for name in seiten:
        seiten[name] = seiten[name].replace('src="bilder/betrieb.jpg"', f'src="{bild}"')
        # Verweise zwischen den Seiten werden zu Schaltern der Vorschau.
        for datei, ziel in (("index.html", "start"), ("impressum.html", "impressum"),
                            ("datenschutz.html", "datenschutz")):
            seiten[name] = seiten[name].replace(f'href="{datei}"', f'href="#" data-seite="{ziel}"')

    teile = [KOPF.replace("/*STIL*/", stil)]
    for name, inhalt in seiten.items():
        sichtbar = "" if name == "start" else " hidden"
        teile.append(f'<div class="wg-seite" data-name="{name}"{sichtbar}>\n{inhalt}\n</div>')
    teile.append(SKRIPT)
    return "\n\n".join(teile) + "\n"


KOPF = """<title>Czarnetzki Elektro</title>

<style>
/*STIL*/

/* ---- Nur für die Vorschau, nicht Teil der ausgelieferten Website ---- */
.wg-leiste{position:sticky;top:0;z-index:50;display:flex;flex-wrap:wrap;
 gap:.5rem 1rem;align-items:center;justify-content:space-between;
 background:#111821;color:#E7EDF4;padding:.6rem clamp(1rem,4vw,2.5rem);
 font:600 14px/1.4 var(--sans)}
.wg-leiste .wg-hinweis{font-weight:400;color:#93A3B4;font-size:12.5px}
.wg-leiste .wg-knoepfe{display:flex;flex-wrap:wrap;gap:.4rem}
.wg-leiste button{font:inherit;font-size:13px;padding:.42rem .9rem;border:0;
 border-radius:2px;background:#2B3946;color:#E7EDF4;cursor:pointer}
.wg-leiste button:hover{background:#3A4B5C}
.wg-leiste button[aria-pressed=true]{background:#F0F4F8;color:#111821}
.wg-leiste button.wg-zurueck{background:transparent;color:#93A3B4;
 text-decoration:underline}

.wg-pflege{display:none;background:var(--flaeche);min-height:70vh;
 padding:clamp(1.5rem,5vw,3rem) 0}
body.wg-modus-pflege .wg-pflege{display:block}
body.wg-modus-pflege .wg-seite{display:none}
.wg-pflege .karte-innen{background:var(--grund);border:1px solid var(--linie);
 max-width:44rem;margin:0 auto;padding:clamp(1.25rem,4vw,2.25rem)}
.wg-pflege h2{margin-bottom:.4rem}
.wg-pflege label{display:block;margin:0 0 1.1rem}
.wg-pflege label b{display:block;color:var(--basis);margin-bottom:.3rem;
 font-size:.95rem}
.wg-pflege input[type=text],.wg-pflege input[type=password],
.wg-pflege textarea{width:100%;font:inherit;padding:.7rem .85rem;
 border:1px solid var(--linie-stark);border-radius:2px;
 background:var(--grund);color:var(--basis)}
.wg-pflege textarea{min-height:7rem;resize:vertical}
.wg-pflege button.speichern{font:inherit;font-weight:700;padding:.8rem 1.8rem;
 border:0;border-radius:2px;background:var(--blau);color:#fff;cursor:pointer}
.wg-pflege .meldung{padding:.8rem 1rem;margin:0 0 1.25rem;font-size:.95rem;
 border-left:4px solid var(--blau);background:var(--flaeche);color:var(--basis)}
.wg-pflege .meldung.gut{border-left-color:#2E7D4F}
.wg-pflege .meldung.schlecht{border-left-color:var(--signal)}
.wg-staende{list-style:none;margin:0 0 1rem;padding:0}
.wg-staende li{display:flex;align-items:center;justify-content:space-between;
 gap:1rem;padding:.55rem 0;border-bottom:1px solid var(--linie);font-size:15px}
.wg-staende button{font:inherit;font-size:14px;font-weight:600;
 background:transparent;color:var(--akzent);border:1px solid var(--linie-stark);
 border-radius:4px;padding:.3rem .7rem;cursor:pointer}
.wg-staende button:hover{background:var(--akzent);color:#fff}
.wg-staende .leer{color:var(--gedaempft);font-size:14px;border:0;padding:0}
.wg-bild{display:flex;gap:1rem;align-items:flex-start;
 border-top:1px solid var(--linie);padding-top:1rem;margin-top:1rem}
.wg-bild img{width:130px;height:98px;object-fit:cover;flex:none;
 background:var(--linie)}
.wg-bild .felder{flex:1;min-width:0}
@media(max-width:520px){.wg-bild{flex-direction:column}
 .wg-bild img{width:100%;height:auto}}
@media print{.wg-leiste,.wg-pflege{display:none}}
</style>

<div class="wg-leiste">
  <div>
    <span>Entwurf K&amp;D Webdesign</span>
    <span class="wg-hinweis">· Probefassung im Browser. Änderungen bleiben nur auf diesem Gerät.</span>
  </div>
  <div class="wg-knoepfe">
    <button type="button" data-modus="seite" aria-pressed="true">Website</button>
    <button type="button" data-modus="pflege" aria-pressed="false">Pflegebereich</button>
    <button type="button" class="wg-zurueck">Alles zurücksetzen</button>
  </div>
</div>

<div class="wg-pflege">
  <div class="bahn">
    <div class="karte-innen">
      <div id="wg-anmeldung">
        <h2>Inhalte pflegen</h2>
        <p class="klein">So sieht der Bereich aus, den der Betrieb bekommt.
        Passwort zum Ausprobieren: <code>muster</code></p>
        <div id="wg-meldung"></div>
        <label><b>Passwort</b>
          <input type="password" id="wg-passwort" autocomplete="off"></label>
        <button type="button" class="speichern" id="wg-anmelden">Anmelden</button>
      </div>

      <div id="wg-formular" hidden>
        <h2>Inhalte pflegen</h2>
        <p class="klein" style="margin-bottom:1.25rem">Ändern Sie, was Sie
        brauchen, und klicken Sie unten auf Speichern. Die Änderung ist
        sofort auf der Website sichtbar.</p>
        <div id="wg-meldung2"></div>
        <div id="wg-felder"></div>
        <button type="button" class="speichern" id="wg-speichern">Speichern</button>

        <h2 style="margin-top:2.5rem">Frühere Stände</h2>
        <p class="klein">Etwas versehentlich gelöscht? Hier holen Sie den
        Stand von vorher zurück. Der jetzige wird dabei gesichert.</p>
        <ul class="wg-staende" id="wg-staende"></ul>

        <h2 style="margin-top:2.5rem">Passwort ändern</h2>
        <p class="klein">Mindestens acht Zeichen. Gespeichert wird nur ein
        unumkehrbarer Zahlenwert, nie das Passwort selbst.</p>
        <div id="wg-pwmeldung"></div>
        <label><b>Bisheriges Passwort</b>
          <input type="password" id="wg-pw-alt" autocomplete="off"></label>
        <label><b>Neues Passwort</b>
          <input type="password" id="wg-pw-neu" autocomplete="off"></label>
        <label><b>Neues Passwort wiederholen</b>
          <input type="password" id="wg-pw-neu2" autocomplete="off"></label>
        <button type="button" class="speichern" id="wg-pw-knopf">Passwort ändern</button>
      </div>
    </div>
  </div>
</div>"""


SKRIPT = r"""<script>
/* Der Pflegebereich, in JavaScript nachgebaut.
 *
 * Auf dem Hosting des Kunden macht das PHP: Es liest die Markierungen
 * <!--wg:name-->Text<!--/wg--> aus der HTML-Datei, zeigt sie als Felder und
 * schreibt sie zurueck. Hier passiert dasselbe im Browser, nur dass statt
 * der Datei der Speicher des Browsers beschrieben wird.
 *
 * Feldnamen, Beschriftungen und Verhalten sind absichtlich identisch:
 * wer hier etwas ausprobiert, probiert das echte Verhalten aus.
 */
(function () {
  'use strict';

  var PASSWORT = 'muster';                 // Auslieferstand der Probefassung
  var SCHLUESSEL = 'wg-czarnetzki-v1';
  var PWSCHLUESSEL = 'wg-czarnetzki-pw';
  var STANDSCHLUESSEL = 'wg-czarnetzki-staende';
  var PFLICHT = ['telefon'];               // darf nicht leer bleiben
  var KANTE = 1600;

  var BESCHRIFTUNG = {
    telefon: 'Telefonnummer', mail: 'E-Mail-Adresse',
    oeffnungszeiten: 'Öffnungszeiten', stellenanzeige: 'Stellenanzeige',
    hinweis: 'Aktueller Hinweis', einleitung: 'Einleitungstext',
    bildtitel: 'Bildunterschrift', betrieb: 'Bild aus dem Betrieb',
    anschrift: 'Anschrift', notdienst: 'Hinweis Notdienst'
  };
  function beschriftung(name) {
    return BESCHRIFTUNG[name] ||
      name.charAt(0).toUpperCase() + name.slice(1).replace(/_/g, ' ');
  }

  /* ---- Markierungen im Dokument finden ---------------------------- */
  function stellenSuchen(wurzel) {
    var gehe = document.createNodeIterator(wurzel, NodeFilter.SHOW_COMMENT);
    var texte = {}, bilder = {}, offen = null, knoten;
    while ((knoten = gehe.nextNode())) {
      var wert = knoten.nodeValue.trim();
      var auf = wert.match(/^wg:([a-z0-9_]+)$/);
      var bild = wert.match(/^wg:bild:([a-z0-9_]+)$/);
      if (bild) {
        var img = knoten.nextElementSibling;
        if (img && img.tagName === 'IMG') {
          (bilder[bild[1]] = bilder[bild[1]] || []).push(img);
        }
      } else if (auf) {
        offen = {name: auf[1], start: knoten};
      } else if (wert === '/wg' && offen) {
        (texte[offen.name] = texte[offen.name] || [])
          .push({start: offen.start, ende: knoten});
        offen = null;
      }
    }
    return {texte: texte, bilder: bilder};
  }

  function textLesen(stelle) {
    var s = '', k = stelle.start.nextSibling;
    while (k && k !== stelle.ende) { s += k.textContent; k = k.nextSibling; }
    return s.replace(/\s+/g, ' ').trim();
  }

  function textSchreiben(stelle, wert) {
    var k = stelle.start.nextSibling;
    while (k && k !== stelle.ende) { var n = k.nextSibling; k.remove(); k = n; }
    stelle.ende.parentNode.insertBefore(document.createTextNode(wert), stelle.ende);
  }

  /* Telefonverweis mitziehen, wie verweis_nachziehen() in inhalt.php. */
  function verweisNachziehen(stelle, wert) {
    var a = stelle.start.parentNode;
    while (a && a.tagName !== 'A') { a = a.parentNode; }
    if (!a || a.getAttribute('href').indexOf('tel:') !== 0) { return; }
    var ziffern = wert.replace(/[^0-9+]/g, '');
    if (ziffern.indexOf('00') === 0) { ziffern = '+' + ziffern.slice(2); }
    else if (ziffern.charAt(0) === '0') { ziffern = '+49' + ziffern.slice(1); }
    if (ziffern.length >= 7) { a.setAttribute('href', 'tel:' + ziffern); }
  }

  var stellen = stellenSuchen(document.body);

  /* ---- Gespeicherte Werte anwenden -------------------------------- */
  function gespeichert() {
    try { return JSON.parse(localStorage.getItem(SCHLUESSEL) || '{}'); }
    catch (e) { return {}; }
  }
  function sichern(daten) {
    try { localStorage.setItem(SCHLUESSEL, JSON.stringify(daten)); return true; }
    catch (e) { return false; }
  }
  function anwenden(daten) {
    Object.keys(stellen.texte).forEach(function (name) {
      if (typeof daten[name] === 'string') {
        stellen.texte[name].forEach(function (st) {
          textSchreiben(st, daten[name]);
          verweisNachziehen(st, daten[name]);
        });
      }
    });
    Object.keys(stellen.bilder).forEach(function (name) {
      if (daten['bild:' + name]) {
        stellen.bilder[name].forEach(function (img) {
          img.src = daten['bild:' + name];
        });
      }
      if (typeof daten['alt:' + name] === 'string') {
        stellen.bilder[name].forEach(function (img) {
          img.alt = daten['alt:' + name];
        });
      }
    });
  }
  anwenden(gespeichert());

  /* ---- Passwort ----------------------------------------------------
   * Auf dem Hosting macht das password_hash() in PHP. Hier rechnet der
   * Browser denselben Gedanken nach: gespeichert wird ein Zahlenwert, aus
   * dem sich das Passwort nicht zurueckrechnen laesst.
   */
  function hashen(text) {
    if (!window.crypto || !crypto.subtle) { return Promise.resolve('klar:' + text); }
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(text))
      .then(function (puffer) {
        return Array.prototype.map.call(new Uint8Array(puffer), function (b) {
          return ('0' + b.toString(16)).slice(-2);
        }).join('');
      });
  }
  function pwGespeichert() {
    try { return localStorage.getItem(PWSCHLUESSEL); } catch (e) { return null; }
  }
  function pwPruefen(eingabe) {
    var eigen = pwGespeichert();
    if (!eigen) { return Promise.resolve(eingabe === PASSWORT); }
    return hashen(eingabe).then(function (h) { return h === eigen; });
  }

  /* ---- Frühere Stände ----------------------------------------------
   * Auf dem Hosting liegen sie als Dateikopien im Ordner sicherungen.
   * Hier als Liste im Browser, mit derselben Zahl: zwanzig Staende.
   */
  function staendeLesen() {
    try { return JSON.parse(localStorage.getItem(STANDSCHLUESSEL) || '[]'); }
    catch (e) { return []; }
  }
  function standSichern(daten) {
    var liste = staendeLesen();
    liste.unshift({ zeit: new Date().toISOString(), daten: daten });
    liste = liste.slice(0, 20);
    try { localStorage.setItem(STANDSCHLUESSEL, JSON.stringify(liste)); }
    catch (e) {}
  }
  function zeitLesbar(iso) {
    var d = new Date(iso);
    function zwei(n) { return ('0' + n).slice(-2); }
    return zwei(d.getDate()) + '.' + zwei(d.getMonth() + 1) + '.' +
      d.getFullYear() + ', ' + zwei(d.getHours()) + ':' + zwei(d.getMinutes()) +
      ' Uhr';
  }

  /* ---- Umschalten zwischen Website und Pflegebereich --------------- */
  var leiste = document.querySelector('.wg-leiste');
  leiste.addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (!b) { return; }
    if (b.classList.contains('wg-zurueck')) {
      try {
        localStorage.removeItem(SCHLUESSEL);
        localStorage.removeItem(PWSCHLUESSEL);
        localStorage.removeItem(STANDSCHLUESSEL);
      } catch (err) {}
      location.reload();
      return;
    }
    var modus = b.dataset.modus;
    if (!modus) { return; }
    document.body.classList.toggle('wg-modus-pflege', modus === 'pflege');
    leiste.querySelectorAll('button[data-modus]').forEach(function (x) {
      x.setAttribute('aria-pressed', String(x === b));
    });
    window.scrollTo(0, 0);
  });

  /* Verweise zwischen den drei Seiten */
  document.body.addEventListener('click', function (e) {
    var a = e.target.closest('a[data-seite]');
    if (!a) { return; }
    e.preventDefault();
    zeigeSeite(a.dataset.seite);
  });
  function zeigeSeite(name) {
    document.querySelectorAll('.wg-seite').forEach(function (s) {
      s.hidden = s.dataset.name !== name;
    });
    document.body.classList.remove('wg-modus-pflege');
    leiste.querySelectorAll('button[data-modus]').forEach(function (x) {
      x.setAttribute('aria-pressed', String(x.dataset.modus === 'seite'));
    });
    window.scrollTo(0, 0);
  }

  /* ---- Anmeldung --------------------------------------------------- */
  var meldung = document.getElementById('wg-meldung');
  document.getElementById('wg-anmelden').addEventListener('click', function () {
    var eingabe = document.getElementById('wg-passwort');
    pwPruefen(eingabe.value).then(function (gut) {
      if (gut) {
        document.getElementById('wg-anmeldung').hidden = true;
        document.getElementById('wg-formular').hidden = false;
        felderZeichnen();
        staendeZeichnen();
      } else {
        meldung.innerHTML = '<p class="meldung schlecht">Passwort stimmt nicht.</p>';
        eingabe.value = '';
        eingabe.focus();
      }
    });
  });
  document.getElementById('wg-passwort').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { document.getElementById('wg-anmelden').click(); }
  });

  /* ---- Das Formular ------------------------------------------------ */
  function felderZeichnen() {
    var ziel = document.getElementById('wg-felder');
    var html = '';
    Object.keys(stellen.texte).forEach(function (name) {
      var wert = textLesen(stellen.texte[name][0]);
      var mehrfach = stellen.texte[name].length > 1
        ? ' <span class="klein">(steht ' + stellen.texte[name].length +
          '× auf der Seite und wird überall geändert)</span>' : '';
      html += '<label><b>' + beschriftung(name) + mehrfach + '</b>';
      html += wert.length > 70
        ? '<textarea data-feld="' + name + '"></textarea>'
        : '<input type="text" data-feld="' + name + '">';
      html += '</label>';
    });
    Object.keys(stellen.bilder).forEach(function (name) {
      var img = stellen.bilder[name][0];
      html += '<div class="wg-bild"><img src="' + img.src + '" alt="" ' +
        'data-vorschau="' + name + '"><div class="felder">' +
        '<label><b>' + beschriftung(name) + '</b>' +
        '<input type="file" accept="image/jpeg,image/png,image/webp" ' +
        'data-bild="' + name + '"></label>' +
        '<label><b>Bildbeschreibung</b>' +
        '<input type="text" data-alt="' + name + '"></label></div></div>';
    });
    ziel.innerHTML = html;
    // Werte setzen (nicht über value="" im HTML, sonst zerbricht Text mit ")
    Object.keys(stellen.texte).forEach(function (name) {
      ziel.querySelector('[data-feld="' + name + '"]').value =
        textLesen(stellen.texte[name][0]);
    });
    Object.keys(stellen.bilder).forEach(function (name) {
      ziel.querySelector('[data-alt="' + name + '"]').value =
        stellen.bilder[name][0].alt;
    });
  }

  /* Bild verkleinern, dasselbe was bild_ablegen() auf dem Server tut. */
  function bildVerkleinern(datei) {
    return new Promise(function (fertig, schiefgegangen) {
      if (!/^image\/(jpeg|png|webp)$/.test(datei.type)) {
        schiefgegangen(new Error('Das ist kein Bild. Erlaubt sind JPG, PNG und WEBP.'));
        return;
      }
      var leser = new FileReader();
      leser.onerror = function () { schiefgegangen(new Error('Datei nicht lesbar.')); };
      leser.onload = function () {
        var bild = new Image();
        bild.onerror = function () { schiefgegangen(new Error('Das ist kein Bild.')); };
        bild.onload = function () {
          var faktor = Math.min(1, KANTE / Math.max(bild.width, bild.height));
          var tafel = document.createElement('canvas');
          tafel.width = Math.round(bild.width * faktor);
          tafel.height = Math.round(bild.height * faktor);
          tafel.getContext('2d').drawImage(bild, 0, 0, tafel.width, tafel.height);
          fertig({
            daten: tafel.toDataURL('image/jpeg', 0.82),
            breite: tafel.width, hoehe: tafel.height,
            vorher: bild.width + '×' + bild.height
          });
        };
        bild.src = leser.result;
      };
      leser.readAsDataURL(datei);
    });
  }

  var meldung2 = document.getElementById('wg-meldung2');
  document.getElementById('wg-speichern').addEventListener('click', function () {
    var daten = gespeichert();
    var ziel = document.getElementById('wg-felder');
    var zahl = 0;

    /* Pflichtfelder. Auf einer Handwerkerseite ist eine verschwundene
       Telefonnummer der teuerste Tippfehler. */
    for (var i = 0; i < PFLICHT.length; i++) {
      var feld = ziel.querySelector('[data-feld="' + PFLICHT[i] + '"]');
      if (feld && feld.value.trim() === '') {
        meldung2.innerHTML = '<p class="meldung schlecht">Die ' +
          beschriftung(PFLICHT[i]) + ' darf nicht leer bleiben. ' +
          'Es wurde nichts gespeichert.</p>';
        felderZeichnen();     // die alte Nummer wieder ins Feld holen
        return;
      }
    }

    /* Vor jeder Aenderung den jetzigen Stand wegschreiben. */
    standSichern(JSON.parse(JSON.stringify(daten)));

    Object.keys(stellen.texte).forEach(function (name) {
      var wert = ziel.querySelector('[data-feld="' + name + '"]').value
        .replace(/\s+/g, ' ').trim();
      if (wert !== textLesen(stellen.texte[name][0])) {
        daten[name] = wert;
        stellen.texte[name].forEach(function (st) {
          textSchreiben(st, wert);
          verweisNachziehen(st, wert);
        });
        zahl += stellen.texte[name].length;
      }
    });
    Object.keys(stellen.bilder).forEach(function (name) {
      var alt = ziel.querySelector('[data-alt="' + name + '"]').value.trim();
      if (alt !== stellen.bilder[name][0].alt) {
        daten['alt:' + name] = alt;
        stellen.bilder[name].forEach(function (img) { img.alt = alt; });
        zahl += 1;
      }
    });

    var dateien = [];
    Object.keys(stellen.bilder).forEach(function (name) {
      var feld = ziel.querySelector('[data-bild="' + name + '"]');
      if (feld.files && feld.files[0]) { dateien.push({name: name, datei: feld.files[0]}); }
    });

    if (!dateien.length) { fertigMelden(daten, zahl, ''); return; }

    Promise.all(dateien.map(function (d) {
      return bildVerkleinern(d.datei).then(function (erg) {
        daten['bild:' + d.name] = erg.daten;
        stellen.bilder[d.name].forEach(function (img) { img.src = erg.daten; });
        var v = ziel.querySelector('[data-vorschau="' + d.name + '"]');
        if (v) { v.src = erg.daten; }
        return erg.vorher + ' → ' + erg.breite + '×' + erg.hoehe;
      });
    })).then(function (notizen) {
      fertigMelden(daten, zahl + notizen.length,
        ' Bild verkleinert: ' + notizen.join(', ') + '.');
    }).catch(function (fehler) {
      meldung2.innerHTML = '<p class="meldung schlecht">' + fehler.message + '</p>';
    });
  });

  function fertigMelden(daten, zahl, zusatz) {
    var ok = sichern(daten);
    meldung2.innerHTML = '<p class="meldung ' + (ok ? 'gut' : 'schlecht') + '">' +
      (ok ? zahl + ' Stelle(n) gespeichert.' + zusatz +
            ' Sehen Sie oben unter „Website“ nach.'
          : 'Der Browser konnte nicht speichern (Bild zu groß?). ' +
            'Auf der Seite ist die Änderung trotzdem zu sehen.') + '</p>';
    felderZeichnen();
    staendeZeichnen();
  }

  /* ---- Die Liste der früheren Stände ------------------------------- */
  function staendeZeichnen() {
    var ziel = document.getElementById('wg-staende');
    var liste = staendeLesen();
    if (!liste.length) {
      ziel.innerHTML = '<li class="leer">Noch kein früherer Stand. ' +
        'Sobald Sie einmal gespeichert haben, steht er hier.</li>';
      return;
    }
    ziel.innerHTML = liste.slice(0, 8).map(function (st, i) {
      return '<li><span>' + zeitLesbar(st.zeit) + '</span>' +
        '<button type="button" data-stand="' + i + '">zurückholen</button></li>';
    }).join('');
  }

  document.getElementById('wg-staende').addEventListener('click', function (e) {
    var b = e.target.closest('button[data-stand]');
    if (!b) { return; }
    var liste = staendeLesen();
    var st = liste[parseInt(b.dataset.stand, 10)];
    if (!st) { return; }
    standSichern(gespeichert());          // auch das ist rückgängig zu machen
    sichern(st.daten);
    anwenden(st.daten);
    felderZeichnen();
    staendeZeichnen();
    meldung2.innerHTML = '<p class="meldung gut">Der Stand von vorher ist ' +
      'wieder da.</p>';
  });

  /* ---- Passwort ändern --------------------------------------------- */
  document.getElementById('wg-pw-knopf').addEventListener('click', function () {
    var m = document.getElementById('wg-pwmeldung');
    var alt = document.getElementById('wg-pw-alt').value;
    var neu = document.getElementById('wg-pw-neu').value;
    var neu2 = document.getElementById('wg-pw-neu2').value;
    function sag(text, gut) {
      m.innerHTML = '<p class="meldung ' + (gut ? 'gut' : 'schlecht') + '">' +
        text + '</p>';
    }
    pwPruefen(alt).then(function (stimmt) {
      if (!stimmt) { sag('Das bisherige Passwort stimmt nicht.', false); return; }
      if (neu.length < 8) {
        sag('Das neue Passwort braucht mindestens acht Zeichen.', false); return;
      }
      if (neu !== neu2) {
        sag('Die beiden neuen Passwörter sind nicht gleich.', false); return;
      }
      return hashen(neu).then(function (h) {
        try { localStorage.setItem(PWSCHLUESSEL, h); } catch (e) {}
        document.getElementById('wg-pw-alt').value = '';
        document.getElementById('wg-pw-neu').value = '';
        document.getElementById('wg-pw-neu2').value = '';
        sag('Passwort geändert. Beim nächsten Anmelden gilt das neue.', true);
      });
    });
  });

  /* ---- Das Kontaktformular ----------------------------------------- */
  var geladen = Math.floor(Date.now() / 1000);
  var anfrage = document.querySelector('form.anfrage');
  if (anfrage) {
    anfrage.addEventListener('submit', function (e) {
      e.preventDefault();
      var fehler = document.getElementById('fehler');
      var falle = anfrage.querySelector('[name=website]').value;
      var schnell = (Math.floor(Date.now() / 1000) - geladen) < 3;
      var name = anfrage.querySelector('[name=name]').value.trim();
      var mail = anfrage.querySelector('[name=mail]').value.trim();
      var tel = anfrage.querySelector('[name=telefon]').value.trim();
      var text = anfrage.querySelector('[name=nachricht]').value.trim();

      if (falle || schnell) {           // wie formular.php: still schlucken
        zeigeDanke('Von einem Programm. In Wirklichkeit passiert hier nichts.');
        return;
      }
      if (!name || !text || (!mail && !tel)) {
        fehler.hidden = false;
        fehler.textContent = 'Bitte Name, Nachricht und einen Rückweg angeben.';
        return;
      }
      zeigeDanke('An info@pcelektro.de:\n\nName: ' + name +
        '\nE-Mail: ' + (mail || '-') + '\nTelefon: ' + (tel || '-') +
        '\n\n' + text);
      anfrage.reset();
      geladen = Math.floor(Date.now() / 1000);
    });
  }

  function zeigeDanke(inhalt) {
    var kasten = document.getElementById('wg-danke');
    if (!kasten) {
      kasten = document.createElement('div');
      kasten.id = 'wg-danke';
      kasten.className = 'kasten';
      kasten.style.marginTop = '1.5rem';
      anfrage.parentNode.appendChild(kasten);
    }
    kasten.innerHTML = '<h3>Anfrage angekommen</h3>' +
      '<p class="klein">In der ausgelieferten Fassung geht jetzt genau diese ' +
      'E-Mail an den Betrieb, nichts wird gespeichert. Hier wird sie nur ' +
      'angezeigt.</p><pre style="white-space:pre-wrap;font:13px/1.6 var(--mono);' +
      'margin:0;color:var(--basis)"></pre>';
    kasten.querySelector('pre').textContent = inhalt;
    kasten.scrollIntoView({block: 'center'});
  }
})();
</script>"""


if __name__ == "__main__":
    text = bauen()
    ZIEL.write_text(text, encoding="utf-8")
    print(f"{ZIEL} · {len(text) // 1024} KB")
