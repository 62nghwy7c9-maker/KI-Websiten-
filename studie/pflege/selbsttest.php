<?php
/**
 * Selbsttest des Pflegebereichs.
 *
 * Diese Datei prüft auf dem Server selbst, was sonst jemand von Hand im
 * Browser durchklicken müsste. Sie ruft dieselben Funktionen auf, die auch
 * der Pflegebereich benutzt, und zeigt am Ende eine Liste: bestanden oder
 * nicht.
 *
 * Sie verändert dabei Inhalte. Alles, was sie ändert, schreibt sie am Ende
 * wieder zurück. Was sie anlegt, räumt sie weg. Kommt sie unterwegs nicht
 * bis zum Ende, sagt sie das im Bericht.
 *
 * Ohne Schlüssel in der Adresse antwortet sie mit 404, und sie löscht sich
 * auf Knopfdruck selbst.
 */

declare(strict_types=1);
date_default_timezone_set('Europe/Berlin');

/* Vor jedem Einsatz neu erzeugen:
 *   php -r "echo bin2hex(random_bytes(8));"
 * Der Schluessel steht in der Adresse und ist das Einzige, was diese Datei
 * schuetzt, solange sie auf dem Server liegt. */
const SCHLUESSEL = '8356dde68024af1c';

if (!hash_equals(SCHLUESSEL, (string) ($_GET['s'] ?? ''))) {
    http_response_code(404);
    exit;
}

if (isset($_GET['weg'])) {
    echo @unlink(__FILE__)
        ? 'Selbsttest gelöscht.'
        : 'Löschen fehlgeschlagen, bitte im Dateimanager entfernen.';
    exit;
}

require __DIR__ . '/inhalt.php';

/* ---- Sammelstelle für die Ergebnisse -------------------------------- */
$punkte = [];
function pruefen(string $nr, string $frage, bool $gut, string $befund): void
{
    global $punkte;
    $punkte[] = ['nr' => $nr, 'frage' => $frage, 'gut' => $gut, 'befund' => $befund];
}

/* Was wir verändern, merken wir uns hier und stellen es am Ende zurück. */
$urzustand = felder_lesen('index.html');
$zurueckgestellt = false;

/* ==== 1  Dateien und Gestaltung ====================================== */
$fehlend = [];
foreach (['index.html', 'impressum.html', 'datenschutz.html', 'danke.html', 'stil.css'] as $d) {
    if (!is_file(SEITEN . '/' . $d)) { $fehlend[] = $d; }
}
pruefen('1', 'Alle Seiten und die Gestaltung liegen auf dem Server',
    $fehlend === [],
    $fehlend === [] ? 'index, impressum, datenschutz, danke und stil.css sind da'
                    : 'Es fehlen: ' . implode(', ', $fehlend));

$html = (string) @file_get_contents(SEITEN . '/index.html');
$css = @filesize(SEITEN . '/stil.css') ?: 0;
pruefen('1b', 'Die Startseite bindet die Gestaltung ein',
    str_contains($html, 'stil.css') && $css > 2000,
    'stil.css ist ' . round($css / 1024, 1) . ' KB gross und wird eingebunden');

/* ==== 2  Verweise auf Impressum und Datenschutz ====================== */
$impr = str_contains($html, 'impressum.html');
$dsgvo = str_contains($html, 'datenschutz.html');
pruefen('2', 'Impressum und Datenschutz sind von der Startseite verlinkt',
    $impr && $dsgvo,
    ($impr ? 'Impressum verlinkt' : 'IMPRESSUM FEHLT') . ', '
    . ($dsgvo ? 'Datenschutz verlinkt' : 'DATENSCHUTZ FEHLT'));

/* ==== 3  Das Schloss am Pflegebereich ================================= */
$hash = passwort_hash('');
pruefen('3', 'Ein Passwort ist hinterlegt',
    $hash !== '' && str_starts_with($hash, '$2y$'),
    $hash === '' ? 'KEIN Passwort hinterlegt, der Bereich waere gesperrt'
                 : 'Ein verschluesseltes Passwort liegt in passwort.php');
pruefen('3b', 'Ein falsches Passwort wird abgewiesen',
    $hash !== '' && !password_verify('offensichtlich-falsch', $hash),
    'Der Vergleich lehnt ein falsches Passwort ab');

/* ==== 4  Der entscheidende Punkt: Speichern und Uebertragen ========== */
$probe = '02271 000' . random_int(100, 999);
[$ok, $meldung] = felder_schreiben_ueberall('index.html', ['telefon' => $probe]);

$stellen = 0;
$verweise = 0;
$seiten_mit = [];
foreach (DATEIEN as $d) {
    $t = (string) @file_get_contents(SEITEN . '/' . $d);
    $n = substr_count($t, '<!--wg:telefon-->' . htmlspecialchars($probe, ENT_QUOTES, 'UTF-8'));
    if ($n > 0) { $seiten_mit[] = $d; }
    $stellen += $n;
    $verweise += substr_count($t, 'tel:' . telefon_ziel($probe));
}
pruefen('4', 'Eine geaenderte Nummer steht danach auf ALLEN Seiten',
    $ok && count($seiten_mit) >= 3 && $stellen >= 5,
    $ok ? "{$stellen} Stellen auf " . count($seiten_mit) . ' Seiten geaendert: '
          . implode(', ', $seiten_mit)
        : 'Speichern abgelehnt: ' . $meldung);
pruefen('4b', 'Die antippbaren Verweise ziehen mit',
    $verweise >= 5 && $verweise === $stellen,
    "{$verweise} Verweise auf tel:" . telefon_ziel($probe)
    . ($verweise === $stellen ? ', genau so viele wie Textstellen'
                              : ', ABER ' . $stellen . ' Textstellen'));

/* ==== 5  Pflichtfeld ================================================= */
[$ok2, $meldung2] = felder_schreiben('index.html', ['telefon' => '   ']);
$immer_noch = felder_lesen('index.html')['telefon'] ?? '';
pruefen('5', 'Eine leere Telefonnummer wird abgelehnt',
    !$ok2 && $immer_noch === $probe,
    !$ok2 ? 'Abgelehnt mit: ' . $meldung2 . ' Die Nummer steht unveraendert da.'
          : 'ANGENOMMEN, das darf nicht sein');

/* ==== 6  Frueheren Stand zurueckholen ================================ */
$staende = sicherungen_liste('index.html');
if ($staende === []) {
    pruefen('6', 'Ein frueherer Stand laesst sich zurueckholen', false,
        'Keine Sicherung vorhanden, Ordner nicht beschreibbar?');
} else {
    [$ok3, $meldung3] = sicherung_zurueckholen('index.html', $staende[0]['datei']);
    $danach = felder_lesen('index.html')['telefon'] ?? '';
    pruefen('6', 'Ein frueherer Stand laesst sich zurueckholen',
        $ok3 && $danach !== $probe,
        $ok3 ? 'Zurueckgeholt, die Nummer lautet wieder ' . $danach
             : 'Fehlgeschlagen: ' . $meldung3);
}

/* ==== 7  Bild austauschen, samt Drehung ============================== */
$bilder = bilder_lesen('index.html');
if ($bilder === [] || !function_exists('imagecreatetruecolor')) {
    pruefen('7', 'Ein Bild laesst sich austauschen', false,
        $bilder === [] ? 'Kein markiertes Bild auf der Seite'
                       : 'Dieser Server kann keine Bilder verarbeiten');
} else {
    $name = array_key_first($bilder);
    $tmp = sys_get_temp_dir() . '/wg_probe_' . getmypid() . '.jpg';
    $b = imagecreatetruecolor(2400, 1200);
    imagefilledrectangle($b, 0, 0, 2399, 1199, imagecolorallocate($b, 200, 200, 200));
    imagejpeg($b, $tmp, 88);
    imagedestroy($b);
    $vorher = @filesize(SEITEN . '/' . strtok($bilder[$name]['src'], '?')) ?: 0;
    [$ok4, $meldung4] = bild_schreiben('index.html', (string) $name, [
        'error' => UPLOAD_ERR_OK, 'tmp_name' => $tmp,
        'size' => filesize($tmp), 'name' => 'probe.jpg', 'type' => 'image/jpeg',
    ]);
    $pfad = SEITEN . '/' . strtok(bilder_lesen('index.html')[$name]['src'], '?');
    $masse = @getimagesize($pfad);
    @unlink($tmp);
    pruefen('7', 'Ein grosses Foto wird angenommen und verkleinert',
        $ok4 && $masse && $masse[0] <= BILD_KANTE,
        $ok4 ? "2400 Pixel hochgeladen, {$masse[0]} Pixel abgelegt (Grenze " . BILD_KANTE . ')'
             : 'Fehlgeschlagen: ' . $meldung4);
    pruefen('7b', 'Die Ausrichtung von Handyfotos wird ausgewertet',
        function_exists('exif_read_data'),
        function_exists('exif_read_data')
            ? 'exif ist vorhanden, hochkant fotografierte Bilder werden gedreht'
            : 'exif fehlt auf diesem Server, Bilder gehen ungedreht durch (kein Fehler)');
    $bstaende = bild_staende('index.html');
    pruefen('7c', 'Das vorherige Bild ist zurueckholbar',
        !empty($bstaende[$name]),
        !empty($bstaende[$name])
            ? count($bstaende[$name]) . (count($bstaende[$name]) === 1 ? ' frueheres Bild steht bereit' : ' fruehere Bilder stehen bereit')
            : 'Keine Bildsicherung gefunden');
    if (!empty($bstaende[$name])) {
        bild_zurueckholen('index.html', $bstaende[$name][0]['datei']);
    }
}

/* ==== 8  Anfragen: ablegen, anzeigen, loeschen ======================= */
$kennzeichen = 'SELBSTTEST-' . bin2hex(random_bytes(4));
$eintrag = str_repeat('=', 60) . "\n"
    . "Neue Anfrage über die Website von Selbsttest\n\n"
    . "Name:      {$kennzeichen}\n"
    . "E-Mail:    selbsttest@example.de\n"
    . "Telefon:   -\n"
    . 'Eingang:   ' . date('d.m.Y, H:i') . " Uhr\n\n"
    . "Nachricht:\nDieser Eintrag stammt aus dem Selbsttest.\nMail: nein\n\n";

$vorher_zahl = count(anfragen_lesen());
$abgelegt = @file_put_contents(ANFRAGEN,
    (is_file(ANFRAGEN) ? '' : RIEGEL) . $eintrag, FILE_APPEND | LOCK_EX) !== false;
$liste = anfragen_lesen();
$gefunden = null;
foreach ($liste as $a) {
    if ($a['name'] === $kennzeichen) { $gefunden = $a; break; }
}
pruefen('8', 'Eine Anfrage wird abgelegt und im Pflegebereich angezeigt',
    $abgelegt && $gefunden !== null,
    $gefunden !== null
        ? 'Abgelegt und wiedergefunden, ' . count($liste) . (count($liste) === 1 ? ' Anfrage' : ' Anfragen') . ' insgesamt'
        : 'Die Anfrage kam nicht in der Liste an');

if ($gefunden !== null) {
    [$ok5, $meldung5] = anfragen_loeschen($gefunden['kennung']);
    $nachher_zahl = count(anfragen_lesen());
    pruefen('8b', 'Eine Anfrage laesst sich wieder loeschen',
        $ok5 && $nachher_zahl === $vorher_zahl,
        $ok5 ? 'Geloescht, wieder ' . $nachher_zahl . ($nachher_zahl === 1 ? ' Anfrage' : ' Anfragen') . ' wie vorher'
             : 'Fehlgeschlagen: ' . $meldung5);
}

pruefen('8c', 'Der Mailversand dieses Servers',
    true,
    function_exists('mail')
        ? 'mail() ist vorhanden. Ob der Anbieter wirklich versendet, zeigt erst eine echte Anfrage.'
        : 'mail() ist gesperrt. Anfragen kommen nur ueber die Anzeige im Pflegebereich an.');

/* ==== 9  Die verschlossenen Dateien ================================== */
/* Zwei Bauarten, beide gueltig: passwort.php und anfragen.php tragen den
   Riegel als erste Zeile, inhalt.php prueft stattdessen selbst, ob sie
   direkt aufgerufen wurde. Geprueft wird, ob eine der beiden greift. */
$verriegelt = [];
foreach (['inhalt.php', 'passwort.php', 'anfragen.php'] as $d) {
    $p = __DIR__ . '/' . $d;
    if (!is_file($p)) { continue; }
    $anfang = (string) @file_get_contents($p, false, null, 0, 2500);
    $verriegelt[$d] = str_starts_with($anfang, '<?php http_response_code(404)')
        || str_contains($anfang, 'SCRIPT_FILENAME');
}
$alle = $verriegelt !== [] && !in_array(false, $verriegelt, true);
pruefen('9', 'Die vertraulichen Dateien sperren sich selbst',
    $alle,
    $alle ? 'Geschuetzt: ' . implode(', ', array_keys($verriegelt))
          : 'UNGESCHUETZT: ' . implode(', ', array_keys($verriegelt, false, true)));

$ht = @file_get_contents(__DIR__ . '/.htaccess');
pruefen('9b', 'Die zusaetzliche Sperre des Servers ist eingerichtet',
    $ht !== false && str_contains($ht, 'anfragen\.php') && str_contains($ht, 'passwort\.php'),
    $ht === false ? 'Keine .htaccess gefunden'
                  : 'inhalt.php, passwort.php und anfragen.php stehen in der Sperrliste');

$wache = is_file(SICHERUNG . '/index.php');
pruefen('9c', 'Der Ordner mit den Sicherungen ist verschlossen',
    $wache, $wache ? 'Eine Wache liegt im Ordner' : 'Keine Wache im Sicherungsordner');

/* ==== 10  Der Server selbst =========================================== */
$probe_datei = SEITEN . '/.schreibprobe.tmp';
$schreibbar = @file_put_contents($probe_datei, 'x') !== false;
if ($schreibbar) { @unlink($probe_datei); }
pruefen('10', 'PHP-Version und Schreibrechte',
    version_compare(PHP_VERSION, '8.0', '>=') && $schreibbar,
    'PHP ' . PHP_VERSION . ', Ordner ' . ($schreibbar ? 'beschreibbar' : 'NICHT beschreibbar'));

/* ==== Alles zuruecksetzen ============================================ */
if ($urzustand !== []) {
    $zurueckgestellt = felder_schreiben_ueberall('index.html', $urzustand)[0];
}
$jetzt = felder_lesen('index.html');
$gleich = ($jetzt['telefon'] ?? '') === ($urzustand['telefon'] ?? '');

header('Content-Type: text/html; charset=UTF-8');
$bestanden = count(array_filter($punkte, static fn($p) => $p['gut']));
$gesamt = count($punkte);
?>
<!doctype html>
<html lang="de">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Selbsttest</title>
<style>
 body{font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;
      max-width:46rem;margin:2rem auto;padding:0 1rem;color:#14201C;background:#F2F4F1}
 h1{font-size:1.5rem;margin:0 0 .3rem}
 .kopf{color:#5E6B66;margin:0 0 1.6rem}
 .zahl{display:inline-block;padding:.35rem .8rem;border-radius:3px;font-weight:700;
       background:<?= $bestanden === $gesamt ? '#E2EFE7;color:#1a7f4b' : '#F6E4DF;color:#b0271c' ?>}
 table{border-collapse:collapse;width:100%;background:#FBFCFA;
       border:1px solid #C3CDC8;margin-bottom:1.5rem}
 td{border-bottom:1px solid #E4E9E6;padding:.6rem .7rem;vertical-align:top}
 tr:last-child td{border-bottom:0}
 td.nr{width:2.6rem;font-family:ui-monospace,monospace;color:#5E6B66;font-size:.85rem}
 td.ja{width:2rem;color:#1a7f4b;font-weight:700}
 td.nein{width:2rem;color:#b0271c;font-weight:700}
 b{display:block}
 small{color:#5E6B66}
 .hinweis{background:#FBFCFA;border:1px solid #C3CDC8;border-left:3px solid #1F4E5F;
          padding:.9rem 1rem;margin-bottom:1.5rem;font-size:.95rem}
 .warn{border-left-color:#b0271c}
 a.weg{color:#b0271c}
</style>

<h1>Selbsttest</h1>
<p class="kopf">Pflegebereich, geprüft am <?= date('d.m.Y, H:i') ?> Uhr</p>

<p><span class="zahl"><?= $bestanden ?> von <?= $gesamt ?> bestanden</span></p>

<table>
<?php foreach ($punkte as $p): ?>
  <tr>
    <td class="nr"><?= htmlspecialchars($p['nr']) ?></td>
    <td class="<?= $p['gut'] ? 'ja' : 'nein' ?>"><?= $p['gut'] ? '✓' : '✗' ?></td>
    <td>
      <b><?= htmlspecialchars($p['frage']) ?></b>
      <small><?= htmlspecialchars($p['befund']) ?></small>
    </td>
  </tr>
<?php endforeach; ?>
</table>

<div class="hinweis<?= $gleich ? '' : ' warn' ?>">
  <b>Zurückgesetzt:</b>
  <?= $gleich
      ? 'Die Telefonnummer steht wieder auf ' . htmlspecialchars($urzustand['telefon'] ?? '?')
        . '. Der Testeintrag in den Anfragen ist gelöscht, das Bild ist zurückgeholt.'
      : 'ACHTUNG: Die Telefonnummer konnte nicht zurückgesetzt werden. Bitte im Pflegebereich '
        . 'nachsehen und von Hand auf ' . htmlspecialchars($urzustand['telefon'] ?? '?') . ' stellen.' ?>
</div>

<div class="hinweis">
  <b>Was dieser Test nicht prüfen kann</b>
  Wie die Seite auf einem echten Handy aussieht, und ob eine Mail wirklich im
  Postfach ankommt. Beides braucht ein Gerät bzw. ein Postfach und geht nur von Hand.
</div>

<p><a class="weg" href="?s=<?= SCHLUESSEL ?>&amp;weg=1">Diesen Selbsttest jetzt löschen</a></p>
