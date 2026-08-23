---
name: kundenweg
description: Der ganze Weg eines Betriebs, von der Messung seiner alten Website bis zur Uebergabe der neuen. Nutze diesen Skill, sobald es um einen Kunden geht: Website-Check erstellen, Anschreiben, einen zugesagten Betrieb anlegen, Angaben erheben, Seite bauen, pruefen, Paket schnueren, Hosting, Domain, Abnahme. Auch bei "liefere X aus", "neue Kundenwebsite", "Check verschicken", "Livegang", "Uebergabe", "wo steht der Kunde".
---

# Der Kundenweg

Ein Befehl beantwortet immer die Frage "was ist jetzt dran":

```
python -m pipeline kunde stand
```

Er nennt fuer jeden Betrieb die Stufe, das Naechste und den fertigen Befehl
dazu. Steht das Naechste bei einem Menschen, steht das auch da. **Fang jede
Sitzung damit an.**

## Warum es diesen Ablauf gibt

Jede Regel hier steht wegen eines Fehlers, der einmal wirklich passiert ist:

- Eine Testanfrage ging an die echte Adresse des Kunden.
- Ein eingebautes Notfallpasswort liess jeden in den Pflegebereich.
- Die Datenschutzerklaerung sagte "nicht gespeichert", waehrend gespeichert wurde.
- Eine Anfrage lag auf dem Server, und niemand sah sie je.
- Der Eingangszeitpunkt war sechs Stunden falsch, weil der Server im Ausland stand.
- Das Auslieferpasswort stand im Klartext in drei ausgedruckten Papieren.

Keiner davon fiel beim Lesen des Codes auf. Alle fielen auf, als jemand
nachgesehen hat. Deshalb sieht jetzt bei jedem Kunden derselbe Pruefstand
nach, und zwar automatisch.

## Die Kette

### 1 · Betriebe finden und messen

```
python -m pipeline finden --ort Kerpen --branche handwerk
python -m pipeline stapel --liste leads/<datei>.md
```

Ergebnis: je Betrieb ein `kunden/<slug>/messung.json` mit Messwerten und
Befunden.

### 2 · Check und Anschreiben

```
python -m pipeline pakete --slug <slug>
```

Ergebnis: druckfertiger Check, Dossier und ein Anschreiben-Entwurf.

**Der Entwurf wird nie verschickt, sondern gelesen.** Kalte Werbemails an
Betriebe brauchen nach § 7 Abs. 2 Nr. 2 UWG eine Einwilligung, auch im B2B.
Postalische Werbung braucht sie nicht. Der Entwurf ist deshalb ein Brief.

### 3 · Der Betrieb sagt zu

```
python -m pipeline kunde anlegen --slug <slug> --kurzname <name>
```

Legt `studie/<name>/` an, uebernimmt aus der Messung, was als **Vermutung**
taugt, und schreibt den Fragebogen `ERHEBUNG.md`.

Der Unterschied zwischen `vermutet` und `bestaetigt` ist der Kern des
Ganzen: Was in der Messung stand, ist ungeprueft und dient nur dazu, den
Fragebogen vorzubefuellen. **Auf die Seite kommt nur, was der Betrieb selbst
gesagt hat.**

### 4 · Angaben erheben

`ERHEBUNG.md` ausdrucken, zum Termin mitnehmen, Antworten nach
`stammdaten.json` unter `bestaetigt` uebertragen.

Gibt es eine Angabe beim Betrieb wirklich nicht, kommt `entfaellt` hinein.
Leer heisst "noch nicht gefragt", `entfaellt` heisst "gefragt, gibt es
nicht". Ein Impressum ohne Umsatzsteuer-ID kann richtig sein. Ein Impressum,
bei dem niemand gefragt hat, ist es nie.

### 5 · Texte schreiben

`studie/<name>/texte.md`. Fakten stehen in `stammdaten.json`, hier gehoert
die Prosa hin. Das Format steht in `pipeline/texte.py`.

Diese Trennung ist keine Schoenheit: Fakten kommen vom Betrieb und muessen
stimmen, Saetze schreiben wir und muessen zum Betrieb passen. Beides in einer
Datei zu mischen fuehrt dazu, dass beim Umformulieren eine Rufnummer
verrutscht.

Der Ton kommt aus dem Betrieb, nicht aus einem Muster. Was er auf seiner
alten Seite ueber sich schreibt, ist das beste Material. **Nichts erfinden:**
keine Referenz, keine Zahl, keine Auszeichnung, die nicht belegt ist.

### 6 · Bauen

```
python -m pipeline kunde bauen <name>
```

Erzeugt den kompletten `webroot/` und die vier Papiere. Fehlt eine
Pflichtangabe, bricht der Bau ab und nennt sie. Es gibt keinen Platzhalter,
der versehentlich live gehen kann.

Ein fuenftes Papier entsteht absichtlich nicht: `LIESMICH.md` haelt fest,
woher die Inhalte dieses einen Entwurfs stammen und was daran offen ist. Das
schreibt ein Mensch, sonst entstuende ein Dokument, das aussieht wie eine
Herkunftsangabe, aber keine ist.

### 7 · Pruefen

```
python -m pipeline kunde pruefen <name>
```

Zwanzig Punkte, unter anderem: ueberall dieselbe Rufnummer, Formular zeigt
auf den Betrieb, Datenschutzerklaerung beschreibt genau das, was der Code
tut, Pflegebereich byteweise wie die Vorlage, kein Werkzeug im Paket.

Der Pruefstand nennt am Ende selbst, was er **nicht** messen kann. Diese vier
Punkte bleiben Handarbeit und duerfen nie als erledigt gelten.

### 8 · Packen

```
python -m pipeline kunde packen <name>
```

Laeuft nur bei gruenem Pruefstand. Erzeugt zwei Pakete und wuerfelt ein
Passwort.

- `<name>-website.zip` geht an den Kunden. Echter Empfaenger im Formular.
- `<name>-TEST.zip` ist fuer unser Testgeraet. Andere Adresse, alle Seiten
  auf `noindex`, Selbsttest liegt bei.

**Das Passwort erscheint genau einmal auf dem Bildschirm.** Sofort
weitergeben und dazusagen, dass es nirgends nachschlagbar ist. Es steht in
keiner Datei und in keinem Papier.

Das Werkzeug `selbsttest.php` darf nie im Auslieferpaket landen. Es
veraendert Inhalte, um sie zu pruefen.

### 9 · Auf einem Testgeraet beweisen

Der Pflegebereich muss einmal auf echtem Webspace gelaufen sein, bevor ein
Kunde ihn sieht. Lokale Tests finden die Haelfte nicht: Zeitzone,
Schreibrechte, gesperrte Funktionen.

Testpaket hochladen, dann `pflege/selbsttest.php?s=<schluessel>` aufrufen.
Neunzehn Pruefungen, Ergebnis als Liste. Was sie aendert, stellt sie zurueck.

### 10 · Freigabe des Kunden

`FREIGABEBLATT.md` ausgefuellt und unterschrieben zurueck. **Ohne
Unterschrift wird an keiner Domain gedreht.** Nicht aus Foermlichkeit: Beim
Umstellen kann seine Firmenpost ausfallen.

Drei Antworten haengen an allem Weiteren: sein Hostinganbieter, ob ein
Auftragsverarbeitungsvertrag besteht, und wie lange der Anbieter Protokolle
aufbewahrt. Solange die beiden letzten fehlen, steht dazu **nichts** in seiner
Datenschutzerklaerung. Der Bau laesst diese Saetze dann einfach weg.

### 11 · Sein Hosting pruefen

Braucht seine FTP-Zugangsdaten. Erfahrungsgemaess der langsamste Schritt, und
zwar nicht wegen der Technik: kaum ein Handwerksbetrieb hat sie griffbereit.
Frueh fragen, nicht am Liefertag.

Drei Bedingungen, in dieser Reihenfolge: **PHP 8**, **Ordner beschreibbar**,
**Mailversand**. Der Webordner heisst je nach Anbieter `htdocs`, `www`,
`public_html` oder `httpdocs`.

Laeuft kein Mailversand, ist das kein Ausschluss: Die Anfragen landen in
`pflege/anfragen.php` und werden im Pflegebereich angezeigt.

### 12 · Auf seine Vorschau-Adresse

Jetzt die **Auslieferfassung**, nicht die Testfassung. Danach die vierzehn
Punkte aus `LIVEGANG.md`, Abschnitt 4.

Punkt 6 ist der entscheidende: Telefonnummer im Pflegebereich aendern, dann
das Impressum aufrufen. Steht sie dort auch, funktioniert die ganze Mechanik.

Punkt 10 ist der Grund fuer diese Stufe: Kontaktformular absenden, und die
Mail muss in seinem Postfach liegen. Vorher nirgends pruefbar.

### 13 · Domain umstellen

Vollstaendig in `LIVEGANG.md`, Abschnitt 5. Drei Dinge, die niemand
vergessen darf:

- **Alle DNS-Eintraege aufschreiben, bevor irgendetwas geaendert wird.** A,
  CNAME, TXT, SPF, DKIM und vor allem **MX**. Das ist der Rueckweg.
- **MX exakt uebernehmen.** Ein falscher MX-Eintrag heisst: seine Firmenmails
  kommen nicht mehr an, und er merkt es erst, wenn ein Kunde sich beschwert.
- **Dienstag bis Donnerstag vormittags.** Nie freitags, nie vor einem Feiertag.

Danach beide Richtungen pruefen: Mail an ihn, Mail von ihm heraus.

### 14 · Uebergabe

`ANLEITUNG.html` ausdrucken und mit ihm durchgehen. **Er** meldet sich an,
**er** aendert etwas, **er** holt einen Stand zurueck. Wer es einmal selbst
gemacht hat, ruft spaeter nicht an.

Dann aendert er das Passwort, und wir sehen dabei weg. Danach kommen wir
selbst nicht mehr hinein, und genau das ist der Punkt.

Zum Schluss aussprechen, dass die Arbeit endet. Sonst steht die Erwartung im
Raum und wir arbeiten ein Jahr umsonst.

## Regeln, die auf jeder Stufe gelten

**Nichts erfinden.** Keine Zahl, keine Frist, keine Zusage ueber Dritte, die
nicht geprueft ist. Besonders in Rechtstexten: Was in Impressum und
Datenschutzerklaerung steht, muss dem entsprechen, was die Software tut.
Stimmt der Code nicht mehr mit dem Text ueberein, ist das ein Fehler im
Produkt, keine Formulierungsfrage. Der Pruefstand misst genau das.

**Keine Zugangsdaten in Dateien oder ins Repo.** Passwoerter nur als Hash auf
dem Server. Das Klartext-Passwort erscheint einmal beim Packen und wird
muendlich oder auf Papier uebergeben.

**Fotos kommen vom Betrieb.** Keine gekauften Bilder mit Menschen darauf, die
nicht er ist. Sein Logo verwenden wir nicht.

**Nichts Kundenspezifisches in `studie/pflege/`.** Das ist die Vorlage fuer
den naechsten Kunden. Namen, Adressen und Nummern gehoeren nach
`studie/<name>/stammdaten.json`.

**Am Pflegebereich nur in der Vorlage aendern, nie beim Kunden.** Der
Pruefstand vergleicht byteweise. Wer beim Kunden aendert, faellt auf.

**Nichts von Hand im `webroot/`.** Der naechste Bau macht es weg. Der
Pruefstand merkt es und sagt es. Was fehlt, gehoert nach `texte.md` oder
`stammdaten.json`.

**Achtung beim eingebauten Server von PHP:** `php -S` beantwortet den Aufruf
einer nicht vorhandenen Datei mit `index.php` und liefert 200. Eine Datei,
die im Testordner gar nicht existiert, sieht damit aus wie eine offene Datei.
Bei Sperrtests immer mit wirklich vorhandener Datei pruefen. Fuer echte
Gleichzeitigkeit `PHP_CLI_SERVER_WORKERS=10` setzen.

**Keine Gedankenstriche** in Texten, Kommentaren und Code.

## Was nicht automatisierbar ist

Sag es offen, statt es zu verschleiern:

- **Die Zugangsdaten des Kunden.** Die gibt ein Mensch heraus.
- **Die Entscheidungen des Kunden.** Stimmen die Angaben, welche Fotos, wann
  darf umgestellt werden.
- **Ob eine Mail wirklich ankommt.** Braucht ein Postfach.
- **Wie es auf einem echten Handy aussieht.**
- **Ob die Texte gut sind.**

Alles andere ist Fliessbandarbeit und gehoert in ein Skript.
