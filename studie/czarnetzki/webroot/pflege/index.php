<?php
/**
 * Der Pflegebereich. Eine Seite, ein Passwort, ein paar Felder.
 *
 * Aufrufbar unter https://www.kundendomain.de/pflege/
 *
 * Was er ausdrücklich NICHT ist: ein Redaktionssystem. Der Kunde sieht nur
 * die Felder, die sich erfahrungsgemäß ändern. Er kann keine Seiten anlegen,
 * kein Layout verschieben und nichts löschen, was er nicht selbst
 * geschrieben hat.
 */

declare(strict_types=1);

/* Viele Server stehen im Ausland und rechnen in ihrer eigenen Zeit. Ohne
 * diese Zeile trägt eine Anfrage von 11 Uhr den Eingang 05 Uhr, und
 * Sicherungen bekommen einen Namen, der nicht zum Tag passt. Wir rechnen
 * überall in deutscher Zeit, mit Sommerzeit. */
date_default_timezone_set('Europe/Berlin');
require __DIR__ . '/inhalt.php';

/* ---- Zugang ---------------------------------------------------------
 * Ein Passwort für den Betrieb, als Hash hinterlegt. Erzeugt wird der Hash
 * einmalig mit:  php -r "echo password_hash('IhrPasswort', PASSWORD_DEFAULT);"
 * Im Klartext steht das Passwort nirgends, auch nicht bei uns.
 */
/* Reihenfolge: passwort.php im Ordner (das aendert der Betrieb selbst),
 * dann WG_PFLEGE_HASH. Danach nichts mehr.
 *
 * Hier stand frueher ein eingebautes Passwort als letzte Rueckfallebene.
 * Das war eine Tuer: Fehlte passwort.php, weil sie beim Hochladen
 * uebersprungen, geloescht oder beim Kopieren der Vorlage vergessen
 * wurde, kam jeder mit dem eingebauten Wort herein, und im Anmeldefenster
 * stand kein Wort davon. Der Wert steht ausserdem im Quelltext jedes
 * ausgelieferten Pakets.
 *
 * Jetzt gilt: Ist kein Passwort hinterlegt, ist der Bereich zu. Ausgesperrt
 * ist der richtige Fehlerfall, offen ist der falsche. In dieser Datei steht
 * weiterhin nie etwas Kundenspezifisches. */
$PASSWORT_HASH = (string) getenv('WG_PFLEGE_HASH');

/* Acht Stunden statt der ueblichen 24 Minuten. Wer einen Text tippt,
 * telefoniert zwischendurch und kommt zurueck: Seine Eingabe soll nicht
 * beim Speichern verschwinden. */
ini_set('session.gc_maxlifetime', '28800');
session_set_cookie_params(28800);
session_start();
$meldung = '';
/** Was schiefgegangen ist. Wird zusaetzlich zur Erfolgsmeldung angezeigt. */
$fehler = [];
$erfolg = false;

if (isset($_GET['abmelden'])) {
    session_destroy();
    header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?'));
    exit;
}

/* Ohne hinterlegtes Passwort bleibt der Bereich zu, und zwar sichtbar.
   Ein stiller Fehlschlag waere hier das Gefaehrliche. */
$hash_vorhanden = passwort_hash($PASSWORT_HASH) !== '';
if (!$hash_vorhanden) {
    $meldung = 'Für diesen Bereich ist kein Passwort hinterlegt. '
        . 'Die Datei pflege/passwort.php fehlt. Bitte melden Sie sich bei uns, '
        . 'bis dahin bleibt der Bereich gesperrt.';
}

if ($hash_vorhanden && !empty($_POST['passwort'])) {
    // Kurze Bremse gegen Durchprobieren. Eine Sekunde fällt einem Menschen
    // nicht auf und macht Rateversuche unbrauchbar.
    usleep(700000);
    if (password_verify((string) $_POST['passwort'], passwort_hash($PASSWORT_HASH))) {
        session_regenerate_id(true);
        $_SESSION['angemeldet'] = true;
        $_SESSION['marke'] = bin2hex(random_bytes(16));
    } else {
        $meldung = 'Passwort stimmt nicht.';
    }
}

$angemeldet = !empty($_SESSION['angemeldet']);
$datei = $_REQUEST['datei'] ?? 'index.html';
if (!in_array($datei, DATEIEN, true)) {
    $datei = 'index.html';
}

if ($angemeldet && ($_POST['speichern'] ?? '') !== '') {
    if (!hash_equals($_SESSION['marke'] ?? '', (string) ($_POST['marke'] ?? ''))) {
        $meldung = 'Die Sitzung ist abgelaufen. Bitte noch einmal speichern.';
    } else {
        $werte = [];
        foreach ($_POST['feld'] ?? [] as $name => $wert) {
            $werte[(string) $name] = (string) $wert;
        }
        /* Was gespeichert wurde und was nicht geklappt hat, wird
           getrennt gesammelt. Frueher hat die Meldung eines misslungenen
           Bildes die Erfolgsmeldung des Textes ueberschrieben. Der Betrieb
           las dann nur den Fehler und glaubte, sein Text sei verloren,
           obwohl er laengst gespeichert war. */
        $geschafft = [];

        if ($werte !== []) {
            [$erfolg, $textmeldung] = felder_schreiben_ueberall($datei, $werte);
            if ($erfolg) {
                $geschafft[] = $textmeldung;
            } else {
                $fehler[] = $textmeldung;
            }
        }

        // Alternativtexte der Bilder: kurze Beschreibung fuer Menschen, die
        // das Bild nicht sehen koennen, und fuer Google.
        foreach ($_POST['bildtext'] ?? [] as $name => $wert) {
            bildtext_schreiben($datei, (string) $name, (string) $wert);
        }

        // Hochgeladene Bilder. Eines nach dem anderen, damit eine
        // fehlerhafte Datei die anderen nicht mitreisst.
        $bilder_neu = 0;
        foreach ($_FILES['bild']['name'] ?? [] as $name => $dateiname) {
            if ($dateiname === '') {
                continue;
            }
            $feld = [
                'name' => $_FILES['bild']['name'][$name],
                'type' => $_FILES['bild']['type'][$name],
                'tmp_name' => $_FILES['bild']['tmp_name'][$name],
                'error' => $_FILES['bild']['error'][$name],
                'size' => $_FILES['bild']['size'][$name],
            ];
            [$bild_ok, $bild_meldung] = bild_schreiben($datei, (string) $name, $feld);
            if ($bild_ok) {
                $bilder_neu++;
            } else {
                $fehler[] = $bild_meldung;
            }
        }
        if ($bilder_neu === 1) {
            $geschafft[] = 'Das Bild ist ausgetauscht.';
        } elseif ($bilder_neu > 1) {
            $geschafft[] = $bilder_neu . ' Bilder sind ausgetauscht.';
        }

        $meldung = implode(' ', $geschafft);
        $erfolg = $meldung !== '';
    }
}

/* ---- Passwort aendern ---------------------------------------------- */
if ($angemeldet && ($_POST['passwort_aendern'] ?? '') !== '') {
    if (!hash_equals($_SESSION['marke'] ?? '', (string) ($_POST['marke'] ?? ''))) {
        $meldung = 'Die Sitzung ist abgelaufen. Bitte noch einmal versuchen.';
    } else {
        [$erfolg, $meldung] = passwort_setzen(
            (string) ($_POST['alt'] ?? ''),
            (string) ($_POST['neu'] ?? ''),
            (string) ($_POST['neu2'] ?? ''),
            $PASSWORT_HASH);
    }
}

/* ---- Stand zurueckholen -------------------------------------------- */
/* Loeschen einer Anfrage geht ueber zwei Schritte: erst fragen, dann
   loeschen. Eine Kundenanfrage darf nicht an einem Fehlklick haengen. */
$loeschfrage = '';
if ($angemeldet && ($_POST['anfrage_fragen'] ?? '') !== '') {
    $loeschfrage = (string) $_POST['anfrage_fragen'];
}

if ($angemeldet && ($_POST['anfrage_loeschen'] ?? '') !== '') {
    if (!hash_equals($_SESSION['marke'] ?? '', (string) ($_POST['marke'] ?? ''))) {
        $meldung = 'Die Sitzung ist abgelaufen. Bitte noch einmal versuchen.';
    } else {
        [$erfolg, $meldung] = anfragen_loeschen((string) $_POST['anfrage_loeschen']);
    }
}

if ($angemeldet && ($_POST['bild_zurueckholen'] ?? '') !== '') {
    if (!hash_equals($_SESSION['marke'] ?? '', (string) ($_POST['marke'] ?? ''))) {
        $meldung = 'Die Sitzung ist abgelaufen. Bitte noch einmal versuchen.';
    } else {
        [$erfolg, $meldung] = bild_zurueckholen(
            $datei, (string) $_POST['bild_zurueckholen']);
    }
}

if ($angemeldet && ($_POST['zurueckholen'] ?? '') !== '') {
    if (!hash_equals($_SESSION['marke'] ?? '', (string) ($_POST['marke'] ?? ''))) {
        $meldung = 'Die Sitzung ist abgelaufen. Bitte noch einmal versuchen.';
    } else {
        [$erfolg, $meldung] = sicherung_zurueckholen(
            $datei, (string) $_POST['zurueckholen']);
    }
}

$felder = $angemeldet ? felder_lesen($datei) : [];
$staende = $angemeldet ? sicherungen_liste($datei) : [];
$bilder = $angemeldet ? bilder_lesen($datei) : [];
$anfragen = $angemeldet ? anfragen_lesen() : [];
$bildstaende = $angemeldet ? bild_staende($datei) : [];

/* Vorschaubild ausliefern.
 * Nicht direkt verlinken: Wo die Website relativ zum Pflegebereich liegt,
 * ist von Hosting zu Hosting verschieden. Diese Zeilen reichen die Datei
 * durch und funktionieren in jeder Aufteilung. */
if ($angemeldet && isset($_GET['vorschau'])) {
    $name = (string) $_GET['vorschau'];
    $b = $bilder[$name] ?? null;
    $src = $b ? strtok($b['src'], '?') : false;
    $pfad = $src === false || $src === null ? '' : SEITEN . '/' . $src;
    $info = $pfad !== '' && !str_contains($src, '..') && is_file($pfad)
        ? @getimagesize($pfad) : false;
    if ($info === false) {
        http_response_code(404);
        exit;
    }
    header('Content-Type: ' . $info['mime']);
    header('Cache-Control: no-store');
    readfile($pfad);
    exit;
}
?>
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Inhalte pflegen</title>
<style>
:root{--grund:#FAF8F4;--flaeche:#fff;--basis:#16181C;--text:#3A3A38;
 --gedaempft:#6B665C;--akzent:#A8681B;--linie:#E4DED4;--gut:#3E6B54;--rot:#8A2C1E;
 --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--grund);color:var(--text);font-family:var(--sans);
 font-size:17px;line-height:1.6}
.bahn{max-width:44rem;margin:0 auto;padding:0 1.25rem}
header{background:var(--flaeche);border-bottom:2px solid var(--akzent);
 padding:1.5rem 0}
header .bahn{display:flex;flex-wrap:wrap;gap:.6rem 1rem;align-items:baseline;
 justify-content:space-between}
h1{font-size:1.5rem;margin:0;color:var(--basis)}
a{color:var(--akzent)}
main{padding:2rem 0 4rem}
.reiter{display:flex;flex-wrap:wrap;gap:.5rem;margin:0 0 1.75rem;padding:0;
 list-style:none}
.reiter a{display:block;padding:.5rem .9rem;border:1px solid var(--linie);
 border-radius:4px;text-decoration:none;color:var(--text);background:var(--flaeche)}
.reiter a[aria-current]{border-color:var(--akzent);color:var(--akzent);font-weight:600}
label{display:block;margin:0 0 1.4rem}
label b{display:block;font-weight:600;color:var(--basis);margin-bottom:.35rem}
input[type=text],input[type=password],textarea{width:100%;font:inherit;
 padding:.7rem .8rem;border:1px solid var(--linie);border-radius:4px;
 background:var(--flaeche);color:var(--text)}
textarea{min-height:5.5rem;resize:vertical}
input:focus,textarea:focus{outline:2px solid var(--akzent);outline-offset:1px}
button{font:inherit;font-weight:600;padding:.75rem 1.5rem;border:0;
 border-radius:4px;background:var(--akzent);color:#fff;cursor:pointer}
button:hover{background:#8C5514}
h2{font-size:1.15rem;margin:2rem 0 .4rem;color:var(--basis)}
.bild{display:flex;gap:1rem;align-items:flex-start;padding:1rem 0;
 border-top:1px solid var(--linie)}
.bild img{width:120px;height:90px;object-fit:cover;border-radius:4px;
 background:var(--linie);flex:none}
.bild-felder{flex:1;min-width:0}
.bild-felder label{margin-bottom:.6rem}
.bild-staende{margin-top:.4rem;font-size:14px}
.bild-staende b{display:block;color:var(--gedaempft);font-weight:600;margin-bottom:.2rem}
.bild-staende ul{list-style:none;margin:0;padding:0}
.bild-staende li{display:flex;align-items:center;justify-content:space-between;
 gap:.75rem;padding:.25rem 0;border-bottom:1px solid var(--linie)}
.bild-staende li:last-child{border-bottom:none}
@media(max-width:520px){.bild{flex-direction:column}.bild img{width:100%;height:auto}}
.meldung{padding:.85rem 1rem;border-radius:4px;margin:0 0 1.5rem;
 border-left:4px solid var(--rot);background:#F6E4DF;color:var(--rot)}
.meldung.gut{border-left-color:var(--gut);background:#E7EBE3;color:var(--gut)}
.hinweis{color:var(--gedaempft);font-size:15px;margin:0 0 1.75rem}
.staende ul{list-style:none;margin:0 0 2rem;padding:0}
.aeltere{margin:-1.25rem 0 2rem}
.aeltere summary{cursor:pointer;color:var(--akzent);font-weight:600;font-size:15px;
 padding:.35rem 0}
.aeltere ul{margin-top:.4rem}
.staende li{display:flex;align-items:center;justify-content:space-between;
 gap:1rem;padding:.6rem 0;border-bottom:1px solid var(--linie);font-size:15px}
button.leise{background:transparent;color:var(--akzent);font-weight:600;
 padding:.35rem .7rem;border:1px solid var(--linie);border-radius:4px}
button.leise:hover{background:var(--akzent);color:#fff}
.passwort{max-width:24rem;margin-bottom:2rem}
.anmelden{max-width:22rem}
.anfragen{margin:0 0 2.5rem}
.anfragen h2{margin-top:0}
.anfragen article{border:1px solid var(--linie);border-left:4px solid var(--akzent);
 border-radius:4px;padding:.9rem 1.1rem;margin-bottom:.9rem;background:#fff}
.anfragen .kopf{display:flex;justify-content:space-between;gap:1rem;
 flex-wrap:wrap;margin:0 0 .35rem}
.anfragen .kopf span{color:var(--gedaempft);font-size:14px;white-space:nowrap}
.anfragen .wege{margin:0 0 .6rem;font-size:15px}
.anfragen .wege a,.anfragen .wege span{margin-right:1rem}
.anfragen .wege span{color:var(--gedaempft)}
.anfragen .text{margin:0;white-space:normal}
.anfragen .loeschen{margin:.6rem 0 0;text-align:right}
.anfragen .frage{margin:.6rem 0 0;padding:.6rem .8rem;border-radius:4px;
 background:#F6E4DF;color:var(--rot);font-size:15px}
.anfragen .frage button{margin-left:.6rem}
@media(max-width:520px){.anfragen .kopf span{white-space:normal}}
footer{border-top:1px solid var(--linie);color:var(--gedaempft);font-size:14px}
footer .bahn{padding:1.25rem}
</style>
</head>
<body>
<header><div class="bahn">
  <h1>Inhalte pflegen</h1>
  <?php if ($angemeldet): ?><a href="?abmelden=1">Abmelden</a><?php endif; ?>
</div></header>

<main class="bahn">
<?php if ($meldung): ?>
  <p class="meldung<?= $erfolg ? ' gut' : '' ?>"><?= htmlspecialchars($meldung) ?></p>
<?php endif; ?>
<?php if ($fehler): ?>
  <p class="meldung"><?= htmlspecialchars(implode(' ', array_unique($fehler))) ?></p>
<?php endif; ?>

<?php if (!$angemeldet): ?>
  <form method="post" class="anmelden">
    <label><b>Passwort</b>
      <input type="password" name="passwort" autocomplete="current-password" autofocus>
    </label>
    <button type="submit">Anmelden</button>
  </form>
<?php else: ?>
  <?php if ($anfragen): $sichtbar = array_slice($anfragen, 0, 20); ?>
    <form method="post" class="anfragen">
      <input type="hidden" name="datei" value="<?= htmlspecialchars($datei) ?>">
      <input type="hidden" name="marke" value="<?= htmlspecialchars($_SESSION['marke']) ?>">
      <h2><?= count($anfragen) ?> <?= count($anfragen) === 1 ? 'Anfrage' : 'Anfragen' ?> über die Website</h2>
      <?php foreach ($sichtbar as $a): ?>
        <article>
          <p class="kopf">
            <b><?= htmlspecialchars($a['name'] !== '' ? $a['name'] : 'Ohne Namen') ?></b>
            <span><?= htmlspecialchars($a['eingang']) ?></span>
          </p>
          <?php
            /* Verlinkt wird nur, was auch wirklich eine Adresse oder eine
               Nummer ist. Was jemand sonst in das Feld geschrieben hat,
               steht als Text da und wird nicht anklickbar. */
            $mailziel = filter_var($a['mail'], FILTER_VALIDATE_EMAIL) ? $a['mail'] : '';
            $telziel = $a['telefon'] !== '' ? telefon_ziel($a['telefon']) : '';
          ?>
          <?php if ($a['mail'] !== '' || $a['telefon'] !== ''): ?>
            <p class="wege">
              <?php if ($a['mail'] !== ''): ?>
                <?php if ($mailziel !== ''): ?>
                  <a href="mailto:<?= htmlspecialchars($mailziel) ?>"><?= htmlspecialchars($a['mail']) ?></a>
                <?php else: ?>
                  <span><?= htmlspecialchars($a['mail']) ?></span>
                <?php endif; ?>
              <?php endif; ?>
              <?php if ($a['telefon'] !== ''): ?>
                <?php if ($telziel !== ''): ?>
                  <a href="tel:<?= htmlspecialchars($telziel) ?>"><?= htmlspecialchars($a['telefon']) ?></a>
                <?php else: ?>
                  <span><?= htmlspecialchars($a['telefon']) ?></span>
                <?php endif; ?>
              <?php endif; ?>
            </p>
          <?php endif; ?>
          <p class="text"><?= nl2br(htmlspecialchars($a['nachricht'])) ?></p>
          <?php if ($loeschfrage === $a['kennung']): ?>
            <p class="frage">Diese Anfrage wirklich löschen? Sie ist danach weg.
              <button type="submit" name="anfrage_loeschen"
                      value="<?= htmlspecialchars($a['kennung']) ?>">Ja, löschen</button>
              <button type="submit" name="abbrechen" value="1" class="leise">Abbrechen</button>
            </p>
          <?php else: ?>
            <p class="loeschen">
              <button type="submit" name="anfrage_fragen"
                      value="<?= htmlspecialchars($a['kennung']) ?>" class="leise">löschen</button>
            </p>
          <?php endif; ?>
        </article>
      <?php endforeach; ?>
      <?php if (count($anfragen) > 20): ?>
        <p class="hinweis">Angezeigt sind die letzten 20. Die älteren stehen
        auf dem Server in der Datei pflege/anfragen.php.</p>
      <?php endif; ?>
    </form>
  <?php endif; ?>

  <ul class="reiter">
    <?php foreach (DATEIEN as $d): ?>
      <li><a href="?datei=<?= urlencode($d) ?>"
             <?= $d === $datei ? 'aria-current="page"' : '' ?>>
        <?= htmlspecialchars(seiten_name($d)) ?></a></li>
    <?php endforeach; ?>
  </ul>

  <?php if (!$felder): ?>
    <p class="hinweis">Auf dieser Seite ist nichts zum Bearbeiten
    freigegeben.</p>
  <?php else: ?>
    <p class="hinweis">Ändern Sie, was Sie brauchen, und klicken Sie unten auf
    Speichern. Die Änderung ist sofort auf der Website sichtbar. Von jedem
    Stand wird automatisch eine Sicherung angelegt.</p>
    <form method="post" enctype="multipart/form-data">
      <input type="hidden" name="datei" value="<?= htmlspecialchars($datei) ?>">
      <input type="hidden" name="marke" value="<?= htmlspecialchars($_SESSION['marke']) ?>">
      <?php foreach ($felder as $name => $wert): ?>
        <label>
          <b><?= htmlspecialchars(feld_beschriftung($name)) ?></b>
          <?php if (mb_strlen($wert) > 70): ?>
            <textarea name="feld[<?= htmlspecialchars($name) ?>]"><?= htmlspecialchars($wert) ?></textarea>
          <?php else: ?>
            <input type="text" name="feld[<?= htmlspecialchars($name) ?>]"
                   value="<?= htmlspecialchars($wert) ?>">
          <?php endif; ?>
        </label>
      <?php endforeach; ?>
      <?php if ($bilder): ?>
        <h2>Bilder</h2>
        <p class="hinweis">Ein Bild aussuchen und unten speichern. Zu grosse
        Bilder werden automatisch verkleinert, Sie muessen nichts
        vorbereiten. Bleibt das Feld leer, bleibt das bisherige Bild.</p>
        <?php foreach ($bilder as $name => $b): ?>
          <div class="bild">
            <img src="?datei=<?= urlencode($datei) ?>&amp;vorschau=<?= urlencode((string) $name) ?>" alt="">
            <div class="bild-felder">
              <label><b><?= htmlspecialchars(feld_beschriftung($name)) ?></b>
                <input type="file" name="bild[<?= htmlspecialchars($name) ?>]"
                       accept="image/jpeg,image/png,image/webp">
              </label>
              <label><b>Bildbeschreibung</b>
                <input type="text" name="bildtext[<?= htmlspecialchars($name) ?>]"
                       value="<?= htmlspecialchars($b['alt']) ?>">
              </label>
              <?php if (!empty($bildstaende[$name])): ?>
                <div class="bild-staende">
                  <b>Vorheriges Bild zurückholen</b>
                  <ul>
                    <?php foreach ($bildstaende[$name] as $st): ?>
                      <li><span><?= htmlspecialchars($st['zeit']) ?></span>
                        <button type="submit" name="bild_zurueckholen"
                                value="<?= htmlspecialchars($st['datei']) ?>"
                                class="leise" formnovalidate>zurückholen</button></li>
                    <?php endforeach; ?>
                  </ul>
                </div>
              <?php endif; ?>
            </div>
          </div>
        <?php endforeach; ?>
      <?php endif; ?>
      <button type="submit" name="speichern" value="1">Speichern</button>
    </form>

    <?php if ($staende): ?>
      <h2>Frühere Stände</h2>
      <p class="hinweis">Etwas versehentlich gelöscht oder überschrieben?
      Hier holen Sie den Stand von vorher zurück. Der jetzige wird dabei
      gesichert, Sie können es also auch wieder rückgängig machen.</p>
      <form method="post" class="staende">
        <input type="hidden" name="datei" value="<?= htmlspecialchars($datei) ?>">
        <input type="hidden" name="marke" value="<?= htmlspecialchars($_SESSION['marke']) ?>">
        <ul>
          <?php foreach (array_slice($staende, 0, 8) as $st): ?>
            <li><span><?= htmlspecialchars($st['zeit']) ?></span>
              <button type="submit" name="zurueckholen"
                      value="<?= htmlspecialchars($st['datei']) ?>"
                      class="leise">zurückholen</button></li>
          <?php endforeach; ?>
        </ul>
        <?php $aeltere = array_slice($staende, 8); ?>
        <?php if ($aeltere): ?>
          <details class="aeltere">
            <summary><?= count($aeltere) ?> ältere <?= count($aeltere) === 1 ? 'Stand' : 'Stände' ?></summary>
            <ul>
              <?php foreach ($aeltere as $st): ?>
                <li><span><?= htmlspecialchars($st['zeit']) ?></span>
                  <button type="submit" name="zurueckholen"
                          value="<?= htmlspecialchars($st['datei']) ?>"
                          class="leise">zurückholen</button></li>
              <?php endforeach; ?>
            </ul>
          </details>
        <?php endif; ?>
      </form>
    <?php endif; ?>

    <h2>Passwort ändern</h2>
    <p class="hinweis">Mindestens acht Zeichen. Das Passwort steht nirgends
    auf dem Server, auch wir können es nicht nachsehen.</p>
    <form method="post" class="passwort">
      <input type="hidden" name="datei" value="<?= htmlspecialchars($datei) ?>">
      <input type="hidden" name="marke" value="<?= htmlspecialchars($_SESSION['marke']) ?>">
      <label><b>Bisheriges Passwort</b>
        <input type="password" name="alt" autocomplete="current-password"></label>
      <label><b>Neues Passwort</b>
        <input type="password" name="neu" autocomplete="new-password"></label>
      <label><b>Neues Passwort wiederholen</b>
        <input type="password" name="neu2" autocomplete="new-password"></label>
      <button type="submit" name="passwort_aendern" value="1">Passwort ändern</button>
    </form>
  <?php endif; ?>
<?php endif; ?>
</main>

<footer><div class="bahn">
  Wenn etwas nicht stimmt: 0152&thinsp;01560005. Wir können jeden Stand der
  letzten Wochen zurückholen.
</div></footer>
</body>
</html>
