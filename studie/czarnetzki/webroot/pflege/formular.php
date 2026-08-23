<?php
/**
 * Das Kontaktformular. Nimmt eine Anfrage entgegen und schickt sie per Mail
 * an den Betrieb weiter.
 *
 * Warum überhaupt eine Datei dafür: Eine statische Website ist nur Text auf
 * einer Festplatte. Sie kann nichts entgegennehmen. Damit ein Formular
 * funktioniert, braucht es ein Programm, das den Knopfdruck verarbeitet
 * das ist diese Datei.
 *
 * Warum kein fertiger Dienst: Jeder Formulardienst bekäme die Anfragen der
 * Kunden unserer Kunden zu sehen. Das wäre ein Auftragsverarbeitungsvertrag
 * mehr, ein Anbieter mehr in der Datenschutzerklärung, und eine Abhängigkeit,
 * die niemand braucht. Diese Datei liegt beim Kunden, die Daten gehen direkt
 * in sein Postfach, und niemand sonst sieht sie.
 *
 * Kein Speichern, keine Datenbank, kein Protokoll mit Inhalten.
 */

declare(strict_types=1);

/* Viele Server stehen im Ausland und rechnen in ihrer eigenen Zeit. Ohne
 * diese Zeile trägt eine Anfrage von 11 Uhr den Eingang 05 Uhr, und
 * Sicherungen bekommen einen Namen, der nicht zum Tag passt. Wir rechnen
 * überall in deutscher Zeit, mit Sommerzeit. */
date_default_timezone_set('Europe/Berlin');

/** Wohin die Anfragen gehen. Beim Aufsetzen eintragen. */
const EMPFAENGER = 'info@pcelektro.de';
const BETRIEB = 'Peter Czarnetzki Elektroinstallationen';

/* Wohin jede Anfrage zusätzlich abgelegt wird.
 *
 * Der Mailversand über PHP ist auf günstigem Webspace unzuverlässig:
 * Manche Anbieter sperren ihn, manche Mails landen im Spam, manche
 * verschwinden. Eine Anfrage, die dabei verlorengeht, ist ein verlorener
 * Auftrag. Deshalb wird jede Anfrage hier abgelegt, bevor die Mail
 * überhaupt versucht wird.
 *
 * Die Datei heißt .php und beginnt mit einem Riegel: Wer sie im Browser
 * aufruft, bekommt 404. Das gilt auch auf Servern, die .htaccess
 * ignorieren, denn hier hält PHP selbst die Tür zu. */
const ABLAGE = __DIR__ . '/anfragen.php';
const RIEGEL = "<?php http_response_code(404); exit; ?>\n";

/** Wohin nach dem Absenden zurückgesprungen wird. */
const ZURUECK = '../danke.html';
const ZURUECK_FEHLER = '../index.html?fehler=1#kontakt';

/** Höchstens so viele Anfragen je Stunde von derselben Adresse. */
const HOECHSTENS = 5;

/**
 * Die Adresse, an die eine Anfrage geht.
 *
 * Gelesen wird sie aus den Seiten selbst, aus der Markierung wg:mail. So
 * gibt es genau eine Quelle: Aendert der Betrieb seine Adresse im
 * Pflegebereich, aendert sich damit auch der Empfaenger. Frueher standen
 * beide getrennt, und wer die eine aenderte, vergass die andere.
 *
 * Findet sich keine brauchbare Markierung, gilt der fest eingetragene
 * Wert. Eine Anfrage darf nicht daran scheitern, dass jemand eine
 * Markierung geloescht hat.
 */
function empfaenger(): string
{
    $wurzel = getenv('WG_PFLEGE_SEITEN') ?: dirname(__DIR__);
    foreach (['index.html', 'impressum.html', 'datenschutz.html', 'danke.html'] as $seite) {
        $pfad = $wurzel . '/' . $seite;
        if (!is_file($pfad)) {
            continue;
        }
        $html = (string) @file_get_contents($pfad);
        if (!preg_match('/<!--wg:mail-->(.*?)<!--\/wg-->/s', $html, $t)) {
            continue;
        }
        $wert = trim(html_entity_decode($t[1], ENT_QUOTES, 'UTF-8'));
        if (filter_var($wert, FILTER_VALIDATE_EMAIL)) {
            return $wert;
        }
    }
    return EMPFAENGER;
}

function zurueck(string $ziel): never
{
    header('Location: ' . $ziel, true, 303);
    exit;
}

/** Entfernt Zeilenumbrüche, sonst ließen sich Mail-Kopfzeilen einschleusen. */
function eine_zeile(string $s): string
{
    return trim((string) preg_replace('/[\r\n]+/', ' ', $s));
}

/** Hängt eine Anfrage an die Ablage an. Beim ersten Mal legt sie die Datei
 *  mit dem Riegel davor an. LOCK_EX, damit zwei gleichzeitige Anfragen
 *  sich nicht ins Gehege kommen. */
function ablegen(string $eintrag): bool
{
    $vorspann = is_file(ABLAGE) ? '' : RIEGEL;
    return @file_put_contents(ABLAGE, $vorspann . $eintrag, FILE_APPEND | LOCK_EX) !== false;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    zurueck(ZURUECK_FEHLER);
}

/* ---- Spamabwehr ohne Captcha ---------------------------------------
 * Zwei Fallen, die für Menschen unsichtbar sind:
 *
 * 1. Ein Feld namens "website", das im Formular versteckt ist. Menschen
 *    sehen es nicht und füllen es nicht aus. Automatische Programme füllen
 *    stumpf alles aus, wer hier etwas einträgt, ist keiner.
 * 2. Die Zeit. Ein Mensch braucht mindestens ein paar Sekunden zum Tippen.
 *    Wer in unter drei Sekunden absendet, hat nicht getippt.
 *
 * Das ersetzt ein Captcha und verlangt dem Kunden nichts ab. Ein Meister,
 * der Verkehrsschilder anklicken muss, ruft nicht an, er geht weg.
 */
if (!empty($_POST['website'])) {
    zurueck(ZURUECK);            // still schlucken, kein Hinweis für den Absender
}
$gestartet = (int) ($_POST['zeit'] ?? 0);
if ($gestartet > 0 && (time() - $gestartet) < 3) {
    zurueck(ZURUECK);
}

/* ---- Bremse gegen Massenversand ------------------------------------ */
$spur = sys_get_temp_dir() . '/wg_' . sha1((string) ($_SERVER['REMOTE_ADDR'] ?? ''));
$zaehler = is_file($spur) ? (array) json_decode((string) file_get_contents($spur), true) : [];
$zaehler = array_values(array_filter($zaehler, static fn($t) => $t > time() - 3600));
if (count($zaehler) >= HOECHSTENS) {
    zurueck(ZURUECK_FEHLER);
}
$zaehler[] = time();
@file_put_contents($spur, json_encode($zaehler));

/* ---- Eingaben prüfen ------------------------------------------------ */
$name = eine_zeile((string) ($_POST['name'] ?? ''));
$mail = eine_zeile((string) ($_POST['mail'] ?? ''));
$tel = eine_zeile((string) ($_POST['telefon'] ?? ''));
$text = trim((string) ($_POST['nachricht'] ?? ''));

if ($name === '' || $text === '' || mb_strlen($text) > 5000) {
    zurueck(ZURUECK_FEHLER);
}
if ($mail !== '' && !filter_var($mail, FILTER_VALIDATE_EMAIL)) {
    zurueck(ZURUECK_FEHLER);
}
if ($mail === '' && $tel === '') {
    zurueck(ZURUECK_FEHLER);     // ohne Rückweg ist die Anfrage wertlos
}

/* ---- Mail bauen und senden ------------------------------------------ */
$betreff = 'Anfrage über die Website';
$inhalt = "Neue Anfrage über die Website von " . BETRIEB . "\n\n"
    . "Name:      {$name}\n"
    . "E-Mail:    " . ($mail !== '' ? $mail : '-') . "\n"
    . "Telefon:   " . ($tel !== '' ? $tel : '-') . "\n"
    . "Eingang:   " . date('d.m.Y, H:i') . " Uhr\n\n"
    . "Nachricht:\n{$text}\n";

$empfaenger = empfaenger();

$kopf = [
    'From: ' . BETRIEB . ' <' . $empfaenger . '>',
    'Content-Type: text/plain; charset=UTF-8',
    'X-Mailer: PHP',
];
// Antworten geht direkt an den Absender, der Betrieb drückt einfach
// „Antworten" und muss die Adresse nicht heraussuchen.
if ($mail !== '') {
    $kopf[] = 'Reply-To: ' . $mail;
}

$ok = @mail($empfaenger, '=?UTF-8?B?' . base64_encode($betreff) . '?=',
            $inhalt, implode("\r\n", $kopf));

/* Die Ablage vermerkt, ob die Mail rausging. Steht dort dauerhaft
   "Mail: nein", verschickt dieser Server nicht, und die Anfragen müssen
   aus dieser Datei gelesen werden. */
$abgelegt = ablegen(
    str_repeat('=', 60) . "\n"
    . $inhalt
    . 'Mail: ' . ($ok ? 'ja' : 'nein') . "\n\n"
);

/* Danke sagen, sobald die Anfrage sicher ist. Für den Absender zählt,
   dass sie angekommen ist, nicht auf welchem Weg. Nur wenn beides
   fehlschlägt, ist sie wirklich weg, und dann muss er das erfahren. */
zurueck(($ok || $abgelegt) ? ZURUECK : ZURUECK_FEHLER);
