<?php
/**
 * Private contact and aggregate analytics API for mattsidnell.co.uk.
 * Compatible with the original Python service and SQLite schema.
 * Never outputs private records over HTTP.
 */
declare(strict_types=1);

const MAX_BODY = 16384;
const RETAIN_DAYS = 180;
const ANALYTICS_RETAIN_DAYS = 365;
const ORIGINS = ['https://mattsidnell.co.uk', 'https://www.mattsidnell.co.uk'];
const ENQUIRY_TYPES = [
    'Contract opportunity', 'Agency overflow', 'Website project', 'Custom software', 'General enquiry',
];
const STAT_EVENTS = [
    'pageview' => ['home', 'privacy'],
    'project_click' => [
        'grinders', 'lyneham-flying-club', 'sidnell', 'pixlwrk', 'professional-structures',
        'web-designer-direct', 'digipixel', 'sunnyside', 'lps-garden-buildings',
    ],
    'contact_open' => ['form'],
    'enquiry_saved' => ['form'],
];
const STAT_SOURCES = ['direct', 'internal', 'search', 'social', 'referral'];

function connection(): PDO {
    $path = getenv('CONTACT_DB') ?: '/data/enquiries.sqlite';
    if (!is_dir(dirname($path))) {
        if (!mkdir(dirname($path), 0700, true) && !is_dir(dirname($path))) {
            throw new RuntimeException('Storage directory unavailable');
        }
    }
    $db = new PDO('sqlite:' . $path, null, null, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_TIMEOUT => 10,
    ]);
    $db->exec('PRAGMA busy_timeout = 10000');
    $db->exec('PRAGMA journal_mode = WAL');
    // Keep the exact previous schema and old enquiry records unchanged.
    $db->exec('CREATE TABLE IF NOT EXISTS enquiries (
        id TEXT PRIMARY KEY, created_at TEXT NOT NULL, sender_name TEXT NOT NULL,
        sender_email TEXT NOT NULL, company TEXT NOT NULL, enquiry_type TEXT NOT NULL,
        message TEXT NOT NULL, email_hash TEXT NOT NULL,
        notification_status TEXT NOT NULL DEFAULT \'not_configured\'
    )');
    $db->exec('CREATE INDEX IF NOT EXISTS enquiry_time ON enquiries(created_at)');
    $db->exec('CREATE INDEX IF NOT EXISTS enquiry_email_hash ON enquiries(email_hash,created_at)');
    $db->exec('CREATE TABLE IF NOT EXISTS analytics_daily (
        day TEXT NOT NULL, kind TEXT NOT NULL, target TEXT NOT NULL,
        source TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(day,kind,target,source)
    )');
    return $db;
}
function utcNow(): DateTimeImmutable {
    return new DateTimeImmutable('now', new DateTimeZone('UTC'));
}
function respond(int $code, array $json = []): never {
    http_response_code($code);
    header('Cache-Control: no-store');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: no-referrer');
    if ($code === 204) {
        header('Content-Length: 0');
    } else {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($json, JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE);
    }
    exit;
}
function postBody(int $limit, array $fields): array {
    if (!in_array($_SERVER['HTTP_ORIGIN'] ?? '', ORIGINS, true)) {
        respond(403, ['error' => 'origin_not_allowed']);
    }
    if (!empty($_SERVER['HTTP_SEC_FETCH_SITE']) && $_SERVER['HTTP_SEC_FETCH_SITE'] !== 'same-origin') {
        respond(403, ['error' => 'cross_site']);
    }
    if (strtolower(trim(explode(';', $_SERVER['CONTENT_TYPE'] ?? '')[0])) !== 'application/json') {
        respond(415, ['error' => 'unsupported_media_type']);
    }
    $length = (int) ($_SERVER['CONTENT_LENGTH'] ?? 0);
    if ($length <= 0 || $length > $limit) {
        respond(413, ['error' => 'invalid_size']);
    }
    $raw = file_get_contents('php://input', false, null, 0, $limit + 1);
    if ($raw === false || strlen($raw) !== $length) {
        respond(413, ['error' => 'invalid_size']);
    }
    $data = json_decode($raw, true);
    if (!is_array($data) || array_is_list($data)) {
        respond(422, ['error' => 'invalid_submission']);
    }
    foreach (array_keys($data) as $key) {
        if (!in_array($key, $fields, true)) {
            respond(422, ['error' => 'invalid_submission']);
        }
    }
    return $data;
}
function cleanText(mixed $input, int $max, bool $required = false): string {
    if (!is_string($input)) throw new InvalidArgumentException('Invalid input type');
    $text = trim($input);
    if (strlen($text) > $max || ($required && $text === '')) {
        throw new InvalidArgumentException('Invalid input length');
    }
    if (preg_match('/[\x00-\x08\x0B\x0C\x0E-\x1F]/', $text)) {
        throw new InvalidArgumentException('Control characters');
    }
    return $text;
}
function dayCleanup(PDO $db): void {
    $db->prepare('DELETE FROM enquiries WHERE created_at < ?')
        ->execute([utcNow()->modify('-' . RETAIN_DAYS . ' days')->format('Y-m-d\TH:i:s.uP')]);
    $db->prepare('DELETE FROM analytics_daily WHERE day < ?')
        ->execute([utcNow()->modify('-' . ANALYTICS_RETAIN_DAYS . ' days')->format('Y-m-d')]);
}
function recordStat(PDO $db, string $kind, string $target, string $source): void {
    $q = $db->prepare('INSERT INTO analytics_daily(day,kind,target,source,count)
        VALUES(?,?,?,?,1) ON CONFLICT(day,kind,target,source) DO UPDATE SET count=count+1');
    $q->execute([utcNow()->format('Y-m-d'), $kind, $target, $source]);
}
function handleContact(): never {
    $data = postBody(MAX_BODY, ['name', 'email', 'company', 'enquiry_type', 'message', 'company_url']);
    $key = $_SERVER['HTTP_IDEMPOTENCY_KEY'] ?? '';
    if (!preg_match('/^[A-Za-z0-9._:-]{8,128}$/D', $key)) {
        respond(400, ['error' => 'missing_request_identity']);
    }
    try {
        $name = cleanText($data['name'] ?? '', 120, true);
        $email = strtolower(cleanText($data['email'] ?? '', 254, true));
        $company = cleanText($data['company'] ?? '', 160);
        $kind = cleanText($data['enquiry_type'] ?? '', 60, true);
        $message = cleanText($data['message'] ?? '', 5000, true);
        $trap = cleanText($data['company_url'] ?? '', 200);
        if (!filter_var($email, FILTER_VALIDATE_EMAIL) || !in_array($kind, ENQUIRY_TYPES, true) || strlen($message) < 10) {
            throw new InvalidArgumentException('Invalid enquiry');
        }
    } catch (InvalidArgumentException $e) {
        respond(422, ['error' => 'invalid_submission']);
    }
    // Honeypot: acknowledge without storing spam.
    if ($trap !== '') respond(202, ['accepted' => true]);
    $now = utcNow();
    $hash = hash('sha256', (getenv('CONTACT_RATE_SALT') ?: 'portfolio') . ':' . $email);
    try {
        $db = connection();
        $db->exec('BEGIN IMMEDIATE');
        $q = $db->prepare('SELECT 1 FROM enquiries WHERE id=?');
        $q->execute([$key]);
        if ($q->fetchColumn()) {
            $db->commit();
            respond(202, ['accepted' => true]);
        }
        $since = $now->modify('-2 hours')->format('Y-m-d\TH:i:s.uP');
        $q = $db->prepare('SELECT COUNT(*) FROM enquiries WHERE email_hash=? AND created_at>=?');
        $q->execute([$hash, $since]);
        $bySender = (int) $q->fetchColumn();
        $q = $db->prepare('SELECT COUNT(*) FROM enquiries WHERE created_at>=?');
        $q->execute([$since]);
        $total = (int) $q->fetchColumn();
        if ($bySender >= 4 || $total >= 70) {
            $db->rollBack();
            respond(429, ['error' => 'too_many_requests']);
        }
        $q = $db->prepare('INSERT INTO enquiries
            (id,created_at,sender_name,sender_email,company,enquiry_type,message,email_hash)
            VALUES (?,?,?,?,?,?,?,?)');
        $q->execute([$key, $now->format('Y-m-d\TH:i:s.uP'), $name, $email, $company, $kind, $message, $hash]);
        dayCleanup($db);
        $db->commit();
        respond(202, ['accepted' => true]);
    } catch (Throwable $e) {
        error_log('portfolio storage failure: ' . get_class($e));
        respond(503, ['error' => 'temporarily_unavailable']);
    }
}
function handleAnalytics(): never {
    $data = postBody(512, ['kind', 'target', 'source']);
    if (count($data) !== 3) respond(422, ['error' => 'invalid_event']);
    $kind = $data['kind'] ?? null;
    $target = $data['target'] ?? null;
    $source = $data['source'] ?? null;
    if (!is_string($kind) || !is_string($target) || !is_string($source)
        || !isset(STAT_EVENTS[$kind]) || !in_array($target, STAT_EVENTS[$kind], true)
        || !in_array($source, STAT_SOURCES, true)) {
        respond(422, ['error' => 'invalid_event']);
    }
    try {
        $db = connection();
        recordStat($db, $kind, $target, $source);
        respond(204);
    } catch (Throwable $e) {
        error_log('portfolio aggregate storage failure: ' . get_class($e));
        respond(503, ['error' => 'temporarily_unavailable']);
    }
}
function cliMode(array $args): never {
    $mode = $args[1] ?? 'help';
    if (!in_array($mode, ['list', 'show', 'stats', 'cleanup'], true)) {
        fwrite(STDERR, "Usage: php index.php list | show UUID | stats [days] | cleanup\n");
        exit(2);
    }
    $db = connection();
    if ($mode === 'cleanup') {
        dayCleanup($db);
        echo "Retention cleanup finished\n";
        exit;
    }
    if ($mode === 'stats') {
        $days = (int) ($args[2] ?? 30);
        if ($days < 1 || $days > 365) exit(2);
        $since = utcNow()->modify('-' . ($days - 1) . ' days')->format('Y-m-d');
        $q = $db->prepare('SELECT kind,target,source,SUM(count) AS total
            FROM analytics_daily WHERE day>=? GROUP BY kind,target,source ORDER BY kind,target,source');
        $q->execute([$since]);
        echo json_encode(['period_days' => $days, 'since' => $since,
            'counts' => array_map(fn($x) => [
                'event' => $x['kind'], 'target' => $x['target'],
                'source' => $x['source'], 'count' => (int)$x['total'],
            ], $q->fetchAll())], JSON_PRETTY_PRINT) . "\n";
        exit;
    }
    if ($mode === 'show') {
        if (!preg_match('/^[A-Za-z0-9._:-]{8,128}$/D', $args[2] ?? '')) exit(2);
        $q = $db->prepare('SELECT id,created_at,sender_name,sender_email,company,enquiry_type,message,notification_status FROM enquiries WHERE id=?');
        $q->execute([$args[2]]);
    } else {
        $q = $db->query('SELECT id,created_at,sender_name,sender_email,company,enquiry_type,notification_status
            FROM enquiries ORDER BY created_at DESC LIMIT 30');
    }
    foreach ($q->fetchAll() as $row) echo json_encode(array_values($row), JSON_UNESCAPED_UNICODE) . "\n";
    exit;
}
if (PHP_SAPI === 'cli') cliMode($argv);
$path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
if ($path === '/healthz' && ($_SERVER['REQUEST_METHOD'] ?? '') === 'GET') respond(200, ['ok' => true]);
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') respond(404, ['error' => 'not_found']);
if ($path === '/api/contact') handleContact();
if ($path === '/api/analytics') handleAnalytics();
respond(404, ['error' => 'not_found']);
