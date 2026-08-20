# Word-Fassungen

    node studie/word/konzept.js
    node studie/word/todo.js

Erzeugt `KD-Webdesign-Unternehmenskonzept.docx` und `KD-Webdesign-Aufgabenliste.docx`.

Standard-Word-Optik: Calibri, die eingebauten Überschriftenformate, keine
Farbflächen. Wer die Datei öffnet, soll sie wie jedes andere Word-Dokument
bearbeiten können.

Farben im Text, Vorgabe vom 17.08.2026:

| Farbe | Bedeutung |
|---|---|
| Schwarz `000000` | geprüft und entschieden |
| Rot `C00000` | offen, muss besprochen werden, oder nicht optimal |
| Blau `0070C0` | im Gespräch vom 16./17.08.2026 neu hinzugekommen |

Das Blau ist dieselbe Stufe, die Kira in ihrem ursprünglichen Word-Dokument
für Ergänzungen benutzt hat.

**Die HTML-Fassungen bleiben die Quelle** (`studie/konzept.html`,
`studie/todo.html`). Wer inhaltlich etwas ändert, ändert es dort und in den
beiden Skripten hier — sonst laufen die Fassungen wieder auseinander, und
genau daraus sind drei verschiedene Prüfkataloge entstanden.

`node_modules/` ist nicht eingecheckt; bei Bedarf `npm install docx`.
