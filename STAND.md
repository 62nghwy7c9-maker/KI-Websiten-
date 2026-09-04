# Webgewerk: Stand und Gedächtnis

**Stand:** 4. September 2026
**Zweck:** Alles, was eine neue Sitzung wissen muss, um sofort weiterzuarbeiten.
Wer hier durch ist, kennt das Projekt, die Regeln und die Fallen.

---

## 1 · Wer und was

**Webgewerk** — Kira Moewes und Yannik Dettmer bauen Websites für kleine
Betriebe im Rhein-Erft-Kreis. Kira ist ausdrücklich nicht technisch: Sie
braucht Anweisungen, die sie allein ausführen kann, keine Erklärungen zum
Innenleben.

- Repo: `62nghwy7c9-maker/ki-websiten-`
- Branch: `claude/sparring-ki-websites-dach-xdb9xc`
- Kontakt: `webgewerk@gmx.de`, Telefon 0152 01560005 (Yannik)
- Anschrift: Bachstraße 109, 50171 Kerpen

**Das Modell in einem Satz:** Aus der Website eines Betriebs wird automatisch
ein nachprüfbarer Mängel-Check. Der Check ist der Türöffner, die neue Website
das Produkt.

---

## 2 · Der Ablauf

Ein Befehl beantwortet jederzeit, was dran ist:

```
python -m pipeline kunde stand
```

Er nennt für jeden Betrieb die Stufe, das Nächste und den fertigen Befehl.
Steht das Nächste bei einem Menschen, steht das auch da. **Jede Sitzung damit
anfangen.**

### Phase A — bis zum Anschreiben (automatisiert)

```
python -m pipeline finden --ort Kerpen --branche handwerk
python -m pipeline stapel --liste leads/<datei>.md
python -m pipeline pakete --slug <slug>
```

Ergebnis je Betrieb: `kunden/<slug>/messung.json`, ein druckfertiger Check,
ein Dossier, ein Anschreiben-Entwurf.

### Phase C — nach der Zusage (seit 3.9. automatisiert)

```
python -m pipeline kunde anlegen --slug <slug> --kurzname <name>
python -m pipeline kunde erhebung <name>     # Fragebogen für den Termin
python -m pipeline kunde bauen <name>        # webroot + vier Papiere
python -m pipeline kunde pruefen <name>      # 20 Invarianten
python -m pipeline kunde packen <name>       # zwei ZIPs, neues Passwort
```

Danach: Testgerät, Freigabeblatt, sein Hosting, Vorschau, Domain, Übergabe.
Vollständig im Skill `.claude/skills/kundenweg/SKILL.md`.

### Die Trennung, an der alles hängt

| Datei | Inhalt | Herkunft |
|---|---|---|
| `stammdaten.json` | Fakten | **der Betrieb selbst** |
| `texte.md` | Sätze | wir |
| `studie/pflege/vorlage/` | alles Mechanische | für jeden Kunden gleich |

In `stammdaten.json` gibt es zwei Blöcke: `vermutet` (aus der Messung seiner
alten Seite, ungeprüft, nur zum Vorbefüllen des Fragebogens) und `bestaetigt`
(hat er selbst gesagt). **Auf die Seite kommt nur `bestaetigt`.**

Fehlt eine Pflichtangabe, bricht der Bau ab und nennt sie. Es gibt keinen
Platzhalter, der versehentlich live gehen kann.

Für Angaben, die es beim Betrieb wirklich nicht gibt, steht `entfaellt`. Leer
heißt „noch nicht gefragt". Ein Impressum ohne Umsatzsteuer-ID kann richtig
sein; ein Impressum, bei dem niemand gefragt hat, nie.

---

## 3 · Was fertig ist

- **Pipeline Phase A:** 11 Betriebe gemessen, 11 Checks und Dossiers erzeugt.
- **Pipeline Phase C:** neu, 61 Tests grün.
- **Czarnetzki** (Peter Czarnetzki Elektroinstallationen, Bergheim,
  `pcelektro.de`): der erste vollständige Entwurf. Stufe *gepackt, wartet auf
  Freigabe*. 20 von 20 Prüfungen bestanden. Beide Pakete geschnürt.
- **Pflegebereich:** Der Betrieb ändert Texte, Bilder und Nummern selbst.
  Kein CMS, keine Datenbank, kein Framework. Marker im HTML:
  `<!--wg:telefon-->02271 45550<!--/wg-->`. Eine Änderung schlägt auf alle
  Seiten durch.
- **Selbsttest:** `pflege/selbsttest.php?s=<schlüssel>` — der Server prüft
  sich selbst, 19 Prüfungen, stellt jede Änderung zurück. Entstanden, weil
  ich den Kundenserver nicht erreichen kann.
- **Eigene Website:** Entwurf steht in `studie/eigene-website/`, nicht online.

---

## 4 · Harte Regeln

Diese gelten immer, ohne Nachfrage:

1. **Nichts erfinden.** Keine Zahl, keine Frist, keine Quelle, kein Schwellwert,
   keine Zusage über Dritte, die nicht geprüft ist.
2. **Entwürfe werden nie versendet.** Die Pipeline erzeugt Briefe, ein Mensch
   verschickt sie. Kalte Werbemails an Betriebe brauchen nach § 7 Abs. 2 Nr. 2
   UWG eine Einwilligung, auch im B2B. Postalische Werbung nicht.
3. **Keine Zugangsdaten in Dateien oder ins Repo.** Passwörter nur als Hash
   auf dem Server. Das Klartext-Passwort erscheint einmal beim Packen und
   wird mündlich übergeben.
4. **Keine Stockfotos von Menschen, die nicht wir sind.** Fotos kommen vom
   Betrieb.
5. **Das Logo des Kunden verwenden wir nicht.**
6. **Keine Gedankenstriche** in Texten, Kommentaren und Code.
7. **Nichts Kundenspezifisches in `studie/pflege/`.** Das ist die Vorlage.
8. **Nichts von Hand im `webroot/`.** Der nächste Bau macht es weg, und der
   Prüfstand merkt es.
9. **Kurz antworten.** Kein unnötiger Text, wenn nicht danach gefragt wurde.

---

## 5 · Fehler, die schon passiert sind

Jede Regel und jede Prüfung steht wegen eines dieser Fälle. Keiner fiel beim
Lesen des Codes auf; alle fielen auf, als jemand nachgesehen hat.

- Eine Testanfrage ging an die echte Adresse des Kunden.
- Ein eingebautes Notfallpasswort ließ jeden in den Pflegebereich, wenn
  `passwort.php` fehlte.
- Die Datenschutzerklärung sagte „nicht gespeichert", während gespeichert
  wurde. Ich hatte das selbst eingebaut, als ich das Anfragen-Protokoll
  ergänzte.
- Anfragen lagen auf dem Server, und niemand konnte sie lesen: ein Briefkasten
  ohne Schlüssel.
- Der Eingangszeitpunkt war sechs Stunden falsch, weil der Server im Ausland
  stand.
- Das Auslieferpasswort stand im Klartext in drei ausgedruckten Papieren.
- `absender.json` nannte `hallo@webgewerk.com`. Die Domain gibt es nicht;
  jedes Anschreiben hätte eine tote Rückadresse getragen.

---

## 6 · Technische Eigenheiten, die man teuer lernt

- **`php -S` lügt bei Sperrtests.** Der eingebaute Server beantwortet den
  Aufruf einer *nicht vorhandenen* Datei mit `index.php` und liefert 200. Eine
  Datei, die gar nicht existiert, sieht damit aus wie eine offene Datei. Immer
  mit wirklich vorhandener Datei prüfen.
- **`PHP_CLI_SERVER_WORKERS=10`** setzen, sonst ist `php -S` einkernig und
  jeder Gleichzeitigkeitstest läuft in eine Zeitüberschreitung.
- **Selbstschutz statt `.htaccess`:** Datendateien heißen `.php` und beginnen
  mit `<?php http_response_code(404); exit; ?>`. Damit schützen sie sich auch
  dort, wo `.htaccess` ignoriert wird (nginx).
- **Sperren beim Schreiben** liegt auf einer eigenen `anfragen.lock`, nicht
  auf `anfragen.php`. Beim Umbenennen wird die Datei ersetzt, und ein
  wartender Schreiber schriebe ins Leere.
- **InfinityFree blockiert Rechenzentrums-IPs.** Ich komme nicht auf Kiras
  Testseite: WebFetch 403, Proxy 503, echter Chromium `ERR_CONNECTION_RESET`.
  **Cowork kommt durch.** Deshalb der Umweg über Cowork, und deshalb der
  Selbsttest, der den Server sich selbst prüfen lässt.
- **InfinityFree verschickt keine Mails.** Das Kontaktformular ist dort nie
  vollständig prüfbar.
- **Verwechslungsgefahr:** `studie/czarnetzki/` ist der Kunde,
  `kunden/bergheim_peter-czarnetzki-...` ist seine Messung. Zwei Ordner,
  ein Betrieb.

---

## 7 · Offene Punkte

**Blockiert den ersten Abschluss**

1. Die Vorführseite läuft nicht. Zuletzt kam ein 404 von InfinityFree.
   Datei: `studie/czarnetzki/czarnetzki-TEST.zip`, Passwort `sDj5uvDELGMCJp`,
   Selbsttest-Schlüssel `aee7f97f2c0d4902`.
2. Herr Czarnetzki hat nicht zugesagt. `FREIGABEBLATT.md` ausgedruckt
   mitnehmen.
3. Vier fertige Befunde sind nicht freigegeben: Sander-Bau, Lindam,
   Merzenich, Labau.

**Ungeklärt, braucht einen Menschen**

- Gewerbeanmeldung und Rechtsform. Im Impressum steht „Webgewerk GbR".
  Frage an IHK Köln oder Steuerberatung, keine Rechtsberatung von uns.
- `webgewerk.com` ist nicht registriert.
- Hoster: InfinityFree reicht zum Herzeigen, nicht zum Testen. Offene
  Entscheidung, ob ein bezahltes Testgerät angeschafft wird.
- Beide Rechtsseiten sind nach dem Gesetzeswortlaut gegliedert, aber
  anwaltlich nicht geprüft.
- Vier Adressen in Kerpen, die Kiras Vater kennt, sollen besucht werden.

**Bekannte Lücken in der Pipeline**

- Prüfpunkt 23 hat keinen Text. Prüfpunkte 12, 13 und 20 haben ein leeres
  `beleg`-Feld.
- Die eigene Website besteht den eigenen Prüfkatalog nicht: kein Formular,
  keine Domain, kein Google-Profil, zwei Platzhalter.

---

## 8 · Wo was liegt

```
CLAUDE.md                     Auftrag, Architektur, Prüfkatalog
STAND.md                      diese Datei
TODO.md                       offene Punkte, abgehakt und datiert
absender.json                 unsere eigenen Angaben
.claude/skills/kundenweg/     der ganze Kundenweg als Skill

pipeline/
  finden, messung, befunde    Phase A
  check, dossier, anschreiben Phase A
  stammdaten, texte, vorlagen Phase C: Daten und Format
  seite, papiere, drucken     Phase C: bauen
  pruefstand                  Phase C: 20 Invarianten
  kunde                       Phase C: Zustand ablesen
  ausliefern                  Phase C: Pakete schnüren

studie/pflege/                die Vorlage für jeden Kunden
  vorlage/seite/              HTML-Gerüst und stil.css
  vorlage/papiere/            die vier Kundendokumente
  inhalt.php, index.php       der Pflegebereich
  selbsttest.php              das Prüfwerkzeug

studie/czarnetzki/            der erste Kunde
kunden/, checks/, out/        Messungen und Checks der elf Betriebe
```

---

## 9 · So startet eine neue Sitzung

1. `python -m pipeline kunde stand`
2. Diese Datei und `CLAUDE.md` lesen.
3. Bei allem, was mit einem Kunden zu tun hat: der Skill `kundenweg` greift
   automatisch.

Kira fragen, bevor etwas Unumkehrbares passiert: Domain umstellen, an einen
Kunden schicken, Dateien beim Kunden löschen.
