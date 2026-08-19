/* Aufgabenliste Webgewerk als Word-Datei.
 *
 * Regel dieser Fassung (Kira, 19.08.): Jede Zeile hat einen Verantwortlichen
 * und eine Frist. Ohne beides gehört sie nicht in die Liste. Zeilen ohne
 * Termin sind deshalb entweder mit einem Datum versehen oder gestrichen und
 * unten begründet worden.
 *
 * Der Inhalt steht in studie/aufgaben.json und wird von dieser Datei und von
 * studie/todo-bauen.js gelesen — damit Word-Fassung und HTML-Fassung nicht
 * auseinanderlaufen können.
 */
const B = require("./bauen.js");
const { SCHWARZ: S, ROT: R, BLAU: BL, p, h, titel, liste, tabelle, abstand,
        dokument, legende, Packer, fs, path } = B;

const daten = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "aufgaben.json"), "utf8"));

const FARBE = { S, R, BL };

const inhalt = [];
const add = (...x) => inhalt.push(...x.flat());

// Eine Aufgabenzeile: Kästchen, Wer, Bis wann, Aufgabe.
function aufgaben(zeilen) {
  return tabelle(["", "Wer", "Bis wann", "Aufgabe"],
    zeilen.map(([wer, frist, text, grund, farbe]) => {
      const f = FARBE[farbe] || S;
      const aufgabe = grund
        ? [[text + " ", f, true], ["— " + grund, f]]
        : [[text, f]];
      return ["☐", [[wer, f, true]], [[frist, f, true]], aufgabe];
    }),
    [420, 800, 1500, 6280]);
}

add(titel("Webgewerk — Was zu tun ist"));
add(p([["Stand " + daten.stand + " · zusammengeführt aus der Aufgabenliste vom 17.08. und der Terminliste aus dem Konzept. Diese Fassung ersetzt beide.", S]]));
add(p([["Jede Zeile hat einen Verantwortlichen und eine Frist. Was beides nicht hat, steht nicht drin.", S]]));
add(abstand());
add(legende());
add(p([["K = Kira · Y = Yannik · K+Y = beide · C = Claude", S]]));
add(abstand());

add(h("Der Anker: Tag 1", 1));
add(p([["Tag 1 ist der Tag, an dem der erste Check übergeben wird. Vorgeschlagen: " + daten.anker.tag1 + ". Tag 90 ist dann " + daten.anker.tag90 + ". Alle Fristen im Vorlauf hängen an diesem Datum — wird es verschoben, verschieben sich alle mit. Deshalb steht es selbst als erste Aufgabe in der Liste.", BL]]));
add(p([["Ein zweiter Anker ist die Gewerbeanmeldung (" + daten.anker.gruendung + "). An ihr hängen die ELSTER-Frist und die Frist für den Befreiungsantrag bei der Rentenversicherung.", BL]]));

for (const b of daten.bloecke) {
  add(h(b.titel, 1));
  if (b.vorspann) add(p([[b.vorspann, S]]));
  add(aufgaben(b.zeilen));
  add(abstand());
}

add(h("Aus der älteren Liste herausgefallen — und warum", 1));
add(p([["Damit niemand die alte Fassung sucht und die Zeilen vermisst.", S]]));
add(liste(daten.gestrichen.map(([was, warum]) => [[was + " ", BL, true], ["— " + warum, BL]])));
add(abstand());

add(h("Erledigt", 1));
add(liste(daten.erledigt));

const doc = dokument(inhalt);
Packer.toBuffer(doc).then((buf) => {
  const ziel = path.join(__dirname, "Webgewerk-Aufgabenliste.docx");
  fs.writeFileSync(ziel, buf);
  const n = daten.bloecke.reduce((a, b) => a + b.zeilen.length, 0);
  console.log(ziel, Math.round(buf.length / 1024) + " KB,", n, "Aufgaben");
});
