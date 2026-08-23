---
name: auslieferung
description: Eine gebaute Kundenwebsite ausliefern, von der Freigabe bis zur Übergabe. Nutze diesen Skill, sobald es darum geht, eine Website zu einem Kunden zu bringen, sie auf einem Hosting zu prüfen, ein Paket zu schnüren, eine Domain umzustellen oder die Übergabe vorzubereiten. Auch bei "liefere X aus", "Website hochladen", "Abnahme", "Livegang", "Paket bauen", "Übergabe".
---

# Auslieferung einer Kundenwebsite

Der Weg von "der Kunde hat zugesagt" bis "er pflegt seine Seite selbst".
Nicht der Website-Check, das ist die Pipeline und steht in `CLAUDE.md`.

## Was diesen Ablauf teuer macht, wenn man ihn abkürzt

Jeder Punkt hier steht wegen eines Fehlers, der einmal passiert ist:

- Eine Testanfrage ging an die echte Adresse des Kunden.
- Ein eingebautes Notfallpasswort ließ jeden in den Pflegebereich.
- Die Datenschutzerklärung sagte "nicht gespeichert", während gespeichert wurde.
- Eine Anfrage lag auf dem Server, und niemand sah sie je.
- Der Eingangszeitpunkt war sechs Stunden falsch, weil der Server im Ausland stand.

Keiner davon fiel beim Lesen des Codes auf. Alle fielen auf, als jemand
nachgesehen hat.

## Reihenfolge

Die Stufen bauen aufeinander auf. Keine überspringen, auch nicht bei Eile.

### A · Paket bauen

```
python3 studie/pflege/aufsetzen.py studie/<kunde>
```

Erzeugt zwei ZIPs und würfelt ein neues Passwort. **Das Passwort erscheint
genau einmal auf dem Bildschirm.** Gib es der Nutzerin sofort weiter und sag
dazu, dass es nirgends nachschlagbar ist.

- `<kunde>-website.zip` geht an den Kunden. Echter Empfänger im Formular.
- `<kunde>-TEST.zip` ist für unser Testgerät. Anderer Empfänger, alle Seiten
  auf `noindex`, Selbsttest liegt bei.

Das Werkzeug `selbsttest.php` darf **nie** im Auslieferpaket landen. Es
verändert Inhalte, um sie zu prüfen.

### B · Auf einem Testgerät beweisen

Der Pflegebereich muss einmal auf echtem Webspace gelaufen sein, bevor ein
Kunde ihn sieht. Lokale Tests finden die Hälfte nicht: Zeitzone,
Schreibrechte, gesperrte Funktionen, ausgeschaltete Erweiterungen.

Testpaket hochladen, dann `selbsttest.php` aufrufen. Neunzehn Prüfungen,
Ergebnis als Liste. Was sie ändert, stellt sie zurück.

Zwei Dinge kann sie nicht, die bleiben Handarbeit:

- Wie die Seite auf einem **echten Handy** aussieht.
- Ob eine **Mail wirklich ankommt**. Das geht erst auf dem Hosting des Kunden.

### C · Freigabe des Kunden

`studie/<kunde>/FREIGABEBLATT.md` ausgefüllt und unterschrieben zurück.
**Ohne Unterschrift wird an keiner Domain gedreht.** Nicht aus Förmlichkeit:
Beim Umstellen kann seine Firmenpost ausfallen.

Drei Antworten hängen an allem Weiteren: sein Hostinganbieter, ob ein
Auftragsverarbeitungsvertrag besteht, und wie lange der Anbieter Protokolle
aufbewahrt. Solange die beiden letzten fehlen, steht dazu **nichts** in seiner
Datenschutzerklärung. Lieber nichts eintragen als etwas Falsches.

### D · Sein Hosting prüfen

Braucht seine FTP-Zugangsdaten. Erfahrungsgemäß der langsamste Schritt, und
zwar nicht wegen der Technik: kaum ein Handwerksbetrieb hat sie griffbereit.
Früh fragen, nicht am Liefertag.

Drei Bedingungen, in dieser Reihenfolge zu prüfen:

1. **PHP 8** vorhanden
2. **Ordner beschreibbar** (sonst kein Pflegebereich)
3. **Mailversand** erlaubt

Der Webordner heißt je nach Anbieter `htdocs`, `www`, `public_html` oder
`httpdocs`.

Läuft kein Mailversand, ist das kein Ausschluss: Die Anfragen landen in
`pflege/anfragen.php` und werden im Pflegebereich angezeigt. Sag dem Kunden,
dass er dort nachsieht.

### E · Auf seine Vorschau-Adresse

Jetzt die **Auslieferfassung**, nicht die Testfassung. Danach die vierzehn
Punkte aus `studie/<kunde>/LIVEGANG.md`, Abschnitt 4.

Der entscheidende ist Punkt 6: Telefonnummer im Pflegebereich ändern, dann das
Impressum aufrufen. Steht sie dort auch, funktioniert die ganze Mechanik.
Steht sie nicht dort, ist der Rest egal.

Punkt 10 ist der Grund für diese Stufe: Kontaktformular absenden, und die Mail
muss in seinem Postfach liegen. Vorher nirgends prüfbar.

Er bestätigt die Vorschau schriftlich. WhatsApp genügt.

### F · Domain umstellen

Vollständig in `LIVEGANG.md`, Abschnitt 5. Drei Dinge, die niemand vergessen
darf:

- **Alle DNS-Einträge aufschreiben, bevor irgendetwas geändert wird.** A,
  CNAME, TXT, SPF, DKIM und vor allem **MX**. Das ist der Rückweg.
- **MX exakt übernehmen.** Ein falscher MX-Eintrag heißt: seine Firmenmails
  kommen nicht mehr an, und er merkt es erst, wenn ein Kunde sich beschwert.
- **Dienstag bis Donnerstag vormittags.** Nie freitags, nie vor einem Feiertag.

Danach beide Richtungen prüfen: Mail an ihn, Mail von ihm heraus. Erst dann
ist der Umzug fertig.

### G · Übergabe

`ANLEITUNG.html` ausdrucken und mit ihm durchgehen. **Er** meldet sich an,
**er** ändert etwas, **er** holt einen Stand zurück. Wer es einmal selbst
gemacht hat, ruft später nicht an.

Dann ändert er das Passwort, und wir sehen dabei weg. Danach kommen wir selbst
nicht mehr hinein, und genau das ist der Punkt.

Zum Schluss aussprechen, dass die Arbeit endet. Sonst steht die Erwartung im
Raum und wir arbeiten ein Jahr umsonst.

## Regeln, die in jeder Stufe gelten

**Nichts erfinden.** Keine Zahl, keine Frist, keine Zusage über Dritte, die
nicht geprüft ist. Das gilt besonders in Rechtstexten: Was in Impressum und
Datenschutzerklärung steht, muss dem entsprechen, was die Software tut.
Stimmt der Code nicht mehr mit dem Text überein, ist das ein Fehler im
Produkt, nicht eine Formulierungsfrage.

**Keine Zugangsdaten in Dateien oder ins Repo.** Passwörter nur als Hash auf
dem Server. Das Klartext-Passwort erscheint einmal beim Aufsetzen und wird
mündlich oder auf Papier übergeben.

**Nichts Kundenspezifisches in `studie/pflege/`.** Das ist die Vorlage für den
nächsten Kunden. Adressen, Namen und Nummern gehören in `studie/<kunde>/`.

**Vorlage und Kundenfassung von `inhalt.php` und `index.php` bleiben
byteweise gleich.** Wer eine ändert, ändert beide. Sonst driften sie
auseinander und der nächste Kunde erbt einen alten Fehler.

**Nach jeder Änderung am Pflegebereich:** Anmelden mit richtigem und falschem
Passwort, speichern und die Übertragung auf alle Seiten nachzählen, einen
Stand zurückholen, Passwort ändern, und die Direktaufrufe von `inhalt.php`,
`passwort.php`, `anfragen.php` und `sicherungen/` prüfen. Alle vier müssen 404
mit 0 Bytes liefern.

**Achtung beim eingebauten Server von PHP:** `php -S` beantwortet den Aufruf
einer nicht vorhandenen Datei mit `index.php` und liefert 200. Eine Datei, die
im Testordner gar nicht existiert, sieht damit aus wie eine offene Datei. Bei
Sperrtests immer mit wirklich vorhandener Datei prüfen.

**Keine Gedankenstriche** in Texten, Kommentaren und Code.

## Was nicht automatisierbar ist

Sag das offen, statt es zu verschleiern:

- **Die Zugangsdaten des Kunden.** Die gibt ein Mensch heraus, nicht eine
  Software.
- **Die Entscheidungen des Kunden.** Stimmen die Angaben, welche Fotos, wann
  darf umgestellt werden.
- **Ob eine Mail wirklich ankommt.** Braucht ein Postfach.
- **Wie es auf einem echten Handy aussieht.**

Alles andere ist Fließbandarbeit und gehört in ein Skript.
