<?php
declare(strict_types=1);

// Fixed destinations: never accept mail headers or recipient addresses from a request.
const ENQUIRY_TO = '109dentaloffice@gmail.com';
const ENQUIRY_FROM = 'website@109dental.ca';
const ENQUIRY_SUBJECT = 'New website enquiry | 109 Dental';
const ENQUIRY_REASONS = [
    'appointment' => 'Request an appointment',
    'change' => 'Change an appointment',
    'call' => 'Please call me',
    'office' => 'General office question',
];

function enquiry_validate(array $input): array {
    $fields = [];
    foreach (['name', 'phone', 'email', 'reason', 'comments', 'website', 'csrf', 'request_id'] as $key) {
        if (!isset($input[$key]) || !is_string($input[$key])) {
            throw new InvalidArgumentException('Please check the form fields and try again.');
        }
        $fields[$key] = trim($input[$key]);
        if (!preg_match('//u', $fields[$key])) throw new InvalidArgumentException('Please use valid text.');
    }
    foreach (['name', 'phone', 'email', 'reason'] as $key) {
        if (preg_match('/[\x00-\x1f\x7f]/', $fields[$key])) throw new InvalidArgumentException('Please check your contact details.');
    }
    if ($fields['name'] === '' || mb_strlen($fields['name']) > 120) throw new InvalidArgumentException('Enter your name (up to 120 characters).');
    $digits = preg_replace('/\D/', '', $fields['phone']);
    if (strlen($fields['phone']) > 40 || strlen($digits) < 7 || strlen($digits) > 20 || !preg_match('/^[0-9+().\s#xext-]+$/i', $fields['phone'])) throw new InvalidArgumentException('Enter a valid phone number.');
    if (strlen($fields['email']) > 254 || !filter_var($fields['email'], FILTER_VALIDATE_EMAIL)) throw new InvalidArgumentException('Enter a valid email address.');
    if (!isset(ENQUIRY_REASONS[$fields['reason']])) throw new InvalidArgumentException('Choose what we can help you with.');
    if (mb_strlen($fields['comments']) > 2000 || preg_match('/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/', $fields['comments'])) throw new InvalidArgumentException('Comments must be plain text, no longer than 2,000 characters.');
    if ($fields['website'] !== '') throw new InvalidArgumentException('We could not send this enquiry. Please call the clinic.');
    if (!preg_match('/^[a-f0-9]{64}$/', $fields['request_id'])) throw new InvalidArgumentException('Please refresh the form before sending.');
    return $fields;
}

function enquiry_send(array $fields): bool {
    $body = "109 Dental website enquiry\n\nName: {$fields['name']}\nPhone: {$fields['phone']}\nEmail: {$fields['email']}\nRequest: " . ENQUIRY_REASONS[$fields['reason']] . "\n\nComments:\n{$fields['comments']}\n\nThis is an enquiry, not a confirmed appointment.\n";
    return @mail(ENQUIRY_TO, ENQUIRY_SUBJECT, $body, [
        'From' => '109 Dental website <' . ENQUIRY_FROM . '>',
        'Reply-To' => $fields['email'],
        'MIME-Version' => '1.0',
        'Content-Type' => 'text/plain; charset=UTF-8',
    ]);
}

function enquiry_process(array $fields, string $ip, string $directory, callable $send, ?int $clock = null): array {
    $now = $clock ?? time();
    if (!is_dir($directory) && !@mkdir($directory, 0700, true) && !is_dir($directory)) throw new RuntimeException('Storage unavailable');
    $handle = @fopen($directory . '/state.json', 'c+');
    if (!$handle || !flock($handle, LOCK_EX)) throw new RuntimeException('Storage unavailable');
    @chmod($directory . '/state.json', 0600);
    try {
        $raw = stream_get_contents($handle);
        $state = $raw === '' ? ['key' => bin2hex(random_bytes(32)), 'records' => []] : json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
        $records = array_values(array_filter($state['records'], fn($r) => $r['time'] > $now - 86400));
        $ipHash = hash_hmac('sha256', $ip, $state['key']);
        $digest = hash_hmac('sha256', json_encode(array_intersect_key($fields, array_flip(['name','phone','email','reason','comments']))), $state['key']);
        $id = hash_hmac('sha256', $fields['request_id'], $state['key']);
        foreach ($records as $r) {
            if ($r['id'] === $id || ($r['digest'] === $digest && $r['time'] > $now - 3600)) {
                return $r['status'] === 'sent' ? [200, 'already_sent'] : [409, 'uncertain'];
            }
        }
        $recent = count(array_filter($records, fn($r) => $r['time'] > $now - 60));
        $perIp = count(array_filter($records, fn($r) => $r['ip'] === $ipHash && $r['time'] > $now - 3600));
        if ($recent >= 5 || $perIp >= 5 || count($records) >= 80) return [429, 'limited'];
        // Persist before sending: a process interruption must not trigger a second email on retry.
        $records[] = ['id'=>$id,'digest'=>$digest,'ip'=>$ipHash,'time'=>$now,'status'=>'pending'];
        $write = function () use ($handle, &$state, &$records): void {
            $state['records'] = $records;
            $json = json_encode($state, JSON_THROW_ON_ERROR);
            rewind($handle);
            if (!ftruncate($handle, 0) || fwrite($handle, $json) !== strlen($json) || !fflush($handle)) throw new RuntimeException('Storage unavailable');
        };
        $write();
        $accepted = $send($fields);
        $records[array_key_last($records)]['status'] = $accepted ? 'sent' : 'failed';
        $write();
        return $accepted ? [200, 'sent'] : [503, 'failed'];
    } finally {
        flock($handle, LOCK_UN);
        fclose($handle);
    }
}

function enquiry_response(int $status, array $data): never {
    http_response_code($status);
    echo json_encode($data);
    exit;
}

if (defined('ENQUIRY_LIBRARY_ONLY') && PHP_SAPI === 'cli') return;
ini_set('display_errors', '0');
// Do not emit enquiry data or mail errors to application logs.
ini_set('log_errors', '0');
header('Content-Type: application/json; charset=UTF-8');
header('Cache-Control: no-store, private, max-age=0');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: no-referrer');
try {
    $host = strtolower($_SERVER['HTTP_HOST'] ?? '');
    if (!in_array($host, ['109dental.ca','www.109dental.ca','blueviolet-rhinoceros-423405.hostingersite.com'], true)) enquiry_response(403, ['error'=>'Use the clinic website to send your enquiry.']);
    // Require TLS as reported by the web server; do not trust a client-supplied proxy header.
    if (($_SERVER['HTTPS'] ?? '') !== 'on' && ($_SERVER['SERVER_PORT'] ?? '') != 443) enquiry_response(403, ['error'=>'Please use HTTPS to send your enquiry.']);
    $method = $_SERVER['REQUEST_METHOD'] ?? '';
    if (!in_array($method, ['GET','POST'], true)) { header('Allow: GET, POST'); enquiry_response(405, ['error'=>'Method not allowed.']); }
    if (($_SERVER['HTTP_X_ENQUIRY_REQUEST'] ?? '') !== '1') enquiry_response(403, ['error'=>'Please use the enquiry form.']);
    if ($method === 'POST' && ($_SERVER['HTTP_ORIGIN'] ?? '') !== 'https://' . $host) enquiry_response(403, ['error'=>'Please refresh the form and try again.']);
    session_name('clinic_enquiry');
    session_start(['use_strict_mode'=>1,'cookie_secure'=>1,'cookie_httponly'=>1,'cookie_samesite'=>'Strict','cookie_path'=>'/','cookie_lifetime'=>0]);
    if ($method === 'GET') {
        if (!isset($_SESSION['csrf']) || ($_SESSION['expires'] ?? 0) < time()) {
            $_SESSION['csrf'] = bin2hex(random_bytes(32));
            $_SESSION['expires'] = time() + 3600;
        }
        enquiry_response(200, ['csrf'=>$_SESSION['csrf'], 'request_id'=>bin2hex(random_bytes(32))]);
    }
    if ((int)($_SERVER['CONTENT_LENGTH'] ?? 0) > 20000) enquiry_response(413, ['error'=>'The enquiry is too long.']);
    $fields = enquiry_validate($_POST);
    if (!isset($_SESSION['csrf']) || !hash_equals($_SESSION['csrf'], $fields['csrf']) || ($_SESSION['expires'] ?? 0) < time()) enquiry_response(403, ['error'=>'Your form session expired. Refresh this page before sending.']);
    session_write_close();
    // Outside public_html, isolated to this domain. Stores only keyed hashes, timestamps and outcomes.
    [$status, $result] = enquiry_process($fields, $_SERVER['REMOTE_ADDR'] ?? '', dirname(__DIR__, 2) . '/.109-enquiry-private', 'enquiry_send');
    $messages = [
        'sent'=>'Your enquiry has been accepted for email delivery to our team. Sending this form does not confirm an appointment. Our team will follow up with you.',
        'already_sent'=>'This enquiry was already accepted. It has not been sent again. Our team will follow up with you.',
        'uncertain'=>'We could not confirm a new delivery. To avoid a duplicate enquiry, please call or email the clinic instead of sending again.',
        'limited'=>'Too many enquiries have been sent recently. Please call or email the clinic.',
        'failed'=>'We could not send your enquiry. Please call or email the clinic.',
    ];
    if ($status === 429) header('Retry-After: 3600');
    enquiry_response($status, [$status === 200 ? 'message' : 'error'=>$messages[$result]]);
} catch (InvalidArgumentException $error) {
    enquiry_response(422, ['error'=>$error->getMessage()]);
} catch (Throwable $error) {
    enquiry_response(503, ['error'=>'The enquiry service is unavailable. Please call or email the clinic.']);
}
