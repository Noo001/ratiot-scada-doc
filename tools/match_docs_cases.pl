#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use open ':std', ':encoding(UTF-8)';

my $docs_dir = $ARGV[0] || 'sources/extracted/scada-docs-6.41.10-md';
my $out_file = $ARGV[1] || 'sources/extracted/scada-docs-6.41.10-md/case_matches.md';

opendir my $dh, $docs_dir or die "Cannot open $docs_dir: $!";
my @md_files = sort grep { /\.md$/i && $_ ne 'index.md' && $_ ne 'case_matches.md' } readdir($dh);
closedir $dh;

my @cases = (
    { id => 1,  name => 'Ошибки создания ресурсов при первом запуске', terms => [qw(resource creation error creating resource container null context unavailable)] },
    { id => 2,  name => 'Режимы лицензирования free / trial', terms => [qw(free license trial license 100 tags licensing mode)] },
    { id => 3,  name => 'Инсталлятор перезаписывает файлы', terms => [qw(installer overwrite replace file wizard_1.png)] },
    { id => 4,  name => 'Импорт Modbus CSV/XML', terms => [qw(modbus csv xml register import export encoding)] },
    { id => 5,  name => 'eventLog сбрасывает колонки', terms => [qw(event log eventlog journal columns width)] },
    { id => 6,  name => 'Дерево тегов / абсолютная модель', terms => [qw(tag tree absolute model digital twin)] },
    { id => 7,  name => 'NoSQL-хранилище событий', terms => [qw(nosql event storage event store cassandra)] },
    { id => 8,  name => 'HTML-сниппет сдвигает layout', terms => [qw(html snippet layout dashboard)] },
    { id => 9,  name => 'Лицензирование / activation key', terms => [qw(activation key license file install path)] },
    { id => 10, name => 'Магазин приложений', terms => [qw(store client marketplace application store)] },
    { id => 11, name => 'Вёрстка страницы 404', terms => [qw(404 not found page)] },
    { id => 12, name => 'Брендинг AggreGate', terms => [qw(aggregate logo branding rebrand oem)] },
    { id => 13, name => 'Драйвера и расширения', terms => [qw(plugins drivers extensions system tree)] },
    { id => 14, name => '/web/* 404 JSON', terms => [qw(404 json web server spa)] },
    { id => 15, name => 'Ссылки справки', terms => [qw(help documentation link buff-lab)] },
    { id => 16, name => 'Вкладки Информации о сервере', terms => [qw(server information tabs overflow)] },
    { id => 17, name => 'Раздел Пользователи', terms => [qw(users container user list)] },
);

sub score_file {
    my ($path, $terms) = @_;
    open my $fh, '<:encoding(UTF-8)', $path or return 0;
    my $text = do { local $/; <$fh> };
    close $fh;
    $text = lc $text;
    my $score = 0;
    for my $term (@$terms) {
        my $t = ' ' . lc($term) . ' ';
        my $pos = -1;
        while (($pos = index($text, $t, $pos + 1)) >= 0) {
            $score += length($term);
        }
    }
    return $score;
}

open my $out, '>:encoding(UTF-8)', $out_file or die "Cannot write $out_file: $!";
print $out "# Сопоставление баг-кейсов с разделами справки RatioT SCADA 6.41.10\n\n";
print $out "_Источник: `sources/extracted/scada-docs-6.41.10-md/`_\n\n";

for my $case (@cases) {
    print $out "## Кейс $case->{id}. $case->{name}\n\n";
    my @matches;
    for my $file (@md_files) {
        my $score = score_file("$docs_dir/$file", $case->{terms});
        next unless $score > 0;
        push @matches, { file => $file, score => $score };
    }
    @matches = sort { $b->{score} <=> $a->{score} } @matches;
    @matches = @matches[0..9] if @matches > 10;
    if (@matches) {
        print $out "| Релевантность | Файл |\n|---|---|\n";
        for my $m (@matches) {
            print $out "| $m->{score} | [$m->{file}]($m->{file}) |\n";
        }
    } else {
        print $out "_Релевантных разделов не найдено._\n";
    }
    print $out "\n";
}

close $out;
print "Matches written to $out_file\n";
