#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use open ':std', ':encoding(UTF-8)';
use File::Path qw(make_path);
use File::Basename;

my $md_dir  = $ARGV[0] || 'sources/extracted/scada-docs-6.41.10-md';
my $out_dir = $ARGV[1] || 'scada/docs-6.41.10';
make_path($out_dir) unless -d $out_dir;

my @chapters = (
    { slug => 'intro', title => 'Введение и обзор платформы' },
    { slug => 'install', title => 'Установка, запуск и обслуживание' },
    { slug => 'architecture', title => 'Архитектура и конфигурация сервера' },
    { slug => 'users', title => 'Пользователи, права и безопасность' },
    { slug => 'model', title => 'Модель данных, контексты и классы' },
    { slug => 'devices', title => 'Устройства, драйверы и протоколы' },
    { slug => 'database', title => 'Базы данных, хранилище, история' },
    { slug => 'webui', title => 'Web UI, HMI и дашборды' },
    { slug => 'scripts', title => 'Скрипты, выражения и запросы' },
    { slug => 'events', title => 'События, аварии и уведомления' },
    { slug => 'cluster', title => 'Кластер, отказоустойчивость и распределённые вычисления' },
    { slug => 'network', title => 'Сетевое управление' },
    { slug => 'desktop', title => 'Десктопный клиент' },
    { slug => 'integration', title => 'Интеграция, приложения и отчёты' },
    { slug => 'tutorials', title => 'Учебники и устранение неполадок' },
);

my %chapter_for;
$chapter_for{$_->{slug}} = $_ for @chapters;

sub classify {
    my ($file, $title) = @_;
    my $f = lc($file);

    # Tutorials and troubleshooting
    return 'tutorials' if $f =~ /^(tut_|tutorials|troubleshooting)/;

    # Desktop client (must be before 'cl_interactive_guide' trickery)
    return 'desktop' if $f =~ /^cl_/;
    return 'desktop' if $f =~ /^client\.md$/;

    # Access control
    return 'users' if $f =~ /^ac_/;
    return 'users' if $f =~ /^access_control\.md$/;

    # Device servers
    return 'devices' if $f =~ /^ds_/;
    return 'devices' if $f =~ /^device_servers\.md$/;

    # Cluster
    return 'cluster' if $f =~ /^cluster_/;

    # Network management
    return 'network' if $f =~ /^nm_/;
    return 'network' if $f =~ /^network_management\.md$/;

    # Web UI / HMI helpers (sh_)
    return 'webui' if $f =~ /^sh_/;

    # Programming / integration helpers
    return 'scripts' if $f =~ /^int_/;

    # Events / messaging
    return 'events' if $f =~ /^mes_/;

    # Agent / integration
    return 'integration' if $f =~ /^ag_/;

    # Appendix / protocol / formatting reference
    return 'integration' if $f =~ /^ap_/;

    # Introduction / overview / general
    return 'intro' if $f =~ /^(basics|introduction|about_company|scada|products|ru_docs_64|agent|copyright|mdocsru|feedback|space|time|appendixes)\./;
    return 'intro' if $f =~ /^(basics|introduction|about_company|scada|products|ru_docs_64|agent|copyright|mdocsru|feedback|space|time|appendixes|copyright|index|mdocsru)$/;

    # Installation, startup, maintenance
    return 'install' if $f =~ /^ls_(installation|upgrade|deployment|requirements|startup|shutdown|service|maintenance|backups|migration|uninstallation)/;
    return 'install' if $f =~ /^uninstallation\.md$/;

    # Architecture / server configuration
    return 'architecture' if $f =~ /^ls_(architecture|system|status|memory|command|configuration|config|netadmin|common|plugins|remote|safe|resources|autorun|deployment)/;
    return 'architecture' if $f =~ /^basics_(structure|data_model|versions|app_development|low_code|customization)\./;

    # Users / permissions / security
    return 'users' if $f =~ /^ls_(users|groups|password|license|validity|permissions)/;

    # Model / contexts / classes
    return 'model' if $f =~ /^ls_(conref|models|devices|classes)/;

    # Devices / drivers / protocols
    return 'devices' if $f =~ /^ls_(drivers|connectivity|device)/;

    # Database / storage / history
    return 'database' if $f =~ /^ls_(database|nosql|storage|history|logging|media|cassandra)/;

    # Web UI / HMI / dashboards
    return 'webui' if $f =~ /^ls_(wui|widgets|dashboards|web|visualization)/;

    # Scripts / expressions / queries
    return 'scripts' if $f =~ /^ls_(internals|queries|sql|scripts|actions|dynamic|programming|expression)/;

    # Events / alerts / notifications
    return 'events' if $f =~ /^ls_(conref_events|alerts|event|correlators|email|sms|messaging)/;

    # Cluster / failover / distributed
    return 'cluster' if $f =~ /^ls_(failover|distributed|machine|jobs)/;

    # Network management
    return 'network' if $f =~ /^ls_netadmin/;

    # Integration / API / applications / reports
    return 'integration' if $f =~ /^ls_(applications|plugins|store|reports|trackers|geofences|workflows|favourites|media|resources|remote|command)/;
    return 'integration' if $f =~ /^integration\.md$/;

    return 'other';
}

# Read all files
opendir my $dh, $md_dir or die "Cannot open $md_dir: $!";
my @md_files = sort grep { /\.md$/i && $_ ne 'case_matches.md' && $_ ne 'index.md' } readdir($dh);
closedir $dh;

my @all_records;
my %grouped;

for my $file (@md_files) {
    my $path = "$md_dir/$file";
    open my $fh, '<:encoding(UTF-8)', $path or do { warn "Cannot read $path: $!"; next; };
    my $content = do { local $/; <$fh> };
    close $fh;

    my $title = $file;
    if ($content =~ /^#\s+(.+)/m) {
        $title = $1;
        $title =~ s/\s+/ /g;
        $title =~ s/^\s+|\s+$//g;
    }

    my $chapter = classify($file, $title);
    push @all_records, { file => $file, title => $title, chapter => $chapter, content => $content };
    push @{ $grouped{$chapter} }, $all_records[-1];
}

# Move 'other' items to nearest chapters by broad keyword match
for my $r (@{ $grouped{other} // [] }) {
    my $f = lc($r->{file});
    my $t = lc($r->{title});
    my $ch = 'intro';
    $ch = 'install' if $f =~ /install|startup|upgrade|migration|backup|maintenance|requirements/;
    $ch = 'architecture' if $f =~ /config|architecture|system|command|netadmin|plugins|autorun|safe/;
    $ch = 'users' if $f =~ /user|group|password|license|permission|access|cardholder|account/;
    $ch = 'model' if $f =~ /conref|model|device(?!server)|class|context/;
    $ch = 'devices' if $f =~ /driver|device|server|opc|modbus|mqtt|bacnet|snmp/;
    $ch = 'database' if $f =~ /database|nosql|storage|history|log|cassandra|sql/;
    $ch = 'webui' if $f =~ /wui|widget|dashboard|web|visual|hmi|gui|component|builder|view/;
    $ch = 'scripts' if $f =~ /internal|expression|query|script|function|variable|binding|programming/;
    $ch = 'events' if $f =~ /event|alert|alarm|notification|email|sms|message|correlator/;
    $ch = 'cluster' if $f =~ /cluster|failover|distributed|machine|job/;
    $ch = 'network' if $f =~ /network|nm|interface|ip|connection|comm/;
    $ch = 'desktop' if $f =~ /client|ide|editor|window|menu|toolbar|dialog|viewer|report|report/;
    $ch = 'integration' if $f =~ /agent|api|appendix|application|plugin|store|report|tracker|geofence|workflow|resource|remote|protocol|import|export|format|charset/;
    $ch = 'tutorials' if $f =~ /tut|tutorial|troubleshoot|guide/;
    $r->{chapter} = $ch;
    push @{ $grouped{$ch} }, $r;
}
$grouped{other} = [] if exists $grouped{other};

# HTML helpers
sub escape_html {
    my ($s) = @_;
    $s =~ s/&/&amp;/g;
    $s =~ s/</&lt;/g;
    $s =~ s/>/&gt;/g;
    return $s;
}

sub normalize_md {
    my ($md, $title) = @_;
    # Remove source line
    $md =~ s/^\s*_Источник:\s*`[^`]+`_\s*\n+//m;
    # Remove any trailing "… выдержка обрезана" artifacts
    $md =~ s/\n*_… выдержка обрезана[^\n]*//;
    return $md;
}

sub inline_fmt {
    my ($s) = @_;

    # Protect inline code spans first with a marker unlikely to collide
    my @codes;
    $s =~ s/`([^`]+)`/push @codes, $1; "\x{27e6}CODE" . scalar(@codes) . "\x{27e7}"/ge;

    # Images and internal links → plain text only
    $s =~ s/!\[([^\]]*)\]\([^)]+\)/$1/g;
    $s =~ s/\[([^\]]+)\]\([^)]+\)/$1/g;
    # Nested-link markers like [[?]](url) → [?]
    $s =~ s/\[\[([^\]]+)\]\]\([^)]+\)/[$1]/g;

    # Escape HTML entities before generating HTML tags
    $s = escape_html($s);

    # Bold + italic (asterisks and underscores)
    $s =~ s/\*\*\*(.+?)\*\*\*/<strong><em>$1<\/em><\/strong>/g;
    $s =~ s/\*\*(.+?)\*\*/<strong>$1<\/strong>/g;
    $s =~ s/\*(.+?)\*/<em>$1<\/em>/g;
    $s =~ s/___(.+?)___/<strong><em>$1<\/em><\/strong>/g;
    $s =~ s/__(.+?)__/<strong>$1<\/strong>/g;
    # Single underscores denote emphasis, avoid identifiers with internal underscores
    $s =~ s/(?<![A-Za-z0-9])_((?:[^_]|_(?=[A-Za-z0-9]))+?)_(?![A-Za-z0-9])/<em>$1<\/em>/g;

    # Restore code spans
    for (my $i = 0; $i < @codes; $i++) {
        my $code = escape_html($codes[$i]);
        my $marker = "\x{27e6}CODE" . ($i + 1) . "\x{27e7}";
        $s =~ s/\Q$marker\E/<code>$code<\/code>/g;
    }
    return $s;
}

sub md_to_html {
    my ($md, $title) = @_;
    $md = normalize_md($md, $title);
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
            if ($list_type) {
                # Look ahead: if next non-empty line is also a list item, keep list open
                my $j = $i + 1;
                while ($j < @lines && $lines[$j] =~ /^\s*$/) { $j++; }
                if ($j < @lines && $lines[$j] =~ /^\s*[-*\d]/) {
                    $i++;
                    next;
                }
                push @out, "</$list_type>"; $list_type = '';
            }
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
            my $tag = "h" . ($level + 1);
            push @out, "<$tag>" . inline_fmt($2) . "</$tag>";
            $i++;
            next;
        }

        # Unordered list marker (require whitespace after marker so *bold* isn't a list)
        if ($line =~ /^\s*[-]\s+(.*)$/ || $line =~ /^\s*\*\s+(.*)$/) {
            my $content = $1;
            if ($content eq '') {
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

sub parse_table {
    my (@lines) = @_;
    my @rows;

    # Locate the Markdown table separator (| --- | --- |).
    # If it exists, the row immediately above it is the header.
    my $sep_idx = -1;
    for (my $i = 0; $i < @lines; $i++) {
        my $line = $lines[$i];
        next unless defined $line && $line =~ /^\|/;
        if ($line =~ /^\|\s*(?:\s*[-:]+\s*\|)+\s*$/) {
            $sep_idx = $i;
            last;
        }
    }

    my $row_idx = 0;
    my $header_done = ($sep_idx < 0) ? 1 : 0;
    for my $line (@lines) {
        next unless defined $line && $line =~ /^\|/;
        if ($row_idx == $sep_idx) {
            $row_idx++;
            next;
        }
        my @cells = split /\|/, $line;
        shift @cells if @cells && $cells[0] =~ /^\s*$/;
        pop @cells if @cells && $cells[-1] =~ /^\s*$/;
        @cells = map { s/^\s+|\s+$//g; $_ } @cells;
        next unless @cells;
        my $tag = $header_done ? 'td' : 'th';
        push @rows, '<tr>' . join('', map { "<$tag>" . inline_fmt($_) . "</$tag>" } @cells) . '</tr>';
        $header_done = 1 if $row_idx == $sep_idx - 1;
        $row_idx++;
    }
    return @rows ? "<table class=\"md-table\">" . join('', @rows) . "</table>" : '';
}

# Build chapter pages
my @chapter_nav;
for my $ch (@chapters) {
    push @chapter_nav, { slug => $ch->{slug}, title => $ch->{title} };
}

for my $ch (@chapters) {
    my $slug = $ch->{slug};
    my $records = $grouped{$slug} // [];
    next unless @$records;

    # Local TOC
    my @toc = map { "<li><a href=\"#" . section_id($_->{file}) . "\">" . escape_html($_->{title}) . "</a></li>" } @$records;

    # Content
    my @sections;
    for my $r (@$records) {
        my $id = section_id($r->{file});
        my $html = md_to_html($r->{content}, $r->{title});
        push @sections, <<"SECTION";
<section id="$id" class="doc-section">
$html
</section>
SECTION
    }

    my $nav_html = join("\n", map {
        my $active = ($_->{slug} eq $slug) ? ' class="active"' : '';
        "<a href=\"$_->{slug}.html\"$active>$_->{title}</a>"
    } @chapter_nav);

    my $page = page_template(
        $ch->{title},
        $ch->{title},
        $nav_html,
        "<section id=\"intro\"><h2>Оглавление главы</h2><ul>" . join("\n", @toc) . "</ul></section>\n\n" . join("\n\n", @sections)
    );

    open my $out, '>:encoding(UTF-8)', "$out_dir/$slug.html" or die "Cannot write $out_dir/$slug.html: $!";
    print $out $page;
    close $out;

    print "Wrote $slug.html with ", scalar(@$records), " sections\n";
}

# Build index
my @index_parts;
for my $ch (@chapters) {
    my $records = $grouped{$ch->{slug}} // [];
    next unless @$records;
    my @items = map { "<li>" . escape_html($_->{title}) . "</li>" } @$records;
    my @visible = @items ? @items[0..($#items < 19 ? $#items : 19)] : ();
    my $count = scalar @$records;
    push @index_parts, <<"CHAPTER";
<section id="$ch->{slug}">
<h2><a href="$ch->{slug}.html">$ch->{title}</a></h2>
<p>Разделов: <strong>$count</strong>.</p>
<ul class="chapter-toc">
@{[ join("\n", @visible) ]}
</ul>
@{[ @items > 20 ? '<p><em>… и другие разделы — см. главу.</em></p>' : '' ]}
</section>
CHAPTER
}

my $index_nav = join("\n", map { "<a href=\"$_->{slug}.html\">$_->{title}</a>" } @chapter_nav);
my $index_page = page_template(
    'RatioT SCADA 6.41.10 — документация',
    'Документация RatioT SCADA 6.41.10',
    $index_nav,
    "<section id=\"intro\"><h2>О чём эта документация</h2><p>Это переиздание встроенной справки RatioT SCADA 6.41.10 в удобном для чтения виде. Материал сгруппирован по темам и не обрезан. Внутренние ссылки преобразованы в текст.</p></section>\n\n" . join("\n\n", @index_parts)
);

open my $idx, '>:encoding(UTF-8)', "$out_dir/index.html" or die "Cannot write $out_dir/index.html: $!";
print $idx $index_page;
close $idx;

print "Done. Wrote ", scalar(@chapters), " chapter pages and index.html\n";

sub section_id {
    my ($file) = @_;
    my $id = $file;
    $id =~ s/\.md$//;
    $id =~ s/[^a-zA-Z0-9_-]/-/g;
    return $id;
}

sub page_template {
    my ($title, $heading, $nav, $main) = @_;
    return <<"HTML";
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
  <title>@{[ escape_html($title) ]}</title>
  <link rel="stylesheet" href="../style.css">
  <style>
    .chapter-toc { columns: 1; }
    \@media (min-width: 700px) { .chapter-toc { columns: 2; } }
    .doc-section { margin-bottom: 64px; padding-bottom: 32px; border-bottom: 1px solid var(--border); }
    .doc-section:last-of-type { border-bottom: none; }
    .md-table { font-size: .9rem; width: auto; }
    .md-table th, .md-table td { padding: 8px 10px; }
    .md-table tr:first-child td { font-weight: 600; background: #f0f4f8; }
    .md-table th { font-weight: 600; background: #e2e8f0; }
    aside nav { max-height: calc(100vh - 140px); overflow-y: auto; }
    aside nav a { white-space: normal; }
    pre { overflow-x: auto; }
    .breadcrumbs { font-size: .9rem; color: var(--muted); margin-bottom: 16px; }
    .breadcrumbs a { color: var(--accent); text-decoration: none; }
    .breadcrumbs a:hover { text-decoration: underline; }
    .breadcrumbs span[aria-current="page"] { color: var(--text); font-weight: 500; }
  </style>
</head>
<body>
  <div class="layout">
    <aside>
      <h1>RatioT SCADA</h1>
      <div class="subtitle">Справка 6.41.10</div>
      <nav>
        <a href="index.html">← Оглавление справки</a>
        <a href="../index.html">← Главная</a>
$nav
      </nav>
    </aside>

    <main>
      <nav class="breadcrumbs" aria-label="Хлебные крошки">
        <a href="../index.html">Главная</a>
        <span aria-hidden="true">→</span>
        <a href="index.html">Оглавление справки</a>
        <span aria-hidden="true">→</span>
        <span aria-current="page">@{[ escape_html($heading) ]}</span>
      </nav>
      <section id="intro">
        <h1>@{[ escape_html($heading) ]}</h1>
      </section>

$main

      <footer>
        Документация RatioT SCADA 6.41.10.
      </footer>
    </main>
  </div>

  <script>
    const sections = document.querySelectorAll('section[id]');
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
}
