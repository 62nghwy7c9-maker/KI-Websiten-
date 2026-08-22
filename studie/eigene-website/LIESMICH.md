# Die eigene Website

Gleiche Bauweise wie bei jedem Kundenprojekt: `webroot/` wird hochgeladen,
fertig.

**Kein Pflegebereich.** Diese Seite pflegen wir selbst, direkt in den
Dateien. Ein Login auf der eigenen Seite wäre eine Angriffsfläche ohne
Gegenwert. Der Bereich ist etwas, das wir verkaufen, nicht etwas, das wir
brauchen. Vom Formular bleibt `formular.php`, es hängt an nichts anderem.

## Gestaltung

Richtung übernommen von **sanity.io/context** (angesehen am 21.08.2026):
sehr helle Fläche, sehr große und eng gesetzte Überschriften, ein einziger
warmer Akzent, ein Punktraster als einziges grafisches Motiv, viel Luft
zwischen den Abschnitten, abwechselnd links und rechts gesetzte Zeilen,
Pfeillinks, Fragen als Ausklapper.

**Übernommen ist die Gestaltungssprache, sonst nichts.** Kein Code, kein
Text, kein Bild, keine Schrift von dort. Das Punktraster ist ein
`radial-gradient` aus drei Zeilen CSS, die Schriften sind Systemschriften.
Das ist der Unterschied zwischen einer Gestaltungsrichtung und einer Kopie —
und er ist wichtig, weil wir mit derselben Frage bei Kunden zu tun haben
werden.

## Der Name

Ausgeliefert wird **Moewes & Dettmer**. Der Name steht in einem Feld des
Pflegebereichs: Ein anderer Name ist eine Eingabe und ein Klick, keine
Umbauaktion. Geprüft — beim Ändern des Feldes werden alle 20 Stellen auf
allen vier Seiten mitgezogen.

Zur Entscheidung, Stand 21.08.2026:

| | dafür | dagegen |
|---|---|---|
| **Moewes & Dettmer** | frei als Domain, unverwechselbar, zwei haftende Menschen — genau das Verkaufsargument | sagt nicht, was wir tun; braucht die Zeile darunter |
| **Webgewerk** | sagt, was wir tun, gut zu merken | **webgewerk.de ist vergeben** (geprüft am 21.08., geparkt bei offline@i-mem.net); „Gewerk" heißt Handwerk, die Zielgruppe ist breiter |
| **K&D Webagentur** | neutral | zwei Buchstaben sagen nichts und sind nicht suchbar; „Webagentur" ist die Schublade, gegen die das ganze Konzept argumentiert |

## Was noch fehlt

1. **Ladungsfähige Anschrift** — Impressum und Datenschutz tragen
   `[Straße und Hausnummer]`, der rote Kasten weist darauf hin. Ohne sie
   darf die Seite nicht online.
2. **Domain und E-Mail** — `moewes-dettmer.de` hatte am 21.08. keinen
   DNS-Eintrag; das ist ein Hinweis, kein Beleg. Bei DENIC prüfen.
   Zusätzlich `moewes-dettmer.com` und die Schreibweise mit `ö` sichern —
   den Namen wird man am Telefon buchstabieren müssen.
3. **Telefonnummer bestätigen** (0162 3242260).
4. **Rechtstexte prüfen lassen.**

## Bewegung

Vier Regeln, damit es nicht nach Effekt aussieht:

1. Nichts bewegt sich von selbst. Alles hängt an einer Handlung des
   Besuchers: scrollen, zeigen, aufklappen.
2. Nichts wiederholt sich. Was eingeblendet ist, bleibt.
3. Kurz, zwischen 200 und 600 Millisekunden.
4. Wer im Betriebssystem weniger Bewegung eingestellt hat, bekommt keine.

Im Einzelnen: der Prüfvorgang im Aufmacher, das Punktraster zieht beim
Scrollen leicht mit, Abschnitte blenden beim Erreichen ein, Listen und
Karten gestaffelt mit 34 Millisekunden Abstand, die beiden Zahlen im
Streifen zählen einmal hoch, die Kopfleiste setzt sich beim Scrollen ab,
Karten heben sich unter dem Zeiger, Antworten im Fragenblock klappen auf.

Rund 60 Zeilen JavaScript. Keine Bibliothek, kein Bild, keine Schrift von
fremden Servern.

## Geprüft

PHP 8.4.19 und Chromium, in der Aufteilung, in der hochgeladen wird:

- Alle vier Seiten und das Bild laden.
- Prüfvorgang bei 0, 50 und 100 Prozent Scrollweg: 0, 3 und 7 Befunde.
- Zahlen zählen auf 19 und 990.
- Staffelung mit 0 / 34 / 68 / 102 Millisekunden.
- Kopfleiste schaltet ab 8 Pixel Scrollweg.
- `prefers-reduced-motion` zeigt alles fertig und ohne Bewegung.
- Ohne JavaScript ist die Seite vollständig da.
- Zehn Breiten von 320 bis 2560 ohne Querscrollen, heller und dunkler
  Modus, kein Konsolenfehler.
