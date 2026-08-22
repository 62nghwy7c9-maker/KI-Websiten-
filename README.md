# KI-Websiten

Konzept und Pipeline für die Website-Check-Akquise.

## Dokumente

| Datei | Inhalt |
|---|---|
| `studie/word/KD-Webdesign-Unternehmenskonzept.docx` | Das Konzept. **Quelle der Wahrheit.** Erzeugt aus `studie/word/konzept.js`. |
| `Konzept.docx` | Kiras Ursprungsfassung vom 12.08. Nur noch als Beleg, nicht mehr bearbeiten. |
| `CLAUDE.md` | Masterprompt und Projekt-Brief für Claude Code |
| `studie/todo.html` | Die Aufgabenliste. Erzeugt aus `studie/aufgaben.json`. |
| `TODO.md` | Offene Punkte der Pipeline und der eigenen Firmenseite |
| `PLAN-90-TAGE.html` | Umsetzungsplan bis 09.11.2026, mit Abbruchkriterien |

Die HTML-Dateien im Browser öffnen und mit Strg+P als PDF speichern.

`KONZEPT-WEBDESIGN.md` und `.html` sind am 22.08. gelöscht worden. Das
Unternehmenskonzept erklärt sie ausdrücklich für ersetzt, und eine zweite,
ältere Fassung desselben Papiers führt nur dazu, dass jemand mit der
falschen arbeitet.

## Pipeline

Stufe 0 bis 4 aus dem Konzept. **Erzeugt Entwürfe, versendet nie selbst.**

```
pipeline/katalog.py    Prüfkatalog: Schwellwerte und Schweregrade. Nur Daten.
pipeline/modelle.py    Datenmodell — der eingefrorene Vertrag zwischen den Stufen
pipeline/register.py   Kontakt-Register (CSV, route-Feld, Dedup)
pipeline/messung.py    Stufe 1: misst eine Website, liefert Rohfakten
pipeline/cli.py        Kommandozeile
schemas/               JSON-Schema des Prüfberichts
fixtures/gophai/       gespeicherte Testseite, damit Tests ohne Netz laufen
```

### Benutzen

```bash
python -m pipeline messen --url elektro-mueller.de \
    --firma "Elektro Müller" --ort Kerpen --branche handwerk

python -m pipeline register      # Stand des Kontakt-Registers
```

Für die Ladezeit zusätzlich `--psi --psi-key <Schlüssel>`
(Schlüssel: Google Cloud Console, PageSpeed Insights API).

### Testen

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

Die Laufzeit selbst braucht nur Python 3.11 und die Standardbibliothek —
sie läuft auf jedem Rechner ohne Installation.

## Was nicht im Repo liegt

`register/*.csv` und `out/*.json` sind absichtlich ausgeschlossen. Dort stehen
Kontaktdaten angesprochener Betriebe; die gehören nicht in ein Git-Repository.
Sie leben auf dem Rechner, auf dem gearbeitet wird.

## Stand

- **M0** Datenmodell, Register, Schema — fertig
- **M1** Stufe 1, automatische Prüfpunkte — fertig, gegen Gophai geprüft
- **M2** Befundbildung und Auswahl — offen
- **M3** Check-Renderer — braucht die Absenderangaben (Anschrift, Telefon)
- **M4** Anschreiben plus Freigabe-Gate — offen
