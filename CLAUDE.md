# Masterprompt & Projekt-Brief — Website-Check-Pipeline

**Für Claude Code.** Lege diese Datei als `CLAUDE.md` bzw. Projekt-Brief ins Repo-Root. Sie ist die Quelle der Wahrheit: zuerst das Konzept mit den offenen Entscheidungen schließen, dann die Pipeline in Phasen bauen.

---

## 1 · Deine Rolle & Auftrag

Du bist mein Engineering-Partner für eine KI-Websiteagentur. Wir gewinnen kleine Betriebe (Handwerk, Gastro, Vereine im DACH-Raum), indem wir ihre bestehende Website automatisiert prüfen, einen neutralen **Website-Check** erstellen und per Mail zusenden. Zwei Aufträge, in dieser Reihenfolge:

1. **Konzept fertigstellen** — die offenen Entscheidungen (Abschnitt 9) mit mir klären, *bevor* Code entsteht. Frag mich, wenn etwas offen ist. Rate oder erfinde nichts.
2. **Pipeline bauen** — nach der Architektur (Abschnitt 3) in den Milestones (Abschnitt 11).

### Arbeitsregeln (verbindlich)

- **Plan-first.** Artefakt-Formate (Abschnitt 5) einfrieren, bevor du eine Stufe codest. Das Format ist der Vertrag zwischen den Stufen.
- **Nichts erfinden.** Keine Zahlen, Quellen, APIs oder Schwellwerte behaupten. Unsicheres als „zu verifizieren" markieren und mich fragen.
- **Keine Benchmark-Zahl ohne belegte Quelle.** Jede „Was es kostet"-Aussage im Check muss eine geprüfte Quelle haben (Abmahnrisiko §7 UWG). Ohne Quelle → Platzhalter, nicht raten.
- **Keine Umsatzversprechen** im Check oder in der Mail — nicht abschätzbar, rechtlich riskant.
- **Harter Mensch-Gate vor jedem Versand.** Die Pipeline erzeugt *Entwürfe*, sendet nie selbst.
- **Gegen Gophai Thai als Fixture testen.** Jede Stufe an diesem realen Beispiel prüfen (Daten in Abschnitt 12).
- Widersprich mir direkt, wenn ein Weg klar besser ist. Begründet, ohne Abfederung.

---

## 2 · Zielbild & Systemgrenze

**In einem Satz:** Aus einer Firmen-URL wird automatisiert ein qualifizierter, neutral formulierter, gebrandeter Website-Check plus Anschreiben-Entwurf — bis zum Punkt, an dem ein Mensch freigibt und sendet.

**In Scope (diese Pipeline):** Kandidat einlesen → Website messen → Befund → Check-Artefakt → Anschreiben-Entwurf → Freigabe-Gate.

**Out of Scope (bleibt manuell):** Vorstellungsgespräch, Vertrag, Beratung, Website-Produktion. Nicht bauen.

**Mockup** ist **nicht** Teil der Erstmail, sondern eine separate, nachgelagerte Stufe für *interessierte* Leads (Phase B, Abschnitt 7). Begründung: das Mockup ist teuer (Handarbeit) und rechtlich heikel (fremdes Logo/Farben) — es gehört nicht in den massenhaften Kaltversand, sondern ins Gespräch nach erkennbarem Interesse.

---

## 3 · Architektur

**Phase A — automatisiert bis zum Gate, für jeden Kandidaten:**

```
Stufe 0  Kandidat & Eingang   → Firma, URL, Branche, Ort, Kontakt-Mail
         Vorfilter: Ausschlusskriterien + Dedup gegen Kontakt-Register
Stufe 1  Messung              → Prüfkatalog gegen die URL, Rohfakten je Prüfpunkt
Stufe 2  Befund               → Schwellwerte/Gewichte anwenden, Auswahl (Abschnitt 6)
                                Output: Befund-Artefakt (JSON)
Stufe 3  Check-Artefakt       → gebrandeter Check (HTML → PDF) aus dem Befund
Stufe 4  Anschreiben          → Mail-Entwurf, verweist auf den Check, ein CTA
         ── GATE: Mensch prüft & gibt frei ──  → Versand (manuell/halbautomatisch)
```

**Phase B — pro interessiertem Lead, nach Antwort:**

```
Reply → Mockup (Handarbeit, rechtlich gegated) → Vorbereitung Vorstellungsgespräch
```

Jede Stufe hat: **Eingang** (definiertes Format), **Ausgabe-Artefakt** (fixes Format), **Gate** (was geprüft wird, bevor es weitergeht).

---

## 4 · Prüfkatalog (Stufe 1/2)

Das ist das Herz. Aktuell existiert nur die Stichwortliste — sie muss zur messbaren Spezifikation werden. Fülle Schwellwerte und Belege **gemeinsam mit mir**; unten mein Vorschlag, markiert wo zu verifizieren.

**Spalten je Prüfpunkt:** was gemessen · Methode/Quelle · auto/manuell · Befund-Auslöser (Schwelle) · Schweregrad (1–3) · Benchmark/Beleg für die „Was es kostet"-Aussage.

### Kern (branchenübergreifend)

| # | Prüfpunkt | Methode / Quelle | Auto? | Befund-Auslöser (Vorschlag) | Beleg-Status |
|---|-----------|------------------|-------|------------------------------|--------------|
| 1 | Erreichbarkeit | HTTP-Status, Fetch | auto | Seite nicht erreichbar / 4xx/5xx | belegbar |
| 2 | HTTPS | Zertifikat + Redirect auf https | auto | kein gültiges HTTPS | belegbar |
| 3 | Mobiltauglichkeit | `viewport`-Meta + Lighthouse Mobile | auto* | nicht responsive / Lighthouse-Mobile schwach | *verifizieren |
| 4 | Ladezeit (mobil) | PageSpeed Insights API (LCP) | auto | LCP > 2,5 s „verbesserungswürdig", > 4 s „schlecht" (Google Core Web Vitals) | Schwelle belegt; Kosten-Satz zu belegen |
| 5 | Klickbare Telefonnummer | `tel:`-Link vorhanden | auto | keine klickbare Nummer auf Mobil | belegbar |
| 6 | Kontaktweg | Formular / Mail / Telefon sichtbar | auto+ | kein klarer Kontaktweg | belegbar |
| 7 | Impressum | Vorhanden + Pflichtfelder §5 DDG | auto (Existenz) / manuell (Vollständigkeit) | fehlt/unvollständig/widersprüchlich | belegbar |
| 8 | Aktualität | **schwer objektiv messbar** — Copyright-Jahr, letzte sichtbare Änderung | manuell/Heuristik | nur mit belegbarem Indiz nutzen | heikel — als Urteil markieren |
| 9 | Karriereseite | Existenz „Jobs/Karriere" | auto+ | keine (v. a. Handwerk: Mitarbeitergewinnung) | belegbar |
| 10 | Funktionierendes Formular | Vorhandensein prüfen; **nicht** blind absenden | manuell | Formular fehlt/fehlerhaft | belegbar |
| 11 | Seitentitel | `<title>` vorhanden, kein Vorlagen-Default | auto | leer/Default/„Startseite" | belegbar |
| 12 | Meta-Description | vorhanden, sinnvoll | auto | fehlt → leere Google-Vorschau | belegbar |
| 13 | Eigene Domain | keine Baukasten-Subdomain (…metro.bar o. ä.) | auto | Fremdadresse statt eigener Domain | belegbar |
| 14 | Local SEO / GEO | Google-Unternehmensprofil vorhanden, NAP konsistent | manuell/API* | kein Profil / widersprüchliche Daten | *verifizieren |
| 15 | Platzhalter/Fremdtext | Heuristik + Sichtprüfung | manuell | sichtbarer Vorlagen-/Fremdtext | belegbar (Einzelfall) |

### Branchen-Zusatz

| Branche | Prüfpunkt | Auslöser |
|---------|-----------|----------|
| Gastro | Speisekarte als echter Text (nicht Bild/PDF) | Karte nur als Bild → für Google unlesbar |
| Gastro | Online-Bestellung / Catering-Anfrage möglich | kein Bestell-/Anfrageweg |
| Handwerk | Karriere-/Bewerbungsweg | fehlt (Fokus Mitarbeitergewinnung) |
| Verein | Mitglieds-/Kontaktweg, emotionale Ansprache | fehlt |

**Scoring-Regeln:** Schweregrad 1–3 je Prüfpunkt. Ein „Befund" entsteht nur, wenn der Auslöser sicher belegbar ist (kein Verdacht). `Aktualität` und `Formular` sind Urteilspunkte → nur mit konkretem Indiz einsetzen.

---

## 5 · Artefakt-Formate (einfrieren vor Code)

### Befund-Artefakt (Ausgabe Stufe 2)

```json
{
  "kandidat": { "firma": "", "url": "", "branche": "", "ort": "", "kontakt_mail": "" },
  "stand": "YYYY-MM-DD",
  "messung": [
    { "id": 4, "pruefpunkt": "Ladezeit mobil", "wert": "LCP 4,8 s",
      "quelle": "PageSpeed Insights", "auto": true }
  ],
  "befunde": [
    { "id": 4, "titel": "", "beobachtung": "", "was_es_kostet": "",
      "beleg": "", "schweregrad": 3, "behebbarkeit": "hoch" }
  ],
  "qualifiziert": true,
  "auswahl_fuer_check": [2, 4, 3, 13, 5]
}
```

`beobachtung` = neutrale Tatsache. `was_es_kostet` = Konsequenz, **nur mit `beleg`**. Ohne Beleg kein Satz.

### Check-Artefakt (Ausgabe Stufe 3)

Format: **HTML → PDF**. Die Vorlage existiert bereits (das redesignte, minimal-editoriale Template — separat geliefert). Renderer nutzt dieses Template und füllt die 4–5 ausgewählten Befunde. Aufbau: Kopf (Betrieb/Stand) · nummerierte Befunde (Beobachtung + „Was es kostet") · Abschluss (positiver Ausblick, ein weicher CTA) · Fußzeile (Quelle/Stand). **Kein Preis** im Check.

### Anschreiben-Entwurf (Ausgabe Stufe 4)

Kurz. Aufbau: konkreter Bezug zum Betrieb (Hook, ein Satz, warum diese Firma) → Check als Anhang/Link → **genau ein CTA**: unverbindliches Gespräch. Neutraler Ton. Kein Umsatzversprechen. Kein Preis (kommt ins Gespräch).

---

## 6 · Auswahl- & Qualifikationslogik

Zwei Regeln, die im Konzept unter „Befunde" vermischt sind — trenne sie:

- **Qualifikation:** ≥ 3 belegte Befunde auf der *vollen* Messung → Kandidat lohnt sich. Sonst verwerfen.
- **Präsentationsdeckel:** max. 4–5 Befunde *auf dem Check* (nicht überladen).
- **Sortierregel** (welche 4–5 von vielen): nach `Schweregrad × Behebbarkeit`, absteigend. Bei Gleichstand: Punkte bevorzugen, die im Gespräch/Angebot ohnehin gelöst werden. **Nur Probleme zeigen, die wir auch beheben.**

---

## 7 · Mockup (Phase B) — noch zu entscheiden

Nicht in der Erstmail. Ablauf: erst **drei Mockups von Hand** bauen, echten Zeitaufwand messen *und festhalten, was zwischen den dreien variiert* — die Vorlage muss genau diese Varianz auffangen. Dann erst eine Vorlage ableiten. Offen (mit mir klären): was zeigt das Mockup (überarbeitete Startseite?), Fidelity, Anzahl, Format — und die rechtliche Kernfrage: **echtes Kundenlogo/-farben ja/nein** (Abschnitt 10).

---

## 8 · Gates & Zustand

**Mensch-Gates:** (a) nach Befund, vor Check-Aufwand — Qualifikation bestätigen; (b) **hart vor Versand** — Freigabe (UWG); (c) Phase B: Mockup-Freigabe.

**Register/Zustand (bauen):**

- **Kontakt-Register** — jeder angeschriebene Betrieb, mit Datum. Stufe 0 prüft dagegen (Ausschlusskriterium „bereits kontaktiert").
- **Kandidatenliste** — Quelle klären: manuelle Einzel-URL oder Batch aus Tabelle/DB.
- **Artefakt-Ablage** — Namensschema, z. B. `checks/{ort}_{firma}_{YYYY-MM}/`.
- **Lauf-Log** — welche Stufe, welches Ergebnis, für Nachvollzug.

---

## 9 · Offene Entscheidungen — ZUERST mit Kira klären

| ID | Entscheidung | Meine Empfehlung |
|----|--------------|------------------|
| D1 | Check-Branding: Agentur-Identität vs. Kundenmarke | **Agentur-Identität** (konsistent, wirkt seriöser). Kundenmarke gehört ins Mockup. Max. eine Akzentfarbe pro Kunde tauschen. |
| D2 | Mockup in Erstmail? | **Nein** — Phase B, nach Interesse. |
| D3 | Logo/Farben im Mockup rechtlich | Vor dem Skalieren klären (Anwaltstermin). |
| D4 | Check-Zustellung: PDF-Anhang / gehostete Seite / beides | **PDF-Anhang** als Standard, optional Link. |
| D5 | Auslöser: Einzel-URL vs. Batch | Für v1 **Einzel-URL**, Batch später. |
| D6 | Schwellwerte je Prüfpunkt final | Gemeinsam füllen (Abschnitt 4). |
| D7 | Benchmark-Quellen belegen | Vor erstem echten Versand. Ich kann recherchieren. |
| D8 | Mitarbeiter-Schwellen 5–50 | Annahme lt. Konzept, „nach 20 Gesprächen prüfen". |
| D9 | Welche Branche für v1? | **Eine** wählen (Gophai → Gastro liegt als Fixture vor). |

---

## 10 · Rechtliches (vor dem Skalieren, ein Anwaltstermin)

- §7 UWG: Kaltakquise per Mail an Unternehmen — Abmahnrisiko.
- Verwendung fremder Logos/Farben im Mockup — der eigentlich offene Punkt.
- Eigentum am Mockup, wenn kein Vertrag zustande kommt.
- Belegpflicht aller Benchmark-Aussagen im Check.
- Vertrag/AGB, Haftung, Impressum-/Datenschutz-Leistung — später, blockiert den Bau nicht.

---

## 11 · Bauplan / Milestones

| M | Inhalt | Fertig, wenn |
|---|--------|--------------|
| M0 | Repo, Datenmodell, Kontakt-Register | Befund-JSON-Schema steht, Register liest/schreibt |
| M1 | Stufe 1: Auto-Prüfpunkte (1–7, 11–13) an einer URL | Rohmessung für Gophai als JSON |
| M2 | Stufe 2: Befund + Auswahllogik | qualifizierter Befund mit 4–5 sortierten Punkten |
| M3 | Stufe 3: Check-Renderer (Template → PDF) | Gophai-Check reproduziert das gelieferte Design |
| M4 | Stufe 4: Anschreiben-Generator + Freigabe-Gate | Entwurf + Stopp vor Versand |
| M5 | Batch + Dedup übers Register | Liste → mehrere Checks, keine Dubletten |
| M6 | Phase B: Mockup-Workflow | nach D2/D3 |

**Erste baubare Scheibe:** M1 gegen Gophai Thai (Fixture unten). Repo grob:

```
/pipeline   stufen 0–4        /templates  check-template.html
/schemas    befund.json       /register   kontakte.(csv|sqlite)
/fixtures   gophai/           /out        checks/
```

---

## 12 · Wiederverwendung deines bestehenden Ordners (ausstehend)

Sobald der Ordner hochgeladen ist, prüfe ich gezielt auf Wiederverwendbarkeit: (1) Prüf-/Scraping-Logik → Stufe 1, (2) Prompt-Struktur → Stufe 2/4, (3) Check-Renderer → Stufe 3, (4) Datenmodell/Ablage, (5) Secrets/Keys sauber trennen. Kriterium: übernehmen nur, was ins fixe Artefakt-Format passt; sonst neu.

**Fixture Gophai Thai** (Gastro): URL `gophai-thaiimbiss.metro.bar`, Ort Kerpen. Bekannte Befunde als Testfall: Fremdtext-Platzhalter, Speisekarte nur als Bild, widersprüchliche Öffnungszeiten + falsche Impressum-Mail, keine eigene Domain + fehlende Meta-Description, kein Online-Bestellweg.

---

## 13 · Was ich (Kira) dir liefere / du mich fragst

- Ich lade den **bestehenden Pipeline-Ordner** hoch und gebe in Claude Code Zugang zu allen **bereits gebauten Websites**.
- Du klärst mit mir **D1–D9**, bevor du die betroffene Stufe baust.
- Bei Schwellwerten und Benchmarks: Vorschlag machen, als ungeprüft markieren, mich bestätigen lassen.
