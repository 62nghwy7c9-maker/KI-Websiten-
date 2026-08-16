/* Erzeugt die beiden Arbeitsdokumente als Word-Dateien.
 *
 *   node studie/word/bauen.js
 *
 * Bewusst Standard-Word-Optik: Calibri, die eingebauten Überschriften,
 * keine Farbflächen, keine Rahmen außer in Tabellen. Wer das Dokument
 * öffnet, soll es wie jedes andere Word-Dokument bearbeiten können.
 *
 * Farben im Text (Vorgabe vom 17.08.2026):
 *   schwarz  geprüft und entschieden
 *   rot      offen, muss besprochen werden, oder nicht optimal
 *   blau     in diesem Gespräch neu hinzugekommen
 */
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  LevelFormat, PageBreak,
} = require("docx");
const fs = require("fs");
const path = require("path");

const SCHWARZ = "000000";
const ROT = "C00000";     // Word-Standardrot
const BLAU = "0070C0";    // dieselbe Blaustufe wie in Kiras Ursprungsdokument

/* ---- Bausteine ---------------------------------------------------- */

// Ein Absatz. Text kann ein String sein oder eine Liste [text, farbe, fett].
function p(inhalt, opt = {}) {
  const stuecke = Array.isArray(inhalt) ? inhalt : [[inhalt, opt.farbe || SCHWARZ]];
  return new Paragraph({
    spacing: { after: opt.eng ? 60 : 160, line: 276 },
    indent: opt.einzug ? { left: 360 } : undefined,
    alignment: opt.mitte ? AlignmentType.CENTER : undefined,
    children: stuecke.map(([t, farbe, fett]) => new TextRun({
      text: t, color: farbe || SCHWARZ, bold: !!fett,
      italics: !!opt.kursiv, size: opt.klein ? 18 : 22,
    })),
  });
}

function h(text, stufe, farbe) {
  const grade = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3];
  return new Paragraph({
    heading: grade[stufe - 1],
    spacing: { before: stufe === 1 ? 320 : 260, after: 120 },
    children: [new TextRun({ text, color: farbe || SCHWARZ })],
  });
}

function titel(text) {
  return new Paragraph({
    heading: HeadingLevel.TITLE,
    spacing: { after: 120 },
    children: [new TextRun({ text, color: SCHWARZ })],
  });
}

// Aufzählung. Jeder Eintrag: String oder [text, farbe] oder Liste von Stücken.
function liste(eintraege, farbeStandard) {
  return eintraege.map((e) => {
    let stuecke;
    if (typeof e === "string") stuecke = [[e, farbeStandard || SCHWARZ]];
    else if (typeof e[0] === "string" && (e.length === 1 || typeof e[1] === "string"))
      stuecke = [[e[0], e[1] || farbeStandard || SCHWARZ]];
    else stuecke = e;
    return new Paragraph({
      numbering: { reference: "punkte", level: 0 },
      spacing: { after: 80, line: 276 },
      children: stuecke.map(([t, farbe, fett]) => new TextRun({
        text: t, color: farbe || farbeStandard || SCHWARZ, bold: !!fett, size: 22,
      })),
    });
  });
}

function zelle(inhalt, breite, kopf, farbe) {
  const stuecke = Array.isArray(inhalt) ? inhalt : [[inhalt, farbe || SCHWARZ]];
  return new TableCell({
    width: { size: breite, type: WidthType.DXA },
    shading: kopf ? { type: ShadingType.CLEAR, fill: "F2F2F2" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({
      spacing: { after: 0, line: 260 },
      children: stuecke.map(([t, f, fett]) => new TextRun({
        text: t, color: f || SCHWARZ, bold: kopf || !!fett, size: 20,
      })),
    })],
  });
}

function tabelle(kopf, zeilen, breiten) {
  const gesamt = breiten.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: gesamt, type: WidthType.DXA },
    columnWidths: breiten,
    rows: [
      new TableRow({
        tableHeader: true,
        children: kopf.map((t, i) => zelle(t, breiten[i], true)),
      }),
      ...zeilen.map((z) => new TableRow({
        children: z.map((t, i) => zelle(t, breiten[i], false)),
      })),
    ],
  });
}

function abstand() { return new Paragraph({ spacing: { after: 120 }, children: [] }); }

const NUMMERIERUNG = {
  config: [{
    reference: "punkte",
    levels: [{
      level: 0, format: LevelFormat.BULLET, text: "•",
      alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 360, hanging: 200 } } },
    }],
  }],
};

function dokument(kinder) {
  return new Document({
    numbering: NUMMERIERUNG,
    styles: {
      default: {
        document: { run: { font: "Calibri", size: 22 }, paragraph: { spacing: { line: 276 } } },
      },
    },
    sections: [{
      properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
      children: kinder,
    }],
  });
}

/* ---- Legende, in beiden Dokumenten gleich -------------------------- */
function legende() {
  return [
    p([["Farben in diesem Dokument: ", SCHWARZ, true]]),
    ...liste([
      [["Schwarz", SCHWARZ, true], [" — geprüft und entschieden.", SCHWARZ]],
      [["Rot", ROT, true], [" — offen, muss besprochen werden, oder nicht optimal.", ROT]],
      [["Blau", BLAU, true], [" — im Gespräch vom 16./17.08.2026 neu hinzugekommen.", BLAU]],
    ]),
    abstand(),
  ];
}

module.exports = {
  SCHWARZ, ROT, BLAU, p, h, titel, liste, tabelle, abstand, dokument, legende,
  Packer, Paragraph, PageBreak, TextRun, fs, path,
};
