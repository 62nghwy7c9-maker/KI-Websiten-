# K&D Webdesign — die eigene Website

Ersetzt `studie/seite/` (Webgewerk). Gleiches Schema wie bei den Kunden:
statische Seiten plus Pflegebereich. Wer Websites nach diesem Muster
verkauft, muss die eigene Seite genauso bauen — sonst ist das erste, was ein
Kunde sieht, ein Widerspruch.

## Was hier liegt

```
seite/            die Website
  index.html      Onepager: Check, was wir bauen, Pflegebereich, Ablauf, Preise, Kontakt
  impressum.html  mit sichtbarem Sperrvermerk, solange die Anschrift fehlt
  datenschutz.html inklusive Art.-14-Absatz zum Website-Check
  danke.html      nach dem Absenden
  stil.css        warmes Weiß, Anthrazit, ein Akzent in Ocker
  bilder/pflegebereich.png  echter Bildschirmausschnitt, Beispieldaten
pflege/           Pflegebereich und Formular
demo.html         Probefassung fürs Browserfenster
demo_bauen.py     erzeugt demo.html aus seite/
```

## Was sich gegenüber der Vorfassung geändert hat

- **Name:** K&D Webdesign statt Webgewerk, in allen Unterlagen.
- **Zielgruppe:** nicht mehr nur Handwerk. Die Seite spricht Handwerk,
  Gastronomie, Vereine, Praxen und Handel an — mit je einem eigenen Absatz,
  der sagt, was in dieser Branche typischerweise fehlt.
- **Der Pflegebereich ist ein Verkaufsargument geworden.** Er hat einen
  eigenen Abschnitt mit Bildschirmausschnitt. Das kann kein Wettbewerber aus
  der Preisklasse zeigen.
- **19 Prüfpunkte stehen einzeln auf der Seite.** Wer prüfen lässt, soll
  vorher lesen können, was geprüft wird.

## Was noch fehlt — vor dem Livegang

1. **Ladungsfähige Anschrift.** Impressum und Datenschutz tragen
   `[Straße und Hausnummer]`. Der rote Kasten im Impressum weist darauf hin
   und wird danach gelöscht. **Ohne die Anschrift darf die Seite nicht
   online gehen.**
2. **Domain und E-Mail.** `kd-webdesign.de` ist nicht geprüft; die Adresse
   `hallo@kd-webdesign.de` steht schon auf der Seite und in `absender.json`.
3. **Telefonnummer bestätigen.** Auf der Seite steht 0162 3242260. Es waren
   zwei im Umlauf.
4. **Betreuungspreis bestätigen.** Auf der Seite stehen 69 € im Monat; die
   Zahl 59 stand ebenfalls im Raum. Das Feld ist im Pflegebereich änderbar.
5. **Rechtstexte prüfen lassen.** Beides ist sorgfältig geschrieben, aber
   keine Rechtsberatung.

## Einrichten

Wie bei jedem Kundenprojekt: Inhalt von `seite/` in den Webspace, `pflege/`
daneben, `WG_PFLEGE_SEITEN` auf den Ordner mit den HTML-Dateien setzen,
`WG_PFLEGE_HASH` mit einem eigenen Passwort belegen. Ohne den letzten Schritt
gilt das Musterpasswort.

## Geprüft

PHP 8.4.19 und Chromium: alle vier Seiten laden, Bild lädt, Pflegebereich
liest sieben Felder und ein Bild, Speichern ändert alle Vorkommen und zieht
Impressum, Datenschutz und Danke-Seite mit, alle sieben `tel:`-Verweise
wandern mit. Kein Konsolenfehler. Nicht prüfbar: der Mailversand.
