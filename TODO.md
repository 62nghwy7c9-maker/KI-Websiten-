# Offene Punkte

**Stand:** 13. August 2026
**Gilt für:** Webgewerk — Check-Pipeline und eigene Firmenseite

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

Entwurf: `studie/firmenseite.html` · Vorschau unter
`claude.ai/code/artifact/769987cb-b408-4317-a577-cd3a047ccbaf`

| | Punkt | Wer |
|---|---|---|
| ☐ | **Zwei Selbstbeschreibungen** schreiben, je ein bis zwei Sätze | K und Y |
| ☐ | **Impressum** und **Datenschutzerklärung** inhaltlich liefern | K |
| ☐ | Prüfen, wie **Franklin Gothic** auf einem Windows-Rechner aussieht | K |
| ☐ | Entscheiden: **Kontaktformular** ja oder nein — und wenn ja, über welchen Weg | K |
| ☐ | **Prüfkatalog Punkt für Punkt** über die eigene Seite laufen lassen (Schritt 5 aus dem Ablauf) | C |
| ☐ | **Domain** klären, dann Seite online stellen | K/Y |
| ☐ | **Hosting** wählen — mit PHP, falls ein Formular kommen soll | K/Y |

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
| ☐ | Bei **denic.de/webwhois** nachsehen, wem `webgewerk.de` gehört, und nach dem Preis fragen | K/Y |
| ☐ | Falls das nichts wird: `webgewerk-kerpen.de` auf Verfügbarkeit prüfen | K/Y |
| ☐ | `webgewerk.com` als Reserve sichern (rund 12 €/Jahr), **nicht** als Hauptadresse | K/Y |

**Belegter Stand vom 13.08.2026:**

- `webgewerk.de` — **registriert**. Sie löst auf und liefert eine leere Seite
  mit `offline@i-mem.net` aus. Geparkt, kein Wettbewerber.
- `webgewerk.com`, `web-gewerk.com`, `web-gewerk.net`, `webgewerk.org`,
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
| 13.08.2026 | Firmenname entschieden: **Webgewerk**, Zusatz „Ihr Gewerk im Fokus" |
| 13.08.2026 | Regelwerk auf den Check angewandt — Farben, verbotene Wörter entfernt, Kontaktnamen ergänzt |
| 13.08.2026 | Entwurf der eigenen Firmenseite steht |
| 12.08.2026 | Pipeline reproduziert alle vier von Hand erstellten Befunde |
| 12.08.2026 | Elf Pakete erzeugt, je fünf Dateien |
| 12.08.2026 | Stufe 4 (Anschreiben) nachgeliefert — war als M4 geplant, aber nie gebaut |
