/* Die Todo-Liste als Word-Datei — eine Seite Papier, keine Tabellen.
 *
 * Kira, 19.08.: „Ich will eine einfache Todo-Liste, die mir genau sagt, was
 * ich noch tun muss." Und danach: „Ohne Datum, nur Reihenfolge."
 *
 * Deshalb eine einzige durchnummerierte Liste. Was oben steht, kommt zuerst.
 * Kein Datum, kein Grund, keine Farben, keine Tabellen, keine Abschnitte.
 * Die Termine stehen weiter in aufgaben.json — sie stehen nur nicht mehr auf
 * dem Blatt, das abgehakt wird.
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

// Eine Aufgabenzeile: Nummer, Kästchen, Aufgabe, dahinter der Name.
function zeile(nr, text, wer, wann) {
  const kinder = [
    new TextRun({ text: String(nr).padStart(2, " ") + ".  ", color: S, size: 22 }),
    new TextRun({ text: "☐   ", color: S, size: 22 }),
    new TextRun({ text: text, color: S, size: 22 }),
  ];
  // Nur die Aufgaben, die an einem Ereignis hängen, tragen noch einen
  // Zusatz — bei ihnen ist die Reihenfolge allein keine Anweisung.
  if (wann) kinder.push(new TextRun({ text: ` (${wann})`, color: S, size: 20 }));
  kinder.push(new TextRun({ text: `   · ${wer}`, color: S, size: 20 }));
  return new Paragraph({
    spacing: { after: 100, line: 264 },
    indent: { left: 560, hanging: 560 },
    children: kinder,
  });
}

/* Aus der Frist wird der Auslöser — oder nichts.
 * Ein reines Datum fällt weg. „vor der ersten Rechnung" bleibt, weil es
 * keine Frist ist, sondern die Bedingung, unter der die Aufgabe ansteht. */
function auslöser(frist) {
  if (/^\d{2}\.\d{2}\.$/.test(frist)) return "";
  return frist
    .replace(/,? *spätestens \d{2}\.\d{2}\.?/, "")
    .replace(/ ab \d{2}\.\d{2}\.?/, "")
    .trim();
}

function kurzfassung(text) {
  if (d.kurz && d.kurz[text]) return d.kurz[text];
  return text.length > 85 ? text.split(" — ")[0] : text;
}

const inhalt = [];
const add = (...x) => inhalt.push(...x.flat());

add(titel("Was ich noch tun muss"));
add(p([["K&D Webdesign · Stand " + d.stand + " · in der Reihenfolge, in der es gemacht wird.", S]]));
add(p([["Von oben nach unten. Was weiter unten steht, setzt meistens etwas weiter oben voraus. Warum eine Aufgabe drinsteht, steht im Unternehmenskonzept — zum Abhaken braucht man es nicht.", S]]));

let nr = 0;
for (const block of d.bloecke) {
  for (const z of block.zeilen) {
    if (z[0] === "C") continue;
    nr++;
    add(zeile(nr, kurzfassung(z[2]), NAME[z[0]] || z[0], auslöser(z[1])));
  }
}
const gesamt = nr;

add(p([["", S]]));
add(p([["Nummer 1 ist die einzige, die wirklich eilt: Ohne die ladungsfähige Anschrift darf keiner der elf fertigen Checks das Haus verlassen.", S]]));

const doc = dokument(inhalt);
Packer.toBuffer(doc).then((buf) => {
  const ziel = path.join(__dirname, "KD-Webdesign-Todo.docx");
  fs.writeFileSync(ziel, buf);
  console.log(ziel, Math.round(buf.length / 1024) + " KB,", gesamt, "Aufgaben");
});
