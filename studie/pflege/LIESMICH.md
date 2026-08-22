# Pflegebereich und Kontaktformular

Zwei offene Punkte aus dem Konzept, die sich als **ein** Punkt herausgestellt
haben: „Der Kunde kann nichts selbst ändern" (7.1) und „Kontaktformular"
(ebenfalls 7.1). Beides braucht dasselbe — ein kleines Programm auf dem
Webspace des Kunden. Hier liegt es.

## Warum es das überhaupt braucht

Eine statische Website ist Text auf einer Festplatte. Ein Server schickt diesen
Text an den Browser und tut sonst nichts. Deshalb kann eine statische Seite von
sich aus weder ein Formular entgegennehmen noch ihren eigenen Text ändern —
dazu müsste jemand da sein, der zuhört.

Diese drei Dateien sind dieser Jemand. Sie sind in PHP geschrieben, weil PHP
auf jedem deutschen Hosting-Tarif vorhanden ist, den ein Handwerksbetrieb
hat — IONOS, Strato, All-Inkl, Hetzner, Netcup. Nichts wird installiert,
nichts läuft über uns, es gibt keine Datenbank und keinen Fremddienst.

## Die Dateien

| Datei | Was sie tut |
|---|---|
| `inhalt.php` | Liest und schreibt die bearbeitbaren Stellen. Wird nie direkt aufgerufen. |
| `index.php` | Der Pflegebereich, den der Kunde sieht: Passwort, Felder, Speichern. |
| `formular.php` | Nimmt eine Anfrage entgegen und schickt sie ins Postfach des Betriebs. |
| `formular-baustein.html` | Der HTML-Block, der in die Kundenseite kopiert wird. |
| `danke.html` | Die Seite nach dem Absenden. |
| `beispiel/index.html` | Beispielseite eines Betriebs, zum Ausprobieren. |

## Wie eine Stelle bearbeitbar wird

Im HTML der Kundenseite bekommt die Stelle zwei Markierungen:

```html
<p>Telefon: <a href="tel:+4922371234567"><!--wg:telefon-->02237 1234567<!--/wg--></a></p>
```

Mehr nicht. Der Pflegebereich findet diese Markierungen von selbst, zeigt sie
als Formularfeld an und schreibt den neuen Text an genau dieselbe Stelle
zurück. Das HTML drumherum sieht der Kunde nie.

Wird das Feld `telefon` oder `mail` geändert, wird der anklickbare Verweis
(`tel:` / `mailto:`) mitgezogen. Ohne das stünde auf der Seite die neue Nummer,
und der Anruf ginge an die alte — Prüfpunkt 5 unseres eigenen Katalogs, und
niemandem würde es auffallen.

## Wie ein Bild austauschbar wird

Dieselbe Idee, eine Markierung direkt vor dem Bild:

```html
<!--wg:bild:team-->
<img src="bilder/team.jpg" alt="Unser Team vor dem Firmenwagen">
```

Der Kunde sieht dann das aktuelle Bild, ein Auswahlfeld und die
Bildbeschreibung. Was er hochlädt, wird geprüft (nur JPG, PNG, WEBP — und
zwar am Inhalt, nicht an der Dateiendung), auf 1600 Pixel lange Kante
verkleinert und unter demselben Dateinamen abgelegt. Das alte Bild wandert
vorher in die Sicherungen.

**Warum verkleinert wird:** Aus einem Telefon kommen 4000 Pixel und mehrere
Megabyte. Ungefragt hochgeladen macht das eine schnelle Seite langsam —
Prüfpunkt 4, mit dem wir selbst argumentieren. Der Kunde soll darüber nicht
nachdenken müssen.

Hinter dem Dateinamen im HTML steht danach eine Zählnummer
(`bilder/team.jpg?v=1787259003`). Ohne sie zeigt der Browser des Inhabers
noch tagelang das alte Bild und er ruft an, weil „nichts passiert ist".

Sinnvolle Feldnamen, für die es schon eine Beschriftung gibt: `telefon`,
`mail`, `oeffnungszeiten`, `stellenanzeige`, `hinweis`, `einleitung`,
`leistungen`, `notdienst`, `anschrift`, `ueber_uns`. Andere Namen gehen auch,
dann steht der Name selbst als Beschriftung da.

**Die Grenze bleibt eng.** Bearbeitbar wird nur, was sich tatsächlich ändert.
Alles, was der Kunde eingibt, wird als Text behandelt und maskiert — er kann
das Layout nicht zerlegen, weil er es nie zu sehen bekommt. Ein Baukasten ist
ausdrücklich nicht das Ziel.

## Einrichten beim Kunden

1. Ordner `pflege/` in den Webspace legen, die drei PHP-Dateien hinein.
2. Passwort setzen. Hash einmalig erzeugen:
   `php -r "echo password_hash('DasPasswort', PASSWORD_DEFAULT);"`
   und als Umgebungsvariable `WG_PFLEGE_HASH` hinterlegen. Steht keine
   da, gilt das Muster-Passwort aus `index.php` — **das muss vor dem
   Livegang weg.**
3. Liegt die Website nicht im Ordner daneben, den Pfad über
   `WG_PFLEGE_SEITEN` setzen.
4. In `formular.php` `EMPFAENGER` und `BETRIEB` eintragen.
5. `formular-baustein.html` in die Kontaktseite kopieren, `danke.html`
   danebenlegen.
6. Markierungen in die Kundenseite setzen.
7. Ordner `pflege/` per `.htaccess` zusätzlich absichern, wenn der Hoster das
   anbietet — Gürtel und Hosenträger.

## Was geprüft ist und was nicht

**Geprüft** (lokal, PHP 8.4.19):

- Felder lesen aus einer Beispielseite: 5 Stellen gefunden.
- Speichern: Werte landen an der richtigen Stelle, das HTML drumherum bleibt
  Zeichen für Zeichen unverändert (per `diff` verglichen).
- Sicherung wird vor jedem Speichern angelegt, 20 Stände je Datei bleiben.
- `tel:`-Verweis wird mitgezogen: `02237 55 66 77` → `tel:+492237556677`,
  `0221 / 98 76 54` → `tel:+49221987654`.
- Anmeldung mit falschem Passwort scheitert, mit richtigem nicht.
- Bild austauschen: ein Foto mit 4000 × 3000 Pixeln wird zu 1600 × 1200 und
  30 KB, das alte Bild liegt in den Sicherungen, die Zählnummer im HTML wird
  gesetzt.
- Eine als Bild getarnte PDF-Datei wird abgewiesen („Das ist kein Bild").
- Bildbeschreibung ändern und wieder auslesen.
- Formular: gefüllte Spamfalle und Absenden in unter drei Sekunden werden
  stillschweigend verworfen (der Absender bekommt trotzdem die Dankeseite —
  ein Spamprogramm soll nicht lernen, woran es gescheitert ist).

**Nicht geprüft**, weil im Container nicht prüfbar:

- Der tatsächliche Mailversand. `mail()` ist hier nicht eingerichtet; die
  Anfrage landet deshalb auf der Fehlerseite. Beim ersten Pilotprojekt ist das
  der erste Test auf dem echten Hosting.
- Das Verhalten unter einem echten Hosting-Tarif (Dateirechte, `open_basedir`).

## Was das für das Konzept bedeutet

- Der Grund, warum es keine Betreuung mehr gibt: Der Pflegebereich nimmt dem
  Kunden genau die Arbeit ab, für die sie bezahlt worden wäre. Das entwertet
  Schärfe: Öffnungszeiten, Telefonnummer, Stellenanzeige und Hinweise macht
  der Kunde selbst, sofort und ohne uns zu fragen.
- Das Abhängigkeitsargument im Verkauf wird stärker: „Ihre Domain, Ihr Vertrag,
  Ihre Rechnung — und die Sachen, die sich ständig ändern, ändern Sie selbst."
- Die Anforderung an das Hosting wächst um einen Punkt: Es muss PHP können.
  Das können alle üblichen Tarife; ein reiner Baukasten-Tarif kann es nicht —
  aber der scheitert ohnehin schon daran, dass man dort keine eigenen Dateien
  hochladen darf.
