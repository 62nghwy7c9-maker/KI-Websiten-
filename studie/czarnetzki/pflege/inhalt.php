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
    ['index.html', 'impressum.html', 'datenschutz.html', 'danke.html'],
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
        // Alle Vorkommen, nicht nur das erste: Die Telefonnummer steht auf
        // einer Handwerkerseite im Kopf und im Kontaktblock. Ein Feld, das
        // nur die Haelfte aendert, ist schlimmer als keins.
        $neu_html = preg_replace(
            '/(<!--wg:' . preg_quote($name, '/') . '-->).*?(<!--\/wg-->)/s',
            '${1}' . str_replace('$', '\$', $sicher) . '${2}',
            $html,
            -1,
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
        // Zwischen dem oeffnenden a-Tag und der Markierung darf Text stehen
        // („Anrufen: 02271 45550"), aber kein weiteres Element — sonst
        // erwischt die Regel den falschen Verweis.
        '/(<a[^>]*href=")' . preg_quote($schema, '/') . '[^"]*("[^>]*>[^<]{0,40}<!--wg:'
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

/** Lesbarer Name einer Seite für die Reiter im Pflegebereich. */
function seiten_name(string $datei): string
{
    $bekannt = [
        'index.html' => 'Startseite',
        'impressum.html' => 'Impressum',
        'datenschutz.html' => 'Datenschutz',
        'danke.html' => 'Danke-Seite',
    ];
    return $bekannt[$datei] ?? $datei;
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
        'betreuung' => 'Preis der Betreuung',
        'gebiet' => 'Wo wir arbeiten',
        'bildtitel' => 'Bildunterschrift',
        'betrieb' => 'Bild aus dem Betrieb',
        'pflege' => 'Bild vom Pflegebereich',
    ];
    return $bekannt[$name] ?? ucfirst(str_replace('_', ' ', $name));
}

/**
 * Schreibt Werte in alle Seiten, die dieselbe Markierung tragen.
 *
 * Die Telefonnummer steht auf der Startseite, im Impressum und in der
 * Datenschutzerklärung. Ein Pflegebereich, in dem man sie dreimal
 * einzeln ändern muss, produziert genau den Fehler, den er verhindern
 * soll: zwei richtige Nummern und eine alte.
 *
 * @param array<string,string> $neu
 * @return array{0:bool,1:string}
 */
function felder_schreiben_ueberall(string $datei, array $neu): array
{
    [$ok, $meldung] = felder_schreiben($datei, $neu);
    if (!$ok) {
        return [$ok, $meldung];
    }
    $weitere = 0;
    foreach (DATEIEN as $andere) {
        if ($andere === $datei) {
            continue;
        }
        $vorhanden = felder_lesen($andere);
        $treffer = array_intersect_key($neu, $vorhanden);
        if (!$treffer) {
            continue;
        }
        [$ok2, ] = felder_schreiben($andere, $treffer);
        if ($ok2) {
            $weitere += count($treffer);
        }
    }
    if ($weitere > 0) {
        $meldung .= " Auf den anderen Seiten mitgeändert: {$weitere}.";
    }
    return [true, $meldung];
}

/* ====================================================================
 * Bilder
 * ====================================================================
 * Text zu ändern reicht nicht. Das Zweithäufigste, was ein Betrieb an
 * seiner Website ändern will, ist ein Bild — neues Fahrzeug, neues Team,
 * fertige Baustelle. Deshalb dasselbe Verfahren wie beim Text: eine
 * Markierung im HTML, direkt vor dem Bild.
 *
 *     <!--wg:bild:team-->
 *     <img src="bilder/team.jpg" alt="Unser Team">
 *
 * Der Kunde wählt eine Datei aus, wir prüfen sie, rechnen sie klein und
 * legen sie unter demselben Namen ab. Am HTML ändert sich nur die
 * Zählnummer hinter dem Dateinamen — sonst zeigt der Browser tagelang das
 * alte Bild aus seinem Zwischenspeicher.
 */

/** Grösster Wert, den ein Bild nach dem Verkleinern haben darf. */
const BILD_KANTE = 1600;
const BILD_GUETE = 82;
const BILD_MAX_BYTES = 8 * 1024 * 1024;

const BILD_TYPEN = [
    IMAGETYPE_JPEG => 'jpg',
    IMAGETYPE_PNG => 'png',
    IMAGETYPE_WEBP => 'webp',
];

/**
 * Sucht alle markierten Bilder in einer Datei.
 *
 * @return array<string,array{src:string,alt:string}>
 */
function bilder_lesen(string $datei): array
{
    $pfad = SEITEN . '/' . $datei;
    if (!is_file($pfad)) {
        return [];
    }
    $html = (string) file_get_contents($pfad);
    preg_match_all(
        '/<!--wg:bild:([a-z0-9_]{1,40})-->\s*<img\b([^>]*)>/i',
        $html,
        $treffer,
        PREG_SET_ORDER
    );
    $bilder = [];
    foreach ($treffer as $t) {
        $bilder[$t[1]] = [
            'src' => attribut($t[2], 'src'),
            'alt' => attribut($t[2], 'alt'),
        ];
    }
    return $bilder;
}

/** Holt den Wert eines Attributs aus einem img-Tag. */
function attribut(string $tag, string $name): string
{
    if (preg_match('/\b' . preg_quote($name, '/') . '="([^"]*)"/i', $tag, $m)) {
        return html_entity_decode($m[1], ENT_QUOTES, 'UTF-8');
    }
    return '';
}

/**
 * Nimmt eine hochgeladene Datei entgegen und ersetzt das markierte Bild.
 *
 * @param array $datei_feld ein Eintrag aus $_FILES
 * @return array{0:bool,1:string}
 */
function bild_schreiben(string $datei, string $name, array $datei_feld): array
{
    if (!in_array($datei, DATEIEN, true) || !preg_match('/^[a-z0-9_]{1,40}$/', $name)) {
        return [false, 'Unbekanntes Bild.'];
    }
    if (($datei_feld['error'] ?? UPLOAD_ERR_NO_FILE) === UPLOAD_ERR_INI_SIZE) {
        return [false, 'Das Bild ist zu groß für diesen Server. Bitte melden Sie sich bei uns.'];
    }
    if (($datei_feld['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK) {
        return [false, 'Beim Hochladen ist etwas schiefgegangen.'];
    }
    if (($datei_feld['size'] ?? 0) > BILD_MAX_BYTES) {
        return [false, 'Das Bild ist größer als 8 MB.'];
    }

    // Nicht auf die Dateiendung verlassen: Was zählt, ist der Inhalt.
    $info = @getimagesize($datei_feld['tmp_name']);
    if ($info === false || !isset(BILD_TYPEN[$info[2]])) {
        return [false, 'Das ist kein Bild. Erlaubt sind JPG, PNG und WEBP.'];
    }

    $bilder = bilder_lesen($datei);
    if (!isset($bilder[$name])) {
        return [false, 'Diese Stelle gibt es auf der Seite nicht.'];
    }
    $src = strtok($bilder[$name]['src'], '?');           // Zählnummer abschneiden
    if ($src === false || str_contains($src, '..') || str_starts_with($src, '/')) {
        return [false, 'Der Bildpfad ist ungültig.'];
    }
    $ziel = SEITEN . '/' . $src;
    if (!is_dir(dirname($ziel))) {
        return [false, 'Der Bildordner fehlt auf dem Server.'];
    }

    // Altes Bild sichern, bevor es überschrieben wird.
    if (is_file($ziel)) {
        if (!is_dir(SICHERUNG)) {
            @mkdir(SICHERUNG, 0775, true);
        }
        @copy($ziel, SICHERUNG . '/' . date('Y-m-d_H-i-s') . '_' . basename($ziel));
    }

    if (!bild_ablegen($datei_feld['tmp_name'], $ziel, $info)) {
        return [false, 'Das Bild konnte nicht gespeichert werden.'];
    }

    return zaehlnummer_erhoehen($datei, $name);
}

/**
 * Verkleinert das Bild und legt es ab.
 *
 * Warum verkleinern: Ein Betrieb fotografiert mit dem Telefon, und aus dem
 * Telefon kommen 4000 Pixel und sechs Megabyte. Ungefragt hochgeladen macht
 * das eine schnelle Seite langsam — Prüfpunkt 4, der Punkt, mit dem wir
 * selbst argumentieren. Der Kunde soll darüber nicht nachdenken müssen.
 */
function bild_ablegen(string $quelle, string $ziel, array $info): bool
{
    if (!function_exists('imagecreatefromstring')) {
        return @move_uploaded_file($quelle, $ziel) || @copy($quelle, $ziel);
    }
    $roh = @file_get_contents($quelle);
    $bild = $roh === false ? false : @imagecreatefromstring($roh);
    if ($bild === false) {
        return @copy($quelle, $ziel);
    }
    [$breite, $hoehe] = [imagesx($bild), imagesy($bild)];
    $faktor = min(1.0, BILD_KANTE / max($breite, $hoehe));
    if ($faktor < 1.0) {
        $klein = imagescale($bild, (int) round($breite * $faktor));
        if ($klein !== false) {
            imagedestroy($bild);
            $bild = $klein;
        }
    }
    $endung = strtolower(pathinfo($ziel, PATHINFO_EXTENSION));
    $ok = match ($endung) {
        'png' => imagepng($bild, $ziel, 6),
        'webp' => imagewebp($bild, $ziel, BILD_GUETE),
        default => imagejpeg($bild, $ziel, BILD_GUETE),
    };
    imagedestroy($bild);
    return (bool) $ok;
}

/**
 * Erhöht die Zählnummer hinter dem Dateinamen im HTML.
 *
 * Ohne sie zeigt der Browser des Betriebsinhabers noch tagelang das alte
 * Bild und er ruft an, weil „nichts passiert ist".
 */
function zaehlnummer_erhoehen(string $datei, string $name): array
{
    $pfad = SEITEN . '/' . $datei;
    $html = (string) file_get_contents($pfad);
    $stempel = (string) filemtime($pfad);
    $neu = preg_replace_callback(
        '/(<!--wg:bild:' . preg_quote($name, '/') . '-->\s*<img\b[^>]*\bsrc=")([^"]*)(")/i',
        static function (array $m) use ($stempel): string {
            $pfad = strtok($m[2], '?');
            return $m[1] . $pfad . '?v=' . $stempel . $m[3];
        },
        $html,
        1,
        $anzahl
    );
    if ($neu === null || $anzahl === 0) {
        return [true, 'Bild gespeichert.'];
    }
    @copy($pfad, SICHERUNG . '/' . date('Y-m-d_H-i-s') . '_' . $datei);
    file_put_contents($pfad, $neu);
    sicherungen_aufraeumen($datei);
    return [true, 'Bild gespeichert.'];
}

/** Schreibt den Alternativtext eines markierten Bildes. */
function bildtext_schreiben(string $datei, string $name, string $alt): bool
{
    if (!in_array($datei, DATEIEN, true) || !preg_match('/^[a-z0-9_]{1,40}$/', $name)) {
        return false;
    }
    $pfad = SEITEN . '/' . $datei;
    $html = (string) file_get_contents($pfad);
    $sicher = htmlspecialchars(
        trim((string) preg_replace('/\s+/u', ' ', $alt)),
        ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    $neu = preg_replace(
        '/(<!--wg:bild:' . preg_quote($name, '/') . '-->\s*<img\b[^>]*\balt=")([^"]*)(")/i',
        '${1}' . str_replace('$', '\$', $sicher) . '${3}',
        $html,
        1,
        $anzahl
    );
    if ($neu !== null && $anzahl > 0) {
        file_put_contents($pfad, $neu);
        return true;
    }
    return false;
}
