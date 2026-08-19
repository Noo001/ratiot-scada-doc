#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use open ':std', ':encoding(UTF-8)';

my $tsv_file = $ARGV[0] || 'sources/extracted/changelog/changelog_parsed.tsv';
my $out_file = $ARGV[1] || 'sources/extracted/changelog/changelog_bug_cases_report.md';

open my $fh, '<:encoding(UTF-8)', $tsv_file or die "Cannot read $tsv_file: $!";
my $header = <$fh>;
my @records;
while (<$fh>) {
    chomp;
    my @cols = split /\t/, $_, 4;
    next unless @cols == 4;
    push @records, {
        version => $cols[0],
        type    => $cols[1],
        code    => $cols[2],
        text    => ' ' . lc($cols[3]) . ' ',
        text_orig => $cols[3],
    };
}
close $fh;

# Helpers
sub has {
    my ($text, $term) = @_;
    $term = ' ' . lc($term) . ' ';
    return index($text, $term) >= 0;
}

sub has_any {
    my ($text, $terms) = @_;
    for my $t (@$terms) { return 1 if has($text, $t); }
    return 0;
}

sub has_all {
    my ($text, $terms) = @_;
    for my $t (@$terms) { return 0 unless has($text, $t); }
    return 1;
}

sub score_match {
    my ($text, $required_groups, $bonus_terms, $exclude_terms) = @_;
    # required_groups: array of arrays; match at least one term from each group
    return 0 unless @$required_groups;
    my $score = 0;
    for my $group (@$required_groups) {
        my $ok = 0;
        my $best = 0;
        for my $t (@$group) {
            if (has($text, $t)) {
                $ok = 1;
                $best = length($t) if length($t) > $best;
            }
        }
        return 0 unless $ok;
        $score += $best;
    }
    for my $t (@$bonus_terms) {
        $score += length($t) if has($text, $t);
    }
    for my $t (@$exclude_terms) {
        return 0 if has($text, $t);
    }
    return $score;
}

my @cases = (
    {
        id => 1,
        title => 'Ошибки создания ресурсов при первом запуске сервера',
        required => [
            ['error creating resource', 'cannot invoke', 'container is null', 'context unavailable', 'context was not created'],
        ],
        bonus => ['avatar', 'workflowmodel', 'maintenance', 'server startup', 'first start'],
        exclude => ['resource filter', 'filter resources'],
        notes => 'Проблема инициализации встроенных ресурсов сервера (avatarManagement, workflowModel, maintenance).',
    },
    {
        id => 2,
        title => 'Режимы лицензирования free / trial не описаны в документации',
        required => [
            ['free license', 'trial license', '100 tags', 'free mode', 'trial mode', 'trial period'],
        ],
        bonus => ['licensing', 'license type', 'license mode'],
        exclude => [],
        notes => 'Режимы free/trial — специфика RatioT. В базовом AggreGate, скорее всего, не встречаются.',
    },
    {
        id => 3,
        title => 'Инсталлятор запрашивает перезапись собственных файлов',
        required => [
            ['wizard_1.png', 'wizard_2.png', 'replace file', 'overwrite own', 'installer overwrite'],
        ],
        bonus => ['installer', 'setup', 'installation files'],
        exclude => [],
        notes => 'Проблема упаковки инсталлятора (перезапись собственных файлов).',
    },
    {
        id => 4,
        title => 'Импорт Modbus-регистров из CSV/XML теряет имена, описания и адреса',
        required => [
            ['modbus', 'cyrillic', 'encoding'],
            ['csv', 'xml', 'import', 'export', 'encoding', 'register'],
        ],
        bonus => ['modbus', 'register', 'registers', 'csv', 'xml'],
        exclude => [],
        notes => 'Проблема импорта/экспорта Modbus-регистров в форматах CSV/XML. В данном changelog Modbus не упоминается; найдена связанная проблема с кодировкой кириллицы.',
    },
    {
        id => 5,
        title => 'eventLog сбрасывает настройки колонок при поступлении событий',
        required => [
            ['event log', 'eventlog', 'event journal', 'journal of events'],
            ['column', 'columns', 'width', 'visibility', 'manual width'],
        ],
        bonus => ['settings', 'reset', 'default'],
        exclude => [],
        notes => 'Проблема компонента журнала событий: сброс настроек колонок.',
    },
    {
        id => 6,
        title => 'В дереве тегов невозможно выбрать абсолютную модель в качестве источника',
        required => [
            ['tag tree', 'tree of tags', 'absolute model', 'model source', 'tag source'],
        ],
        bonus => ['digital twin', 'source', 'tree'],
        exclude => [],
        notes => 'Проблема дерева тегов / цифрового двойника.',
    },
    {
        id => 7,
        title => 'NoSQL-хранилище событий ломает сервер',
        required => [
            ['nosql'],
            ['event storage', 'event store', 'event storages', 'storage'],
        ],
        bonus => ['embedded', 'cassandra', 'windows', 'event'],
        exclude => [],
        notes => 'Критическая проблема переключения хранилища событий на NoSQL.',
    },
    {
        id => 8,
        title => 'HTML-сниппет сдвигает layout дашборда',
        required => [
            ['html snippet', 'html component', 'html snipet'],
        ],
        bonus => ['dashboard', 'layout', 'shift', 'snipet'],
        exclude => [],
        notes => 'Проблема отображения HTML-сниппета на дашборде.',
    },
    {
        id => 9,
        title => 'Установка в нестандартную папку + замена лицензии приводит к отказу лицензирования',
        required => [
            ['activation key', 'license file', 'license activation'],
        ],
        bonus => ['install path', 'installation directory', 'license', 'license server'],
        exclude => ['license information tab'],
        notes => 'Проблема лицензирования при нестандартной установке / замене файла лицензии.',
    },
    {
        id => 10,
        title => 'Локальный магазин приложений отсутствует в веб-клиенте',
        required => [
            ['store client', 'marketplace', 'application store', 'store server', 'store.xml'],
        ],
        bonus => ['store plugin', 'store client'],
        exclude => ['data store', 'nosql store', 'event store', 'storage'],
        notes => 'Проблема доступности плагина Store Client / магазина приложений.',
    },
    {
        id => 11,
        title => 'Вёрстка страницы 404',
        required => [
            ['404'],
            ['page not found', 'not found page', 'not found error'],
        ],
        bonus => ['html', 'layout', 'logo'],
        exclude => ['workflow', 'rest api', 'web service'],
        notes => 'Визуальная проблема страницы 404 (DKC logo). Специфика RatioT.',
    },
    {
        id => 12,
        title => 'В дистрибутиве остался логотип и брендинг AggreGate',
        required => [
            ['rebrand', 'branding', 'oem installer', 'original platform name'],
        ],
        bonus => ['logo', 'aggregate', 'oem'],
        exclude => ['aggregate.digital'],
        notes => 'Проблема брендинга. Специфика RatioT.',
    },
    {
        id => 13,
        title => 'Раздел «Драйвера и расширения» открывает корень системного дерева',
        required => [
            ['pluginsglobalconf', 'drivers and extensions'],
        ],
        bonus => ['plugin container', 'system tree', 'root tree', 'plugins subsystem'],
        exclude => [],
        notes => 'Проблема навигации в системном дереве к плагинам/драйверам.',
    },
    {
        id => 14,
        title => 'Несуществующие страницы /web/* возвращают JSON вместо HTML 404',
        required => [
            ['404', 'not found'],
            ['json', 'rest api', 'web server', 'spa', 'ssr', 'crawler'],
        ],
        bonus => ['html', 'error page', 'status code'],
        exclude => ['workflow'],
        notes => 'Проблема обработки 404 для SPA-путей (/web/*).',
    },
    {
        id => 15,
        title => 'Ссылки на справку из веб-клиента ведут на маркетинговый сайт',
        required => [
            ['help link', 'documentation link', 'context help', 'help text', 'help icon'],
        ],
        bonus => ['documentation', 'help', 'buff-lab'],
        exclude => [],
        notes => 'Проблема ссылок справки из веб-клиента. Специфика RatioT (buff-lab.ru).',
    },
    {
        id => 16,
        title => 'Вкладки «Информации о сервере» обрезаются и не переносятся',
        required => [
            ['server information', 'server info', 'information about server'],
            ['tab', 'tabs', 'overflow', 'clip', 'wrap'],
        ],
        bonus => ['tab bar', 'tabs'],
        exclude => [],
        notes => 'UI-проблема вкладок информации о сервере.',
    },
    {
        id => 17,
        title => 'Раздел «Пользователи» открывает корень системного дерева',
        required => [
            ['users container', 'user list', 'users tree'],
        ],
        bonus => ['users', 'user', 'tree', 'container'],
        exclude => ['user permissions', 'user observer', 'authorized user', 'user password'],
        notes => 'Проблема навигации к списку пользователей.',
    },
);

my @results;
for my $case (@cases) {
    my @matches;
    for my $r (@records) {
        my $score = score_match($r->{text}, $case->{required}, $case->{bonus}, $case->{exclude});
        next unless $score > 0;

        my $confidence;
        if ($score >= 30) {
            $confidence = 'Высокая';
        } elsif ($score >= 15) {
            $confidence = 'Средняя';
        } else {
            $confidence = 'Низкая';
        }

        push @matches, {
            version    => $r->{version},
            type       => $r->{type},
            code       => $r->{code},
            text       => $r->{text_orig},
            confidence => $confidence,
            score      => $score,
        };
    }

    @matches = sort { $b->{score} <=> $a->{score} || $b->{version} cmp $a->{version} } @matches;
    @matches = @matches[0..9] if @matches > 10;

    push @results, {
        case    => $case,
        matches => \@matches,
    };
}

open my $out, '>:encoding(UTF-8)', $out_file or die "Cannot write $out_file: $!";

print $out "# Сравнение changelog AggreGate с баг-кейсами RatioT SCADA\n\n";
print $out "**Версия RatioT в кейсах:** 6.41.09-2456  \n";
print $out "**Источник changelog:** https://aggregate.digital/ru/changelog.html  \n";
print $out "**Дата анализа:** " . localtime() . "  \n\n";
print $out "> **Важно:** changelog относится к базовой платформе AggreGate. Часть багов RatioT (брендинг, навигация, ссылки на `buff-lab.ru`, страница 404 DKC) являются кастомизациями и в базовом changelog могут отсутствовать. Совпадения по ним могут быть косвенными.\n\n";

print $out "## Сводная таблица\n\n";
print $out "| Кейс | Название | Найдено совпадений | Лучшая уверенность | Версия исправления |\n";
print $out "|---:|---|---:|---|---|\n";
for my $res (@results) {
    my $c = $res->{case};
    my @m = @{$res->{matches}};
    my $count = scalar @m;
    my ($best_conf, $best_ver) = ('Нет', '-');
    if (@m) {
        $best_conf = $m[0]->{confidence};
        $best_ver  = $m[0]->{version};
    }
    print $out "| $c->{id} | $c->{title} | $count | $best_conf | $best_ver |\n";
}

print $out "\n---\n\n";

for my $res (@results) {
    my $c = $res->{case};
    my @m = @{$res->{matches}};

    print $out "## Кейс $c->{id}. $c->{title}\n\n";
    print $out "$c->{notes}\n\n";

    if (@m) {
        print $out "### Возможные соответствия в changelog\n\n";
        print $out "| Уверенность | Версия | Тип | Код | Описание |\n";
        print $out "|---|---|---|---|---|\n";
        for my $m (@m) {
            my $desc = $m->{text};
            $desc =~ s/\|/\\|/g;
            print $out "| $m->{confidence} | $m->{version} | $m->{type} | $m->{code} | $desc |\n";
        }
    } else {
        print $out "**Прямых совпадений в changelog не найдено.**\n\n";
        print $out "Возможные причины:\n";
        print $out "- Проблема специфична для сборки RatioT и не отражена в базовом changelog AggreGate.\n";
        print $out "- Описание в changelog сформулировано иначе, чем в кейсе.\n";
        print $out "- Исправление ещё не выпущено или не попало в опубликованный changelog.\n";
    }
    print $out "\n";
}

print $out "## Рекомендации по проверке\n\n";
print $out "1. **С наибольшей вероятностью исправлены в базовой платформе:**\n";
print $out "   - **Кейс 5** (eventLog колонки): найдено несколько пунктов про колонки Event Log в 6.40.06. Возможно, часть проблемы уже исправлена.\n";
print $out "   - **Кейс 7** (NoSQL-хранилище): AGG-20199 в 6.41.05 напрямую про NoSQL embedded storage on Windows — потенциально связано с падением сервера.\n";
print $out "2. **Возможны косвенные совпадения (требуют ручной проверки):**\n";
print $out "   - **Кейс 1** (ошибки создания ресурсов): AGG-20303 про ошибку создания контекста.\n";
print $out "   - **Кейс 4** (Modbus CSV/XML): в changelog нет Modbus; найдены общие проблемы с кодировкой кириллицы (AGG-20539).\n";
print $out "   - **Кейс 8** (HTML-сниппет): AGG-19839 про HTML snippet component.\n";
print $out "   - **Кейс 12** (брендинг): AGG-19101 про OEM-инсталляторы.\n";
print $out "   - **Кейс 14** (404 JSON): AGG-19298 про 404 при SSR.\n";
print $out "   - **Кейс 15** (ссылки справки): AGG-20208 про help text в Expression Builder.\n";
print $out "3. **Нет совпадений в базовом changelog (скорее всего, специфика RatioT):**\n";
print $out "   - Кейсы 2, 3, 6, 9, 10, 11, 13, 16, 17 — брендинг, лицензирование, навигация, инсталлятор, локализация.\n";

close $out;
print "Report written to $out_file\n";
