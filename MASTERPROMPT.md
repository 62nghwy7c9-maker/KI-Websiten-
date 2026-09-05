# Auftrag: Websites verkaufen, viele und schnell

Dieser Text ist der Einstieg in einen neuen Chat. Er trennt drei Dinge streng
voneinander, damit nichts durcheinandergeht:

- **Was Kira will.** Ihre Worte, ihre Entscheidung.
- **Was schon da ist.** Nachprüfbar im Repo.
- **Was offen ist.** Fragen, keine Antworten.

Was hier nicht steht, ist nicht entschieden. Nichts hinzudichten.

---

## 1 · Was Kira will

**Ziel:** Erst einmal so viele Kunden wie möglich und so viele Websites wie
möglich in möglichst kurzer Zeit verkaufen.

**Ausdrücklich nicht:** eine nachhaltige Markenlaufbahn aufbauen. Das kommt
später, jetzt nicht.

## 2 · Ihre zwei Startwege

### Weg 1 · Die Kontakte ihres Vaters

Kira liefert später eine **Leadliste** mit Kontakten. Aufgabe: daraus die
herausfiltern, bei denen es sich anbietet. Die gefilterten zeigt sie ihrem
Vater. Danach werden diese Leute angesprochen, entweder von ihr oder von
ihrem Vater.

Die Liste liegt noch nicht vor. Ohne sie ist dieser Weg blockiert.

### Weg 2 · Eine Website für ihre Schule

Kira könnte für ihre Schule eine Website bauen. Mehr hat sie dazu nicht
gesagt. Fragen dazu stehen unter Punkt 5.

---

## 3 · Was schon da ist

Repo `62nghwy7c9-maker/ki-websiten-`, Branch
`claude/sparring-ki-websites-dach-xdb9xc`.

**Erster Befehl in jeder Sitzung:**

```
python -m pipeline kunde stand
```

Sagt für jeden Betrieb die Stufe, das Nächste und den fertigen Befehl.

**Die Kette läuft.** Von der Messung einer fremden Website bis zur Übergabe
der neuen:

```
python -m pipeline finden --ort <ort> --branche handwerk
python -m pipeline stapel --liste leads/<datei>.md
python -m pipeline pakete --slug <slug>
python -m pipeline kunde anlegen --slug <slug> --kurzname <name>
python -m pipeline kunde erhebung <name>
python -m pipeline kunde bauen <name>
python -m pipeline kunde pruefen <name>
python -m pipeline kunde packen <name>
```

Der vollständige Ablauf steht im Skill `.claude/skills/kundenweg/SKILL.md`
und greift bei allem, was mit einem Kunden zu tun hat, von selbst.

**Stand der Teile**

- 11 Betriebe gemessen, 11 Checks und Dossiers erzeugt
- 63 Tests grün
- **Czarnetzki** (Peter Czarnetzki Elektroinstallationen, Bergheim): der
  erste vollständige Entwurf, Stufe *gepackt, wartet auf Freigabe*. Prüfstand
  20 von 20, Selbsttest 19 von 19 auf einem echten PHP-Server. Er hat noch
  nicht zugesagt.
- Vorführseite liegt auf `webgewerk.42web.io/czarnetzki/`. Ob die dort
  aufgespielte Fassung aktuell ist, war beim Schreiben dieses Textes offen.
- Vier fertige Befunde sind nicht freigegeben: Sander-Bau, Lindam,
  Merzenich, Labau.

Alles Weitere zum Stand steht in `STAND.md`, die Architektur in `CLAUDE.md`.

---

## 4 · Was gilt

Diese Punkte sind nicht neu verhandelbar, sie stehen fest oder folgen aus dem
Gesetz.

**Kalte Werbemails an Betriebe brauchen nach § 7 Abs. 2 Nr. 2 UWG eine
Einwilligung, auch im B2B.** Postalische Werbung braucht sie nicht.
Telefonwerbung gegenüber Betrieben braucht wenigstens eine mutmaßliche
Einwilligung, und die Gerichte legen das eng aus. Wer eine Einwilligung hat,
muss sie im Streitfall beweisen können; dafür gibt es drei Spalten im
Register:

```
python -m pipeline register --einwilligung <schluessel> --durch "..." --wie "..."
python -m pipeline register        # zeigt unten die Liste MAIL ERLAUBT
```

**Nichts erfinden.** Keine Zahl, keine Frist, keine Quelle, kein Schwellwert,
keine Zusage über Dritte, die nicht geprüft ist.

**Entwürfe werden nie versendet.** Die Pipeline erzeugt Briefe, ein Mensch
verschickt sie.

**Keine Zugangsdaten in Dateien oder ins Repo.**

**Keine fremden Fotos von Menschen, kein Logo des Kunden.**

**Nichts Kundenspezifisches in `studie/pflege/`**, das ist die Vorlage.

**Keine Gedankenstriche** in Texten, Kommentaren und Code.

**Kurz antworten.** Kein unnötiger Text.

---

## 5 · Was offen ist

Nicht beantworten, sondern Kira fragen.

**Zur Leadliste**

- Nach welchen Kriterien soll gefiltert werden?
- Wie viele Kontakte sollen am Ende übrig bleiben?
- Hat ihr Vater zu diesen Betrieben eine Verbindung, oder ist das eine
  getrennte Liste?

**Zur Schulwebsite**

- Welche Schule, und gibt es dort schon eine Website?
- Wer entscheidet das an der Schule?
- Soll das bezahlt werden oder nicht?
- Was soll dabei herauskommen: Geld, ein Beispiel zum Herzeigen, oder etwas
  anderes?

**Zum Verkauf allgemein**

- Zu welchem Preis? Im Konzept stehen 990 € und 1.490 €, davon war zuletzt
  aber nicht mehr die Rede.
- Wird die Website vor dem Ja gebaut oder danach?
- Was ist im Preis enthalten und was nicht, besonders Hosting und Support?

**Weiterhin ungeklärt**

- Gewerbeanmeldung und Rechtsform. Im Impressum steht „Webgewerk GbR".
  Frage an IHK Köln oder Steuerberatung.
- `webgewerk.com` ist nicht registriert.
- Hoster: InfinityFree zeigt Seiten an, verschickt aber keine Mails und
  blockiert Prüfwerkzeuge.

---

## 6 · So anfangen

1. `python -m pipeline kunde stand`
2. `STAND.md` und `CLAUDE.md` lesen
3. Die Fragen aus Punkt 5 stellen, die für den nächsten Schritt nötig sind.
   Nicht alle auf einmal.

Vor allem Unumkehrbaren fragen: Domain umstellen, etwas an einen Kunden
schicken, Dateien auf einem Server löschen.
