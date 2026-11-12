<?php
declare(strict_types=1);
define('ENQUIRY_LIBRARY_ONLY', true);
require dirname(__DIR__) . '/api/enquiry.php';
function check(bool $ok, string $message): void { if (!$ok) throw new RuntimeException($message); }
$valid = ['name'=>'Synthetic test','phone'=>'780-999-0693','email'=>'test@example.com','reason'=>'office','comments'=>'TEST ONLY','website'=>'','csrf'=>str_repeat('a',64),'request_id'=>str_repeat('b',64)];
check(enquiry_validate($valid)['name'] === $valid['name'], 'Valid enquiry rejected');
foreach ([['name',''],['email',"test@example.com\r\nBcc: wrong@example.com"],['name',"Name\r\nInjected"],['phone','abc'],['email','invalid'],['reason','invalid'],['comments',str_repeat('a',2001)],['website','bot'],['email',[]]] as [$key,$value]) {
    $input=$valid; $input[$key]=$value; $rejected=false;
    try { enquiry_validate($input); } catch (InvalidArgumentException $e) { $rejected=true; }
    check($rejected, 'Unsafe field accepted: '.$key);
}
$dir = sys_get_temp_dir().'/109-enquiry-test-'.bin2hex(random_bytes(6));
$sends=0;
$sender=function($fields) use (&$sends) { $sends++; return true; };
try {
    check(enquiry_process($valid,'192.0.2.1',$dir,$sender,100000)===[200,'sent'],'Initial send');
    check(enquiry_process($valid,'192.0.2.1',$dir,$sender,100001)===[200,'already_sent'],'Request duplicate');
    $copy=$valid; $copy['request_id']=str_repeat('c',64);
    check(enquiry_process($copy,'192.0.2.2',$dir,$sender,100002)===[200,'already_sent'],'Content duplicate across sessions');
    check($sends===1,'Duplicate caused mail');
    for($i=1;$i<=4;$i++) { $copy['request_id']=hash('sha256',(string)$i); $copy['comments']='TEST '.$i; check(enquiry_process($copy,'192.0.2.1',$dir,$sender,100010+$i)[0]===200,'Allowed send'); }
    $copy['request_id']=hash('sha256','six'); $copy['comments']='Sixth';
    check(enquiry_process($copy,'192.0.2.2',$dir,$sender,100020)===[429,'limited'],'Global per-minute limit');
    check(enquiry_process($copy,'192.0.2.1',$dir,$sender,100080)===[429,'limited'],'Per-IP hourly limit');
    check(enquiry_process($copy,'192.0.2.2',$dir,fn($f)=>false,100080)===[503,'failed'],'Mail failure');
    check(enquiry_process($copy,'192.0.2.2',$dir,$sender,100081)===[409,'uncertain'],'Failed retry deduplicated');
    $raw=file_get_contents($dir.'/state.json');
    foreach (['test@example.com','TEST ONLY','192.0.2.1','780-999-0693','Synthetic test'] as $private) check(!str_contains($raw,$private),'Private data in state');
    $copy['request_id']=hash('sha256','newday'); $copy['comments']='Next day';
    check(enquiry_process($copy,'192.0.2.1',$dir,$sender,200000)[0]===200,'Expired records');
    check(count(json_decode(file_get_contents($dir.'/state.json'),true)['records'])===1,'Expired records retained');
} finally { if(file_exists($dir.'/state.json')) unlink($dir.'/state.json'); if(is_dir($dir)) rmdir($dir); }
echo "PASS: validation, header injection, honeypot, duplicate suppression, rate limits, mail failures and private-state cleanup. No emails sent.\n";
