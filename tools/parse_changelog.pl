#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use open ':std', ':encoding(UTF-8)';

my $html_file = $ARGV[0] || 'sources/incoming/changelog.html';
my $out_file  = $ARGV[1] || 'sources/extracted/changelog/changelog_parsed.tsv';

open my $fh, '<:encoding(UTF-8)', $html_file or die "Cannot read $html_file: $!";
my $html = do { local $/; <$fh> };
close $fh;

# Extract changelog content between main header and Older Versions
my ($changelog) = $html =~ m{(<h2><b>Changes in 6\.4.*?</h2>.*?)(<h2>Older Versions</h2>|</div>\s*<div class="footer")}s;
$changelog //= $html;

my @records;
my $current_version = '';
my $current_type    = '';

# Split by h2 headers
my @parts = split /<h2>/i, $changelog;

for my $part (@parts) {
    next unless $part =~ /\S/;
    # Extract header text until closing </h2>
    my ($header) = $part =~ /^(.+?)<\/h2>/s;
    next unless defined $header;
    $header =~ s/<[^>]+>//g;
    $header =~ s/^\s+|\s+$//g;

    if ($header =~ /Version\s+(\S+)/i) {
        $current_version = $1;
        $current_type    = '';
        next;
    }
    elsif ($header =~ /^(Bug|Improvement|New Feature|Sub-task|Task|Performance Issue)/i) {
        $current_type = $1;
        # continue to extract li items from this part
    }
    else {
        $current_type = '';
    }

    # Extract list items (some versions use unclosed <li> tags)
    my @lis = split /<li>/i, $part;
    shift @lis; # discard content before first <li>
    for my $li (@lis) {
        next unless $li =~ /\[\s*<a[^>]*>\s*(AGG-\d+)\s*<\/a>\s*\]\s*-\s*/;
        my $code = $1;
        my $text = $li;
        $text =~ s/^\[\s*<a[^>]*>\s*AGG-\d+\s*<\/a>\s*\]\s*-\s*//;
        $text =~ s/<\/li>.*//s;
        $text =~ s/<[^>]+>//g;
        $text =~ s/\s+/ /g;
        $text =~ s/^\s+|\s+$//g;
        push @records, {
            version => $current_version,
            type    => $current_type || 'Other',
            code    => $code,
            text    => $text,
        };
    }
}

open my $out, '>:encoding(UTF-8)', $out_file or die "Cannot write $out_file: $!";
print $out "version\ttype\tcode\ttext\n";
for my $r (@records) {
    my $text = $r->{text};
    $text =~ s/\t/ /g;
    $text =~ s/\r?\n/ /g;
    print $out "$r->{version}\t$r->{type}\t$r->{code}\t$text\n";
}
close $out;

print "Parsed ", scalar(@records), " records to $out_file\n";
