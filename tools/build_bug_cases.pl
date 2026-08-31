#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use open ':std', ':encoding(UTF-8)';

my $pandoc = 'lib/pandoc/pandoc-3.1.11/pandoc.exe';
my $md = 'tests/BUG_CASES.md';
my $out = 'bug_cases.html';

# Extract case anchors and titles from markdown
open my $md_fh, '<:encoding(UTF-8)', $md or die "Cannot read $md: $!";
my $md_text = do { local $/; <$md_fh> };
close $md_fh;
$md_text =~ s/\r//g;

# Drop standalone anchors; we will use pandoc header attributes instead
$md_text =~ s/^<a\s+id="(case-\d+|summary)"><\/a>\n+//mg;

# Extract case anchors and titles for the side navigation
my @nav_items;
while ($md_text =~ /^##\s+(Кейс\s+(\d+)\.\s+.+?|Итог)\s*$/mg) {
    my ($title, $case_num) = ($1, $2);
    my $anchor = defined $case_num ? "case-$case_num" : 'summary';
    $title =~ s/\s+$//;
    push @nav_items, { anchor => $anchor, title => $title };
}

my $toc_html = join("\n", map {
    '        <a href="#' . $_->{anchor} . '">' . $_->{title} . '</a>'
} @nav_items);

# Add pandoc header attributes so generated h2 ids are stable and headings stay intact
$md_text =~ s/^##\s+(Кейс\s+(\d+)\.\s+.+?)$/## $1 {#case-$2}/mg;
$md_text =~ s/^##\s+(Итог)\s*$/## $1 {#summary}/mg;

# Write modified markdown to a temp file and convert with pandoc
my $tmp_md = 'bug_cases_input.md';
open my $tmp_in, '>:encoding(UTF-8)', $tmp_md or die "Cannot write $tmp_md: $!";
print $tmp_in $md_text;
close $tmp_in;

open my $body, '-|:encoding(UTF-8)', $pandoc, $tmp_md, '-t', 'html' or die "Cannot run pandoc: $!";
my $body_html = do { local $/; <$body> };
close $body;

# Post-process body HTML
# 1. Remove carriage returns
$body_html =~ s/\r//g;

# 2. Normalize the h1 title (it currently has an id with cyrillic text)
$body_html =~ s/<h1\s+id="[^"]*"\s*>\s*<\/h1>/<h1 id="top">Баг-кейсы RatioT SCADA<\/h1>/s;
$body_html =~ s/<h1\s+id="[^"]*"\s*>Баг-кейсы RatioT SCADA\s*6\.41\.09<\/h1>/<h1 id="top">Баг-кейсы RatioT SCADA 6.41.09<\/h1>/s;

# 3. Strip the redundant "Оглавление" h2 since we have nav
$body_html =~ s/<h2\s+id="оглавление"\s*>Оглавление<\/h2>\s*<ul>.*?<\/ul>//s;

# 4. Fallback: clean up any remaining h2 ids with inline anchors
$body_html =~ s/<h2\s+id="[^"]*"\s*>\s*<a\s+id="(case-\d+|summary)"><\/a>\s*(.+?)<\/h2>/<h2 id="$1"><a id="$1"><\/a> $2<\/h2>/gs;

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
  <title>Баг-кейсы RatioT SCADA</title>
  <link rel="stylesheet" href="style.css">
  <style>
    .content { padding: 32px 40px; max-width: 900px; }
    .content h1 { font-size: 2rem; margin-bottom: 8px; }
    .content h2 { margin-top: 36px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
    .content h3 { margin-top: 24px; }
    .content p { margin: 12px 0; }
    .content ul, .content ol { margin: 12px 0; padding-left: 24px; }
    .content li { margin: 6px 0; }
    .content code { background: var(--code); padding: 2px 6px; border-radius: 4px; font-family: Consolas, monospace; }
    .content pre { background: var(--code); padding: 16px; border-radius: 8px; overflow-x: auto; }
    .content pre code { background: transparent; padding: 0; }
    .content blockquote { border-left: 4px solid var(--accent); margin: 16px 0; padding: 8px 16px; background: var(--accent-light); }
    .content table { border-collapse: collapse; width: 100%; margin: 16px 0; }
    .content th, .content td { border: 1px solid var(--border); padding: 8px 12px; text-align: left; }
    .content th { background: var(--accent-light); }
    .back { display: inline-block; margin-bottom: 20px; color: var(--accent); text-decoration: none; }
    .back:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="layout">
    <aside>
      <h1>RatioT SCADA</h1>
      <div class="subtitle">Баг-кейсы и тестирование</div>
      <nav>
        <a href="index.html">← На главную</a>
        <a href="scada/index.html">Документация SCADA</a>
        <a href="ux.html">UX-заметки</a>
$toc_html
      </nav>
    </aside>
    <main class="content">
      <a class="back" href="index.html">← На главную</a>
$body_html
    </main>
  </div>

  <script>
    const sections = document.querySelectorAll('h2[id], h1[id]');
    const links = document.querySelectorAll('nav a[href^="#"]');
    if (links.length) {
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
    }
  </script>
</body>
</html>
HTML

open my $fh, '>:encoding(UTF-8)', $out or die "Cannot write $out: $!";
print $fh $html;
close $fh;

print "Generated $out\n";
