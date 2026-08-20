# Offene Punkte

**Stand:** 15. August 2026
**Gilt für:** K&D Webdesign — Check-Pipeline und eigene Firmenseite

Sortiert nach dem, was blockiert. Was oben steht, hält etwas anderes auf.
Erledigtes wird nicht gelöscht, sondern abgehakt und datiert — damit
nachvollziehbar bleibt, was wann entschieden wurde.

Zuständigkeit: **K** = Kira, **Y** = Yannik, **C** = Claude.

---

## 1 · Blockiert den ersten Kundenkontakt

| | Punkt | Wer | Warum es blockiert |
|---|---|---|---|
| ☐ | **Ladungsfähige Anschrift** in `absender.json` eintragen | K/Y | § 5 DDG verlangt sie auf jedem geschäftlichen Dokument. Bis dahin trägt **jeder** der elf Checks oben einen roten Sperrbalken und darf nicht übergeben werden. Das ist der einzige echte Blocker. |
| ☐ | Entscheiden, **welche Telefonnummer** gilt | K/Y | Bisher gab es zwei Angaben: +49 152 01560005 und +49 162 3242260. Eingetragen ist die zweite mit Yanniks Namen. Auf einem gedruckten Blatt ist eine falsche Nummer der teuerste Fehler. |
| ☐ | Die vier fertigen Befunde **freigeben** | K | Sander-Bau, Lindam, Merzenich, Labau. Die Pipeline reproduziert alle vier, aber die Freigabe steht aus. |

---

## 2 · Eigene Firmenseite

Quelle: `studie/seite/` (drei Seiten, ein gemeinsames `stil.css`).
Vorschau: `claude.ai/code/artifact/769987cb-b408-4317-a577-cd3a047ccbaf`
— erzeugt mit `python3 studie/bauen.py`, **nicht von Hand bearbeiten**.

| | Punkt | Wer |
|---|---|---|
| ☐ | **Anschrift** in Impressum und Datenschutz eintragen — die Seiten stehen, nur die Angabe fehlt | K/Y |
| ☐ | **Zwei Selbstbeschreibungen** schreiben, je ein bis zwei Sätze. Solange sie fehlen, steht dort Platzhaltertext — Prüfpunkt 15, an der eigenen Seite | K und Y |
| ☐ | **Kein Google-Unternehmensprofil.** Prüfpunkt 14 verlangt von Kunden, dass Profil und Website übereinstimmen. Wir haben keins | K/Y |
| ☐ | **Domain** klären, dann Seite online stellen | K/Y |
| ☐ | **Hosting** wählen — mit PHP, falls ein Formular kommen soll | K/Y |
| ☐ | **Hostinganbieter in die Datenschutzerklärung** eintragen: Name, Speicherdauer der Protokolle, Vertrag zur Auftragsverarbeitung | C, nach Wahl von K/Y |
| ☐ | Entscheiden: **Kontaktformular** ja oder nein — und wenn ja, über welchen Weg | K |
| ☐ | **Anwaltlich prüfen lassen**, sobald die Rechtsform steht. Beide Rechtsseiten sind nach dem Gesetzeswortlaut gegliedert, aber nicht geprüft | K/Y |
| ☐ | Prüfen, wie die **Systemschrift** auf einem Windows-Rechner aussieht. Es werden keine Schriften mehr geladen; Windows zeigt Segoe UI, Mac zeigt SF | K |
| ☐ | Beim Umzug aufs eigene Hosting `lang="de"` ins `<html>`-Element schreiben. Solange die Seiten keinen eigenen `<html>`-Rahmen haben, setzt ein Skript es nach — das ist ein Notbehelf | C |
| ☑ | **Impressum und Datenschutz als eigene Seiten** angelegt (15.08.) — die Lücken sind sichtbar markiert, nicht erfunden | C |
| ☑ | **Stil in eine gemeinsame Datei** gezogen (15.08.) — `studie/seite/stil.css` | C |
| ☑ | **Prüfkatalog über die eigene Seite gelaufen** (15.08.) — Ergebnis unten | C |

### Ergebnis der Selbstprüfung vom 15.08.2026

Gemessen an der Startseite, Bildschirmbreite 390 px.

| Nr | Punkt | Ergebnis |
|---|---|---|
| 1 | Erreichbarkeit | nicht prüfbar — keine Domain, kein Hosting |
| 2 | HTTPS | nicht prüfbar — kein Hosting |
| 3 | Mobiltauglichkeit | **bestanden** — `viewport` gesetzt, 0 px waagerechtes Scrollen |
| 4 | Ladezeit mobil | Anzeichen gut (35 KB, nichts wird nachgeladen), aber **echte Messung steht aus** — lokal gemessene 96 ms sind kein Beleg |
| 5 | Klickbare Telefonnummer | **bestanden** — zwei `tel:`-Verweise |
| 6 | Kontaktweg | **bestanden** — Telefon und Mail auf der Startseite, ein Klick |
| 7 | Impressum | ~~gerissen~~ → **behoben am 15.08.**, Seite angelegt |
| 8 | Aktualität | **bestanden** — Jahreszahl wird gesetzt, nicht getippt |
| 9 | Karriereseite | nicht anwendbar — wir suchen niemanden |
| 10 | Formular | **gerissen** — kein `<form>`, bekannter Widerspruch (siehe unten) |
| 11 | Seitentitel | **bestanden** |
| 12 | Meta-Description | **bestanden** — 128 Zeichen, im Fenster 50–160 |
| 13 | Eigene Domain | **gerissen** — es gibt keine |
| 14 | Google-Unternehmensprofil | **gerissen** — existiert nicht |
| 15 | Platzhaltertext | **gerissen** — zwei Stellen „Noch offen" |

Fünf Befunde am 15.08., einer davon noch am selben Tag behoben. Der
Schwellwert `QUALIFIKATION_AB_BEFUNDEN` steht bei drei — nach unserem
eigenen Maßstab wären wir also ein Kandidat, bei dem sich ein Anschreiben
lohnt. Zwei der verbleibenden vier lösen sich mit Domain und Hosting von
selbst auf; Google-Profil und Platzhaltertext nicht.

### Der Widerspruch beim Formular

Der eigene Prüfkatalog verlangt ein *funktionierendes* Kontaktformular, nicht
nur eine mailto-Adresse. Die Technikvorgabe verbietet gleichzeitig Fremddienste
und Datenbanken. Beides zusammen geht nur mit einem eigenen kleinen Skript auf
dem eigenen Hosting.

**Solange kein Formular da ist, besteht die eigene Seite den eigenen Katalog
nicht** — an genau dem Punkt, den sie bei Kunden bemängelt.

---

## 3 · Domain

| | Punkt | Wer |
|---|---|---|
| ☐ | Bei **denic.de/webwhois** nachsehen, wem `kd-webdesign.de` gehört, und nach dem Preis fragen | K/Y |
| ☐ | Falls das nichts wird: `webgewerk-kerpen.de` auf Verfügbarkeit prüfen | K/Y |
| ☐ | `kd-webdesign.com` als Reserve sichern (rund 12 €/Jahr), **nicht** als Hauptadresse | K/Y |

**Belegter Stand vom 13.08.2026:**

- `kd-webdesign.de` — **registriert**. Sie löst auf und liefert eine leere Seite
  mit `offline@i-mem.net` aus. Geparkt, kein Wettbewerber.
- `kd-webdesign.com`, `web-gewerk.com`, `web-gewerk.net`, `webgewerk.org`,
  `web-gewerk.org` — **nicht registriert** (Registerabfrage mit bestandener
  Kontrolle).
- `.de`, `.koeln`, `.nrw`, `.eu` — **nicht prüfbar**. Für diese Endungen gibt
  es keine öffentliche Registerabfrage; fehlender DNS-Eintrag ist kein Nachweis.

Begründung gegen `.com` und gegen den Bindestrich: Ein Meister im
Rhein-Erft-Kreis erwartet `.de`, und ein Bindestrich muss am Telefon
buchstabiert werden.

---

## 4 · Pipeline — bekannte Lücken

| | Punkt | Wer |
|---|---|---|
| ☐ | **Screenshots** entstehen im Container nur bei HTTP-Seiten (2 von 11). Auf einem Rechner ohne diese Sperre bei allen — muss einmal echt geprüft werden | K |
| ☐ | **Platzhalter auf Unterseiten** werden nicht gefunden. Die Handfunde „mehr als ?? Jahren" (Apeler) und „(Bild in Beratungssituation)" (Maler Manufaktur) fehlen deshalb | C |
| ☐ | **Overpass-Live-Abruf** ist ungetestet — die Container-IP ist gesperrt. Der Weg über overpass-turbo.eu funktioniert und ist geprüft | K |
| ☐ | **Kosten-Sätze ohne Beleg**: Meta-Description, eigene Domain, Speisekarte als Bild. Sie erscheinen im Check nur als Beobachtung. Quelle suchen oder so belassen | C |
| ☐ | **Kandidat für Prüfpunkt 7 gefunden, noch nicht eingebaut:** § 33 Abs. 2 Nr. 1 DDG macht ein unvollständiges Impressum zur Ordnungswidrigkeit, § 33 Abs. 6 Nr. 3 nennt einen Bußgeldrahmen bis 50.000 €. Quelle: gesetze-im-internet.de/ddg. **Vor dem Einbau ein zweites Mal unabhängig prüfen** — die Zahl ginge auf ein Blatt, das ein Meister in die Hand bekommt | C |
| ☐ | **Google für Jobs als Prüfpunkt** aufnehmen — dann steht im Dossier, ob die Stellen eines Betriebs dort auffindbar sind | C |
| ☐ | Konzept nachziehen: **eigene Unterseite je Stelle** (Google verlangt das, im Konzept steht es noch anders) | C |

---

## 5 · Konzept und Regelwerk

| | Punkt | Wer |
|---|---|---|
| ☐ | **Preisleiter streichen.** Der Preis steht mit 1.800 € fest und öffentlich auf der Website. Damit lässt sich nicht mehr messen, wo die Ablehnung einsetzt. Abschnitt 4 des Konzepts sagt noch etwas anderes | C |
| ☐ | **Leistungsumfang festschreiben:** vier Adressen — Startseite, `/jobs`, Impressum, Datenschutz | C |
| ☐ | **Was an der Google-für-Jobs-Aussage falsch war** — Kira hat widersprochen, aber nicht gesagt, welcher Teil. Steht so im Konzept | K |

---

## 6 · Rechtlich — vor dem Skalieren

Vollständig in KONZEPT-WEBDESIGN.md, Abschnitt 10. Die drei, die zuerst
anstehen:

| | Punkt | An wen |
|---|---|---|
| ☐ | **§ 7 Abs. 2 Nr. 2 UWG** — kalte Werbemails brauchen auch im B2B eine Einwilligung. Betrifft den Versand unmittelbar; Briefe sind nicht erfasst | Fachanwalt Wettbewerbsrecht |
| ☐ | **GbR** — zwei gemeinsam auftretende Personen bilden ohne weiteres Zutun eine GbR mit gesamtschuldnerischer Haftung | Steuerberatung / IHK |
| ☐ | **Gewerbeanmeldung**, Webdesign ist gewerblich und nicht freiberuflich | Gewerbeamt, Steuerberatung |

---

## 7 · Ungetestete Annahme, an der alles hängt

**Ob der Check überhaupt Gespräche erzeugt, ist unbekannt.** Stichprobe bisher:
eins. Damit ist die Antwortquote des Kanals ungetestet.

*(Übernommen aus PLAN-90-TAGE.md, Abschnitt „Offener Punkt". Der Plan
unterstellt, dass Gophai der einzige verschickte Check war.)*

**Der Test:** Elf Pakete liegen fertig. Sobald die Anschrift steht, ausdrucken
und hinfahren. Criedlig liegt zentral in Kerpen und ist der kürzeste Weg zum
Üben; Czarnetzki hat mit zehn Befunden den stärksten Fall.

Gemessen wird nur eins: **Wie viele antworten?**

Der A/B-Test läuft dabei mit — sechs der elf Checks tragen den Abschnitt „Was
schon gut ist", fünf nicht. Nach den ersten Rückmeldungen ist damit beantwortet,
ob Anerkennung hilft oder Druck wegnimmt.

---

## Erledigt

| Datum | Punkt |
|---|---|
| 15.08.2026 | Impressum und Datenschutz als eigene Seiten, Stil in `stil.css` geteilt, Sperrbalken nach dem Muster des Kundenchecks |
| 15.08.2026 | Selbstprüfung gelaufen — fünf Befunde, zwei davon vorher unbekannt |
| 15.08.2026 | Firmenseite auf das Gerüst aus `durchgeplant-` umgestellt: Plan-Set-Motiv, Systemschriften, Dunkelmodus, Sicherheitsnetz ohne JavaScript |
| 15.08.2026 | **Three.js und Kristall entfernt.** An ihrer Stelle steht der Prüfvorgang selbst. 674 KB → 32 KB |
| 15.08.2026 | Entschieden: K&D Webdesign und durchgeplant sind verwandt, aber unterscheidbar — gleiches Motiv, eigene Farben |
| 14.08.2026 | Vorspann der Firmenseite neu gebaut: dunkle Bühne, Kristall in Ocker statt Schiefergrau, Satz und Objekt nebeneinander statt übereinander |
| 14.08.2026 | **Fehlendes `viewport`-Meta gefunden und behoben.** Die eigene Seite wäre auf dem Handy in Desktop-Breite geladen — Prüfpunkt 3 aus dem eigenen Katalog, an der eigenen Seite gerissen |
| 13.08.2026 | Firmenname entschieden: **K&D Webdesign**, Zusatz „Ihr Gewerk im Fokus" |
| 13.08.2026 | Regelwerk auf den Check angewandt — Farben, verbotene Wörter entfernt, Kontaktnamen ergänzt |
| 13.08.2026 | Entwurf der eigenen Firmenseite steht |
| 12.08.2026 | Pipeline reproduziert alle vier von Hand erstellten Befunde |
| 12.08.2026 | Elf Pakete erzeugt, je fünf Dateien |
| 12.08.2026 | Stufe 4 (Anschreiben) nachgeliefert — war als M4 geplant, aber nie gebaut |
