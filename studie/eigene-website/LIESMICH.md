# Die eigene Website

Ersetzt `studie/kd-webdesign/`. Gleiche Bauweise wie bei jedem Kundenprojekt:
`webroot/` wird hochgeladen, fertig.

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
3. **Telefonnummer und Betreuungspreis bestätigen** (0162 3242260, 69 €).
4. **Rechtstexte prüfen lassen.**

## Geprüft

PHP 8.4.19 und Chromium, in der Aufteilung, in der es hochgeladen wird:
alle vier Seiten und das Bild laden, Pflegebereich liest acht Felder und ein
Bild, Speichern ändert 12 Stellen und zieht 8 weitere auf den anderen Seiten
mit, ein Foto mit 3600 × 2400 wird zu 1600 × 1066, heller und dunkler Modus,
Handy ab 390 px, kein Konsolenfehler.
