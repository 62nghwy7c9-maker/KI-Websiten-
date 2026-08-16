/* Aufgabenliste Webgewerk als Word-Datei. */
const B = require("./bauen.js");
const { SCHWARZ: S, ROT: R, BLAU: BL, p, h, titel, liste, tabelle, abstand,
        dokument, legende, Packer, fs, path } = B;

const inhalt = [];
const add = (...x) => inhalt.push(...x.flat());

// Eine Aufgabenzeile als Tabelle: Kästchen, Wer, Aufgabe.
function aufgaben(zeilen) {
  return tabelle(["", "Wer", "Aufgabe"],
    zeilen.map(([wer, text, grund, farbe]) => {
      const f = farbe || S;
      const aufgabe = grund
        ? [[text + " ", f, true], ["— " + grund, f]]
        : [[text, f]];
      return ["☐", [[wer, f, true]], aufgabe];
    }),
    [500, 900, 7600]);
}

add(titel("Webgewerk — Was zu tun ist"));
add(p([["Stand 17.08.2026 · alle offenen Punkte aus dem Unternehmenskonzept und dem Konzept-Check", S]]));
add(p([["Sortiert nach dem, was blockiert. Was oben steht, hält etwas anderes auf.", S]]));
add(abstand());
add(legende());
add(p([["K = Kira · Y = Yannik · K+Y = beide · C = Claude", S]]));
add(abstand());

add(h("Blockiert alles", 1, R));
add(p([["Die ladungsfähige Anschrift fehlt. Ohne sie trägt jeder Check einen roten Sperrbalken (§ 5 DDG) und darf nicht übergeben werden. Elf fertige Pakete warten nur darauf. Es ist eine Entscheidung, keine Recherche — und sie dauert fünf Minuten.", R]]));

add(h("1 · Diese Woche — Entscheidungen, keine Arbeit", 1));
add(p([["Alles hier sind Festlegungen, die nichts kosten außer einem Entschluss, und von denen anderes abhängt.", S]]));
add(aufgaben([
  ["K+Y", "Ladungsfähige Anschrift festlegen und in absender.json eintragen", "danach fallen die Sperrbalken auf allen elf Checks und auf der Firmenseite", R],
  ["K+Y", "Entscheiden, welche Telefonnummer gilt", "bisher zwei im Umlauf: 0152 01560005 und 0162 3242260. Auf einem gedruckten Blatt ist eine falsche Nummer der teuerste Fehler", R],
  ["K+Y", "Klären: Betreuung 69 € oder 59 € im Monat", "im Konzept stehen 69 €, am 17.08. fiel die Zahl 59. Bestätigen, bevor sie auf ein Angebot kommt", R],
  ["K", "Die zwei Selbstbeschreibungen schreiben, je ein bis zwei Sätze", "solange sie fehlen, steht auf der eigenen Seite Platzhaltertext — Prüfpunkt 15, an der eigenen Seite gerissen", R],
  ["K+Y", "Vier fertige Befunde freigeben: Sander-Bau, Lindam, Merzenich, Labau", "die Pipeline reproduziert alle vier, die Freigabe steht aus", S],
  ["K+Y", "Termin mit der Rechtsberatung in der Familie vereinbaren — mit festem Datum", "unentgeltliche Hilfe hat keine Rechnung und deshalb keinen Druck. Sie ist das Erste, was liegen bleibt", BL],
  ["K+Y", "Entscheiden, was der Kunde selbst bedienen kann — drei Wege stehen zur Wahl", "hängt technisch am Kontaktformular: beides braucht dieselbe Sorte Endpunkt. Zusammen entscheiden", BL],
]));
add(abstand());

add(h("2 · Vorlauf — rund sechs Wochen bis Tag 1", 1));
add(p([["Tag 1 ist der Tag, an dem der erste Check übergeben wird. Alles hier muss vorher stehen.", S]]));
add(aufgaben([
  ["K+Y", "Verfügbare Wochenstunden, feste Tage und Uhrzeiten schriftlich festhalten", "ohne diese Zahl ist die Wirtschaftlichkeit nicht rechenbar und der 90-Tage-Plan nicht planbar. Der wichtigste offene Punkt", R],
  ["K+Y", "Wovon wir im ersten Jahr leben — schriftlich, mit Betrag und Monaten", "das Neugeschäft bringt im ersten Jahr 21–44 € je Arbeitsstunde. Wer das nicht vorher weiß, hört nach dem dritten Kunden auf", R],
  ["K+Y", "Schriftlicher GbR-Gesellschaftsvertrag", "Gewinnverteilung, Geschäftsführung, Kündigung, Ausscheiden, Umgang mit laufenden Kundenverträgen", S],
  ["K+Y", "Gewerbeanmeldung je Gesellschafter beim Gewerbeamt der Wohnsitzgemeinde", "", S],
  ["Y", "Vermögensschaden-/IT-Haftpflicht: drei Angebote einholen, abschließen", "300–700 €/Jahr. Bei unbeschränkter Privathaftung nicht optional", S],
  ["Y", "Vertrag und AGB vorformulieren und prüfen lassen", "Abnahme mit Rügefrist und Eskalation, Mahnwesen, Rechte an übernommenen Texten, Herausgabe bei Ende", BL],
  ["Y", "§ 7 UWG und die DSGVO-Kette bis Anthropic an eine Fachstelle geben", "falls die Familienberatung dort nicht zu Hause ist — beides sind Spezialgebiete", BL],
  ["Y", "Domain sichern und geschäftliche E-Mail einrichten", "Stand 13.08.: webgewerk.de ist registriert und geparkt, webgewerk.com frei. Bei denic.de/webwhois nach dem Halter fragen", S],
  ["Y", "DPMA-Markenrecherche auf entgegenstehende Marken", "", S],
  ["K", "Formulardienst mit EU-Serverstandort und AV-Vertrag auswählen", "ohne ihn ist kein Projekt auslieferbar — der Kontaktweg ist Prüfpunkt 6 des eigenen Katalogs", R],
  ["K", "Verzeichnis von Verarbeitungstätigkeiten anlegen (Art. 30 DSGVO)", "", S],
  ["K", "Bauanleitung schreiben, damit die Produktion nicht an einer Person hängt", "derzeit kann nur Kira produzieren. Fällt sie aus, steht alles", BL],
  ["K+Y", "Betriebsliste mit Sperrlisten-Spalte und Wiedervorlage sowie Zeitprotokoll anlegen", "", BL],
  ["Y", "Art.-14-Datenschutzhinweis als Beilage zum Check formulieren", "", S],
  ["K+Y", "Von den Arbeitsproben schriftliche Zeigeerlaubnis einholen", "zwei Sätze per Mail. Ohne sie wird nichts gezeigt", BL],
  ["Y", "Wettbewerberpreise belegen: sieben Angebotsseiten, Preis und Abrufdatum, Screenshot", "rund eine Stunde. Danach steht fest, ob wirklich IONOS und STRATO der Hauptgegner sind", R],
  ["K+Y", "Eine belastbare Zahl zum Fachkräftemangel suchen", "nützlich fürs Gespräch, aber nicht mehr die Grundlage — der Betrieb rechnet selbst (Konzept 3.1)", BL],
  ["K", "Preis für einen halben Tag Fotoaufnahmen festlegen, Fotograf fragen", "Anhaltspunkt: vier bis fünf Stunden zu 70 €", BL],
  ["C", "Eigene Website fertigstellen", "Impressum und Datenschutz mit Anschrift, Selbstbeschreibungen einsetzen, Sperrbalken entfernen", S],
  ["C", "Entscheiden: lokale Ladezeitmessung oder Googles PageSpeed-API", "der Satz „Google bewertet über 4 Sekunden als schlecht“ trägt nur, wenn die Zahl auch von Google kommt", BL],
]));
add(abstand());

add(h("3 · Tag 1 bis 90 — der eigentliche Test", 1));
add(p([["Gemessen wird eins: Wie viele antworten? Die Antwortquote des Kanals ist bis heute ungetestet — Stichprobe eins.", S]]));
add(aufgaben([
  ["K+Y", "40 Checks übergeben, in Touren zu fünf Betrieben", "einzeln ausgefahren wäre die persönliche Übergabe mit dem Zeitziel unvereinbar. Gebündelt fällt die Fahrzeit je Check auf zwölf Minuten", BL],
  ["K+Y", "Ist-Zeit je Check mitschreiben, ab dem ersten", "der Weg von zwei Stunden auf 45 Minuten verdoppelt den effektiven Stundensatz", S],
  ["K+Y", "Drei Pilotkunden gewinnen, versetzt starten mit rund zwei Wochen Abstand", "damit die Auswertung von Projekt 1 vor dem Baubeginn von Projekt 2 steht", BL],
  ["K", "Ist-Zeit je Projekt nach Arbeitsschritt erfassen", "Projekt 1 auswerten, bevor Projekt 2 beginnt", BL],
  ["K+Y", "Wöchentlicher Termin, 60–90 Minuten, Kennzahlen eintragen", "fester Punkt: Stimmt der Katalog im Code noch mit Anhang A überein?", BL],
  ["K", "Nach Projekt 3: Produktionsvorlage ableiten und entscheiden, ob Paket S bleibt", "beworben wird „ab 990 €“, verkauft werden soll M. Entweder S streichen oder zuschneiden", R],
  ["C", "Prüfpunkte 1–5 und 11–13 automatisieren", "", S],
]));
add(abstand());

add(h("4 · Pipeline — bekannte Lücken", 1));
add(aufgaben([
  ["C", "Feld „gruende“ in die Pipeline: ein bis drei individuelle Gründe je Betrieb, jeder mit Beleg", "erscheint im Dossier und im Anschreiben, nie auf dem gedruckten Check", BL],
  ["C", "Auswahlregel zweistufig umsetzen", "erst filtern, was das Paket behebt, dann nach Schweregrad sortieren", BL],
  ["C", "Platzhalter auf Unterseiten werden nicht gefunden", "die Handfunde „mehr als ?? Jahren“ (Apeler) und „(Bild in Beratungssituation)“ (Maler Manufaktur) fehlen deshalb", R],
  ["K", "Screenshots einmal auf einem Rechner ohne Netzsperre prüfen", "im Container entstehen sie nur bei HTTP-Seiten, also 2 von 11", R],
  ["K", "Overpass-Live-Abruf testen", "die Container-IP ist gesperrt. Der Weg über overpass-turbo.eu funktioniert und ist geprüft", S],
  ["C", "Google für Jobs als Prüfpunkt aufnehmen", "", S],
  ["C", "Kostensatz für Prüfpunkt 7 belegen: § 33 DDG nennt einen Bußgeldrahmen bis 50.000 €", "Quelle liegt vor, aber die Zahl geht auf ein Blatt, das ein Meister in die Hand bekommt — vorher ein zweites Mal prüfen", R],
]));
add(abstand());

add(h("5 · Später, aber nicht vergessen", 1));
add(aufgaben([
  ["K+Y", "Google-Unternehmensprofil für Webgewerk anlegen", "Prüfpunkt 14 verlangt von Kunden, dass Profil und Website übereinstimmen. Wir haben keins", R],
  ["K+Y", "Einwandbehandlung ausarbeiten", "die drei Einwände stehen als Entwurf im Konzept 4.4 — verfeinern statt neu anfangen", BL],
  ["K+Y", "Zweiter Kanal: Betriebe ohne Website ansprechen", "erst nach den ersten 20 Checks, damit sich die Kanäle nicht vermischen", BL],
  ["K", "Barrierefreiheit: Betroffenheit nach dem BFSG klären", "", R],
  ["Y", "E-Rechnungs-Empfang und revisionssichere Ablage einrichten", "", S],
  ["Y", "Separates Konto für die Steuerrücklage — 30 % jeder Einnahme", "", S],
  ["K+Y", "DRV-Statusklärung § 7a SGB IV und Befreiungsantrag § 6 Abs. 1a SGB VI", "", S],
  ["Y", "Steuerberatung: § 19 UStG beibehalten oder verzichten", "", S],
  ["K", "AVV-Vorlage für Betreuungskunden erstellen (Art. 28 DSGVO)", "", S],
  ["C", "Die drei überholten Konzeptfassungen löschen oder als überholt kennzeichnen", "vier Dokumente im Umlauf waren der Grund für drei verschiedene Prüfkataloge", BL],
]));
add(abstand());

add(h("Erledigt", 1));
add(liste([
  "17.08. — Konzept überarbeitet: Webgewerk, Preisliste, 19 Prüfpunkte, Hosting beim Kunden",
  "17.08. — Abnahme mit Rügefrist und Eskalation geregelt",
  "17.08. — Verfahren für den Domainumzug samt MX-Sicherung ausgearbeitet",
  "17.08. — Sperrliste, Anlassfilter, Löschfristen, Gründe je Betrieb aufgenommen",
  "17.08. — Kein zweiter Anruf; Wiedervorlage nur mit neuem Messergebnis",
  "17.08. — Betriebe ohne Website: eigener kurzer Einstieg statt Ausschluss",
  "17.08. — Fotos und Texte als Zusatzleistung, Fotograf ohne Provision",
  "17.08. — Kapitalbedarf vollständig beziffert: 995–1.764 €",
  "16.08. — Konzept-Check: 43 Befunde in zwei Durchgängen",
  "15.08. — Impressum und Datenschutz als eigene Seiten, Stil geteilt",
  "15.08. — Prüfkatalog über die eigene Seite gelaufen",
  "14.08. — Fehlendes viewport-Meta gefunden und behoben",
  "13.08. — Firmenname entschieden: Webgewerk",
  "12.08. — Pipeline reproduziert alle vier von Hand erstellten Befunde",
  "12.08. — Elf Pakete erzeugt, je fünf Dateien",
]));

const doc = dokument(inhalt);
Packer.toBuffer(doc).then((buf) => {
  const ziel = path.join(__dirname, "Webgewerk-Aufgabenliste.docx");
  fs.writeFileSync(ziel, buf);
  console.log(ziel, Math.round(buf.length / 1024) + " KB");
});
