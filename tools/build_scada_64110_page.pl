#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use open ':std', ':encoding(UTF-8)';
use File::Basename;

my $md_dir   = $ARGV[0] || 'sources/extracted/scada-docs-6.41.10-md';
my $out_html = $ARGV[1] || 'scada/docs-6.41.10.html';
my $case_matches = "$md_dir/case_matches.md";

open my $cm, '<:encoding(UTF-8)', $case_matches or die "Cannot read $case_matches: $!";
my $cm_text = do { local $/; <$cm> };
close $cm;

my @sections = split /\n## Кейс \d+\. /, $cm_text;
shift @sections; # remove intro

my @cases;
for my $sec (@sections) {
    my @lines = split /\n/, $sec;
    my $title = shift @lines;
    my @files;
    my $count = 0;
    for my $line (@lines) {
        if ($line =~ /^\|\s*(\d+)\s*\|\s*\[([^\]]+)\]\([^)]*\)\s*\|/) {
            push @files, { score => $1, file => $2 };
            $count++;
            last if $count >= 3;
        }
    }
    push @cases, { title => $title, files => \@files };
}

sub read_md_excerpt {
    my ($file, $max_chars) = @_;
    $max_chars ||= 4000;
    my $path = "$md_dir/$file";
    return (undef, "Файл не найден: $file") unless -f $path;
    open my $fh, '<:encoding(UTF-8)', $path or return (undef, "Не удалось открыть $file: $!");
    my $text = do { local $/; <$fh> };
    close $fh;

    # Try to extract title from first heading
    my $title = $file;
    if ($text =~ /^#\s+(.+)/) {
        $title = $1;
    }

    # Trim to reasonable excerpt length, do not break inside fenced code block
    my $excerpt = '';
    if (length($text) <= $max_chars) {
        $excerpt = $text;
    } else {
        my $cut = substr($text, 0, $max_chars);
        # If inside a code fence, extend to closing fence
        my $open_fences = () = $cut =~ /```/g;
        if ($open_fences % 2 == 1) {
            my $rest = substr($text, $max_chars);
            if ($rest =~ /(.*?```)/s) {
                $cut .= $1;
            }
        }
        # Try to end at the last paragraph boundary in the second half of the cut
        my $boundary = -1;
        if ($cut =~ /\n\n(?=[^\n])/g) {
            my @pos;
            while ($cut =~ /\n\n/g) { push @pos, pos($cut); }
            for my $p (reverse @pos) {
                if ($p > $max_chars * 0.55) { $boundary = $p; last; }
            }
        }
        if ($boundary > 0) {
            $cut = substr($cut, 0, $boundary);
        }
        $excerpt = $cut . "\n\n_… выдержка обрезана; полный раздел доступен в локальной папке `sources/extracted/scada-docs-6.41.10-md/`._";
    }
    return ($title, $excerpt);
}

sub md_to_html {
    my ($md) = @_;
    my @lines = split /\n/, $md;
    my @out;
    my $in_pre = 0;
    my $pre_buf = '';
    my $list_type = ''; # 'ul' or 'ol'
    my $pending_li = 0;

    my $i = 0;
    while ($i < @lines) {
        my $line = $lines[$i];
        $line =~ s/\r$//;

        if ($line =~ /^```(.*)$/) {
            if ($in_pre) {
                my $lang = $1 || '';
                push @out, "<pre><code" . ($lang ? " class=\"lang-$lang\"" : '') . ">$pre_buf</code></pre>";
                $pre_buf = '';
                $in_pre = 0;
            } else {
                if ($list_type) { push @out, "</$list_type>"; $list_type = ''; }
                $pending_li = 0;
                $in_pre = 1;
            }
            $i++;
            next;
        }

        if ($in_pre) {
            $pre_buf .= ($pre_buf ? "\n" : '') . escape_html($line);
            $i++;
            next;
        }

        # Empty line
        if ($line =~ /^\s*$/) {
            if ($list_type) { push @out, "</$list_type>"; $list_type = ''; }
            $pending_li = 0;
            $i++;
            next;
        }

        # Tables: collect contiguous lines starting with |
        if ($line =~ /^\|/) {
            if ($list_type) { push @out, "</$list_type>"; $list_type = ''; }
            $pending_li = 0;
            my @tbl_lines = ($line);
            $i++;
            while ($i < @lines) {
                my $next = $lines[$i];
                $next =~ s/\r$//;
                last unless $next =~ /^\s*(?:\|.*)?$/ && $next =~ /\|/;
                push @tbl_lines, $next;
                $i++;
            }
            my $tbl = parse_table(@tbl_lines);
            push @out, $tbl if $tbl;
            next;
        }

        # Headings
        if ($line =~ /^(#{1,6})\s+(.+)$/) {
            if ($list_type) { push @out, "</$list_type>"; $list_type = ''; }
            $pending_li = 0;
            my $level = length($1);
            push @out, "<h" . ($level + 1) . ">" . inline_fmt($2) . "</h" . ($level + 1) . ">";
            $i++;
            next;
        }

        # Unordered list marker
        if ($line =~ /^\s*[-*]\s*(.*)$/) {
            my $content = $1;
            if ($content eq '') {
                # Empty marker: next non-empty line belongs to this list item
                $pending_li = 1;
                $i++;
                next;
            }
            if ($list_type && $list_type ne 'ul') { push @out, "</$list_type>"; $list_type = ''; }
            unless ($list_type) { $list_type = 'ul'; push @out, '<ul>'; }
            push @out, "<li>" . inline_fmt($content) . "</li>";
            $pending_li = 0;
            $i++;
            next;
        }

        # Ordered list
        if ($line =~ /^\s*\d+[.)]\s+(.+)$/) {
            if ($list_type && $list_type ne 'ol') { push @out, "</$list_type>"; $list_type = ''; }
            unless ($list_type) { $list_type = 'ol'; push @out, '<ol>'; }
            push @out, "<li>" . inline_fmt($1) . "</li>";
            $pending_li = 0;
            $i++;
            next;
        }

        # If pending list item, wrap this paragraph as a list item
        if ($pending_li) {
            unless ($list_type) { $list_type = 'ul'; push @out, '<ul>'; }
            push @out, "<li>" . inline_fmt($line) . "</li>";
            $pending_li = 0;
            $i++;
            next;
        }

        # Other line → paragraph with inline formatting
        if ($list_type) { push @out, "</$list_type>"; $list_type = ''; }
        push @out, "<p>" . inline_fmt($line) . "</p>";
        $i++;
    }

    if ($in_pre) {
        push @out, "<pre><code>$pre_buf</code></pre>";
    }
    if ($list_type) { push @out, "</$list_type>"; }

    return join("\n", @out);
}

sub escape_html {
    my ($s) = @_;
    $s =~ s/&/&amp;/g;
    $s =~ s/</&lt;/g;
    $s =~ s/>/&gt;/g;
    return $s;
}

sub inline_fmt {
    my ($s) = @_;
    $s = escape_html($s);
    # Images → plain alt text
    $s =~ s/!\[([^\]]*)\]\([^)]+\)/$1/g;
    # Links → span with title
    $s =~ s/\[([^\]]+)\]\([^)]+\)/<span class=\"md-link\" title=\"Внутренняя ссылка справки\">$1<\/span>/g;
    # Bold + italic (asterisks and underscores)
    $s =~ s/\*\*\*(.+?)\*\*\*/<strong><em>$1<\/em><\/strong>/g;
    $s =~ s/\*\*(.+?)\*\*/<strong>$1<\/strong>/g;
    $s =~ s/\*(.+?)\*/<em>$1<\/em>/g;
    $s =~ s/___(.+?)___/<strong><em>$1<\/em><\/strong>/g;
    $s =~ s/__(.+?)__/<strong>$1<\/strong>/g;
    # Do not convert single underscores (common inside identifiers like ls_conref_root)
    # Code
    $s =~ s/`([^`]+)`/<code>$1<\/code>/g;
    return $s;
}

sub parse_table {
    my (@lines) = @_;
    my @rows;
    my $first = 1;
    for my $line (@lines) {
        next unless $line =~ /^\|/;
        # separator line like | --- | --- |
        next if $line =~ /^\|\s*(?:---+\s*\|)+\s*$/;
        my @cells = split /\|/, $line;
        shift @cells if @cells && $cells[0] =~ /^\s*$/;
        pop @cells if @cells && $cells[-1] =~ /^\s*$/;
        @cells = map { s/^\s+|\s+$//g; $_ } @cells;
        next unless @cells;
        my $tag = $first ? 'th' : 'td';
        push @rows, '<tr>' . join('', map { "<$tag>" . inline_fmt($_) . "</$tag>" } @cells) . '</tr>';
        $first = 0;
    }
    return @rows ? "<table class=\"md-table\">" . join('', @rows) . "</table>" : '';
}

# Build main content
my @nav;
my @main_parts;

my $case_num = 1;
for my $case (@cases) {
    my $id = "case-$case_num";
    push @nav, "<a href=\"#$id\">Кейс $case_num. $case->{title}</a>";

    my @items_html;
    for my $item (@{ $case->{files} }) {
        my ($title, $excerpt) = read_md_excerpt($item->{file});
        unless (defined $title) {
            $title = $item->{file};
            $excerpt = "_Раздел недоступен._";
        }
        my $html_excerpt = md_to_html($excerpt);
        push @items_html, <<"ITEM";
<div class="excerpt">
<h4>$title <span class="badge">релевантность: $item->{score}</span></h4>
<p><em>Файл справки:</em> <code>$item->{file}</code></p>
$html_excerpt
</div>
ITEM
    }

    push @main_parts, <<"SECTION";
<section id="$id">
<h2>Кейс $case_num. $case->{title}</h2>
@{[ join("\n", @items_html) ]}
</section>
SECTION

    $case_num++;
}

my $nav_html = join("\n", @nav);
my $main_html = join("\n\n", @main_parts);

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
  <title>RatioT SCADA 6.41.10 — карта справки по кейсам</title>
  <link rel="stylesheet" href="style.css">
  <style>
    .excerpt { margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border); }
    .excerpt:first-of-type { border-top: none; padding-top: 0; }
    .md-link { color: var(--accent); border-bottom: 1px dashed var(--accent); cursor: help; }
    h5, h6 { margin-top: 18px; font-size: 1rem; color: var(--muted); }
    .md-table { font-size: .88rem; width: auto; }
    .md-table th, .md-table td { padding: 6px 8px; }
    aside nav { max-height: calc(100vh - 140px); overflow-y: auto; }
    aside nav a { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  </style>
</head>
<body>
  <div class="layout">
    <aside>
      <h1>RatioT SCADA</h1>
      <div class="subtitle">Справка 6.41.10 по кейсам</div>
      <nav>
        <a href="index.html">← Общая база знаний</a>
        <a href="#intro">Введение</a>
$nav_html
      </nav>
    </aside>

    <main>
      <section id="intro">
        <h2>Карта встроенной справки RatioT SCADA 6.41.10 по баг-кейсам</h2>
        <p>Эта страница — мост между 17 зафиксированными баг-кейсами и актуальной встроенной справкой сервера <strong>6.41.10</strong>. Для каждого кейса выбраны три наиболее релевантных раздела справки; под каждым разделом дана краткая выдержка.</p>
        <p>Источник: локальная копия встроенной справки <code>sources/extracted/scada-docs-6.41.10-md/</code>. Полные md-разделы хранятся только локально и не публикуются в репозитории.</p>
        <div class="note">
          <strong>Зачем это нужно:</strong> при анализе бага можно сразу попасть в нужный раздел официальной справки и понять, ожидаемое ли поведение описано в документации или это действительно дефект.
        </div>
      </section>

$main_html

      <footer>
        Построено автоматически из <code>case_matches.md</code> и md-разделов встроенной справки RatioT SCADA 6.41.10.
      </footer>
    </main>
  </div>

  <script>
    const sections = document.querySelectorAll('section[id]');
    const links = document.querySelectorAll('nav a[href^="#"]');
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

open my $out, '>:encoding(UTF-8)', $out_html or die "Cannot write $out_html: $!";
print $out $html;
close $out;

print "Generated $out_html with ", scalar(@cases), " cases.\n";
