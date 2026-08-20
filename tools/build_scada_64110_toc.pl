#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use open ':std', ':encoding(UTF-8)';
use File::Path qw(make_path);
use File::Basename;

my $md_dir   = $ARGV[0] || 'sources/extracted/scada-docs-6.41.10-md';
my $out_dir  = $ARGV[1] || 'scada/docs-6.41.10';
make_path($out_dir) unless -d $out_dir;

opendir my $dh, $md_dir or die "Cannot open $md_dir: $!";
my @md_files = sort grep { /\.md$/i && $_ ne 'case_matches.md' } readdir($dh);
closedir $dh;

my @records;
for my $file (@md_files) {
    my $path = "$md_dir/$file";
    open my $fh, '<:encoding(UTF-8)', $path or do { warn "Cannot read $path: $!"; next; };
    my $title;
    while (my $line = <$fh>) {
        if ($line =~ /^#\s+(.+)/) {
            $title = $1;
            last;
        }
    }
    close $fh;
    $title //= $file;
    $title =~ s/\s+/ /g;
    $title =~ s/^\s+|\s+$//g;
    push @records, { file => $file, title => $title };
}

@records = sort { lc($a->{title}) cmp lc($b->{title}) } @records;

# Group by first letter of title (cyrillic / latin)
my %groups;
for my $r (@records) {
    my $first = substr($r->{title}, 0, 1);
    $first = uc($first);
    $first = 'А-Я' if $first =~ /[А-ЯЁ]/i;
    $first = 'A-Z' if $first =~ /[A-Z]/i;
    $first = '0-9' if $first =~ /[0-9]/i;
    $first = '…' unless $first =~ /[A-ZА-ЯЁ0-9]/i;
    push @{ $groups{$first} }, $r;
}

my $total = scalar @records;

# Build main content
my @main_parts;
my @nav_parts = ('<a href="#top">↑ Наверх</a>');

for my $group (sort keys %groups) {
    my $id = 'group-' . ($group =~ /[А-Я]/ ? 'ru' : ($group =~ /[A-Z]/ ? 'en' : 'other')) . '-' . ord($group);
    $id = 'group-other' if $group eq '…';
    push @nav_parts, "<a href=\"#$id\">$group</a>";

    my @items = map {
        my $safe_title = escape_html($_->{title});
        "<li><code>$_->{file}</code> — $safe_title</li>"
    } @{ $groups{$group} };

    push @main_parts, <<"SECTION";
<section id="$id">
<h2>$group</h2>
<ul>
@{[ join("\n", @items) ]}
</ul>
</section>
SECTION
}

my $main_html = join("\n\n", @main_parts);
my $nav_html = join("\n", @nav_parts);

my $html = <<"HTML";
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta name="robots" content="noindex, nofollow">
  <script>
    (function () {
      if (localStorage.getItem('ratiot-doc-auth') !== 'ok') {
        var pwd = prompt('Доступ к документации. Введите пароль:');
        if (pwd !== '111') {
          document.documentElement.innerHTML = '<body style="font-family:sans-serif;padding:40px;text-align:center;"><h1>Доступ запрещён</h1><p>Неверный пароль.</p></body>';
          throw new Error('Access denied');
        }
        localStorage.setItem('ratiot-doc-auth', 'ok');
      }
    })();
  </script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RatioT SCADA 6.41.10 — оглавление справки</title>
  <link rel="stylesheet" href="../style.css">
  <style>
    .letter-nav { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px; }
    .letter-nav a { display: inline-block; padding: 6px 12px; border: 1px solid var(--border); border-radius: 6px; text-decoration: none; color: var(--text); }
    .letter-nav a:hover { background: var(--accent-light); color: var(--accent); border-color: var(--accent); }
    section h2 { margin-top: 0; }
    section ul { columns: 1; }
    \@media (min-width: 700px) { section ul { columns: 2; } }
    section li { break-inside: avoid; margin-bottom: 6px; font-size: .92rem; }
    aside nav { max-height: calc(100vh - 140px); overflow-y: auto; }
  </style>
</head>
<body id="top">
  <div class="layout">
    <aside>
      <h1>RatioT SCADA</h1>
      <div class="subtitle">Справка 6.41.10 — оглавление</div>
      <nav>
        <a href="../index.html">← База знаний</a>
$nav_html
      </nav>
    </aside>

    <main>
      <section id="intro">
        <h2>Оглавление встроенной справки RatioT SCADA 6.41.10</h2>
        <p>Всего разделов: <strong>$total</strong>. Содержимое отсортировано по алфавиту и сгруппировано по первой букве названия.</p>
        <div class="letter-nav">
@{[ join("\n", map { my $g = $_; my $id = 'group-' . ($g =~ /[А-Я]/ ? 'ru' : ($g =~ /[A-Z]/ ? 'en' : 'other')) . '-' . ord($g); $id = 'group-other' if $g eq '…'; "<a href=\"#$id\">$g</a>" } sort keys %groups) ]}
        </div>
      </section>

$main_html

      <footer>
        Оглавление построено из локальной копии встроенной справки RatioT SCADA 6.41.10.
      </footer>
    </main>
  </div>

  <script>
    const sections = document.querySelectorAll('section[id^="group-"]');
    const links = document.querySelectorAll('nav a[href^="#group-"]');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          links.forEach(link => link.classList.remove('active'));
          const active = document.querySelector('nav a[href="#' + entry.target.id + '"]');
          if (active) active.classList.add('active');
        }
      });
    }, { rootMargin: '-20% 0px -60% 0px' });
    sections.forEach(section => observer.observe(section));

    links.forEach(link => {
      link.addEventListener('click', (e) => {
        const id = link.getAttribute('href').slice(1);
        const el = document.getElementById(id);
        if (el) {
          e.preventDefault();
          el.scrollIntoView({ behavior: 'smooth' });
          history.pushState(null, null, '#' + id);
        }
      });
    });
  </script>
</body>
</html>
HTML

open my $out, '>:encoding(UTF-8)', "$out_dir/index.html" or die "Cannot write $out_dir/index.html: $!";
print $out $html;
close $out;

print "Generated $out_dir/index.html with $total sections.\n";

sub escape_html {
    my ($s) = @_;
    $s =~ s/&/&amp;/g;
    $s =~ s/</&lt;/g;
    $s =~ s/>/&gt;/g;
    return $s;
}
