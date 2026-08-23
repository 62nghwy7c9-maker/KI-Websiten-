<?php
/**
 * Das Kontaktformular. Nimmt eine Anfrage entgegen und schickt sie per Mail
 * an den Betrieb weiter.
 *
 * Warum überhaupt eine Datei dafür: Eine statische Website ist nur Text auf
 * einer Festplatte. Sie kann nichts entgegennehmen. Damit ein Formular
 * funktioniert, braucht es ein Programm, das den Knopfdruck verarbeitet —
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

/** Wohin die Anfragen gehen. Beim Aufsetzen eintragen. */
const EMPFAENGER = 'webgewerk@gmx.de';
const BETRIEB = 'Webgewerk';

/** Wohin nach dem Absenden zurückgesprungen wird. */
const ZURUECK = 'danke.html';
const ZURUECK_FEHLER = 'index.html?fehler=1#kontakt';

/** Höchstens so viele Anfragen je Stunde von derselben Adresse. */
const HOECHSTENS = 5;

function zurueck(string $ziel): never
{
    header('Location: ' . $ziel, true, 303);
    exit;
}

/** Entfernt Zeilenumbrüche — sonst ließen sich Mail-Kopfzeilen einschleusen. */
function eine_zeile(string $s): string
{
    return trim((string) preg_replace('/[\r\n]+/', ' ', $s));
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    zurueck(ZURUECK_FEHLER);
}

/* ---- Spamabwehr ohne Captcha ---------------------------------------
 * Zwei Fallen, die für Menschen unsichtbar sind:
 *
 * 1. Ein Feld namens "website", das im Formular versteckt ist. Menschen
 *    sehen es nicht und füllen es nicht aus. Automatische Programme füllen
 *    stumpf alles aus — wer hier etwas einträgt, ist keiner.
 * 2. Die Zeit. Ein Mensch braucht mindestens ein paar Sekunden zum Tippen.
 *    Wer in unter drei Sekunden absendet, hat nicht getippt.
 *
 * Das ersetzt ein Captcha und verlangt dem Kunden nichts ab. Ein Meister,
 * der Verkehrsschilder anklicken muss, ruft nicht an — er geht weg.
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
    . "E-Mail:    " . ($mail !== '' ? $mail : '—') . "\n"
    . "Telefon:   " . ($tel !== '' ? $tel : '—') . "\n"
    . "Eingang:   " . date('d.m.Y, H:i') . " Uhr\n\n"
    . "Nachricht:\n{$text}\n";

$kopf = [
    'From: ' . BETRIEB . ' <' . EMPFAENGER . '>',
    'Content-Type: text/plain; charset=UTF-8',
    'X-Mailer: PHP',
];
// Antworten geht direkt an den Absender — der Betrieb drückt einfach
// „Antworten" und muss die Adresse nicht heraussuchen.
if ($mail !== '') {
    $kopf[] = 'Reply-To: ' . $mail;
}

$ok = @mail(EMPFAENGER, '=?UTF-8?B?' . base64_encode($betreff) . '?=',
            $inhalt, implode("\r\n", $kopf));

zurueck($ok ? ZURUECK : ZURUECK_FEHLER);
