#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use open ':std', ':encoding(UTF-8)';
use File::Basename;
use File::Path qw(make_path);

my $src_dir = $ARGV[0] || 'sources/extracted/scada-docs-6.41.10';
my $out_dir = $ARGV[1] || 'sources/extracted/scada-docs-6.41.10-md';

make_path($out_dir) unless -d $out_dir;

opendir my $dh, $src_dir or die "Cannot open $src_dir: $!";
my @htm_files = sort grep { /\.htm$/i } readdir($dh);
closedir $dh;

my @records;

for my $file (@htm_files) {
    my $path = "$src_dir/$file";
    open my $fh, '<:encoding(UTF-8)', $path or do { warn "Cannot read $path: $!"; next; };
    my $html = do { local $/; <$fh> };
    close $fh;

    my ($title) = $html =~ /<title>(.*?)<\/title>/si;
    $title //= $file;
    $title =~ s/\s+/ /g;
    $title =~ s/^\s+|\s+$//g;
    $title =~ s/\s*-\s*Welcome to RatioT SCADA\s*!//i;
    $title =~ s/^\s+|\s+$//g;

    my ($article) = $html =~ /<article id="content" role="main">(.*?)<\/article>/si;
    unless ($article) {
        warn "No article content in $file\n";
        next;
    }

    my $md = html_to_markdown($article, $title);

    my $out_file = $file;
    $out_file =~ s/\.htm$/.md/i;
    my $out_path = "$out_dir/$out_file";

    open my $out, '>:encoding(UTF-8)', $out_path or do { warn "Cannot write $out_path: $!"; next; };
    print $out "_Источник: `$file`_\n\n";
    unless ($md =~ /^#\s/) {
        print $out "# $title\n\n";
    }
    print $out $md;
    print $out "\n";
    close $out;

    push @records, {
        file  => $file,
        title => $title,
        md    => $out_file,
    };
}

# Build index
my $index_path = "$out_dir/index.md";
open my $idx, '>:encoding(UTF-8)', $index_path or die "Cannot write $index_path: $!";
print $idx "# Оглавление встроенной справки RatioT SCADA 6.41.10\n\n";
print $idx "_Всего разделов: ", scalar(@records), "_\n\n";
for my $r (@records) {
    print $idx "- [$r->{title}]($r->{md}) — `$r->{file}`\n";
}
close $idx;

print "Extracted ", scalar(@records), " files to $out_dir\n";
print "Index: $index_path\n";

sub html_to_markdown {
    my ($html, $title) = @_;

    # Remove scripts and styles
    $html =~ s/<script[^>]*>.*?<\/script>//gs;
    $html =~ s/<style[^>]*>.*?<\/style>//gs;

    # Remove hidden content
    $html =~ s/<div class="hidden-content"[^>]*>.*?<\/div>//gs;

    # Remove headerlink anchors
    $html =~ s/<a class="headerlink"[^>]*>.*?<\/a>//gs;

    # Convert tables BEFORE removing tags
    $html =~ s/<table[^>]*>(.*?)<\/table>/convert_table($1)/gesi;

    # Convert headings
    $html =~ s/<h1[^>]*>(.*?)<\/h1>/\n# $1\n/gsi;
    $html =~ s/<h2[^>]*>(.*?)<\/h2>/\n## $1\n/gsi;
    $html =~ s/<h3[^>]*>(.*?)<\/h3>/\n### $1\n/gsi;
    $html =~ s/<h4[^>]*>(.*?)<\/h4>/\n#### $1\n/gsi;
    $html =~ s/<h5[^>]*>(.*?)<\/h5>/\n##### $1\n/gsi;
    $html =~ s/<h6[^>]*>(.*?)<\/h6>/\n###### $1\n/gsi;

    # Convert paragraphs
    $html =~ s/<p[^>]*>(.*?)<\/p>/\n$1\n/gsi;

    # Convert lists
    $html =~ s/<ul[^>]*>(.*?)<\/ul>/\n$1\n/gsi;
    $html =~ s/<ol[^>]*>(.*?)<\/ol>/\n$1\n/gsi;
    $html =~ s/<li[^>]*>(.*?)<\/li>/\n- $1/gsi;

    # Convert bold/italic
    $html =~ s/<strong[^>]*>(.*?)<\/strong>/**$1**/gsi;
    $html =~ s/<b[^>]*>(.*?)<\/b>/**$1**/gsi;
    $html =~ s/<em[^>]*>(.*?)<\/em>/*$1*/gsi;
    $html =~ s/<i[^>]*>(.*?)<\/i>/*$1*/gsi;

    # Convert code
    $html =~ s/<code[^>]*>(.*?)<\/code>/`$1`/gsi;
    $html =~ s/<pre[^>]*>(.*?)<\/pre>/\n```\n$1\n```\n/gsi;

    # Convert links
    $html =~ s/<a[^>]*href="([^"]+)"[^>]*>(.*?)<\/a>/[$2]($1)/gsi;

    # Convert images
    $html =~ s/<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>/![$2]($1)/gsi;
    $html =~ s/<img[^>]*src="([^"]+)"[^>]*>/![]($1)/gsi;

    # Remove remaining tags
    $html =~ s/<[^>]+>//g;

    # Decode entities
    $html =~ s/&nbsp;/ /g;
    $html =~ s/&lt;/</g;
    $html =~ s/&gt;/>/g;
    $html =~ s/&amp;/&/g;
    $html =~ s/&quot;/"/g;
    $html =~ s/&#(\d+);/chr($1)/ge;

    # Remove duplicated title heading
    my $first_line = '';
    if ($html =~ /^(#\s*.*?)\n/) {
        $first_line = $1;
        $first_line =~ s/^\s+|\s+$//g;
    }
    my $title_heading = '# ' . $title;
    $title_heading =~ s/^\s+|\s+$//g;
    if (lc($first_line) eq lc($title_heading)) {
        $html =~ s/^#\s*\Q$title\E\s*\n+//i;
    }

    # Clean whitespace
    $html =~ s/\n\s*\n+/\n\n/g;
    $html =~ s/^\s+|\s+$//g;

    return $html;
}

sub convert_table {
    my ($table_html) = @_;
    $table_html =~ s/<colgroup[^>]*>.*?<\/colgroup>//gsi;
    $table_html =~ s/<thead[^>]*>(.*?)<\/thead>/$1/gsi;
    $table_html =~ s/<tbody[^>]*>(.*?)<\/tbody>/$1/gsi;
    $table_html =~ s/<tfoot[^>]*>(.*?)<\/tfoot>/$1/gsi;

    my @rows;
    while ($table_html =~ /<tr[^>]*>(.*?)<\/tr>/gsi) {
        my $row = $1;
        my @cells;
        while ($row =~ /<t[dh][^>]*>(.*?)<\/t[dh]>/gsi) {
            my $cell = $1;
            $cell =~ s/<[^>]+>//g;
            $cell =~ s/\s+/ /g;
            $cell =~ s/^\s+|\s+$//g;
            $cell = ' ' unless length $cell;
            push @cells, $cell;
        }
        push @rows, '| ' . join(' | ', @cells) . ' |' if @cells;
    }

    return "\n[TABLE]\n" unless @rows;

    # Add separator after first row if it looks like header
    if (@rows >= 2 && $rows[0] =~ /\*\*/) {
        my $sep = '| ' . join(' | ', map { '---' } split /\s*\|\s*/, $rows[0]) . ' |';
        $sep =~ s/\|\s+\|/|/g;
        $sep =~ s/^\| //;
        $sep =~ s/ \|$//;
        # simpler separator
        my @cols = split /\s*\|\s*/, $rows[0];
        shift @cols if @cols && $cols[0] eq '';
        pop @cols if @cols && $cols[-1] eq '';
        $sep = '| ' . join(' | ', map { '---' } @cols) . ' |';
        splice @rows, 1, 0, $sep;
    }

    return "\n" . join("\n", @rows) . "\n";
}
