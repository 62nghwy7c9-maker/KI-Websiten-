<?php
/**
 * Gemeinsame Hilfsmittel für Pflegebereich und Formular.
 *
 * Kein Framework, keine Bibliothek, keine Datenbank. Eine Datei, die auf
 * jedem deutschen Hosting-Tarif läuft, der PHP kann — und das können alle.
 *
 * Der Grundgedanke: Die Website bleibt reines HTML. Bearbeitbare Stellen
 * werden im HTML markiert:
 *
 *     <!--wg:telefon-->0162 3242260<!--/wg-->
 *
 * Der Pflegebereich liest diese Markierungen, zeigt sie als Formularfelder
 * und schreibt die neuen Werte an genau dieselbe Stelle zurück. Zwischen den
 * Markierungen steht Text, sonst nichts — der Kunde kann das Layout nicht
 * zerlegen, weil er es nie zu sehen bekommt.
 */

declare(strict_types=1);

/* Verzeichnis mit den HTML-Dateien der Website.
 * Auf dem Hosting des Kunden liegt der Pflegebereich in einem Unterordner
 * neben der Seite; wo genau, sagt WG_PFLEGE_SEITEN. Ohne Angabe wird der
 * Ordner daneben genommen. */
define('SEITEN', getenv('WG_PFLEGE_SEITEN') ?: __DIR__ . '/../seite');

/** Wohin Sicherungen geschrieben werden. */
const SICHERUNG = __DIR__ . '/sicherungen';

/* Erlaubte Dateien. Alles andere wird nicht angefasst — der Kunde kann
 * ueber diesen Weg an keine andere Datei auf dem Server heran. Aufgefuehrt
 * wird nur, was auch tatsaechlich vorhanden ist. */
define('DATEIEN', array_values(array_filter(
    ['index.html', 'impressum.html', 'datenschutz.html'],
    fn (string $d): bool => is_file(SEITEN . '/' . $d)
)));

/**
 * Sucht alle markierten Stellen in einer Datei.
 *
 * @return array<string,string> Feldname => aktueller Text
 */
function felder_lesen(string $datei): array
{
    $pfad = SEITEN . '/' . $datei;
    if (!is_file($pfad)) {
        return [];
    }
    $html = (string) file_get_contents($pfad);
    $treffer = [];
    preg_match_all(
        '/<!--wg:([a-z0-9_]{1,40})-->(.*?)<!--\/wg-->/s',
        $html,
        $treffer,
        PREG_SET_ORDER
    );
    $felder = [];
    foreach ($treffer as $t) {
        $text = html_entity_decode($t[2], ENT_QUOTES, 'UTF-8');
        // Der Einzug aus der HTML-Datei gehoert nicht ins Formular: im
        // Browser wird er ohnehin zu einem Leerzeichen. Wer den Text sonst
        // bearbeitet, sieht die Einrueckung als Fehler und loescht sie mit.
        $felder[$t[1]] = trim((string) preg_replace('/\s+/u', ' ', $text));
    }
    return $felder;
}

/**
 * Schreibt neue Werte in eine Datei zurück.
 *
 * Vorher wird eine Sicherung angelegt. Nicht aus Vorsicht, sondern weil ein
 * Kunde, der aus Versehen den halben Text löscht, sonst uns anruft — und wir
 * dann in einem Git-Verlauf suchen, den er nicht bedienen kann.
 *
 * @param array<string,string> $neu
 * @return array{0:bool,1:string} Erfolg und Meldung
 */
function felder_schreiben(string $datei, array $neu): array
{
    if (!in_array($datei, DATEIEN, true)) {
        return [false, 'Unbekannte Datei.'];
    }
    $pfad = SEITEN . '/' . $datei;
    if (!is_writable($pfad)) {
        return [false, 'Die Datei ist schreibgeschützt. Bitte melden Sie sich bei uns.'];
    }
    $html = (string) file_get_contents($pfad);

    if (!is_dir(SICHERUNG)) {
        @mkdir(SICHERUNG, 0775, true);
    }
    $stempel = date('Y-m-d_H-i-s');
    @file_put_contents(SICHERUNG . "/{$stempel}_{$datei}", $html);
    sicherungen_aufraeumen($datei);

    $geaendert = 0;
    foreach ($neu as $name => $wert) {
        if (!preg_match('/^[a-z0-9_]{1,40}$/', $name)) {
            continue;
        }
        $wert = trim(preg_replace('/\R/u', ' ', $wert) ?? '');
        // Der Kunde schreibt Text, kein HTML. Alles wird maskiert — damit
        // kann er weder das Layout zerschießen noch versehentlich ein
        // offenes <div> hinterlassen.
        $sicher = htmlspecialchars($wert, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
        $neu_html = preg_replace(
            '/(<!--wg:' . preg_quote($name, '/') . '-->).*?(<!--\/wg-->)/s',
            '${1}' . str_replace('$', '\$', $sicher) . '${2}',
            $html,
            1,
            $anzahl
        );
        if ($neu_html !== null && $anzahl > 0) {
            $html = $neu_html;
            $geaendert += $anzahl;
            $html = verweis_nachziehen($html, $name, $wert);
        }
    }

    if (file_put_contents($pfad, $html) === false) {
        return [false, 'Speichern fehlgeschlagen.'];
    }
    return [true, "{$geaendert} Stelle(n) gespeichert."];
}

/**
 * Zieht den anklickbaren Verweis mit, wenn Telefon oder E-Mail geändert wurden.
 *
 * Ohne diesen Schritt entsteht der schlimmste denkbare Fehler: Auf der Seite
 * steht die neue Nummer, der Tippen-Verweis wählt aber weiter die alte. Das
 * ist genau Prüfpunkt 5 unseres eigenen Katalogs — und es fiele niemandem
 * auf, weil die Seite richtig aussieht.
 */
function verweis_nachziehen(string $html, string $name, string $wert): string
{
    if ($name === 'telefon') {
        $ziel = telefon_ziel($wert);
        if ($ziel === '') {
            return $html;
        }
        $schema = 'tel:';
    } elseif ($name === 'mail') {
        $ziel = trim($wert);
        if (!filter_var($ziel, FILTER_VALIDATE_EMAIL)) {
            return $html;   // im Zweifel den alten Verweis stehen lassen
        }
        $schema = 'mailto:';
    } else {
        return $html;
    }

    return (string) preg_replace(
        '/(<a[^>]*href=")' . preg_quote($schema, '/') . '[^"]*("[^>]*>\s*<!--wg:'
            . preg_quote($name, '/') . '-->)/',
        '${1}' . $schema . str_replace('$', '\$', rawurlencode_erhalten($ziel)) . '${2}',
        $html
    );
}

/** Wandelt „02237 55 66 77" in „+492237556677". */
function telefon_ziel(string $wert): string
{
    $ziffern = preg_replace('/[^0-9+]/', '', $wert) ?? '';
    if (str_starts_with($ziffern, '00')) {
        $ziffern = '+' . substr($ziffern, 2);
    } elseif (str_starts_with($ziffern, '0')) {
        $ziffern = '+49' . substr($ziffern, 1);
    }
    return strlen($ziffern) >= 7 ? $ziffern : '';
}

/** Maskiert nur, was in einem Attribut stören würde. */
function rawurlencode_erhalten(string $wert): string
{
    return htmlspecialchars($wert, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/** Behält die letzten 20 Sicherungen je Datei. */
function sicherungen_aufraeumen(string $datei, int $behalten = 20): void
{
    $liste = glob(SICHERUNG . "/*_{$datei}") ?: [];
    sort($liste);
    foreach (array_slice($liste, 0, max(0, count($liste) - $behalten)) as $alt) {
        @unlink($alt);
    }
}

/** Kurzer, lesbarer Name für ein Feld. */
function feld_beschriftung(string $name): string
{
    $bekannt = [
        'telefon' => 'Telefonnummer',
        'mail' => 'E-Mail-Adresse',
        'oeffnungszeiten' => 'Öffnungszeiten',
        'stelle' => 'Offene Stelle',
        'stelle_text' => 'Text zur offenen Stelle',
        'notdienst' => 'Hinweis Notdienst',
        'anschrift' => 'Anschrift',
        'ueber_uns' => 'Über uns',
        'einleitung' => 'Einleitungstext',
        'stellenanzeige' => 'Stellenanzeige',
        'hinweis' => 'Aktueller Hinweis',
        'leistungen' => 'Leistungen',
    ];
    return $bekannt[$name] ?? ucfirst(str_replace('_', ' ', $name));
}
