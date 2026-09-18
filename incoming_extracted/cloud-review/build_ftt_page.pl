use strict; use warnings; use utf8;
my ($frag_file, $out_file) = @ARGV;
open my $fh, '<:encoding(UTF-8)', $frag_file or die $!;
my $frag = do { local $/; <$fh> };
close $fh;

# 1. Strip the broken docx TOC ("Оглавление" h1 + broken TOC paragraphs up to first real section)
$frag =~ s{<h1 id="оглавление">.*?(?=<h1 id="1-общие-сведения">)}{}s;

# 2. Convert paragraph-styled-as-heading artifact back to a paragraph
$frag =~ s{<h2 id="отдельные-сценарии-[^"]*">(.*?)</h2>}{<p><em>$1</em></p>}s;

# 3. Render checkbox placeholders
$frag =~ s/\[ \]/☐/g;

my @nav;
while ($frag =~ /<h1 id="([^"]+)">([^<]+)</g) {
  my ($id, $title) = ($1, $2);
  next if $id =~ /^(функциональные-технические|оглавление)/;
  (my $short = $title) =~ s/^(\d+)\..*/$1./;
  push @nav, [$id, $title];
}

my $nav_html = join('', map { qq{        <a href="#$_->[0]" title="$_->[1]">$_->[1]</a>\n} } @nav);

my $page = <<'HEAD';
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
  <title>ФТТ RatioT.Cloud (чтение на портале)</title>
  <link rel="stylesheet" href="../../style.css">
  <style>
    main h1 { margin-top: 56px; }
    main h2 { margin-top: 32px; }
    .banner {
      background: var(--panel);
      border: 1px solid var(--border);
      border-left: 4px solid var(--accent);
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 32px;
      color: var(--muted);
      line-height: 1.5;
    }
  </style>
</head>
<body>
  <div class="layout">
    <aside>
      <h1>RatioT Cloud</h1>
      <div class="subtitle">ФТТ — чтение на портале</div>
      <nav>
NAVPLACEHOLDER      </nav>
    </aside>

    <main>
      <div class="banner">
        Редакция <strong>v004 от 14.09.2026</strong> — снимок для чтения. Правки ведутся в исходном RatioT.Cloud_FTT.docx; после каждой редакции эта страница перегенерируется. Замечания по ревью — в <a href="../review/index.html">протоколе разногласий</a>.
      </div>
CONTENTPLACEHOLDER
      <footer>
        ФТТ RatioT.Cloud, редакция v004 от 14 сентября 2026. Страница сгенерирована для чтения на портале.
      </footer>
    </main>
  </div>

  <script>
    const headings = document.querySelectorAll('main h1[id]');
    const links = document.querySelectorAll('nav a[href^="#"]');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          links.forEach(link => link.classList.remove('active'));
          const active = document.querySelector('nav a[href="#' + entry.target.id + '"]');
          if (active) active.classList.add('active');
        }
      });
    }, { rootMargin: '-10% 0px -75% 0px' });
    headings.forEach(h => observer.observe(h));
  </script>
</body>
</html>
HEAD

$page =~ s/NAVPLACEHOLDER/$nav_html/;
$page =~ s/CONTENTPLACEHOLDER/$frag/;

open my $out, '>:encoding(UTF-8)', $out_file or die $!;
print $out $page;
close $out;
print "OK: ", scalar(@nav), " nav items\n";
