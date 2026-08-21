# Czarnetzki: die Seite ans Netz bringen

Von oben nach unten abarbeiten. Teil 1 komplett, dann erst Teil 2.
Was in eckigen Klammern steht, ist zum Abhaken.

## Was man dafür braucht

- Die Datei `czarnetzki-website.zip`
- Einen Hosting-Zugang mit PHP, auf den eigenen Namen
- Eine eigene E-Mail-Adresse zum Testen des Formulars
- Das Passwort für den Pflegebereich: `Heerstrasse15A`

Teil 1 kann eine Person allein machen. Teil 2 nicht: Dort geht es um den
Kunden, seine Unterschrift und seine Domain.

## Teil 1: Bei uns testen

Hier passiert nichts, was den Kunden betrifft. Wir stellen nur fest, ob
alles funktioniert.

- [ ] **1. Ausweisprüfung abschließen.** Der Anbieter will wissen, wer den
  Vertrag abschließt. Das macht Yannik, der Link kam per E-Mail. Ein
  Personalausweis reicht.

- [ ] **2. Die Zugangsdaten-Mail suchen.** Im Postfach nach "all-inkl"
  suchen, auch im Spam-Ordner. In der Mail stehen mehrere Blöcke. Wir
  brauchen den Block **KAS**. Darunter stehen ein Login, der aussieht wie
  `w01abc23`, und ein Passwort.

- [ ] **3. Anmelden auf kas.all-inkl.com.** Ins erste Feld kommt der Login
  aus Schritt 2, **nicht** die E-Mail-Adresse. Das ist der häufigste
  Fehler.

- [ ] **4. Die Dateien hochladen.** Im KAS "WebFTP" öffnen. Auf dem eigenen
  Rechner die Datei `czarnetzki-website.zip` entpacken. Darin liegt ein
  Ordner `webroot`. **Den Inhalt** dieses Ordners in den Ordner `htdocs`
  ziehen, nicht den Ordner selbst. `htdocs` ist der Ort, an dem die
  Website liegt.

- [ ] **5. Die Datei `INSTALLATION.txt` löschen.** Die ist nur für uns und
  hat auf einer Website nichts zu suchen.

- [ ] **6. Den Empfänger des Kontaktformulars umstellen.** Wichtig, sonst
  geht die Testmail an den echten Kunden. Im WebFTP die Datei
  `pflege/formular.php` öffnen. Ganz oben steht eine Zeile mit
  `info@pcelektro.de`. Diese Adresse durch die eigene ersetzen, speichern.
  **Vor der Übergabe an den Kunden wieder zurückstellen.**

- [ ] **7. HTTPS einschalten.** Im KAS unter SSL. Meist ein Klick. Danach
  steht im Browser ein kleines Schloss neben der Adresse.

- [ ] **8. Die vorläufige Adresse notieren.** Sie endet auf
  `.kasserver.com` und steht im KAS. Auf ihr wird getestet, nicht auf
  einer echten Domain.

## Der Test

Alles auf der vorläufigen Adresse. Bei jedem Punkt steht, was zu sehen
sein muss.

- [ ] **9.** Startseite aufrufen. Sie steht da, mit Bild und Farben. Kommt
  nur nackter Text, fehlt eine Datei beim Hochladen.
- [ ] **10.** Auf dem Handy aufrufen. Echtes Handy. Nichts läuft seitlich
  über den Rand.
- [ ] **11.** Impressum und Datenschutz sind unten auf der Seite
  erreichbar.
- [ ] **12.** Die Adresse mit `/pflege` dahinter aufrufen und anmelden.
  Das Auslieferpasswort lautet `Heerstrasse15A`. Es erscheint die Übersicht
  mit den Reitern.
- [ ] **13.** Telefonnummer ändern und speichern. Es kommt eine Meldung,
  dass gespeichert wurde.
- [ ] **14. Der wichtigste Punkt.** Jetzt das Impressum aufrufen. Steht
  dort die neue Nummer? Wenn ja, funktioniert der ganze Pflegebereich.
  Wenn nein, brauchen wir gar nicht weitermachen.
- [ ] **15.** Telefonnummer leeren und speichern. Es muss eine Meldung
  kommen, dass nichts gespeichert wurde, und die alte Nummer muss wieder
  dastehen.
- [ ] **16.** Ganz unten einen früheren Stand zurückholen. Der alte Text
  ist wieder da.
- [ ] **17.** Ein Foto vom Handy hochladen. Es erscheint auf der Website.
- [ ] **18. Der zweite wichtige Punkt.** Kontaktformular ausfüllen und
  absenden. Kommt die E-Mail an? Das lässt sich nur hier prüfen, nie
  vorher.
- [ ] **19.** Passwort ändern, abmelden, mit dem neuen anmelden. Und
  einmal mit dem alten versuchen: muss scheitern.
- [ ] **20. Der dritte wichtige Punkt.** Die Adresse `/pflege/inhalt.php`
  direkt eintippen. Es **muss** eine Fehlermeldung kommen. Erscheint dort
  Text, ist eine Schutzeinstellung nicht aktiv.
- [ ] **21.** Dasselbe mit `/pflege/sicherungen/`. Auch hier muss ein
  Fehler kommen, keine Dateiliste.

Erst wenn 9 bis 21 stimmen, geht es weiter.

## Teil 2: Beim Kunden

- [ ] **22. Termin mit Herrn Czarnetzki.** Freigabeblatt mitnehmen und
  unterschreiben lassen. Besonders die Öffnungszeiten bestätigen lassen,
  die haben wir aus Verzeichnissen und nicht von ihm.

- [ ] **23. Herausfinden, wie er heute hostet.** Eine Frage entscheidet
  alles: Kann er bei seinem jetzigen Anbieter eigene Dateien hochladen?
  - **Ja**, und seine E-Mails laufen über dieselbe Firma: der einfache Fall.
  Wir tauschen nur die Dateien aus. Seine E-Mails können nicht ausfallen.
  - **Nein**: die Domain zieht um. Der Fall mit Risiko, siehe Schritt 26.

- [ ] **24. Hosting auf seinen Namen.** Seine Adresse, seine
  Bankverbindung. Niemals auf unseren Vertrag. Sonst hängt sein Betrieb
  an uns, auch wenn wir längst raus sind.

- [ ] **25. Dateien hochladen und die Punkte 9 bis 21 nochmal prüfen.**
  Diesmal auf seinem Hosting. Alles nochmal, nicht aus dem Gedächtnis.
  Dabei zuerst prüfen, dass in `pflege/formular.php` wieder
  `info@pcelektro.de` steht und nicht die Testadresse aus Schritt 6.

- [ ] **26. Nur wenn die Domain umzieht.** In dieser Reihenfolge, ohne
  Abkürzung:
  1. Alle bestehenden Einträge beim alten Anbieter abfotografieren, besonders
  die mit dem Kürzel **MX**. Das sind die für E-Mail. Diese Liste ist der
  Rückweg.
  2. 24 Stunden vorher die Gültigkeitsdauer der Einträge auf 5 Minuten stellen.
  3. Umstellen **Dienstag bis Donnerstag vormittags**. Nie freitags. Nur die
  Einträge für die Website ändern, die MX-Einträge genau übernehmen.
  4. Sofort testen: Seite aufrufen, eine Testmail an ihn schicken, eine von
  seinem Postfach heraus schicken. Erst wenn beides ankommt, ist der Umzug
  fertig.
  5. Den alten Tarif frühestens einen Monat später kündigen.

- [ ] **27. Die Anleitung ausdrucken** und mit ihm am Rechner durchgehen.
  Er meldet sich selbst an, ändert selbst etwas, holt selbst einen Stand
  zurück. Wer es einmal gemacht hat, ruft später nicht an.

- [ ] **28. Ihn selbst das Passwort ändern lassen.** Er tippt es ein, wir
  sehen es nicht.

- [ ] **29. Zugangsdaten übergeben** und klar sagen, dass unsere Arbeit
  hier endet. Sonst steht die Erwartung im Raum, dass wir weiter
  zuständig sind.

## Adressen

- Technische Verwaltung: [kas.all-inkl.com](https://kas.all-inkl.com)
- Dateien hochladen: [webftp.all-inkl.com](https://webftp.all-inkl.com)
- Vertrag und Kündigung: [all-inkl.com/login](https://all-inkl.com/login/)

## Wenn etwas klemmt

**Die Seite bleibt weiß oder zeigt wirren Text.** Die Dateien liegen eine
Ebene zu tief. `index.html` muss direkt in `htdocs` liegen, nicht in einem
Unterordner.

**Der Pflegebereich sagt "schreibgeschützt".** Die Dateirechte sind zu
eng. Im Dateimanager des Anbieters für die vier HTML-Dateien und den
Ordner `pflege` Schreibrecht setzen.

**Das Kontaktformular schickt nichts.** Manche Anbieter regeln den
Mailversand anders. Dort nachfragen. Die Telefonnummer steht sichtbar
oben auf der Seite, es geht also nichts verloren.

**Nach der Umstellung kommen keine E-Mails mehr.** Die abfotografierten
MX-Einträge sofort zurücksetzen. Deshalb Schritt 26.1.
