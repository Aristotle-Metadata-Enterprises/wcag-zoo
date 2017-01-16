require File::Temp;
use File::Temp ();
use File::Temp qw/ :seekable /;
use JSON;

$my_html = "<html><head><body><h2>This is wrong, it should be h1";

$tmp = File::Temp->new();
print $tmp $my_html;
$tmp->seek( 0, SEEK_END );

$fn = $tmp->filename;

$results = `zookeeper tarsier $fn -J`;
@json_results = decode_json($results);
$filename = @{@{@json_results[0]}[0]}[0];
$len = scalar @{@{@{@{@json_results[0]}[0]}[1]}{'failures'}};
print "$filename $len failures\n";
