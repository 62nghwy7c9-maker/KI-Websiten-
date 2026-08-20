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
require __DIR__ . '/inhalt.php';

/* ---- Zugang ---------------------------------------------------------
 * Ein Passwort für den Betrieb, als Hash hinterlegt. Erzeugt wird der Hash
 * einmalig mit:  php -r "echo password_hash('IhrPasswort', PASSWORD_DEFAULT);"
 * Im Klartext steht das Passwort nirgends — auch nicht bei uns.
 */
$PASSWORT_HASH = getenv('WG_PFLEGE_HASH')
    ?: '$2y$12$h4R2JvM2UlDA4HtrSNSG3.M2vh4gg4f2g8mMbZXUjOG30sjbbwkG2'; // "muster"

session_start();
$meldung = '';
$erfolg = false;

if (isset($_GET['abmelden'])) {
    session_destroy();
    header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?'));
    exit;
}

if (!empty($_POST['passwort'])) {
    // Kurze Bremse gegen Durchprobieren. Eine Sekunde fällt einem Menschen
    // nicht auf und macht Rateversuche unbrauchbar.
    usleep(700000);
    if (password_verify((string) $_POST['passwort'], $PASSWORT_HASH)) {
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
        [$erfolg, $meldung] = felder_schreiben_ueberall($datei, $werte);

        // Alternativtexte der Bilder — kurze Beschreibung für Menschen, die
        // das Bild nicht sehen können, und für Google.
        foreach ($_POST['bildtext'] ?? [] as $name => $wert) {
            bildtext_schreiben($datei, (string) $name, (string) $wert);
        }

        // Hochgeladene Bilder. Eines nach dem anderen, damit eine
        // fehlerhafte Datei die anderen nicht mitreisst.
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
            if (!$bild_ok) {
                $erfolg = false;
                $meldung = $bild_meldung;
            }
        }
    }
}

$felder = $angemeldet ? felder_lesen($datei) : [];
$bilder = $angemeldet ? bilder_lesen($datei) : [];

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
@media(max-width:520px){.bild{flex-direction:column}.bild img{width:100%;height:auto}}
.meldung{padding:.85rem 1rem;border-radius:4px;margin:0 0 1.5rem;
 border-left:4px solid var(--rot);background:#F6E4DF;color:var(--rot)}
.meldung.gut{border-left-color:var(--gut);background:#E7EBE3;color:var(--gut)}
.hinweis{color:var(--gedaempft);font-size:15px;margin:0 0 1.75rem}
.anmelden{max-width:22rem}
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

<?php if (!$angemeldet): ?>
  <form method="post" class="anmelden">
    <label><b>Passwort</b>
      <input type="password" name="passwort" autocomplete="current-password" autofocus>
    </label>
    <button type="submit">Anmelden</button>
  </form>
<?php else: ?>
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
        Bilder werden automatisch verkleinert &mdash; Sie muessen nichts
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
            </div>
          </div>
        <?php endforeach; ?>
      <?php endif; ?>
      <button type="submit" name="speichern" value="1">Speichern</button>
    </form>
  <?php endif; ?>
<?php endif; ?>
</main>

<footer><div class="bahn">
  Wenn etwas nicht stimmt: 0162&thinsp;3242260. Wir können jeden Stand der
  letzten Wochen zurückholen.
</div></footer>
</body>
</html>
