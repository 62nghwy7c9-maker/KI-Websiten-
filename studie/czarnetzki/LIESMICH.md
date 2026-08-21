# Peter Czarnetzki Elektroinstallationen — Entwurf

Erste vollständige Website nach dem Konzept: statische Seiten, Pflegebereich,
Kontaktformular. Inhaltliche Grundlage ist der bestehende Onepager
`pcelektro.de` (abgerufen am 20.08.2026) — **nichts ist erfunden**: Leistungen,
Kundenkreis, das Bauvorhaben Deutschlandradio, die E-Check-Passage und alle
Angaben im Impressum stammen wörtlich oder sinngemäß von dort.

## Was hier liegt

```
webroot/                  ← genau das kommt in den Webspace
  index.html              Onepager
  impressum.html          neu — die alte Seite zitierte § 6 TDG, aufgehoben 2007
  datenschutz.html        neu — es gab nur eine PDF-Datei
  danke.html              nach dem Absenden des Formulars
  stil.css                keine fremden Schriften, keine fremden Abrufe
  bilder/betrieb.jpg      Platzhalter, im Pflegebereich austauschbar
  INSTALLATION.txt        Anleitung zum Hochladen, danach löschen
  pflege/                 Pflegebereich und Formular
    .htaccess             sperrt die Sicherungen und die Hilfsdatei
czarnetzki-website.zip    dasselbe als fertiges Paket
demo.html                 Probefassung fürs Browserfenster
demo_bauen.py             erzeugt demo.html aus webroot/
```

**Der Ordner `webroot/` ist das Produkt.** Sein Inhalt wird unverändert in
das Webverzeichnis gelegt — htdocs, httpdocs, public_html, je nach Anbieter.
Danach läuft alles, ohne dass etwas eingestellt werden muss: Der
Pflegebereich findet die Seiten von selbst, weil er eine Ebene tiefer liegt.

## Was der Check bemängelt hat und was jetzt gilt

| Prüfpunkt | Alt | Neu |
|---|---|---|
| 2 · HTTPS | kein HTTPS | Sache des Hostings, beim Livegang einzurichten |
| 3 · Handy | keine viewport-Angabe | vorhanden, Layout getestet bis 390 px |
| 5 · Telefonnummer | nicht antippbar | 8 antippbare `tel:`-Verweise |
| 6 · Kontaktweg | keiner gefunden | Nummer im Kopf, Formular, E-Mail |
| 7 · Impressum | fehlte ganz | vollständig nach § 5 DDG |
| 9 · Stellen | keine Seite | eigener Abschnitt, vom Betrieb selbst pflegbar |
| 10 · Formular | keins | `formular.php`, direkt ins Postfach |
| 11 · Seitentitel | „PC Elektro" | Betriebsname, Gewerk und Ort |
| 12 · Beschreibung | fehlte | vorhanden |

Offen bleibt Prüfpunkt 14 (Google-Unternehmensprofil) — das gehört auf die
Übergabeliste, es ist Sache des Betriebs.

## Einrichten auf dem Hosting

1. **Inhalt von `webroot/` hochladen.** Fertig — es ist nichts einzustellen.
2. **`INSTALLATION.txt` löschen.**
3. **Passwort ändern.** Ausgeliefert wird `Heerstrasse15A`; der Hash steht in
   `pflege/index.php`, das Passwort selbst nirgends auf dem Server. Ersetzen:
   `php -r "echo password_hash('NeuesPasswort', PASSWORD_DEFAULT);"`
4. `EMPFAENGER` in `pflege/formular.php` steht bereits auf
   `info@pcelektro.de`.
5. Voraussetzung an den Tarif: PHP und eigene Dateien hochladen dürfen.
   Beides kann jeder übliche Tarif; ein reiner Baukasten-Tarif nicht.

## Was geprüft ist

Das Paket wurde **frisch entpackt und ohne jede Einstellung gestartet** —
genau so, wie es beim Kunden ankommt. PHP 8.4.19 und Chromium:

- Alle vier Seiten laden (HTTP 200), das Bild auch.
- Pflegebereich: falsches Passwort scheitert, richtiges nicht.
- Speichern ändert **alle** Vorkommen: Die Telefonnummer steht achtmal auf den
  vier Seiten und wird überall zugleich geändert, samt der acht
  `tel:`-Verweise.
- Eine Änderung auf der Startseite zieht Impressum und Datenschutz mit.
- Bild austauschen: 3600 × 2400 wird zu 1600 × 1067; eine als Bild getarnte
  PDF-Datei wird abgewiesen.
- Vor jedem Speichern wird gesichert.
- `pflege/inhalt.php` direkt aufgerufen antwortet mit 404.
- Nach dem Speichern zeigt die aufgerufene Website die neuen Werte, das
  hochgeladene Bild erscheint verkleinert mit neuer Zählnummer.
- Formular: gefüllte Spamfalle und Absenden in unter drei Sekunden werden
  still verworfen; fehlt der Rückweg, kommt die Fehlerseite.

**Nicht geprüft:** der tatsächliche Mailversand — `mail()` gibt es im
Container nicht. Das ist der erste Test auf dem echten Hosting.

## Die Probefassung

`demo.html` ist dieselbe Seite, nur dass der Pflegebereich in JavaScript
nachgebaut ist und im Browser speichert statt in der Datei. Feldnamen,
Beschriftungen, Verkleinerung der Bilder und das Verhalten des Formulars sind
identisch. Passwort: `muster`. „Alles zurücksetzen" stellt den Auslieferstand
wieder her.

Sie entsteht aus `webroot/` — wer die Website ändert, führt danach
`python3 studie/czarnetzki/demo_bauen.py` aus.

## Was noch fehlt

- **Fotos.** Ohne Bildmaterial vom Betrieb bleibt der Platzhalter stehen.
  Zwei Wege stehen im Konzept 4.3: wir machen die Aufnahmen, oder der
  Fotograf.
- **Gründungsjahr.** Auf der alten Seite steht keins. Solange es nicht belegt
  ist, steht kein „seit 19xx" auf der Seite.
- **Öffnungszeiten** sind angenommen (Mo–Fr 7:00–16:30) und im Vorgespräch zu
  bestätigen.
- **Die Stellenanzeige** ist bewusst ein sichtbarer Platzhalter — er zeigt
  dem Betrieb, wo er selbst schreibt.
