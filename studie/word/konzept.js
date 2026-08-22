/* Unternehmenskonzept Webgewerk als Word-Datei. */
const B = require("./bauen.js");
const { SCHWARZ: S, ROT: R, BLAU: BL, p, h, titel, liste, tabelle, abstand,
        dokument, legende, Packer, fs, path } = B;

const inhalt = [];
const add = (...x) => inhalt.push(...x.flat());

/* ---- Kopf ---------------------------------------------------------- */
add(titel("Webgewerk — Unternehmenskonzept"));
add(p([["Fassung 17.08.2026 · Kira Moewes und Yannik Dettmer · Kerpen, Rhein-Erft-Kreis", S]]));
add(p([["Diese Fassung ersetzt alle vorherigen — insbesondere die Fassung vom 16.08.2026, die Datei Webgewerb_Konzept.docx und KONZEPT-WEBDESIGN.md. Wer eine ältere Fassung findet, arbeitet mit der falschen.", BL]]));
add(abstand());
add(legende());

/* ---- Ubersicht der offenen Punkte ----------------------------------
 * Wird aus studie/aufgaben.json erzeugt, nicht von Hand gepflegt. Sonst
 * stehen in Konzept und Aufgabenliste zwei verschiedene Listen offener
 * Punkte — und genau das ist am 19.08. aufgefallen: fuenf Punkte aus dem
 * Konzept hatten es nie in eine Aufgabenliste geschafft.
 */
const aufgaben = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "aufgaben.json"), "utf8"));

function sortierschluessel(wo) {
  if (wo.startsWith("Anhang")) return [99, 0];
  const teile = wo.split(" ")[0].split(".").map(Number);
  return [teile[0] || 0, teile[1] || 0];
}

const offene = [];
for (const block of aufgaben.bloecke) {
  for (const z of block.zeilen) {
    if (z.length < 6) continue;
    const [wer, frist, was, , farbe, wo] = z;
    offene.push({ wo, was, wer, frist, farbe: farbe === "BL" ? BL : R });
  }
}
offene.sort((a, b) => {
  const [x1, y1] = sortierschluessel(a.wo), [x2, y2] = sortierschluessel(b.wo);
  return x1 - x2 || y1 - y2;
});

add(h("Was in diesem Dokument noch offen ist", 1, R));
add(p([["Alle rot gesetzten Stellen auf einen Blick, damit man sie nicht suchen muss. Die Nummer ist der Abschnitt, in dem sie steht; die Frist ist dieselbe wie in der Aufgabenliste. Beide Dokumente lesen dieselbe Datei — sie koennen nicht auseinanderlaufen.", R]]));
add(tabelle(
  ["Wo", "Was offen ist", "Wer", "Bis wann"],
  offene.map((o) => [
    [[o.wo, o.farbe, o.wo.startsWith("Anhang")]],
    [[o.was, o.farbe, o.wo.startsWith("Anhang")]],
    [[o.wer, o.farbe]],
    [[o.frist, o.farbe]],
  ]),
  [900, 5300, 900, 1900]));
add(abstand());

add(p([["Zwei Punkte stehen bewusst nicht in der Aufgabenliste, weil sie keine Aufgaben sind, sondern Bewertungen dieses Konzepts — sie werden nicht abgehakt, sondern widerlegt oder bestaetigt:", R]]));
add(tabelle(["Wo", "Was zu bezweifeln ist", "Wer"],
  aufgaben.konzept_bewertungen.map(([wo, was, wer]) =>
    [[[wo, R]], [[was, R]], [[wer, R]]]),
  [900, 6400, 1700]));
add(abstand());
add(p([["Blau gesetzt ist alles, was in den Gespraechen vom 16. bis 19.08.2026 neu hinzugekommen ist — das ist rund ein Drittel dieses Dokuments und steht nicht in dieser Uebersicht, weil es sonst eine zweite Fassung des Konzepts waere.", BL]]));

/* ---- 1 Kurzfassung -------------------------------------------------- */
add(h("1 · Kurzfassung", 1));
add(p([["Webgewerk", BL], [" baut kleinen Betrieben im Rhein-Erft-Kreis eine neue Website zum festen Preis und mit festem Termin. Der Einstieg ist ein kostenloser, individuell erstellter Website-Check, der belegbare Mängel der Bestandsseite benennt — bevor überhaupt ein Verkaufsgespräch stattfindet.", S]]));
add(liste([
  [["Zielkunde: ", S, true], ["jeder Betrieb im Fahrgebiet Kerpen–Grevenbroich mit bestehender Website und mindestens drei belegten Mängeln — Handwerk, Gastronomie, Vereine, Praxen, Handel. Betriebsgröße im Regelfall 1 bis 50 Mitarbeiter.", BL]],
  [["Angebot: ", S, true], ["Festpreis ab 990 € (Paket S), Standardpaket M 1.490 €, Paket L 2.290 €. 40 % Anzahlung vor Baubeginn.", S]],
  [["Aufwand beim Kunden: ", BL, true], ["ein Vorgespräch, einmal Material zusammenstellen, zwei Rückmeldungen.", BL]],
  [["Alleinstellung: ", S, true], ["fester Preis, fester Termin, ein Ansprechpartner — und ein nachgewiesener Mangel, bevor wir etwas verkaufen.", S]],
]));
add(p([["Geändert: Die frühere Zusage „rund zwei Stunden Zeitaufwand beim Kunden“ ist gestrichen. Sie war nie gemessen und widersprach den Mitwirkungspflichten in 4.3. Die echte Stundenzahl wird in den drei Pilotprojekten erhoben und danach hier eingetragen.", BL]], { kursiv: true, klein: true }));

/* ---- 2 Markt -------------------------------------------------------- */
add(h("2 · Markt und Wettbewerb", 1));
add(p([["Geändert am 20.08.: Der Name ist Webgewerk. Alle Unterlagen tragen ihn; der Konzept-Check vom 16.08. behält den alten Namen, weil er ein datiertes Dokument ist.", BL]]));
add(p([["Die Zielgruppe ist nicht mehr auf das Handwerk beschränkt. Angesprochen wird jeder Betrieb mit einer schlechten Website. Die Begründung ist die Messung selbst: 15 der 19 Prüfpunkte gelten für alle Branchen. Eine Seite, die auf dem Handy nicht lesbar ist, ist es für den Elektriker so wie für den Griechen.", BL]]));
add(p([["Was das kostet: Die belegte Zahl aus 2.1 — 94 % der Handwerksbetriebe haben eine Website — trägt für die anderen Branchen nicht. Für Gastronomie und Vereine liegt keine Quelle vor; das ist ab jetzt eine Annahme.", R]]));
add(p([["Was das bringt: Der Prüfkatalog kann es bereits. Er enthält seit dem 17.08. Zusatzpunkte für Gastronomie (Speisekarte als Text, Weg zur Reservierung) und Vereine (Weg zur Mitgliedschaft) — sie waren gebaut, aber nicht verkauft.", BL]]));
add(h("2.1 Was belegt ist", 2));
add(liste([
  [["94 % der deutschen Handwerksbetriebe haben eine eigene Website", S, true], [" (Bitkom/ZDH 2025, n = 504, repräsentativ, ±4 %). Wir bedienen einen Ersatzmarkt, keinen Erstausstattungsmarkt. Die Ansprache kann nie „Sie brauchen eine Website“ lauten, sondern nur „Ihre Website hat ein konkretes, messbares Problem“.", S]],
  [["Höchstens 45 % der Handwerker-Websites funktionierten mobil optimal", S, true], [" (Bitkom/ZDH 2020). Die belastbarste Stütze des Modells — und sechs Jahre alt. Eine neuere Erhebung existiert nicht.", S]],
  [["76 % nennen Investitionskosten als größtes Digitalisierungshemmnis", S, true], [" (Bitkom/ZDH 2020). Der Festpreis adressiert genau diesen Einwand.", S]],
]));
add(p([["Nicht verwenden: „Jeder zweite Handwerker hat keine Website“ (Gelbe Seiten 2018, rund 100 Betriebe in der Stichprobe) und „nur 35 % haben eine Internetpräsenz“ (kursiert ohne Quelle). Beide widersprechen Bitkom/ZDH und halten einer Nachfrage im Gespräch nicht stand.", S]]));
add(h("Eigene Messreihe — erste Zahlen liegen vor", 3, BL));
add(p([["Elf Betriebe im Fahrgebiet sind vollständig geprüft. Acht davon, also 73 %, haben drei oder mehr belegte Befunde und gelten damit als Zielkunden. Häufigste Befunde: Telefonnummer nicht antippbar (8 von 11), kein Anfrageformular (8), keine Karriereseite (7), nicht für Handys eingerichtet (5), keine Beschreibung für Google (5). Damit ist die Trichterannahme in Abschnitt 11 nicht mehr Annahme, sondern durch eigene Messung gedeckt.", BL]]));

add(h("2.2 Wettbewerb", 2));
add(tabelle(
  ["Segment", "Beispiele", "Preis", "Was dort fehlt"],
  [
    ["Baukasten Selbstbau", "Wix, Jimdo, IONOS, STRATO", "12–30 €/Monat", "Zeit und Können des Kunden"],
    ["Baukasten mit Bau-Service", "IONOS, STRATO", "30–85 €/Mon. · 3 Jahre 1.600–1.800 €", "Eigentum, Individualität, Ansprechpartner"],
    ["Template-Festpreis", "werkerweb, goldfein", "329–699 €", "Beratung, Individualität"],
    ["Direkte Preisnachbarn", "Werbeagentur Landau, meinBetrieb online, PagePartner", "759–1.739 €", [["zu prüfen", R]]],
    ["Kleinagentur individuell", "neuzeitwerber, Netfame", "2.500–5.000 €", "Preis, Tempo"],
    ["Miete / Leasing", "webseiten-fuer-handwerker.net", "75–175 €/Mon., 36 Mon.", "Eigentum an der Seite"],
  ],
  [1900, 2400, 2100, 2600]));
add(abstand());
add(p([["Schlussfolgerung. ", S, true], ["Unser Hauptgegner ist nicht die teure Agentur, sondern das Bau-Service-Abo von IONOS und STRATO. Über drei Jahre landet der Kunde dort bei 1.600 bis 1.800 € — praktisch unserem Preis. Was er dort nicht bekommt: Eigentum an der Seite, echte Individualität und einen Menschen, der zu ihm fährt. Der Preis ist nicht unser Argument.", S]]));
add(p([["Offen — Yannik, vor dem ersten Angebot: Für keinen Wettbewerberpreis in dieser Tabelle gibt es eine Quelle mit Abrufdatum. Ein Dokument, das bei Marktzahlen Stichprobengröße und Fehlertoleranz angibt, kann sich das hier nicht leisten. Vor allem die Zeile „Direkte Preisnachbarn“: Sie liegen im selben Preisband und arbeiten mit vergleichbarem Modell. Die Behauptung, sie seien nicht im Rheinland aktiv, ist ungeprüft. Sieben Angebotsseiten aufrufen, Preis und Datum notieren, Fahrgebiet feststellen.", R]]));

add(h("2.3 Warum wir", 2));
add(liste([
  "Der Check liefert den belegten Mangel vor dem Gespräch. Kein Anbieter in diesem Preissegment tut das.",
  "Persönliche Übergabe im Fahrgebiet. Ein Fernanbieter kann das nicht nachmachen.",
  "KI-gestützte Produktion senkt unsere Kosten. Nach außen kein Verkaufsargument (Abschnitt 5).",
  [["Der Nachteil, den wir aktiv beantworten müssen: neu, ohne Kundenreferenzen. Zwei Antworten: heute die vorhandenen Arbeitsproben, ab dem ersten Livegang die echten Referenzen aus dem Pilotprogramm (9.4).", BL]],
]));

/* ---- 3 Zielgruppe --------------------------------------------------- */
add(h("3 · Zielgruppe und Auswahl", 1));
add(h("3.1 Branchen und Region", 2));
add(liste([
  [["Hauptbranche: ", S, true], ["bau- und ausbaunahe Gewerke — Elektro, Sanitär/Heizung, Fenster/Türen, Innenausbau, Dach, Maler. Verkaufsargument: Außenwirkung und Mitarbeitergewinnung, nicht Auftragsgewinnung.", S]],
  [["Nebenbranchen, später: ", S, true], ["Gastronomie, Vereine. Erweiterung erst nach dem dritten zahlenden Kunden in der Hauptbranche.", S]],
  [["Region: ", S, true], ["Erstkontakt ausschließlich im Fahrgebiet Kerpen, Bergheim, Elsdorf, Bedburg, Grevenbroich. DACH ist Fernziel und kein Planungshorizont.", S]],
  [["Betriebslisten: ", S, true], ["durchgeplant.de, Handwerkskammer-Verzeichnis, OpenStreetMap über Overpass, Google Maps, Gelbe Seiten.", S]],
]));
add(h("Was es dem Betrieb bringt — die Rechnung macht er selbst", 3, BL));
add(p([["Auf die Frage „was bringt mir das?“ darf der Check keine Antwort geben: Umsatzaussagen sind untersagt, und eine erfundene Zahl merkt ein Meister sofort. Die Lösung ist nicht, eine Zahl zu suchen, die wir behaupten dürfen — sondern drei Fragen zu stellen, aus denen er sich seine eigene Zahl macht. Sie gehören ins Vorgespräch, nicht auf den Check:", BL]]));
add(liste([
  [["„Wie lange suchen Sie schon jemanden?“ — Monate mal Deckungsbeitrag eines Gesellen. Die Zahl kennt er, wir nicht.", BL]],
  [["„Wie viele Anfragen lehnen Sie im Monat ab, weil Leute fehlen?“ — macht die Vakanz in Aufträgen sichtbar.", BL]],
  [["„Woher kam Ihr letzter Bewerber?“ — meist über Bekannte. Dann ist die Frage, was passiert, wenn dieser Kanal versiegt.", BL]],
]));
add(p([["Der Vorteil: Die Zahl ist seine, nicht unsere. Sie ist damit glaubwürdiger als jede Statistik und verstößt gegen keine unserer eigenen Regeln. Unsere einzige eigene Zahl bleibt der Kostenvergleich zum Baukasten-Abo aus 2.2.", BL]]));
add(p([["Offen: Der Satz „Wer voll ausgelastet ist, sucht Leute, keine Kunden“ trug bisher die gesamte Positionierung — ohne Quelle. Eine belastbare Branchenzahl bleibt nützlich fürs Gespräch (ZDH-Konjunkturbericht, Handwerkskammer Köln), ist aber nicht mehr die Grundlage.", R]]));

add(h("3.2 Auswahl", 2));
add(liste([
  "Zielkunde ab drei sicher belegten Befunden aus dem Prüfkatalog (Anhang A). Auf den Check kommen maximal vier.",
  "Betriebsgröße 3 bis 50 Mitarbeiter. Annahme, nach 20 Gesprächen prüfen.",
  [["Anlass, wenn erkennbar: ", BL, true], ["offene Stellenanzeige, Betriebsübergabe, Umzug, neuer Standort. Ein Anlass hebt den Betrieb in der Reihenfolge nach vorn — er ersetzt aber keinen Befund.", BL]],
  [["Ausschluss: ", S, true], ["Seite erkennbar in den letzten zwölf Monaten neu gebaut · Betrieb geschlossen, in Insolvenz oder Übergabe · Filiale einer Kette mit zentraler Website · Doppeleintrag oder bereits kontaktiert · kein belegbarer Defekt · ", S], ["Widerspruch nach Art. 21 DSGVO eingelegt", BL]],
]));
add(h("Betriebe ohne Website — eine eigene, sehr kurze Ansprache", 3, BL));
add(p([["Nach Bitkom/ZDH haben rund 6 % der Handwerksbetriebe keine Website. Sie waren bisher ausgeschlossen, weil der Check ohne Bestandsseite nicht funktioniert — es gibt nichts zu messen. Das ist der richtige Grund, aber der falsche Schluss: Es ist zugleich die Gruppe mit dem kürzesten Verkaufsweg, weil kein Bestand verteidigt werden muss.", BL]]));
add(liste([
  [["Kein Check, sondern ein einzelnes Blatt: Was ein Betrieb ohne Website nicht hat — kein Weg für Bewerber, kein Eintrag, den jemand findet, keine Adresse für Angebote. Drei Punkte, keine Messwerte.", BL]],
  [["Statt Befunden: gleich der Entwurf, gebaut aus Google-Profil, Branchenverzeichnis und dem, was am Fahrzeug steht.", BL]],
  [["Eigene Spalte in der Betriebsliste, damit sich die Quote getrennt messen lässt.", BL]],
  [["Grenze: Start frühestens nach den ersten 20 Checks. Solange der Hauptkanal ungetestet ist, wird kein zweiter parallel erprobt — sonst weiß man nicht, welcher gewirkt hat.", BL]],
]));

/* ---- 4 Angebot ------------------------------------------------------ */
add(h("4 · Angebot", 1));
add(h("4.1 Pakete", 2));
add(tabelle(
  ["Paket", "Umfang", "Kalkuliert", "Preis"],
  [
    ["S", "Auftritt, 4–5 Seiten, Übernahme vorhandener Texte, Aufbereitung des gelieferten Bildmaterials, Kontaktformular, Impressum und Datenschutz nach Vorlage", "15 h", "990 €"],
    ["M — Standard", "Auftritt und Karriereseite, 6–8 Seiten, Texte aus Kundenstichpunkten formuliert, technisches SEO-Grundsetup", "22 h", "1.490 €"],
    ["L", "zusätzlich Texte aus einem geführten Interview, erweiterte Bildaufbereitung, bis 12 Seiten", "32 h", "2.290 €"],
  ],
  [1500, 4600, 1200, 1700]));
add(abstand());
add(p([["In jedem Paket enthalten: ", BL, true], ["Einrichtung einer eigenen Domain, falls der Betrieb bisher auf einer Baukasten-Adresse läuft. Die Gebühr von rund 12 € im Jahr zahlt der Kunde direkt beim Anbieter — die Arbeit ist unsere.", BL]]));
add(p([["Nicht enthalten: ", S, true], ["Online-Shop, Buchungs- und Bestellsystem, Mehrsprachigkeit, laufende SEO-Betreuung, Newsletter, Social-Media-Betreuung, Logo-Design, gekaufte Stockfotos, geprüfte Rechtstexte, Einrichtung des Google-Unternehmensprofils. ", S], ["Fotoaufnahmen sind gegen Aufpreis möglich — siehe 4.3.", BL]]));
add(h("Hinweis zum Paket S", 3));
add(p([["990 € bei 15 kalkulierten Stunden ergeben 66 € je Stunde. Realistisch dauern die ersten Projekte das Zwei- bis Dreifache; bei S fällt der effektive Satz damit unter 25 €. S nur verkaufen, wenn der Umfang wirklich bei 4–5 Seiten liegt und die Inhalte vollständig vorliegen — sonst auf M führen.", S]]));
add(p([["Offen — nach Projekt drei: Beworben wird „ab 990 €“, verkauft werden soll M zu 1.490 €. Das widerspricht dem eigenen Ton („jede Aussage nachprüfbar“). Zwei saubere Auswege: S ganz streichen und mit „Festpreis ab 1.490 €“ werben, oder S auf einen Umfang zuschneiden, den es zu diesem Preis wirklich gibt. Entscheiden, sobald die Ist-Zeiten vorliegen.", R]]));

add(h("4.2 Anpassungen, Abnahme, Termine", 2));
add(liste([
  [["Zwei Anpassungsrunden inklusive", S, true], [", im Angebot festgeschrieben. Eine Runde ist eine gesammelte Rückmeldung, nicht ein Einzelwunsch. Ab der dritten Runde 70 €/h, vorher schriftlich angekündigt.", S]],
  [["Abnahme: ", BL, true], ["Nach der zweiten Runde legen wir den Stand schriftlich zur Abnahme vor. Der Kunde hat sieben Tage für eine begründete Rüge; erfolgt keine, gilt die Leistung als abgenommen.", BL]],
  [["Umsetzungszeit vier Wochen ab vollständiger Inhaltslieferung", S, true], [" — nicht ab Vertragsschluss. Der Unterschied gehört ins Angebot, sonst haften wir für die Trägheit des Kunden.", S]],
]));
add(h("Wenn der Kunde nicht abnimmt", 3, BL));
add(p([["Das ist der wahrscheinlichste Konflikt des Geschäfts. Vier Stufen, die im Vertrag stehen müssen — vorher aufgeschrieben, nicht im Streit erfunden:", BL]]));
add(liste([
  [["Die Rüge muss schriftlich und begründet sein und sich auf zugesagte Leistungen beziehen: was im Angebot steht, was in den beiden Runden vereinbart wurde, was der Prüfkatalog verlangt. „Gefällt mir nicht“ ist keine begründete Rüge — Geschmack ist Gegenstand der zwei Runden.", BL]],
  [["Begründete Punkte bessern wir nach. Das ist keine dritte Runde und kostet nichts. Danach läuft die Frist erneut, aber nur für die nachgebesserten Punkte.", BL]],
  [["Bleibt es strittig, hat der Kunde die Wahl: Minderung — wir liefern wie gebaut, er zahlt einen Abschlag von 15 % der Restsumme — oder Rücktritt.", BL]],
  [["Beim Rücktritt behalten wir die Anzahlung als Aufwandsentschädigung, die Seite geht nicht live, der Kunde erhält weder Dateien noch Repository. Eigene Inhalte bekommt er zurück.", BL]],
]));
add(p([["Zu prüfen: Die 15 % und die einbehaltene Anzahlung sind Vorschläge, keine geprüften Klauseln. Beides unterliegt der AGB-Inhaltskontrolle. Ein pauschaler Einbehalt kann unwirksam sein, wenn er den tatsächlichen Aufwand deutlich übersteigt.", R]]));

add(h("4.3 Mitwirkung des Kunden", 2));
add(liste([
  "Inhalte (Texte, Bilder, Logo, Domain- und Hosting-Zugang) innerhalb von 14 Tagen nach Anzahlung. Rückmeldung auf einen Entwurf innerhalb von 7 Tagen.",
  "Nach 30 Tagen ohne Lieferung ruht das Projekt. Die Anzahlung verfällt nicht und wird nicht erstattet, Wiederaufnahme jederzeit möglich.",
  "Bilder liefert der Kunde und garantiert schriftlich, dass er sie verwenden darf. Keine Stockfotos auf eigene Rechnung.",
  [["Übernommene Texte der Bestandsseite: ", BL, true], ["Der Kunde bestätigt schriftlich, dass er sie auf einer neuen Website verwenden darf, und stellt uns von Ansprüchen Dritter frei. Hintergrund: Urheber ist immer die Person, die den Text geschrieben hat (§ 7 UrhG); der Betrieb hat nur die eingeräumten Nutzungsrechte. Schweigt der alte Agenturvertrag, gilt im Zweifel nur der damals vereinbarte Zweck (§ 31 Abs. 5 UrhG) — und das war die alte Seite.", BL]],
  "Unsere Antwortzeit im laufenden Projekt: 2 Werktage.",
]));
add(h("Wenn die Bilder nicht reichen — zwei Wege statt einer Absage", 3, BL));
add(tabelle(
  ["Weg", "Was wir tun", "Preis"],
  [
    [[["Wir machen die Aufnahmen", BL]], [["Ein halber Tag vor Ort: Betrieb, Team, zwei bis drei fertige Arbeiten. Aufbereitung inklusive. Keine Studioqualität, aber aktuell, echt und rechtssicher.", BL]], [["offen", R]]],
    [[["Wir empfehlen einen Fotografen", BL]], [["Namentliche Empfehlung, der Kunde beauftragt und bezahlt direkt. Wir bekommen keine Provision und sagen das auch.", BL]], [["beim Fotografen", BL]]],
    [[["Ohne Fotos", BL]], [["Gestaltung mit Flächen, Farbe und Typografie. Wird vorher gezeigt, damit niemand überrascht wird.", BL]], [["im Preis", BL]]],
  ],
  [2400, 5300, 1300]));
add(abstand());
add(p([["Keine Provision, nie. Wenn wir jemanden empfehlen, empfehlen wir ihn, weil er gut ist. Das gehört im Gespräch gesagt; es ist in diesem Gewerbe ungewöhnlich genug, um aufzufallen.", BL]]));
add(p([["Offen — Kira, vor dem ersten Angebot: Preis für den halben Tag Aufnahmen festlegen (Anhaltspunkt: vier bis fünf Stunden zu 70 €). Und den Fotografen fragen, ob er genannt werden will.", R]]));

add(h("4.4 Feste Fragen im Vorgespräch", 2));
add(liste([
  "Wie läuft der Betrieb, und was ist für die nächsten zwölf Monate geplant?",
  "Welche Inhalte gibt es schon, was bleibt, was wird ersetzt?",
  "Was soll die Website vor allem erreichen — Aufträge, Bewerber oder Seriosität?",
  "Wer entscheidet, und wer liefert die Inhalte?",
  [["Wie lange suchen Sie schon jemanden — und wie viele Anfragen lehnen Sie im Monat ab, weil Leute fehlen? (Die Rechnung macht er, nicht wir — 3.1.)", BL]],
  [["Wer verwaltet heute Domain und E-Mail-Postfach, bei welchem Anbieter — und liegen beide beim selben? (Entscheidet über den Livegang, siehe 7.1.)", BL]],
]));
add(h("Die drei Einwände, die sicher kommen", 3, BL));
add(tabelle(
  ["Einwand", "Antwort"],
  [
    [[["„Zu teuer.“", BL]], [["Gegenrechnung, keine Rechtfertigung: Das Bau-Service-Abo bei IONOS oder STRATO kostet über drei Jahre 1.600 bis 1.800 €. Danach gehört Ihnen nichts. Bei uns gehört Ihnen die Seite ab dem ersten Tag.", BL]]],
    [[["„Das macht mein Neffe.“", BL]], [["Nicht dagegen argumentieren. Fragen, wann er zuletzt Zeit hatte, und auf den Check zeigen: Diese Punkte stehen seit Jahren offen. Anbieten, dass er den Zugang behält.", BL]]],
    [[["„Dafür hab ich keine Zeit.“", BL]], [["Genau darum die feste Liste: ein Vorgespräch, einmal Material zusammenstellen, zwei Rückmeldungen. Termine nach seinem Kalender, auch nach Feierabend.", BL]]],
  ],
  [2400, 6600]));
add(abstand());
add(p([["Entwurf — wird noch ausgearbeitet.", R]]));

/* ---- 5 Positionierung ----------------------------------------------- */
add(h("5 · Positionierung und Marke", 1));
add(liste([
  [["Name: Webgewerk", BL, true], [", Zusatz „Ihr Gewerk im Fokus“. Entschieden.", BL]],
  [["Versprechen in einem Satz: ", S, true], ["„Eine fertige Website für Ihren Betrieb — fester Preis, fester Termin, ein Ansprechpartner.“", S]],
  [["Ton: ", S, true], ["sachlich, konkret, jede Aussage nachprüfbar. Kein Guru-Vokabular, keine Superlative, keine Emojis als Aufzählungszeichen, keine Aussage über Umsatzsteigerung.", S]],
  [["Rolle der KI: ", S, true], ["intern Kostenvorteil in der Produktion. Bei Handwerksbetrieben nach außen kein Verkaufsargument. Auf direkte Nachfrage antworten wir offen.", S]],
  [["Ein Ansprechpartner je Kunde", S, true], [", und zwar der, der das Vorgespräch geführt hat. Da Yannik den Vertrieb führt, trägt der Check ", S], ["Yanniks Namen und Yanniks E-Mail-Adresse", BL, true], [".", S]],
]));
add(p([["Domainrecherche, Stand 22.08.2026, beim Registry Verisign geprueft: ", BL], ["webgewerk.com ist frei", BL, true], [". Die Abfrage liefert 404, die Gegenprobe mit einer vergebenen Domain liefert 200, und es gibt keinen DNS-Eintrag. Die Fassung vom 13.08. behauptete das Gegenteil; dort waren .de und .com verwechselt. ", BL], ["webgewerk.de ist vergeben", BL, true], [" und geparkt, sie loest auf 212.53.215.62 auf. Fuer .de gibt es keine oeffentliche Registerabfrage, hier ist der DNS-Eintrag der Beleg. Fehlender DNS-Eintrag waere umgekehrt kein Nachweis fuer frei.", BL]]));
add(p([["Zu korrigieren: Auf der aktuellen Check-Vorlage steht Yanniks Name mit Kiras Mailadresse. Das ist genau der Widerspruch, den die Regel auflösen soll.", R]]));

/* ---- 6 Preis --------------------------------------------------------- */
add(h("6 · Preis und Erlösmodell", 1));
add(liste([
  [["Verbindliche Festpreise. ", S, true], ["Der Check nennt den Rahmen („Festpreis ab 990 €, fertig in vier Wochen“), das Angebot nennt ihn verbindlich. Die Beratungsleistung ist in jedem Paket enthalten.", S]],
  [["Es wird nicht verhandelt. ", BL, true], ["Wer weniger zahlen will, bekommt weniger Seiten — ein anderes Paket, nicht denselben Umfang billiger. Der frühere Spielraum von 10 % ist gestrichen: Er widersprach der eigenen Begründung, ein verhandelter Preis zerstöre die Alleinstellung.", BL]],
  [["40 % Anzahlung vor Baubeginn", S, true], [", ohne Ausnahme. Schlussrechnung nach Abnahme und Livegang.", S]],
  [["Pilotpreis: ", S, true], ["die ersten drei Projekte zu 50 % (Paket M: 745 €) gegen vollständige Referenzrechte. Befristet auf drei Abschlüsse, danach kein Rabatt.", S]],
]));
add(p([["Marktvergleich: Wartungspakete im Kleinstsegment liegen bei 29–69 €/Monat; ab etwa 89 € erwarten Kunden Reporting und zugesagte Reaktionszeiten. 69 € ist das obere Ende ohne Service-Level-Zusage. Deshalb muss der Leistungsumfang exakt benannt sein.", S]]));

/* ---- 7 Produktion ---------------------------------------------------- */
add(h("7 · Produktion und Technik", 1));
add(h("7.1 Bauweise, Hosting, Domain", 2));
add(p([["Websites werden mit Claude Code als statische Seiten gebaut und je Kunde in einem eigenen Git-Repository versioniert. Ausgeliefert wird HTML, CSS und minimales JavaScript, ohne CMS und ohne Datenbank. Das bringt sehr kurze Ladezeiten — ausgerechnet der Prüfpunkt, mit dem wir bei fremden Seiten argumentieren —, praktisch keine Sicherheitsupdates, kein Plugin-Risiko und eine vollständige Versionshistorie.", S]]));
add(h("Hosting und Domain: betreuen, nicht besitzen", 3, BL));
add(p([["Wir richten beides für den Kunden ein, aber nichts läuft über uns. Das ist der Unterschied zwischen Einrichten und Wiederverkaufen — und er ist wichtig: Ein Wiederverkauf würde uns zum Vertragspartner für Ausfälle machen, die wir nicht verursachen.", BL]]));
add(liste([
  [["Die Domain läuft auf den Namen des Kunden, das Hosting auf seinen Vertrag und seine Rechnung. Für uns entstehen keine laufenden Kosten je Kunde.", BL]],
  [["Wir brauchen Zugang, nicht Eigentum: SFTP- oder Git-Zugang beim Hoster des Kunden, dazu Zugriff auf die Domainverwaltung.", BL]],
  [["Voraussetzung an das Hosting: Es muss das Hochladen eigener Dateien erlauben. Ein reiner Baukasten-Tarif kann das nicht — dort ist ein Wechsel Teil des Projekts.", BL]],
  [["Im Verkauf ein Argument, kein Zugeständnis: „Ihre Domain, Ihr Vertrag, Ihre Rechnung — wir kümmern uns nur darum. Sie sind an keinem Tag von uns abhängig.“", BL]],
]));
add(h("Der Kunde kann nichts selbst ändern — das soll sich ändern", 3, BL));
add(p([["Bisher läuft jede Änderung über uns. Entschieden am 17.08.: Das wird umgebaut. Statt eine schnelle Reaktionszeit zu versprechen, bekommt der Kunde etwas, das er selbst bedienen kann. Eine zugesagte Reaktionszeit ist ein Versprechen, das man brechen kann; ein Feld, das er selbst ändert, ist keins.", BL]]));
add(p([["Die Grenze bleibt eng: kein CMS, keine Datenbank, kein Fremddienst. Selbst bedienbar werden nur die Felder, die sich tatsächlich ändern — Öffnungszeiten, Telefonnummer, eine Stellenanzeige, ein Absatz Text, ein Bild. Ein Baukasten, in dem der Kunde das Layout zerlegen kann, ist ausdrücklich nicht das Ziel.", BL]]));
add(p([["Entschieden am 19.08., gebaut und geprüft: Es wird der eigene kleine Endpunkt beim Hoster des Kunden — drei PHP-Dateien, kein Fremddienst, keine Datenbank, keine laufenden Kosten. Im HTML wird eine änderbare Stelle zwischen zwei Markierungen gesetzt; der Pflegebereich zeigt sie dem Kunden als beschriftetes Formularfeld und schreibt den neuen Text an dieselbe Stelle zurück. Das HTML drumherum bekommt er nie zu sehen. Wird die Telefonnummer geändert, wird der anklickbare Verweis mitgezogen.", BL]]));
add(p([["Dieselbe Entscheidung löst das Kontaktformular, weil es dieselbe Sorte Datei ist: Die Anfrage geht direkt in das Postfach des Betriebs. Kein Formulardienst, kein weiterer AV-Vertrag, kein weiterer Anbieter in der Datenschutzerklärung. Gegen Spam zwei unsichtbare Fallen statt eines Captchas. Damit ist Prüfpunkt 6 auf unseren eigenen Seiten erfüllbar.", BL]]));
add(p([["Bilder gehen genauso: eine Markierung vor dem Bild, und der Kunde tauscht es selbst aus. Was er hochlädt, wird geprüft und automatisch auf 1600 Pixel verkleinert — aus einem Telefon kommen 4000 Pixel und mehrere Megabyte, und ungefragt hochgeladen macht das eine schnelle Seite langsam. Das ist Prüfpunkt 4, mit dem wir selbst argumentieren.", BL]]));
add(p([["Wo die Grenze liegt und bleibt: Text und Bilder an markierten Stellen, mehr nicht. Keine neuen Seiten, kein Verschieben von Blöcken, kein Layout. Wer das will, will einen Baukasten, und dann sind Wix und Jimdo billiger als wir. Der Satz für das Verkaufsgespräch: Alles, was sich bei Ihnen ändert, ändern Sie selbst — alles, was gestaltet werden muss, machen wir.", BL]]));
add(p([["Geprüft: Felder lesen, Speichern ohne Veränderung des umgebenden HTML, Sicherung vor jedem Speichern, Nachziehen des Telefonverweises, Bildaustausch samt Verkleinerung, Abweisung einer als Bild getarnten Datei, Anmeldung mit falschem und richtigem Passwort, beide Spamfallen. Nicht geprüft: der tatsächliche Mailversand — das geht erst auf echtem Hosting und ist der erste Test beim Pilotprojekt.", R]]));

add(h("Livegang: der riskanteste Schritt", 3, BL));
add(p([["An der Domain hängt fast immer das Geschäfts-E-Mail-Postfach. Wer beim Umstellen der Website den Mailverkehr mit abräumt, hat einen Betrieb unerreichbar gemacht. Zwei Fälle, die man vorher unterscheiden muss:", BL]]));
add(tabelle(
  ["Fall", "Woran man ihn erkennt", "Was zu tun ist"],
  [
    [[["A · Website und E-Mail beim selben Anbieter", BL]], [["Der Kunde ruft seine Mails über dieselbe Firma ab, bei der die Seite liegt", BL]], [["Der einfachere Fall. Nur Dateien im Webspace austauschen. An DNS und MX wird nichts angefasst.", BL]]],
    [[["B · Umzug zu einem anderen Anbieter", BL]], [["Der bisherige Tarif erlaubt kein Hochladen eigener Dateien — typisch bei Baukästen", BL]], [["Der riskante Fall. DNS-Einträge ändern sich, MX muss unverändert mitwandern.", BL]]],
  ],
  [2600, 3000, 3400]));
add(abstand());
add(p([["Ablauf für Fall B:", BL, true]]));
add(liste([
  [["Vorher aufschreiben: alle bestehenden DNS-Einträge des alten Anbieters exportieren — besonders MX, aber auch TXT, SPF und DKIM. Diese Liste ist der Rückweg.", BL]],
  [["Neue Seite parallel testen, unter einer Vorschau-Adresse. Der Kunde bestätigt sie, bevor irgendetwas umgestellt wird.", BL]],
  [["TTL senken: 24 Stunden vorher die Gültigkeit der DNS-Einträge auf 5 Minuten setzen.", BL]],
  [["Umstellen Dienstag bis Donnerstag vormittags. Nie freitags, nie vor einem Feiertag. Nur die Einträge für die Website ändern, MX exakt übernehmen.", BL]],
  [["Sofort prüfen: Seite aufrufen, Testmail an das Betriebspostfach und eine von dort heraus. Erst wenn beides ankommt, ist der Umzug fertig.", BL]],
  [["Kunde bestätigt schriftlich, dass seine Mails ankommen. Ohne diese Bestätigung keine Schlussrechnung.", BL]],
  [["TTL nach 48 Stunden ohne Auffälligkeiten wieder anheben.", BL]],
]));
add(p([["Rückweg: Solange die alte Seite beim alten Anbieter noch liegt und die notierten DNS-Einträge vorliegen, ist der Stand von vorher in Minuten wiederhergestellt. Den alten Tarif deshalb frühestens einen Monat nach dem Umzug kündigen — das kostet den Kunden einmalig 15 bis 30 € und ist die günstigste Versicherung im ganzen Projekt.", BL]]));
add(h("Übergabe an den Kunden", 3, BL));
add(p([["Der Kunde bekommt ein vollstaendiges, funktionierendes und ihm gehoerendes Produkt. Es gibt nichts, was er zusaetzlich buchen muss, damit es laeuft.", BL]]));
add(p([["Die Übergabemappe — immer dieselben neun Punkte, immer schriftlich:", BL]]));
add(liste([
  "Die Website live auf seiner Domain, auf seinem Hostingvertrag, auf seinen Namen.",
  "Alle Dateien als ZIP-Archiv, per Mail oder auf einem USB-Stick. Nicht als Einladung zu einem Git-Repository: Ein Meister kann damit nichts anfangen. Wer es doch will, bekommt den Zugang zusätzlich.",
  "Der Pflegebereich mit Passwort. Telefonnummer, Öffnungszeiten, Stellenanzeige und Hinweise ändert er selbst, ohne uns und ohne Kosten.",
  "Das Kontaktformular, das direkt in sein Postfach liefert.",
  "Alle Zugangsdaten auf einem Blatt: Hosting, Domain, Pflegebereich.",
  "Eine Anleitung auf einer Seite: was wo liegt, wie man etwas ändert, wen man anruft.",
  "Impressum und Datenschutzerklärung als Text, damit er sie bei einer Änderung im Betrieb anpassen lassen kann.",
  "Die Übergabeliste: was er selbst erledigen muss — Google-Unternehmensprofil, alte Einträge, Visitenkarten.",
  "Schriftlich die Nutzungsrechte (§ 31 UrhG) und die Schlussrechnung. Er ist Eigentümer und kann jederzeit gehen.",
], BL));
add(p([["Was danach niemand fuer ihn tut: ", BL, true], ["Niemand prüft monatlich, ob die Seite erreichbar ist und das Zertifikat noch gilt. Statisch geht nichts kaputt, aber ein abgelaufenes Zertifikat zeigt jedem Besucher eine Sicherheitswarnung — genau Prüfpunkt 2, mit dem wir verkaufen. Der Betrieb merkt es erst, wenn ein Kunde anruft. Deshalb steht es auf dem Übergabeblatt. Und jede Änderung, die über den Pflegebereich hinausgeht, kostet 70 €/h, mindestens eine halbe Stunde. Beides gehört ins Angebot, nicht ins Kleingedruckte.", BL]]));

add(h("Was der Kunde selbst verwaltet — und was er dafür anfassen muss", 3, BL));
add(p([["Für ihn gibt es drei Stellen, und das ist die ganze Aufteilung. Wer das im Vorgespräch so erklärt, nimmt dem Thema die Größe.", BL]]));
add(tabelle(["Stelle", "Wofür", "Wie oft"], [
  [[["Pflegebereich (seinedomain.de/pflege)", BL]], [["Inhalte: Texte, Öffnungszeiten, Stellenanzeige, Bilder", BL]], [["so oft er will, auch vom Handy", BL]]],
  [[["Konto beim Hoster (IONOS, Strato, All-Inkl)", BL]], [["Vertrag, Rechnungen, E-Mail-Postfächer — und die Domain, wenn sie dort gekauft ist", BL]], [["zweimal im Jahr, wenn überhaupt", BL]]],
  [[["Die Domain", BL]], [["läuft auf seinen Namen, verlängert sich automatisch", BL]], [["nie, solange die Zahlung durchgeht", BL]]],
], [2600, 4600, 1800]));
add(abstand());
add(p([["Seine gesamte Verwaltungsarbeit sind drei Dinge: Zahlungsdaten beim Hoster aktuell halten, die Jahresrechnung nicht wegwerfen, und nichts kündigen, ohne vorher anzurufen. Mehr nicht.", BL]]));
add(p([["Der eine Satz, der in jedes Übergabegespräch gehört: ", BL, true], ["An der Domain hängt nicht nur die Website, sondern auch das Geschäfts-E-Mail-Postfach. Geht eine Zahlung nicht durch, ist beides weg — und wir bekommen davon nichts mit, weil die Rechnung an ihn geht, nicht an uns. Das ist kein Kleingedrucktes, das ist der teuerste Fehler, den ein Betrieb hier machen kann.", BL]]));
add(p([["Unser Zugang ist geliehen, nicht besessen. Waehrend des Projekts haben wir Zugang zu Hosting und Domainverwaltung, nie zu den E-Mail-Postfaechern, und nach der Uebergabe gar nicht mehr. Er kann uns den Zugang jederzeit entziehen; die Website läuft weiter. Genau das ist im Verkauf das Argument gegen das Baukasten-Abo: Sie sind an keinem Tag von uns abhängig.", BL]]));
add(p([["Die Vorlage für das Blatt, das er dazu bekommt, liegt im Repository unter studie/pflege/kundenblatt.md — eine Seite, drei Stellen, seine Zugangsdaten, unsere Telefonnummer.", BL]]));

add(h("WordPress und Baukästen: warum wir da nicht hineinliefern", 3, BL));
add(p([["Unser Produkt sind fertige Seiten. WordPress baut jede Seite bei jedem Aufruf neu aus einer Datenbank zusammen. Beides sind verschiedene Dinge — man kann fertige Seiten nicht in WordPress hochladen. Wer es trotzdem will, verlangt einen Neubau als WordPress-Theme, und damit monatliche Updates, Plugins, Sicherheitslücken und längere Ladezeiten: genau die Prüfpunkte 1, 2 und 4, mit denen wir bei fremden Seiten argumentieren.", BL]]));
add(liste([
  "Der Betrieb hat WordPress und hängt nicht daran — der Normalfall. Unsere Seite ersetzt es. Vorher wird die alte Installation vollständig gesichert, dann wird sie abgeräumt.",
  "Der Betrieb besteht auf WordPress — dann sind wir der falsche Anbieter, und das sagen wir im Vorgespräch. Ein Auftrag, den man nur mit einem anderen Produkt erfüllen kann, ist kein Auftrag.",
], BL));

add(h("7.2 Produktionsvorlage und Abnahme", 2));
add(liste([
  "Die ersten drei Websites werden vollständig von Hand gebaut, mit mitgeschriebener Ist-Zeit je Arbeitsschritt. Erst danach wird daraus eine wiederverwendbare Vorlage abgeleitet.",
  "Annahme, ungeprüft: Die kalkulierten 15, 22 bzw. 32 Stunden gelten erst ab Projekt vier. Für die Pilotprojekte ist das Zwei- bis Dreifache einzuplanen.",
]));
add(h("Definition of Done — geteilt", 3, BL));
add(p([["Der Prüfkatalog hat zwei Aufgaben: Mängel bei fremden Seiten finden und verhindern, dass wir liefern, was wir anstreichen. Für die zweite Aufgabe wird er geteilt:", BL]]));
add(liste([
  [["Was wir steuern", BL, true], [" — Prüfpunkte 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 15 sowie 21, 22, 23. Eine ausgelieferte Seite hat hier null Befunde. Ohne Ausnahme.", BL]],
  [["Was der Kunde steuert", BL, true], [" — Prüfpunkt 13 (eigene Domain), 14 (Google-Unternehmensprofil), 20 (Speisekarte) sowie Punkt 6, solange der Formulardienst nicht entschieden ist. Diese Punkte stehen auf der Übergabeliste und werden schriftlich erklärt.", BL]],
]));
add(p([["Bisher hieß es „besteht den vollständigen Prüfkatalog ohne einen einzigen Befund“. Das war nicht erfüllbar, weil drei Punkte am Kunden hängen — und es hätte auch den ersten Kundenkontakt blockiert. Kein Punkt fällt weg, sie sind nur zugeordnet.", BL]], { kursiv: true, klein: true }));

add(h("7.3 Ablauf", 2));
add(p([["Betrieb geprüft → Check und Designentwurf erstellt → persönlich übergeben → Nachfassanruf nach drei Werktagen → Vorgespräch mit Zieldefinition → Angebot und 40 % Anzahlung → Bau → maximal zwei Anpassungsrunden → ", S], ["Abnahme", BL, true], [" → Livegang auf Kundendomain → ", S], ["Übergabe", BL, true], [" → Schlussrechnung.", S]]));

/* ---- 8 Betrieb ------------------------------------------------------- */
add(h("8 · Betrieb nach Livegang", 1));
add(liste([
  [["Was eine Änderung ist: ", BL, true], ["eine zusammenhängende Anpassung an bestehenden Inhalten — ein Text, ein Bildtausch, Öffnungszeiten, eine Stellenanzeige —, Aufwand bis 30 Minuten. Nicht übertragbar: Zwei nicht genutzte Änderungen im Januar sind im Februar nicht vier.", BL]],
  [["Nicht enthalten: ", S, true], ["neue Seiten, Umbauten, Funktionserweiterungen, SEO-Betreuung, Textarbeit über den Änderungsumfang hinaus — 70 €/h nach schriftlicher Freigabe.", S]],
  [["Kündigung: ", S, true], ["zwölf Monate Mindestlaufzeit, danach monatlich zum Monatsende. Bei Kündigung übergeben wir Repository und Dateien.", S]],
  [["Preisanpassung: ", BL, true], ["frühestens nach 24 Monaten, mit drei Monaten Ankündigung und Sonderkündigungsrecht.", BL]],
  [["Bei Betriebseinstellung unsererseits: ", BL, true], ["Herausgabe aller Dateien und Zugänge binnen 14 Tagen. Gehört in den Vertrag.", BL]],
]));

/* ---- 9 Vertrieb ------------------------------------------------------ */
add(h("9 · Vertrieb", 1));
add(h("9.1 Kanal und Reihenfolge", 2));
add(p([["Rechtssichere Reihenfolge: Website-Check persönlich oder per Post übergeben → telefonisches Nachfassen frühestens drei Werktage später → E-Mail erst, nachdem der Betrieb selbst geantwortet hat.", S]]));
add(p([["Begründung. E-Mail-Werbung an Unternehmen ist ohne vorherige ausdrückliche Einwilligung unzulässig (§ 7 Abs. 2 Nr. 2 UWG) — das gilt auch für LinkedIn- und Xing-Nachrichten. Telefonwerbung im B2B setzt eine mutmaßliche Einwilligung voraus (§ 7 Abs. 2 Nr. 1 UWG), und seit dem Urteil des BVerwG vom 29.01.2025 (6 C 3.23) ist sie zusätzlich datenschutzrechtlich angreifbar. Der zuvor übergebene Check ist der sachliche Anknüpfungspunkt, der den Anruf trägt — ohne ihn rufen wir nicht an.", S]]));
add(liste([
  "Kein Preis im Anschreiben, keine Aussage zu Umsatz oder Erfolg, genau ein Handlungsaufruf: ein unverbindliches Gespräch.",
  [["Genau ein Anruf, und nie ein zweiter. ", BL, true], ["Wer nach dem Check nicht will, wird nicht noch einmal angerufen. Ein zweiter Anruf ohne neuen sachlichen Anlass ist lästig und wettbewerbsrechtlich angreifbar.", BL]],
  [["Wiedervorlage nur mit neuem Inhalt: ", BL, true], ["Nach zwölf Monaten wird die Seite erneut geprüft. Haben sich die Messwerte geändert, ist das ein neuer Check — und damit ein neuer sachlicher Anlass, kein Nachhaken. Ist alles unverändert, passiert nichts.", BL]],
  [["Jedem Check liegt ein Datenschutzhinweis nach Art. 14 DSGVO bei. ", S], ["Ein Widerspruch führt sofort in die Sperrliste (3.2).", BL]],
  [["Weiterempfehlung ist der zweite Kanal und der einzige mit erwartbar besserer Quote. Nach jedem Livegang aktiv danach fragen. Erster konkreter Anknüpfungspunkt: das Umfeld von durchgeplant.", S]],
]));

add(h("9.2 Website-Check", 2));
add(liste([
  [["Maximal vier Befunde. ", S, true], ["Auswahl in zwei Stufen: erst filtern — auf den Check kommt nur, was das angebotene Paket auch behebt —, dann sortieren nach Schweregrad absteigend.", BL]],
  [["Was wir nicht beheben (Punkt 14, Google-Profil), erscheint nicht auf dem gedruckten Check, sondern nur im internen Dossier — als Stoff für das Gespräch.", BL]],
  "Befund und Angebot auf getrennten Seiten: Seite 1–2 neutraler Befund, Seite 3 Ausblick und Preisrahmen.",
  "Der Check nimmt Farben und Anmutung des Betriebs auf, aber nicht dessen Logo. Zwei Farben aus der Bestandsseite, eine von drei Schriftvarianten nach Branche.",
  "Gemessene Fakten statt Wertung: „Ladezeit auf dem Handy: 8,4 Sekunden. Google bewertet über 4 Sekunden als schlecht.“",
]));
add(h("Ein bis drei Gründe je Betrieb — im Dossier, nicht auf dem Check", 3, BL));
add(p([["Der Check zeigt, was kaputt ist. Er sagt nicht, warum dieser Betrieb jetzt eine neue Seite braucht. Genau das entscheidet aber das Gespräch. Deshalb steht in jeder Kundendatei ein kurzer Abschnitt mit ein bis drei individuellen Gründen, jeder mit seinem Beleg — für uns, nie für den Kunden gedruckt.", BL]]));
add(tabelle(
  ["Grund", "Woran wir ihn erkennen", "Satz fürs Gespräch"],
  [
    [[["Sucht Personal", BL]], [["offene Stelle bei Google, Indeed, am Fahrzeug oder am Bauzaun", BL]], [["„Sie suchen einen Gesellen — auf Ihrer Seite steht das nirgends.“", BL]]],
    [[["Übergabe an die nächste Generation", BL]], [["zwei Nachnamen im Impressum, „seit 1978“, Handelsregister", BL]], [["„Wenn der Betrieb übergeben wird, ist die Außenwirkung das Erste, was auffällt.“", BL]]],
    [[["Neuer Standort oder Umzug", BL]], [["Adresse im Google-Profil weicht von der Website ab", BL]], [["„Google und Ihre Seite nennen zwei verschiedene Adressen.“", BL]]],
    [[["Neues Gewerk im Angebot", BL]], [["Google-Profil oder Fahrzeug nennt Leistungen, die auf der Seite fehlen", BL]], [["„Sie machen Wärmepumpen — auf der Seite steht nur Heizung.“", BL]]],
    [[["Wettbewerber sichtbarer", BL]], [["ein Nachbarbetrieb im selben Ort mit klar besserer Seite", BL]], [["nur nennen, wenn er von selbst darauf kommt — nie zuerst", BL]]],
  ],
  [2200, 3200, 3600]));
add(abstand());
add(p([["Regel: Ein Grund ohne Beleg wird nicht notiert. Was wir nicht zeigen können, sagen wir nicht — dieselbe Regel wie beim Befund. Umsetzung in der Pipeline: ein neues Feld „gruende“ je Betrieb.", BL]]));

add(h("9.3 Aufwand je Check", 2));
add(p([["Annahme, ungeprüft: 2 Stunden je bearbeitetem Betrieb. Wird ab dem ersten Check mitgeschrieben. Ziel nach 20 Checks: unter 45 Minuten, erreicht durch Automatisierung der Prüfpunkte 1–5 und 11–13.", S]]));
add(p([["Fahrzeit wird getrennt gerechnet und gebündelt. ", BL, true], ["Die 45 Minuten gelten für die Erstellung, nicht für die Übergabe. Eine Fahrt Kerpen–Grevenbroich und zurück ist rund eine Stunde; einzeln ausgefahren wäre die persönliche Übergabe mit dem Zeitziel unvereinbar. Deshalb werden Checks gesammelt und in Touren zu fünf Betrieben ausgefahren — damit fällt die Fahrzeit je Check auf etwa zwölf Minuten.", BL]]));

add(h("9.4 Pilotprogramm und Kaltstart", 2));
add(liste([
  "Drei Pilotprojekte zu 745 € (Paket M). Gegenleistung schriftlich fixiert: Firmenname als Referenz, Vorher-Nachher-Werte, ein Zitat, Zeigeerlaubnis für Website und Check.",
  [["Versetzt starten, mit rund zwei Wochen Abstand", BL, true], [" — nicht alle drei gleichzeitig und nicht streng nacheinander. Projekt 2 beginnt, wenn Projekt 1 in der ersten Warteschleife steht. Grund: Laufen sie gleichzeitig, kann Projekt 2 nichts aus Projekt 1 lernen — der erklärte Zweck des Pilotprogramms fällt weg. Dazu produziert nur eine Person.", BL]],
  "Vor dem ersten Kundenkontakt steht die eigene Website von Webgewerk, die den Prüfkatalog in den Punkten besteht, die wir steuern.",
]));
add(h("Arbeitsproben statt Referenzen", 3, BL));
add(p([["„Ohne Referenzen“ stimmt nur für Kundenreferenzen. Vorhanden sind mehrere selbst gebaute, vollständige Websites — darunter eine für einen echten Betrieb im Bauumfeld. Im Vorgespräch ist das etwas völlig anderes als nichts: Man kann eine fertige Seite aufschlagen, statt eine Behauptung aufzustellen.", BL]]));
add(liste([
  [["Was wir sagen dürfen: „Die haben wir gebaut.“ Wahr, belegbar, zeigbar.", BL]],
  [["Was wir nicht sagen: „Das ist unser Kunde.“ Es ist keiner, und ein Meister, der nachfragt, merkt den Unterschied sofort.", BL]],
  [["Vor dem Zeigen: schriftliche Erlaubnis des Betriebs einholen. Zwei Sätze per Mail genügen.", BL]],
  [["Sobald das erste Pilotprojekt live ist, tritt die echte Referenz an die Stelle der Arbeitsprobe.", BL]],
]));

add(h("9.5 Was wir nicht wissen", 2));
add(p([["Für die Kombination Check-Übergabe plus telefonisches Nachfassen im deutschen Kleinunternehmenssegment existiert keine belastbare Quote. Wir schätzen hier nicht — wir messen (Abschnitt 11).", S]]));

/* ---- 10 Wirtschaftlichkeit ------------------------------------------- */
add(h("10 · Wirtschaftlichkeit", 1));
add(h("10.1 Fixkosten", 2));
add(tabelle(
  ["Position", "monatlich", "Anmerkung"],
  [
    ["Claude-Abo", "80 €", [["Prüfauftrag: kommerzieller Tarif mit AV-Vertrag nötig", R]]],
    ["Eigene Domain und Hosting", "~10 €", [["nur für uns; Kundenhosting zahlt der Kunde", BL]]],
    ["Vermögensschaden-/IT-Haftpflicht", "25–58 €", "300–700 €/Jahr für eine Zwei-Personen-GbR"],
    [[["Druck und Porto der Checks", BL]], [["50–80 €", BL]], [["bei 20 Checks: 2,50–4 € je Stück, mehrseitiger Farbdruck plus Art.-14-Blatt", BL]]],
    [[["Fahrtkosten", BL]], [["40–70 €", BL]], [["vier Touren im Monat à rund 60 km, 0,30 €/km", BL]]],
    [[["Summe", SCHWARZ_BOLD_HACK()]], [["205–298 €", BL]], [["vorher 150–180 € — Fahrtkosten fehlten ganz", BL]]],
  ],
  [3000, 1600, 4400]));
function SCHWARZ_BOLD_HACK() { return BL; }
add(abstand());

add(h("10.2 Kapitalbedarf bis zum ersten Geld", 2, BL));
add(tabelle(
  ["Position", "Betrag"],
  [
    [[["Gewerbeanmeldung, zwei Personen", BL]], [["30–120 €", BL]]],
    [[["Vermögensschaden-/IT-Haftpflicht, Jahresbeitrag", BL]], [["300–700 €", BL]]],
    [[["Gesellschaftsvertrag GbR", BL]], [["0 € — Familie", BL]]],
    [[["Prüfung von Vertrag und AGB", BL]], [["0 € — Familie", BL]]],
    [[["Domain, Hosting, geschäftliche E-Mail", BL]], [["~50 €", BL]]],
    [[["Laufende Fixkosten bis zur ersten Anzahlung (3 Monate)", BL]], [["615–894 €", BL]]],
    [[["Summe", BL, true]], [["995–1.764 €", BL, true]]],
  ],
  [6200, 2800]));
add(abstand());
add(p([["Das erste Geld ist die Anzahlung des ersten Pilotkunden: 40 % von 745 €, also 298 €.", BL]]));
add(p([["Zwei Hinweise: Unentgeltliche Hilfe hat keine Rechnung und deshalb keinen Druck — sie ist das Erste, was liegen bleibt. Datum in Anhang C eintragen und wie einen bezahlten Termin behandeln. Und: Gesellschaftsvertrag und AGB kann jede juristisch versierte Person prüfen; § 7 UWG bei der Kaltakquise und die DSGVO-Kette bis Anthropic sind Spezialgebiete.", BL]]));
add(p([["Offen — beide, vor Tag 1: Wovon leben wir im ersten Jahr? Das Neugeschäft trägt sich im ersten Jahr nicht als Stundenlohn. Anstellung nebenher, Rücklage, Gründungszuschuss — schriftlich festhalten, mit Betrag und Dauer. Von allen offenen Punkten ist das der, an dem Vorhaben tatsächlich scheitern.", R]]));

add(h("10.3 Was eine Stunde wirklich bringt", 2));
add(p([["Paket S ergibt 66 € je kalkulierter Produktionsstunde, M 68 €, L 72 €. Das ist die halbe Wahrheit, weil die Vertriebszeit fehlt. Vollständig gerechnet, je gewonnenem Kunden (Paket M):", S]]));
add(tabelle(
  ["Szenario", "Vertrieb", "Produktion", "Gesamt", "Umsatz", "je Stunde"],
  [
    ["20 Checks à 2 h → 4 Gespräche → 1 Abschluss", "48 h", "22 h", "70 h", "1.490 €", "21 €"],
    ["20 Checks à 2 h → 4 Gespräche → 2 Abschlüsse", "48 h", "44 h", "92 h", "2.980 €", "32 €"],
    ["20 Checks à 45 Min. → 4 Gespräche → 2 Abschlüsse", "23 h", "44 h", "67 h", "2.980 €", "44 €"],
  ],
  [3400, 1100, 1300, 1000, 1100, 1100]));
add(abstand());
add(p([["Die Konversionsannahmen (20 % Vorgespräch, 5–10 % Abschluss) sind ungeprüft und durch keine Quelle gedeckt. Sie stehen hier, um die Größenordnung sichtbar zu machen — nicht als Planung.", R], ], { kursiv: true, klein: true }));
add(liste([
  "Der Check-Aufwand ist der entscheidende Hebel, nicht der Verkaufspreis. Von zwei Stunden auf 45 Minuten zu kommen verdoppelt den effektiven Stundensatz.",
  "Das Neugeschäft trägt sich im ersten Jahr nicht als Stundenlohn. Es finanziert den Aufbau von Vorlage und Referenzen.",
]));

add(h("10.4 Kein wiederkehrender Umsatz", 2, R));
add(p([["Entschieden am 22.08.2026: Es gibt keine Betreuung. Damit gibt es auch keinen Bestand, der monatlich traegt. Jeder Monat faengt bei null an, und der Umsatz haengt vollstaendig daran, dass neue Auftraege hereinkommen.", R]]));
add(p([["Der Grund ist ein Produktargument, kein kaufmaennisches: Der Pflegebereich nimmt dem Kunden genau die Arbeit ab, fuer die eine Betreuung sonst bezahlt wird. Ein Vertrag, der zwei Inhaltsaenderungen im Monat verkauft, waere neben einem Bereich, in dem der Kunde sie selbst in zwei Minuten macht, schwer zu begruenden. Und die Zusage \u201eNach dem Projekt sind wir raus\u201c vertraegt keinen Dauervertrag.", BL]]));
add(p([["Was das kostet: Die vorige Fassung rechnete mit 20 Betreuungskunden zu 69 €, also 16.560 € im Jahr bei nahezu keinen laufenden Kosten. Dieser Betrag entfaellt ersatzlos. Er war ohnehin fruehestens im dritten Jahr erreichbar; die Planung der ersten beiden Jahre aendert sich dadurch nicht.", BL]]));
add(p([["Was an seine Stelle tritt: Aenderungen ueber den Pflegebereich hinaus werden nach Aufwand berechnet, 70 €/h, mindestens eine halbe Stunde. Das ist kein Ersatz fuer wiederkehrenden Umsatz, sondern Gelegenheitsarbeit. Wer den Ausfall auffangen will, muss mehr Neugeschaeft machen, nicht anders abrechnen.", BL]]));
add(abstand());

add(h("10.5 Rücklagen", 2));
add(p([["30 % jeder Einnahme als Steuerrücklage auf ein separates Konto. Als Kleinunternehmer fällt keine Umsatzsteuer an — Einkommensteuer fällt trotzdem an, und Gewerbesteuer ab 24.500 € Gewerbeertrag der Gesellschaft.", S]]));

/* ---- 11 Kennzahlen --------------------------------------------------- */
add(h("11 · Ziele und Kennzahlen", 1));
add(p([["Tag 1 ist der Tag, an dem der erste Check übergeben wird, nicht der Tag der Gewerbeanmeldung.", S]]));
add(tabelle(
  ["Kennzahl", "Ziel in 90 Tagen", "gemessen wie"],
  [
    ["Geprüfte Betriebe", "60", "Betriebsliste"],
    ["Übergebene Checks", "40", "Betriebsliste"],
    ["Vorgespräche", "8", "Betriebsliste"],
    ["Zahlende Kunden", [["3", BL]], "gestellte Rechnungen"],
    ["Live-Seiten", [["3", BL]], "Betriebsliste"],
    ["Projekte mit erfasster Ist-Zeit", "3", "Zeitprotokoll"],
    ["Zeit je Check", "unter 45 Min. ab Check 20", "Zeitprotokoll"],
  ],
  [3400, 2800, 2800]));
add(abstand());
add(liste([
  [["Wöchentlicher fester Termin von 60 bis 90 Minuten", S, true], [", an dem diese Zahlen eingetragen und besprochen werden. ", S], ["Fester Tagesordnungspunkt: Stimmt der Prüfkatalog im Code noch mit Anhang A überein?", BL]],
  [["Abbruch- und Korrekturkriterien: ", S, true], ["Nach 20 Checks ohne ein einziges Vorgespräch wird der Brief überarbeitet, nicht die Zielgruppe. ", S], ["Nach 35 Checks ohne Vorgespräch wird der Kanal in Frage gestellt. Nach 40 Checks ohne Abschluss wird das Konzept neu bewertet.", BL]],
]));
add(p([["Geändert: Die strengste Schwelle lag bei 60 Checks — bei einem 90-Tage-Ziel von 40. Sie hätte nie ausgelöst.", BL]], { kursiv: true, klein: true }));

/* ---- 12 Rollen -------------------------------------------------------- */
add(h("12 · Rollen, Kapazität, Rechtsform", 1));
add(liste([
  "Yannik: Vertrieb, Erstkontakt, Vorgespräch, Angebot. Kira: Produktion, Technik, Übergabe.",
  [["Der Check trägt Yanniks Namen und Yanniks E-Mail-Adresse.", BL]],
]));
add(p([["Offen — beide, vor Tag 1: Verfügbare Stunden je Woche, feste Tage und Uhrzeiten, schriftlich. Ohne diese Zahl ist Abschnitt 10 nicht rechenbar und Abschnitt 11 nicht planbar. Das ist der wichtigste offene Punkt des Dokuments.", R]]));
add(p([["Offen — Kira, vor Tag 1: Ausfall einer Person. Produzieren kann derzeit nur Kira. Fällt sie aus, steht alles. Mindestens nötig: eine schriftliche Anleitung, wie ein Projekt gebaut und ausgeliefert wird, und Zugriff beider auf alle Zugänge.", R]]));
add(p([["Rechtsform. Die GbR besteht bereits, sobald wir gemeinsam nach außen auftreten — sie entsteht automatisch und auch ohne schriftlichen Vertrag (§ 705 BGB). Wir haften persönlich, unbeschränkt und gesamtschuldnerisch mit dem Privatvermögen (§ 721 BGB). Es gibt nichts zu entscheiden, nur etwas zu regeln: schriftlicher Gesellschaftsvertrag und je eine eigene Gewerbeanmeldung vor dem ersten Kunden.", S]]));

/* ---- 13 Recht --------------------------------------------------------- */
add(h("13 · Recht, Steuern, Datenschutz", 1));
add(p([["Alle Punkte mit Prüfauftrag stehen mit Verantwortlichem und Frist in Anhang C. Das ist keine Rechtsberatung.", S, true]]));
add(h("13.1 Werbung", 2));
add(p([["Kaltakquise per Mail an Unternehmen fällt unter § 7 UWG und trägt ein Abmahnrisiko. Risiko bei Verstoß: Streitwerte von 1.000 bis 6.000 €, Abmahnkosten meist 250 bis 900 €. Teurer wird die vorformulierte Unterlassungserklärung mit Vertragsstrafen von häufig 5.000 € je Fall — solche Erklärungen nie ungeprüft unterschreiben.", S]]));
add(h("13.2 Steuern", 2));
add(liste([
  "Webdesign ist gewerblich (§ 15 EStG), nicht freiberuflich. Der Gewerbesteuer-Freibetrag von 24.500 € (§ 11 GewStG) gilt einmal je Gesellschaft, nicht je Gesellschafter. Der IHK-Beitrag entfällt für Kleingewerbe mit Gewerbeertrag bis 5.200 €; die Mitgliedschaft besteht trotzdem.",
  "Kleinunternehmerregelung § 19 UStG: Nettogrenzen 25.000 € Vorjahr und 100.000 € laufendes Jahr, seit 01.01.2025. Bei Überschreiten der 100.000 € ist bereits der auslösende Umsatz voll steuerpflichtig. Im Gründungsjahr gilt allein die 25.000-€-Grenze.",
  [["Zu prüfen: Ein Verzicht auf § 19 UStG bindet fünf Jahre, bringt aber den Vorsteuerabzug. Da unsere Kunden B2B sind, kostet der Ausweis sie nichts — der Verzicht ist eine ernsthafte Option.", R]],
]));
add(h("13.3 Rechnungen und Aufbewahrung", 2));
add(p([["Empfangspflicht für E-Rechnungen im inländischen B2B seit 01.01.2025, auch für Kleinunternehmer, ohne Übergangsfrist; Archivierung im Originalformat (XML). Eine Ausstellungspflicht besteht für Kleinunternehmer dauerhaft nicht (§ 34a UStDV). Buchungsbelege 8 Jahre (§ 147 Abs. 3 AO), Bücher und Abschlüsse 10 Jahre.", S]]));
add(h("13.4 Datenschutz", 2));
add(liste([
  "Art. 14 DSGVO — Informationspflicht bei Daten aus öffentlichen Quellen. Gelöst durch die Beilage zum Check.",
  [["Art. 21 DSGVO — jeder Widerspruch führt in die Sperrliste und wird vor jedem Versand abgeglichen.", BL]],
  "Art. 30 DSGVO — Verzeichnis von Verarbeitungstätigkeiten ist Pflicht. Die Ausnahme für kleine Unternehmen greift bei regelmäßiger Verarbeitung nicht.",
  [["Claude / Anthropic: Sobald Kundendaten in Claude Code eingegeben werden, ist Anthropic Auftragsverarbeiter. Das erfordert einen Vertrag nach Art. 28, die Nennung im AVV mit dem Kunden und die Aufnahme ins Verarbeitungsverzeichnis. Alternative: konsequente Anonymisierung. Voraussetzung für das erste Projekt.", R]],
]));
add(h("Löschfristen", 3, BL));
add(tabelle(
  ["Fall", "Aufbewahrung", "Begründung"],
  [
    [[["Nur geprüft, nie kontaktiert", BL]], [["12 Monate", BL]], [["Der Betrieb hat nie von uns gehört.", BL]]],
    [[["Check übergeben, keine Reaktion", BL]], [["24 Monate", BL]], [["Berechtigtes Interesse: Doppelansprache vermeiden.", BL]]],
    [[["Abgesagt", BL]], [["24 Monate", BL]], [["danach nur noch Firma und Ort in der Ausschlussliste", BL]]],
    [[["Widerspruch nach Art. 21", BL, true]], [["dauerhaft", BL]], [["Firma, Ort, Datum — mehr nicht. Ohne diesen Minimaleintrag ließe sich die Sperre nicht durchsetzen.", BL]]],
    [[["Kunden", BL]], [["8 bzw. 10 Jahre", BL]], [["gesetzliche Aufbewahrung, § 147 AO", BL]]],
  ],
  [2800, 1900, 4300]));
add(abstand());
add(p([["Durchsicht einmal im Jahr, im Januar, als fester Punkt im Wochentermin.", BL]]));
add(p([["Offen — Kira, vor dem ersten Angebot: Barrierefreiheit. Das Barrierefreiheitsstärkungsgesetz gilt seit Juni 2025. Ob es Handwerksbetriebe mit reiner Informationsseite trifft, ist ungeklärt — Kleinstunternehmen sind voraussichtlich ausgenommen. Das ist eine Prüffrage, keine Rechtsaussage.", R]]));
add(h("13.5 Verträge, Haftung, Versicherung", 2));
add(liste([
  "Widerrufsrecht: Die 14 Tage gelten nur gegenüber Verbrauchern. Maßgeblich ist der Zweck des konkreten Vertrags, nicht der Gewerbeschein. Bei Dienstleistungen erlischt das Widerrufsrecht nach vollständiger Erbringung nur mit ausdrücklicher Zustimmung und bestätigtem Erlöschenshinweis (§ 356 Abs. 4 BGB).",
  [["Vertrag und AGB müssen abdecken: Leistungsumfang, Mitwirkung mit Frist und Folge, ", S], ["Abnahme mit Rügefrist und Eskalation, Zahlungsverzug und Mahnwesen", BL, true], [", Kündigung, Haftung bei Ausfall und Datenverlust, Nutzungsrechte an Bildern, Schriften ", S], ["und übernommenen Texten", BL, true], [", Herausgabe der Dateien bei Ende — auch bei unserer Betriebseinstellung.", S]],
  "Versicherung: Entscheidend ist die Vermögensschaden-/IT-Haftpflicht, nicht die Betriebshaftpflicht. Übliche Deckung 250.000 bis 500.000 €, für eine Zwei-Personen-GbR etwa 300 bis 700 € im Jahr.",
  "Künstlersozialabgabe: Beauftragen wir Texter, Fotografen oder Grafiker als Selbstständige, schuldet die GbR 4,9 % (Satz 2026) auf diese Honorare, Bagatellgrenze 450 € im Kalenderjahr.",
  [["KSK-Mitgliedschaft: Bei unserem Leistungsmix und der gewerblichen Einstufung ist eine Aufnahme unsicher, eine rückwirkende Aufhebung mit Beitragsnachforderung ein reales Risiko. Nachrangig prüfen.", R]],
  "Rentenversicherung: § 2 Satz 1 Nr. 9 SGB VI greift nur, wenn beide Merkmale zusammentreffen — kein versicherungspflichtiger Arbeitnehmer und dauerhaft im Wesentlichen nur ein Auftraggeber. Existenzgründer können sich bis zu drei Jahre befreien lassen (§ 6 Abs. 1a SGB VI).",
]));

/* ---- 14 Risiken ------------------------------------------------------- */
add(h("14 · Risiken", 1));
add(tabelle(
  ["Risiko", "Wirkung", "Gegenmaßnahme"],
  [
    ["Checks führen zu keinem Abschluss", "Modell trägt nicht", "Abbruchkriterien in 11; zuerst den Brief überarbeiten"],
    ["Produktionszeit deutlich über Plan", "Stundensatz kippt, besonders bei S", "Ist-Zeit ab Projekt 1 messen, Vorlage nach Projekt 3"],
    ["Zeitkapazität neben anderen Verpflichtungen", "Projekte bleiben liegen", "feste Wochentermine; Auftragsannahme begrenzen"],
    [[["Ausfall einer Person", BL]], [["Produktion steht komplett", BL]], [["schriftliche Bauanleitung, beidseitiger Zugriff", BL]]],
    [[["Kunde zahlt die Schlussrechnung nicht", BL]], [["60 % offen, Seite ist live", BL]], [["40 % Anzahlung; Mahnstufen im Vertrag; Zahlungsziel 14 Tage", BL]]],
    [[["E-Mail-Ausfall beim Domainumzug", BL]], [["Kunde verloren, keine Referenz", BL]], [["Verfahren in 7.1: MX sichern, Zeitfenster, Testmail", BL]]],
    ["Abmahnung wegen Werbung", "250–900 € plus Vertragsstrafe", [["nur Übergabe und Brief, Telefon erst danach, Sperrliste", BL]]],
    ["Persönliche Haftung der GbR", "Privatvermögen", "Vermögensschadenhaftpflicht, AGB mit Haftungsbegrenzung"],
    ["Kunde will die Seite selbst pflegen", "Einwand im Gespräch", [["offen benennen; künftig selbst bedienbare Felder (7.1)", BL]]],
    ["Abhängigkeit von Claude", "Produktion steht", "Repository und Dateien sind auch ohne Claude nutzbar"],
    ["Erster Pilotkunde springt ab", "keine Referenz", [["drei Piloten versetzt, aber alle drei beauftragt", BL]]],
  ],
  [2800, 2400, 3800]));

/* ---- 15 Meilensteine --------------------------------------------------- */
add(h("15 · Meilensteine", 1));
add(tabelle(
  ["Zeitraum", "Was fertig sein muss"],
  [
    [[["Vorlauf, Wochen −6 bis 0", BL]], [["Gesellschaftsvertrag · zwei Gewerbeanmeldungen · Domain und geschäftliche E-Mail · eigene Website · Vermögensschadenhaftpflicht · Entscheidung Formulardienst und Selbstbedienung · Vertrags- und Angebotsvorlage geprüft · Check-Vorlage mit Absenderangaben und Art.-14-Hinweis · Betriebsliste mit Sperrlisten-Spalte und Zeitprotokoll · verfügbare Wochenstunden schriftlich · Kapitalbedarf und Lebensunterhalt geklärt", BL]]],
    ["Tag 1–30", [["20 Checks übergeben (vier Touren) · erste Vorgespräche · Ist-Zeit je Check gemessen · alle drei Pilotkunden beauftragt, Bau von Projekt 1 begonnen", BL]]],
    ["Tag 30–60", [["Projekt 1 live und abgenommen · Projekte 2 und 3 im Bau, versetzt gestartet · Zeitprotokoll für Projekt 1 ausgewertet und in Projekt 2 übernommen · weitere 20 Checks", BL]]],
    ["Tag 60–90", "drei Pilotprojekte live und abgenommen · Produktionsvorlage abgeleitet · Referenzunterlagen vollständig · Prüfpunkte 1–5 und 11–13 automatisiert · Konzept gegen die Messwerte überarbeitet"],
  ],
  [2200, 6800]));

/* ---- 16 Dokumentation --------------------------------------------------- */
add(h("16 · Dokumentation und Lernprotokoll", 1));
add(liste([
  [["Betriebsliste: ", S, true], ["alle geprüften und angefragten Betriebe. Spalten: Name, Ort, Gewerk, Mitarbeiterzahl, ", S], ["erkennbarer Anlass", BL], [", gefundene Befunde, Datum der Übergabe, Datum des Anrufs, Ergebnis, ", S], ["Widerspruch ja/nein, Wiedervorlage", BL], [", nächster Schritt.", S]],
  "Zeitprotokoll je Projekt und je Check, nach Arbeitsschritt getrennt. Ohne diese Daten sind die Abschnitte 10 und 11 wertlos.",
  "Lernprotokoll: nach jedem Vorgespräch und jeder Absage ein Satz, was daraus folgt. Alle Startwerte werden monatlich dagegen geprüft.",
  [["Abgleich Konzept und Software: Fester Punkt im Wochentermin — stimmt der Katalog in pipeline/katalog.py noch mit Anhang A überein? Aus dieser fehlenden Schleife sind drei verschiedene Katalogfassungen entstanden.", BL]],
  [["Gültigkeitsregel: Jede Fassung trägt im Kopf, welche sie ersetzt. Überholte Fassungen werden gelöscht, nicht abgelegt.", BL]],
]));

/* ---- Anhang A ----------------------------------------------------------- */
add(new (require("docx").Paragraph)({ children: [new (require("docx").PageBreak)()] }));
add(h("Anhang A · Prüfkatalog, 19 Punkte", 1));
add(p([["Dies ist die Fassung, die auch die laufende Software umsetzt und auf der die bereits erzeugten Kundenpakete beruhen. Startwerte, keine Festlegung. Ein Befund entsteht nur bei sicherem Beleg, nie bei Verdacht.", BL]]));
add(p([["Spalte „Wer“: wir = zählt zur Definition of Done, null Befunde bei Auslieferung. Kunde = steht auf der Übergabeliste.", BL]]));
const kat = [
  ["1","Erreichbarkeit","HTTP-Status 4xx/5xx oder keine Antwort binnen 15 s","3","automatisch","wir"],
  ["2","HTTPS","kein HTTPS, ungültiges oder abgelaufenes Zertifikat, oder keine Weiterleitung von http auf https","3","automatisch","wir"],
  ["3","Mobiltauglichkeit","viewport-Angabe fehlt oder die Seite scrollt bei 390 px horizontal","3","automatisch","wir"],
  ["4","Ladezeit mobil","LCP über 4,0 s (Google: schlecht)","2","automatisch","wir"],
  ["5","Klickbare Telefonnummer","Nummer sichtbar, aber kein tel:-Link","2","automatisch","wir"],
  ["6","Kontaktweg","weder Formular noch mailto: noch tel: in zwei Klicks erreichbar","3","automatisch","wir*"],
  ["7","Impressum","Seite fehlt oder Name, Anschrift oder Kontaktweg fehlt","3","teils manuell","wir"],
  ["8","Aktualität","jüngste Jahreszahl liegt mehr als drei Jahre zurück","1","manuell, rückt nach","wir"],
  ["9","Karriereseite","kein Link auf Karriere, Jobs oder Stellen · nur Handwerk","2","automatisch","wir"],
  ["10","Formular","kein <form> auf der Startseite · nie blind absenden","1","automatisch, rückt nach","wir"],
  ["11","Seitentitel","title fehlt, ist leer oder trägt einen Vorlagenwert","2","automatisch","wir"],
  ["12","Meta-Description","fehlt oder kürzer als 50 Zeichen","2","automatisch","wir"],
  ["13","Eigene Domain","die Seite läuft auf einer Baukasten-Adresse","3","automatisch","Kunde"],
  ["14","Google-Unternehmensprofil","kein Profil, oder Adresse/Telefon weichen ab","3","manuell","Kunde"],
  ["15","Platzhalter- und Fremdtext","sichtbarer Vorlagen- oder fremdsprachiger Text","2","manuell","wir"],
  ["20","Speisekarte als Text · Gastro","die Karte ist nur als Bild oder PDF eingebunden","3","manuell","Kunde"],
  ["21","Bestell- oder Anfrageweg · Gastro","kein Weg, eine Bestellung oder Anfrage zu senden","2","automatisch","wir"],
  ["22","Bewerbungsweg · Handwerk","Karriereseite vorhanden, aber kein Bewerbungsweg","2","automatisch","wir"],
  ["23","Weg zur Mitgliedschaft · Verein","weder Formular noch benannter Ansprechpartner","2","manuell","wir"],
];
add(tabelle(["#","Prüfpunkt","Befund wenn","Grad","Erhebung","Wer"],
  kat.map(r => r.map(c => c)), [500, 2100, 3100, 600, 1400, 900]));
add(abstand());
add(p([["* Punkt 6 zählt zu unserer Verantwortung, sobald der Formulardienst entschieden ist. Bis dahin steht er auf der Übergabeliste.", BL]]));
add(p([["Auswahl für den Check: erst filtern — nur was das angebotene Paket behebt —, dann sortieren nach Schweregrad absteigend. Maximal vier auf dem Check. Ab drei Befunden gilt der Betrieb als Zielkunde. Punkte 8 und 10 rücken nur nach, wenn sonst weniger als vier Befunde vorliegen.", BL]]));
add(p([["Entschieden: Die Vorfassung hatte den Katalog auf 13 Punkte gekürzt — während Software, Kundenpakete und Firmenseite bei 19 blieben. 19 gilt, in dieser Nummerierung. Die beiden Einwände der Kürzung bleiben als Regeln erhalten: Aktualität erzeugt nur bei hartem Indiz einen Befund; ein fremdes Formular wird nie abgesendet.", BL]]));

/* ---- Anhang B ----------------------------------------------------------- */
add(h("Anhang B · Aufbau und Textregeln des Website-Checks", 1));
add(liste([
  [["Seite 1–2 — Befund, neutral. ", S, true], ["Bezug zum Betrieb in einem Satz. Dann maximal vier gemessene Befunde, je Befund: was gemessen wurde, der Wert, der Vergleichsmaßstab. Keine Wertung, keine Adjektive.", S]],
  [["Seite 3 — Ausblick und Preis. ", S, true], ["Was die Lösung praktisch bedeutet, unser Preisrahmen und die Umsetzungszeit. Ein Handlungsaufruf: ein unverbindliches Gespräch.", S]],
  [["Gestaltung. ", S, true], ["Zwei Farben aus der Bestandsseite abgeleitet, eine von drei Schriftvarianten nach Branche. Kein Kundenlogo.", S]],
  [["Absenderangaben vollständig auf jeder Ausfertigung: ", S, true], ["Name, ladungsfähige Anschrift, Telefon, geschäftliche E-Mail. Dazu der Datenschutzhinweis nach Art. 14 DSGVO.", S]],
  "Gemessene Fakten statt Bewertung. Keine Behauptung zur Umsatzsteigerung.",
  "Belegte Grundlage für das Ladezeit-Argument sind Googles Core Web Vitals (LCP bis 2,5 s gut, über 4 s schlecht). Die Zahl „53 % springen ab 3 Sekunden ab“ stammt von Google/SOASTA 2016/17 — nur mit Jahresangabe verwenden oder weglassen.",
  "Nur Mängel nennen, die das angebotene Paket auch behebt. Kein Marktvergleich auf dem Check.",
]));
add(p([["Blockiert alles — Kira und Yannik: Ladungsfähige Anschrift. § 5 DDG verlangt sie auf jedem geschäftlichen Dokument. Bis sie eingetragen ist, trägt jeder erzeugte Check einen roten Sperrbalken und darf nicht übergeben werden. Elf Pakete liegen fertig und warten nur darauf.", R]]));

/* ---- Anhang C ----------------------------------------------------------- */
add(h("Anhang C · Gründungs-Checkliste", 1));
add(p([["Jede Zeile hat Verantwortlichen und Frist — ohne beides gehört sie nicht in die Liste.", S]]));
const c = [
  [[["Ladungsfähige Anschrift festlegen und eintragen", R, true]], "beide", [["sofort", R]]],
  [[["Entscheiden, welche Telefonnummer gilt", R]], "beide", [["sofort", R]]],
  [[["Termin mit der Rechtsberatung in der Familie — mit festem Datum", BL]], "beide", [["Woche 1", BL]]],
  ["Schriftlicher GbR-Gesellschaftsvertrag, inkl. Kundenverträge bei Ausscheiden", "beide", "Vorlauf"],
  ["Gewerbeanmeldung je Gesellschafter", "beide", "Vorlauf"],
  ["Fragebogen zur steuerlichen Erfassung über ELSTER", "beide", "1 Monat nach Anmeldung"],
  ["Steuerberatung: § 19 UStG beibehalten oder verzichten", "Yannik", "Vorlauf"],
  ["Vermögensschaden-/IT-Haftpflicht — drei Angebote, abschließen", "Yannik", "Vorlauf"],
  [[["Wovon wir im ersten Jahr leben — schriftlich", R, true]], "beide", [["Vorlauf", R]]],
  ["webgewerk.com sichern, geschäftliche E-Mail einrichten", "Yannik", "sofort"],
  ["DPMA-Markenrecherche auf entgegenstehende Marken", "Yannik", "Vorlauf"],
  ["Eigene Website: besteht den Katalog in den Punkten, die wir steuern", "Kira", "Vorlauf"],
  [[["Entscheiden, was der Kunde selbst bedienen kann — zusammen mit dem Formulardienst", R]], "Kira", [["Vorlauf", R]]],
  ["Formulardienst mit EU-Serverstandort und AV-Vertrag auswählen", "Kira", "Vorlauf"],
  [[["Claude-Tarif prüfen: Vertrag nach Art. 28 DSGVO vorhanden?", R]], "Kira", [["vor erstem Pilotprojekt", R]]],
  ["Verzeichnis von Verarbeitungstätigkeiten anlegen (Art. 30)", "Kira", "Vorlauf"],
  [[["Vertrag und AGB vorformulieren und prüfen lassen — inkl. Abnahme mit Rügefrist, Eskalation, Mahnwesen, Rechte an übernommenen Texten", BL]], "Yannik", "Vorlauf"],
  [[["§ 7 UWG und die DSGVO-Kette bis Anthropic an eine Fachstelle geben, falls die Familienberatung dort nicht zu Hause ist", BL]], "Yannik", [["vor Tag 1", BL]]],
  ["Art.-14-Datenschutzhinweis als Beilage formulieren", "Yannik", "Vorlauf"],
  [[["Betriebsliste (mit Sperrlisten-Spalte und Wiedervorlage) und Zeitprotokoll anlegen", BL]], "beide", "Vorlauf"],
  [[["Verfügbare Wochenstunden, feste Tage und Uhrzeiten schriftlich", R, true]], "beide", [["Vorlauf", R]]],
  [[["Bauanleitung schreiben, damit Produktion nicht an einer Person hängt", BL]], "Kira", [["vor Tag 1", BL]]],
  [[["Wettbewerberpreise mit Quelle und Abrufdatum belegen", R]], "Yannik", [["vor erstem Angebot", R]]],
  [[["Belastbare Zahl zum Fachkräftemangel im Handwerk suchen", BL]], "beide", [["vor Tag 1", BL]]],
  [[["Zeigeerlaubnis für die Arbeitsproben einholen", BL]], "beide", [["vor Tag 1", BL]]],
  [[["Preis für einen halben Tag Fotoaufnahmen festlegen, Fotograf fragen", BL]], "Kira", [["vor erstem Angebot", BL]]],
  [[["Barrierefreiheit: Betroffenheit klären", R]], "Kira", [["vor erstem Angebot", R]]],
  ["E-Rechnungs-Empfang und revisionssichere Ablage einrichten", "Yannik", "vor erster Rechnung"],
  ["DRV-Statusklärung § 7a SGB IV, Befreiungsantrag § 6 Abs. 1a SGB VI", "beide", "binnen 3 Monaten"],
  ["Separates Konto für Steuerrücklage einrichten", "Yannik", "vor erster Rechnung"],
];
add(tabelle(["Aufgabe", "Wer", "Bis wann"], c, [5600, 1300, 2100]));

/* ---- Schreiben ----------------------------------------------------------- */
const doc = dokument(inhalt);
Packer.toBuffer(doc).then((buf) => {
  const ziel = path.join(__dirname, "Webgewerk-Unternehmenskonzept.docx");
  fs.writeFileSync(ziel, buf);
  console.log(ziel, Math.round(buf.length / 1024) + " KB,", inhalt.length, "Absätze");
});
