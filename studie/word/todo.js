/* Die Todo-Liste als Word-Datei — eine Seite Papier, keine Tabellen.
 *
 * Kira, 19.08.: „Ich will eine einfache Todo-Liste, die mir genau sagt, was
 * ich noch tun muss." Deshalb steht hier nur das: eine Zeile je Aufgabe, mit
 * Namen und Datum. Kein Grund, keine Quelle, keine Farben, keine Tabellen.
 *
 * Warum das kein Verlust ist: Das Warum steht im Unternehmenskonzept, und
 * zwar an der Stelle, an der es hingehört. Wer hier eine Zeile nicht
 * versteht, schlägt dort nach — muss es aber beim Abhaken nicht lesen.
 *
 * Aufgaben, die Claude erledigt, stehen nicht drin. Sie sind keine Arbeit
 * für Kira und Yannik und machen die Liste nur länger.
 *
 * Inhalt: studie/aufgaben.json — dieselbe Datei wie für alles andere.
 */
const B = require("./bauen.js");
const { SCHWARZ: S, p, h, titel, dokument, Packer, fs, path } = B;
const { Paragraph, TextRun, AlignmentType } = require("docx");

const d = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "aufgaben.json"), "utf8"));

const NAME = { K: "Kira", Y: "Yannik", "K+Y": "beide" };

// Eine Aufgabenzeile: Kästchen, Aufgabe, dahinter Wer und Wann.
function zeile(text, wer, frist) {
  return new Paragraph({
    spacing: { after: 100, line: 264 },
    indent: { left: 340, hanging: 340 },
    children: [
      new TextRun({ text: "☐   ", color: S, size: 22 }),
      new TextRun({ text: text, color: S, size: 22 }),
      new TextRun({ text: `   (${wer}, ${frist})`, color: S, size: 20 }),
    ],
  });
}

function kurzfassung(text) {
  if (d.kurz && d.kurz[text]) return d.kurz[text];
  return text.length > 85 ? text.split(" — ")[0] : text;
}

const inhalt = [];
const add = (...x) => inhalt.push(...x.flat());

add(titel("Was ich noch tun muss"));
add(p([["Webgewerk · Stand " + d.stand + " · eine Zeile je Aufgabe, mit Namen und Datum.", S]]));
add(p([["Warum eine Aufgabe drinsteht, steht im Unternehmenskonzept. Zum Abhaken braucht man es nicht.", S]]));

let gesamt = 0;
for (const block of d.bloecke) {
  const zeilen = block.zeilen.filter((z) => z[0] !== "C");
  if (!zeilen.length) continue;
  add(h(block.titel.split(" — ")[0], 1));
  for (const z of zeilen) {
    add(zeile(kurzfassung(z[2]), NAME[z[0]] || z[0], z[1]));
    gesamt++;
  }
}

add(h("Zuerst", 1));
add(p([["Die ladungsfähige Anschrift. Ohne sie trägt jeder Check einen roten Sperrbalken und darf nicht übergeben werden — elf fertige Pakete warten nur darauf. Es ist eine Entscheidung, keine Recherche.", S]]));

const doc = dokument(inhalt);
Packer.toBuffer(doc).then((buf) => {
  const ziel = path.join(__dirname, "Webgewerk-Todo.docx");
  fs.writeFileSync(ziel, buf);
  console.log(ziel, Math.round(buf.length / 1024) + " KB,", gesamt, "Aufgaben");
});
