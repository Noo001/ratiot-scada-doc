#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use open ':std', ':encoding(UTF-8)';

my $pandoc = 'lib/pandoc/pandoc-3.1.11/pandoc.exe';
my $md = 'tests/BUG_CASES.md';
my $out = 'bug_cases.html';

open my $body, '-|:encoding(UTF-8)', $pandoc, $md, '-t', 'html' or die "Cannot run pandoc: $!";
my $body_html = do { local $/; <$body> };
close $body;

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
        <a href="index.html">\u2190 На главную</a>
        <a href="scada/index.html">Документация SCADA</a>
        <a href="scada/docs-6.41.10/index.html">Справка 6.41.10</a>
        <a href="ux.html">UX-заметки</a>
      </nav>
    </aside>
    <main class="content">
      <a class="back" href="index.html">\u2190 На главную</a>
$body_html
    </main>
  </div>
</body>
</html>
HTML

open my $fh, '>:encoding(UTF-8)', $out or die "Cannot write $out: $!";
print $fh $html;
close $fh;

print "Generated $out\n";
