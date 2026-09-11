#!/usr/bin/env perl
# Генерация bug_cases.html из tests/BUG_CASES.md (pandoc-версия для окружений без Python).
# Кейсы группируются по полю **Категория:** из markdown:
# 1. Ошибки кастомизации, 2. Ошибки OEM, 3. Ошибки платформы партнёра,
# 0. Не отправлены в АГ (в конец страницы).
use strict;
use warnings;
use utf8;
use open ':std', ':encoding(UTF-8)';

my $pandoc = 'lib/pandoc/pandoc-3.1.11/pandoc.exe';
my $md = 'tests/BUG_CASES.md';
my $out = 'bug_cases.html';

open my $md_fh, '<:encoding(UTF-8)', $md or die "Cannot read $md: $!";
my $md_text = do { local $/; <$md_fh> };
close $md_fh;
$md_text =~ s/\r//g;

# Drop standalone anchors; we will use pandoc header attributes instead
$md_text =~ s/^<a\s+id="(case-\d+|summary)"><\/a>\n+//mg;

# Разбиваем markdown на преамбулу, кейсы и итог
my @heads;
while ($md_text =~ /^##\s+(Кейс\s+(\d+)\.\s+.+?|Итог)\s*$/mg) {
    push @heads, { start => $-[0], headend => $+[0], title => $1, num => $2 };
}
my $preamble_md = substr($md_text, 0, $heads[0]{start});
my $summary_block;
my @cases;
for my $i (0 .. $#heads) {
    my $end = $i < $#heads ? $heads[$i + 1]{start} : length($md_text);
    my $block = substr($md_text, $heads[$i]{headend}, $end - $heads[$i]{headend});
    if (defined $heads[$i]{num}) {
        (my $title = $heads[$i]{title}) =~ s/^Кейс\s+\d+\.\s*//;
        push @cases, { num => $heads[$i]{num}, title => $title, body => $block };
    } else {
        $summary_block = $block;
    }
}

# Категория кейса берётся из поля **Категория:** N. Название; без поля — платформа
my %chapters;
for my $c (@cases) {
    my ($cat, $catname) = (3, 'Ошибки платформы партнёра');
    if ($c->{body} =~ /^\*\*Категория:\*\*\s*(\d+)\.\s*(.+?)\s*$/m) {
        ($cat, $catname) = ($1, $2);
    }
    $c->{body} =~ s/^\*\*Категория:\*\*[^\n]*\n//m;
    $chapters{$cat}{name} //= $catname;
    push @{ $chapters{$cat}{cases} }, $c;
}

# Собираем новый markdown: преамбула, главы с кейсами, итог (категория 0 «Не отправлены в АГ» — в конец)
my $new_md = $preamble_md;
my @nav_items;
for my $cat (sort { $a == 0 ? 1 : $b == 0 ? -1 : $a <=> $b } keys %chapters) {
    my $heading = $cat == 0 ? $chapters{$cat}{name} : "Глава $cat. $chapters{$cat}{name}";
    $new_md .= "## $heading {#cat-$cat .chapter}\n\n";
    $new_md .= "Эти кейсы в АГ не заводились — возможно, исправлены до выхода 6.41.10.\n\n" if $cat == 0;
    push @nav_items, { anchor => "cat-$cat", title => $heading, chapter => 1 };
    for my $c (@{ $chapters{$cat}{cases} }) {
        $new_md .= "## Кейс $c->{num}. $c->{title} {#case-$c->{num}}\n" . $c->{body};
        push @nav_items, { anchor => "case-$c->{num}", title => "$c->{num}. $c->{title}", chapter => 0 };
    }
}
if (defined $summary_block) {
    $new_md .= "## Итог {#summary}\n" . $summary_block;
    push @nav_items, { anchor => 'summary', title => 'Итог', chapter => 1 };
}

my $toc_html = join("\n", map {
    my $class = $_->{chapter} ? 'chapter-link' : 'case-link';
    '        <a href="#' . $_->{anchor} . '" class="' . $class . '">' . $_->{title} . '</a>'
} @nav_items);

# Write modified markdown to a temp file and convert with pandoc
my $tmp_md = 'bug_cases_input.md';
open my $tmp_in, '>:encoding(UTF-8)', $tmp_md or die "Cannot write $tmp_md: $!";
print $tmp_in $new_md;
close $tmp_in;

open my $body, '-|:encoding(UTF-8)', $pandoc, $tmp_md, '-t', 'html' or die "Cannot run pandoc: $!";
my $body_html = do { local $/; <$body> };
close $body;

# Post-process body HTML
# 1. Remove carriage returns
$body_html =~ s/\r//g;

# 2. Normalize the h1 title (it currently has an id with cyrillic text)
$body_html =~ s/<h1\s+id="[^"]*"\s*>\s*<\/h1>/<h1 id="top">Баг-кейсы RatioT SCADA<\/h1>/s;
$body_html =~ s/<h1\s+id="[^"]*"\s*>Баг-кейсы RatioT SCADA\s*6\.41\.09<\/h1>/<h1 id="top">Баг-кейсы RatioT SCADA 6.41\.09<\/h1>/s;

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
    .content h2.chapter { font-size: 1.6rem; margin-top: 52px; color: var(--accent); border-bottom: 2px solid var(--border); }
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
    nav a.chapter-link { font-weight: 700; margin-top: 14px; color: var(--accent); }
    nav a.case-link { padding-left: 22px; font-size: .9rem; }
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

print "Generated $out: " . scalar(@cases) . " кейсов в " . scalar(keys %chapters) . " главах\n";
