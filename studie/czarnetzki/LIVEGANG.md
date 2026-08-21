# Livegang: die Website auf seine Domain bringen

Für Kira. Reihenfolge einhalten, nichts überspringen.
Sein bisheriger Auftritt liegt unter `pcelektro.de`.

---

## 0. Vor allem anderen: die Freigabe

Ohne unterschriebenes FREIGABEBLATT.md wird nichts umgestellt. Darauf
stehen die sechs Fragen, unter anderem die Öffnungszeiten, die wir aus
Verzeichnissen haben und nicht von ihm.

Solange die Freigabe fehlt, ist alles hier verfrüht.

---

## 1. Herausfinden, welcher Fall vorliegt

Das entscheidet über den ganzen Rest. Fragen Sie ihn, oder lassen Sie es
sich am Rechner zeigen:

**Fall A: Er kann bei seinem jetzigen Anbieter eigene Dateien hochladen,
und seine Mails laufen über dieselbe Firma.**
Der einfache Fall. Wir tauschen nur die Dateien im Webspace aus. An DNS und
MX wird nichts angefasst, seine Mails können gar nicht ausfallen.

**Fall B: Sein Tarif erlaubt kein Hochladen eigener Dateien.**
Typisch bei Baukästen. Dann muss ein neuer Tarif her, und die Domain zieht
um. Der riskante Fall, weil dabei die Mail-Einträge angefasst werden.

Drei Fragen, die den Fall klären:

1. Gibt es einen Zugang mit Benutzername und Passwort für einen
   Dateimanager oder für FTP?
2. Steht im Tarif etwas von PHP?
3. Über welche Firma kommen seine Mails, und ist es dieselbe?

---

## 2. Prüfen, ob der Tarif reicht

Gebraucht werden nur zwei Dinge:

- **PHP.** Kann jeder übliche Tarif. Wenn Sie unsicher sind: eine Datei
  `test.php` mit dem Inhalt `<?php echo "geht";` hochladen, im Browser
  aufrufen. Steht dort `geht`, ist alles in Ordnung. Steht dort der
  Programmtext selbst, kann der Tarif kein PHP. Datei danach löschen.
- **Eigene Dateien hochladen dürfen.**

Nicht gebraucht: Datenbank, WordPress, ein Baukasten, irgendein Zusatz.

---

## 3. Hochladen

Den **Inhalt** von `webroot/` in das Webverzeichnis legen. Nicht den Ordner
selbst, nur was darin liegt. Das Verzeichnis heißt je nach Anbieter
`htdocs`, `httpdocs`, `public_html` oder `www`.

Danach muss es dort so aussehen:

    index.html
    impressum.html
    datenschutz.html
    danke.html
    stil.css
    bilder/
    pflege/

`INSTALLATION.txt` danach löschen.

Es ist nichts einzustellen. Der Pflegebereich findet die Seiten von selbst,
weil er eine Ebene tiefer liegt.

---

## 4. Auf der Vorschau-Adresse testen, bevor die Domain umgestellt wird

Fast jeder Anbieter gibt eine vorläufige Adresse, etwas wie
`kunde1234.hoster.de`. Dort läuft die Seite schon, bevor `pcelektro.de`
darauf zeigt. Diese Prüfung findet dort statt, nicht auf der echten Domain.

Prüfen Sie in dieser Reihenfolge:

1. Startseite lädt.
2. Auf dem Handy aufrufen, nicht nur das Fenster schmal ziehen.
3. Impressum und Datenschutz sind erreichbar.
4. **Kontaktformular ausfüllen und absenden. Kommt die Mail an?**
   Das ist der wichtigste Test, und er lässt sich nur hier machen, nie
   vorher. Empfänger steht in `pflege/formular.php`: `info@pcelektro.de`.
   Kommt nichts an, weiter bei Punkt 8.
5. Pflegebereich unter `.../pflege` aufrufen, anmelden, Öffnungszeiten
   ändern, speichern, Startseite neu laden. Steht es da?
6. Einen früheren Stand zurückholen. Kommt der alte Text wieder?
7. HTTPS: Zertifikat im Kundenmenü einschalten, meist ein Klick, und die
   Weiterleitung von `http` auf `https` gleich mit. Danach muss im Browser
   das Schloss stehen.

Erst wenn alle sieben Punkte stimmen, geht es weiter.

---

## 5. Die Domain umstellen

**Bei Fall A entfällt dieser Abschnitt vollständig.** Die Domain zeigt
schon auf diesen Webspace, die Dateien sind ausgetauscht, Sie sind fertig.
Springen Sie zu Abschnitt 6.

**Bei Fall B, in dieser Reihenfolge:**

1. **Alles aufschreiben, was jetzt gilt.** Alle DNS-Einträge beim alten
   Anbieter exportieren oder abfotografieren: A, CNAME, vor allem **MX**,
   dazu TXT, SPF und DKIM. Diese Liste ist der Rückweg. Ohne sie kein
   Umzug.
2. **Er bestätigt die Vorschau-Adresse.** Schriftlich, und sei es per
   WhatsApp. Vorher wird nichts umgestellt.
3. **TTL senken.** 24 Stunden vorher die Gültigkeit der DNS-Einträge auf
   5 Minuten setzen. Das ist der Unterschied zwischen "in fünf Minuten
   zurück" und "in zwei Tagen zurück", wenn etwas schiefgeht.
4. **Umstellen: Dienstag bis Donnerstag vormittags.** Nie freitags, nie vor
   einem Feiertag. Sie wollen den ganzen Tag und den nächsten zum
   Nachbessern haben.
   Dabei **nur die Einträge für die Website ändern. MX exakt übernehmen.**
   Ein falscher MX-Eintrag heißt: seine Mails kommen nicht mehr an, und er
   merkt es erst, wenn ein Kunde sich beschwert.
5. **Sofort prüfen**, nicht später:
   - Seite unter `pcelektro.de` aufrufen.
   - Eine Testmail **an** `info@pcelektro.de` schicken. Kommt sie an?
   - Eine Testmail **von** dort **heraus** schicken. Kommt sie an?
   Erst wenn beide Richtungen laufen, ist der Umzug fertig.
6. **Er bestätigt schriftlich, dass seine Mails ankommen.** Ohne diese
   Bestätigung keine Schlussrechnung.
7. **TTL nach 48 Stunden ohne Auffälligkeiten** wieder anheben.
8. **Den alten Tarif frühestens einen Monat später kündigen.** Solange die
   alte Seite dort noch liegt und die notierten DNS-Einträge vorliegen, ist
   der Stand von vorher in Minuten wiederhergestellt. Das kostet ihn
   einmalig 15 bis 30 Euro und ist die günstigste Versicherung im ganzen
   Projekt.

---

## 6. Übergabe

Erst wenn Abschnitt 4 und 5 abgehakt sind:

1. **Die Anleitung ausdrucken** (`ANLEITUNG.html`, im Browser öffnen und
   drucken) und mit ihm einmal durchgehen, am Rechner,
   nicht am Telefon. Er meldet sich selbst an, ändert selbst etwas, holt
   selbst einen Stand zurück. Wer es einmal gemacht hat, ruft später nicht
   an.
2. **Passwort ändern lassen.** Er tippt es selbst ein, wir sehen es nicht.
   Das ausgelieferte `Heerstrasse15A` gilt danach nicht mehr.
3. **Zugangsdaten übergeben:** Hosting-Zugang, Domain-Zugang, die Adresse
   `pcelektro.de/pflege`. Alles gehört ihm, nicht uns.
4. **Google-Unternehmensprofil** ansprechen. Das ist Prüfpunkt 14 aus dem
   Check und Sache des Betriebs, aber sagen Sie es ihm, statt es
   wegzulassen.
5. **Sagen, dass wir raus sind.** Ohne Betreuungsvertrag endet unsere
   Arbeit hier. Er kann anrufen, aber er zahlt dann nach Aufwand. Das muss
   klar gesagt sein, sonst steht die Erwartung im Raum.

---

## 7. Wenn etwas nicht funktioniert

**Die Seite ist weiß oder zeigt Programmtext.**
Der Tarif kann kein PHP, oder die Dateien liegen eine Ebene zu tief. Prüfen
Sie, ob `index.html` direkt im Webverzeichnis liegt und nicht in einem
Unterordner `webroot`.

**Der Pflegebereich meldet "schreibgeschützt".**
Die Dateirechte im Webspace stehen zu eng. Im Dateimanager des Anbieters
für die vier HTML-Dateien und den Ordner `pflege` Schreibrecht setzen.

**Das Kontaktformular schickt nichts.**
Manche Anbieter versenden nur an eine Adresse derselben Domain, manche
verlangen einen SMTP-Zugang. Beim Anbieter nachfragen, wie Mailversand aus
PHP dort geregelt ist. Solange das offen ist, steht die Telefonnummer
sichtbar oben auf der Seite, es geht also nichts verloren.

**Nach der Umstellung kommen keine Mails mehr.**
Die notierten MX-Einträge zurücksetzen, sofort. Deshalb Abschnitt 5 Punkt 1.
Deshalb TTL 5 Minuten. Deshalb Dienstagvormittag.

**Der Pflegebereich ist von außen erreichbar, aber `sicherungen` auch.**
Dann wertet der Server die `.htaccess` nicht aus. Das ist bei Apache der
Normalfall und bei nginx nicht. Beim Anbieter nachfragen. Es ist kein
akutes Loch, dort liegen nur frühere Fassungen öffentlicher Seiten, aber es
gehört geschlossen.
