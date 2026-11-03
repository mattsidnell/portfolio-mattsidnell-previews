<?php
/**
 * Private administration dashboard for mattsidnell.co.uk.
 *
 * Internal to the PHP-FPM backend. Requires a separately provisioned random
 * password; no default or source-controlled credentials are supported.
 */
declare(strict_types=1);

const ADMIN_SECRET_PATH = '/data/portfolio-admin-password.hash';

function adminSecretPath(): string {
    return getenv('PORTFOLIO_ADMIN_PASSWORD_FILE') ?: ADMIN_SECRET_PATH;
}

const ADMIN_IDLE_SECONDS = 1800;
const ADMIN_ABSOLUTE_SECONDS = 28800;
const ADMIN_MAX_FAILURES = 5;
const ADMIN_BLOCK_SECONDS = 900;

function adminEscape(mixed $value): string {
    return htmlspecialchars((string)($value ?? ''), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function adminSecret(): ?string {
    if (!is_file(adminSecretPath()) || !is_readable(adminSecretPath())) return null;
    $hash = trim((string)file_get_contents(adminSecretPath()));
    return str_starts_with($hash, '$2y$') || str_starts_with($hash, '$argon2')
        ? $hash : null;
}

function adminProvisionCli(array $args): never {
    if (PHP_SAPI !== 'cli' || !in_array($args[1] ?? '', ['provision', 'rotate'], true)) exit(2);
    $mode = $args[1];
    if ($mode === 'provision' && file_exists(adminSecretPath())) {
        fwrite(STDERR, "Admin password already provisioned. Nothing changed.\n");
        exit(3);
    }
    if ($mode === 'rotate' && !file_exists(adminSecretPath())) {
        fwrite(STDERR, "No admin password exists. Use provision.\n");
        exit(3);
    }
    $password = bin2hex(random_bytes(24)); // 192 random bits
    $hash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
    if ($hash === false) throw new RuntimeException('Password hashing failed');
    $dir = dirname(adminSecretPath());
    if (!is_dir($dir) || !is_writable($dir)) {
        fwrite(STDERR, "Private data directory is unavailable.\n");
        exit(3);
    }
    $temporary = $dir . '/.portfolio-admin-' . bin2hex(random_bytes(12));
    $handle = fopen($temporary, 'x');
    if ($handle === false) throw new RuntimeException('Unable to create private credential file');
    chmod($temporary, 0600);
    fwrite($handle, $hash . "\n");
    fflush($handle);
    fclose($handle);
    rename($temporary, adminSecretPath());
    chmod(adminSecretPath(), 0600);
    echo "New private dashboard password (shown only once):\n" . $password . "\n";
    echo "Save it in your password manager. It cannot be recovered from the hash.\n";
    exit;
}

function adminSendHeaders(): void {
    header('Content-Type: text/html; charset=utf-8');
    header('Cache-Control: private, no-store, max-age=0');
    header('Pragma: no-cache');
    header('X-Robots-Tag: noindex, nofollow, noarchive');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: no-referrer');
    header('X-Frame-Options: DENY');
    header("Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'");
}

function adminSession(): void {
    ini_set('session.use_strict_mode', '1');
    ini_set('session.use_only_cookies', '1');
    ini_set('session.use_trans_sid', '0');
    ini_set('session.gc_maxlifetime', (string)ADMIN_ABSOLUTE_SECONDS);
    session_name('__Host-PortfolioAdmin');
    session_set_cookie_params([
        'lifetime' => 0,
        'path' => '/',
        'secure' => true,
        'httponly' => true,
        'samesite' => 'Strict',
    ]);
    session_start();
    if (empty($_SESSION['csrf']) || !is_string($_SESSION['csrf'])) {
        $_SESSION['csrf'] = bin2hex(random_bytes(24));
    }
}

function adminAuthed(string $secret): bool {
    if (empty($_SESSION['portfolio_auth']) ||
        !hash_equals(hash('sha256', $secret), (string)($_SESSION['credential_version'] ?? ''))) {
        return false;
    }
    $now = time();
    if ($now - (int)($_SESSION['last_seen'] ?? 0) > ADMIN_IDLE_SECONDS ||
        $now - (int)($_SESSION['authenticated_at'] ?? 0) > ADMIN_ABSOLUTE_SECONDS) {
        unset($_SESSION['portfolio_auth'], $_SESSION['credential_version']);
        return false;
    }
    $_SESSION['last_seen'] = $now;
    return true;
}

function adminPostAuthorised(): bool {
    $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
    if (!in_array($origin, ORIGINS, true)) return false;
    $fetch = $_SERVER['HTTP_SEC_FETCH_SITE'] ?? '';
    if ($fetch !== '' && $fetch !== 'same-origin') return false;
    $provided = $_POST['csrf'] ?? '';
    return is_string($provided) && hash_equals((string)$_SESSION['csrf'], $provided);
}

function adminLoginKey(string $secret): string {
    $ip = (string)($_SERVER['HTTP_X_REAL_IP'] ?? $_SERVER['REMOTE_ADDR'] ?? 'unknown');
    return hash_hmac('sha256', $ip, $secret);
}

function adminLimit(PDO $db, string $key, bool $failed = false): bool {
    $db->exec('CREATE TABLE IF NOT EXISTS portfolio_admin_attempts (
        key_hash TEXT PRIMARY KEY,
        failures INTEGER NOT NULL,
        blocked_until INTEGER NOT NULL,
        updated_at INTEGER NOT NULL
    )');
    $now = time();
    $db->prepare('DELETE FROM portfolio_admin_attempts WHERE updated_at < ?')
        ->execute([$now - 86400]);
    $db->beginTransaction();
    try {
        $q = $db->prepare('SELECT failures,blocked_until,updated_at FROM portfolio_admin_attempts WHERE key_hash=?');
        $q->execute([$key]);
        $row = $q->fetch();
        if ($row && (int)$row['blocked_until'] > $now) {
            $db->commit();
            return false;
        }
        if ($failed) {
            $failures = $row && ($now - (int)$row['updated_at']) < ADMIN_BLOCK_SECONDS
                ? ((int)$row['failures'] + 1) : 1;
            $blocked = $failures >= ADMIN_MAX_FAILURES ? $now + ADMIN_BLOCK_SECONDS : 0;
            $q = $db->prepare('INSERT INTO portfolio_admin_attempts(key_hash,failures,blocked_until,updated_at)
                VALUES(?,?,?,?) ON CONFLICT(key_hash) DO UPDATE SET
                failures=excluded.failures, blocked_until=excluded.blocked_until, updated_at=excluded.updated_at');
            $q->execute([$key, $failures, $blocked, $now]);
        } elseif ($row) {
            $db->prepare('DELETE FROM portfolio_admin_attempts WHERE key_hash=?')->execute([$key]);
        }
        $db->commit();
        return true;
    } catch (Throwable $e) {
        if ($db->inTransaction()) $db->rollBack();
        throw $e;
    }
}

function adminStyle(): void {
    echo <<<'HTML'
<style>
:root{color-scheme:light;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#122f40;background:#f2fbfe}
*{box-sizing:border-box}body{margin:0;line-height:1.5}a{color:#087e9e}button,select,input{font:inherit}
button{background:#10384a;color:white;border:0;border-radius:8px;padding:11px 18px;cursor:pointer}
button:hover{background:#17627a}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #20bad4;outline-offset:3px}
input{width:100%;border:1px solid #a8cad2;border-radius:8px;padding:13px;background:white}
header{background:#0c2535;color:#e5fcff;padding:22px max(24px,calc((100vw - 1150px)/2))}
header .head{display:flex;align-items:center;justify-content:space-between;gap:22px;flex-wrap:wrap}
header h1{font-size:24px;margin:0}header p{margin:0;color:#a5d5de}header button{background:#255064}
main{max-width:1190px;margin:0 auto;padding:28px 24px 80px}h2{font-size:19px;margin:0 0 15px}
section{margin:26px 0}.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}
.card{background:white;border:1px solid #cbe6ea;border-radius:12px;padding:20px}
.card .big{font-size:34px;font-weight:800;letter-spacing:-.05em}.card small{color:#476c78}
.panel{background:white;border:1px solid #cbe6ea;border-radius:12px;padding:20px;overflow:auto}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;vertical-align:top;padding:12px 10px;border-bottom:1px solid #e2eff2}
th{color:#3c6570;font-size:12px;letter-spacing:.06em;text-transform:uppercase}
tbody tr:last-child td{border-bottom:0}.empty{color:#67848c;padding:14px 0}
.badge{display:inline-block;background:#dcf5fa;border-radius:20px;padding:3px 9px;font-size:12px}
.metrics span{display:block;height:8px;min-width:1px;background:#20c5df;border-radius:8px}
.metrics td:first-child{width:45%}.metrics td:last-child{text-align:right;font-variant-numeric:tabular-nums}
.login{max-width:430px;margin:9vh auto;background:white;border:1px solid #cbe6ea;border-radius:14px;padding:30px}
.login h1{margin:0 0 10px;font-size:26px}.login p{color:#4b7582}
.login label{display:block;font-weight:700;margin-bottom:8px}.login button{width:100%;margin-top:16px}
.note{font-size:13px;color:#5b7880}.error{background:#ffe5df;color:#8d2b24;border-radius:8px;padding:12px}
details{max-width:440px}summary{cursor:pointer;color:#087e9e;font-weight:650}
.message{white-space:pre-wrap;overflow-wrap:anywhere;margin-top:12px;padding:13px;background:#f1f7f9;border-radius:7px}
nav a{color:#e2fbff;text-decoration:none;margin-right:18px}
nav .active{color:#66ddef;border-bottom:2px solid currentColor}
footer{padding:20px 24px;color:#54727b;text-align:center;font-size:13px}
@media(max-width:820px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}.grid{grid-template-columns:1fr}}
@media(max-width:460px){.cards{grid-template-columns:1fr 1fr;gap:8px}.card{padding:12px}.card .big{font-size:27px}
main{padding:18px 12px 60px}header{padding:16px}th,td{padding:9px 6px;font-size:12px}}
</style>
HTML;
}

function adminLoginScreen(string $message = ''): never {
    adminSendHeaders();
    http_response_code($message ? 401 : 200);
    echo '<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        . '<title>Sign in | Portfolio admin</title></head><body>';
    adminStyle();
    echo '<main class="login"><h1>Portfolio admin</h1><p>Private enquiries and website statistics.</p>';
    if ($message) echo '<p class="error" role="alert">' . adminEscape($message) . '</p>';
    echo '<form method="post" action="/admin/login">'
        . '<input type="hidden" name="csrf" value="' . adminEscape($_SESSION['csrf']) . '">'
        . '<label for="admin-password">Password</label>'
        . '<input id="admin-password" type="password" name="password" required autofocus autocomplete="current-password" maxlength="200">'
        . '<button type="submit">Sign in</button></form>'
        . '<p class="note">Protected by HTTPS and an automatically expiring session.</p></main></body></html>';
    exit;
}

function adminMetric(PDO $db, string $kind, string $from): int {
    $q = $db->prepare('SELECT COALESCE(SUM(count),0) FROM analytics_daily WHERE day >= ? AND kind = ?');
    $q->execute([$from, $kind]);
    return (int)$q->fetchColumn();
}

function adminGroup(PDO $db, string $kind, string $column, string $from): array {
    if (!in_array($column, ['target', 'source'], true)) throw new InvalidArgumentException();
    $q = $db->prepare("SELECT $column AS label, SUM(count) AS total FROM analytics_daily
        WHERE day >= ? AND kind = ? GROUP BY $column ORDER BY total DESC LIMIT 12");
    $q->execute([$from, $kind]);
    return $q->fetchAll();
}

function adminRowsTable(array $rows): void {
    if (!$rows) { echo '<p class="empty">No activity recorded in this period.</p>'; return; }
    $max = max(1, (int)$rows[0]['total']);
    echo '<table class="metrics"><tbody>';
    foreach ($rows as $row) {
        $label = adminEscape(str_replace('-', ' ', (string)$row['label']));
        $value = (int)$row['total'];
        echo '<tr><td>' . $label . '</td><td><span style="width:' .
            number_format(100 * $value / $max, 1, '.', '') . '%"></span></td><td>' .
            number_format($value) . '</td></tr>';
    }
    echo '</tbody></table>';
}

function adminDashboard(): never {
    $days = (int)($_GET['days'] ?? 30);
    if (!in_array($days, [7, 30, 90], true)) $days = 30;
    $from = utcNow()->modify('-' . ($days - 1) . ' days')->format('Y-m-d');
    try {
        $db = connection();
        $metrics = [
            'Views' => adminMetric($db, 'pageview', $from),
            'Project clicks' => adminMetric($db, 'project_click', $from),
            'Form opened' => adminMetric($db, 'contact_open', $from),
            'Forms saved' => adminMetric($db, 'enquiry_saved', $from),
        ];
        $projects = adminGroup($db, 'project_click', 'target', $from);
        $sources = adminGroup($db, 'pageview', 'source', $from);
        $q = $db->prepare('SELECT id,created_at,sender_name,sender_email,company,enquiry_type,message,notification_status
            FROM enquiries WHERE created_at >= ? ORDER BY created_at DESC LIMIT 50');
        $q->execute([$from . 'T00:00:00']);
        $enquiries = $q->fetchAll();
    } catch (Throwable $e) {
        error_log('portfolio private admin read failed: ' . get_class($e));
        http_response_code(503);
        adminSendHeaders();
        echo 'Private reporting temporarily unavailable.';
        exit;
    }
    adminSendHeaders();
    echo '<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        . '<title>Portfolio admin | Matt Sidnell</title></head><body>';
    adminStyle();
    echo '<header><div class="head"><div><h1>Portfolio admin</h1><p>mattsidnell.co.uk · private overview</p></div>'
        . '<form method="post" action="/admin/logout"><input type="hidden" name="csrf" value="' .
        adminEscape($_SESSION['csrf']) . '"><button type="submit">Sign out</button></form></div></header>'
        . '<main><nav>';
    foreach ([7,30,90] as $value) {
        echo '<a class="' . ($days === $value ? 'active' : '') . '" href="/admin?days=' . $value . '">' .
            $value . ' days</a>';
    }
    echo '</nav><section><h2>Website activity</h2><div class="cards">';
    foreach ($metrics as $label => $value) {
        echo '<article class="card"><small>' . adminEscape($label) . '</small><div class="big">' .
            number_format($value) . '</div></article>';
    }
    echo '</div><p class="note">Anonymous aggregate events, not unique visitors. Google Analytics has a separate consent-controlled dashboard.</p></section>';
    echo '<section class="grid"><div class="panel"><h2>Popular portfolio projects</h2>';
    adminRowsTable($projects);
    echo '</div><div class="panel"><h2>Traffic sources</h2>';
    adminRowsTable($sources);
    echo '</div></section><section class="panel"><h2>Recent enquiries</h2>';
    if (!$enquiries) {
        echo '<p class="empty">No genuine or test enquiries recorded for this period.</p>';
    } else {
        echo '<table><thead><tr><th>Received (UTC)</th><th>Contact</th><th>Type</th><th>Message</th><th>Notification</th></tr></thead><tbody>';
        foreach ($enquiries as $entry) {
            $synthetic = str_starts_with((string)$entry['id'], 'php-cutover-smoke-');
            echo '<tr><td>' . adminEscape(substr((string)$entry['created_at'], 0, 16)) . '</td>'
                . '<td><strong>' . adminEscape($entry['sender_name']) . '</strong><div>' .
                adminEscape($entry['sender_email']) . '</div><small>' . adminEscape($entry['company']) . '</small></td>'
                . '<td>' . adminEscape($entry['enquiry_type']) .
                ($synthetic ? '<p class="badge">Synthetic test</p>' : '') . '</td>'
                . '<td><details><summary>View message</summary><div class="message">' .
                adminEscape($entry['message']) . '</div></details></td>'
                . '<td>' . adminEscape(str_replace('_', ' ', (string)$entry['notification_status'])) .
                '</td></tr>';
        }
        echo '</tbody></table>';
    }
    echo '<p class="note">Read-only dashboard. A saved enquiry is not proof an email notification was sent. '
        . 'Access expires after 30 minutes of inactivity.</p></section></main>'
        . '<footer>Private portfolio reporting · All times UTC</footer></body></html>';
    exit;
}

function handleAdmin(): never {
    if (PHP_SAPI === 'cli') exit(2);
    $path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
    if (!in_array($path, ['/admin','/admin/','/admin/login','/admin/logout'], true)) {
        http_response_code(404);
        exit;
    }
    $method = $_SERVER['REQUEST_METHOD'] ?? '';
    if (!in_array($method, ['GET', 'POST'], true)) {
        http_response_code(405);
        header('Allow: GET, POST');
        exit;
    }
    $secret = adminSecret();
    if (!$secret) {
        adminSendHeaders();
        http_response_code(503);
        echo 'Private administration is not configured.';
        exit;
    }
    adminSession();
    if ($path === '/admin/login' && $method === 'POST') {
        if (!adminPostAuthorised()) {
            http_response_code(403);
            exit;
        }
        $password = $_POST['password'] ?? '';
        if (!is_string($password) || strlen($password) > 200) adminLoginScreen('Invalid credentials.');
        try {
            $db = connection();
            $key = adminLoginKey($secret);
            if (!adminLimit($db, $key)) {
                http_response_code(429);
                header('Retry-After: 900');
                exit('Too many attempts. Try again later.');
            }
            if (!password_verify($password, $secret)) {
                adminLimit($db, $key, true);
                adminLoginScreen('Invalid credentials.');
            }
            adminLimit($db, $key, false);
        } catch (Throwable $e) {
            error_log('portfolio admin login unavailable: ' . get_class($e));
            http_response_code(503);
            exit('Sign in temporarily unavailable.');
        }
        session_regenerate_id(true);
        $_SESSION['portfolio_auth'] = true;
        $_SESSION['credential_version'] = hash('sha256', $secret);
        $_SESSION['authenticated_at'] = time();
        $_SESSION['last_seen'] = time();
        $_SESSION['csrf'] = bin2hex(random_bytes(24));
        header('Location: /admin', true, 303);
        exit;
    }
    if ($path === '/admin/logout' && $method === 'POST') {
        if (!adminPostAuthorised()) { http_response_code(403); exit; }
        $_SESSION = [];
        session_regenerate_id(true);
        session_destroy();
        header('Location: /admin', true, 303);
        exit;
    }
    if (!in_array($path, ['/admin','/admin/'], true) || $method !== 'GET') {
        http_response_code(405);
        exit;
    }
    if (!adminAuthed($secret)) adminLoginScreen();
    adminDashboard();
}

if (PHP_SAPI === 'cli' && in_array($argv[1] ?? '', ['provision', 'rotate'], true)) adminProvisionCli($argv);
