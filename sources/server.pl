#!/usr/bin/perl
use strict;
use warnings;
use IO::Socket::IP;
use IO::Select;
use File::Spec;

my $port = 8765;
my $root = File::Spec->rel2abs(File::Spec->curdir());

print "Serving $root on http://localhost:$port\n";
print "Open: http://localhost:$port/site/\n";

my %types = (
    html => 'text/html; charset=utf-8',
    css  => 'text/css',
    js   => 'application/javascript',
    json => 'application/json',
    pdf  => 'application/pdf',
    txt  => 'text/plain; charset=utf-8',
    png  => 'image/png',
    jpg  => 'image/jpeg',
    jpeg => 'image/jpeg',
    gif  => 'image/gif',
    svg  => 'image/svg+xml',
    ico  => 'image/x-icon',
);

# Создаём два сокета: IPv4 и IPv6, чтобы localhost работал в любом браузере
my @sockets;
for my $family (qw(AF_INET AF_INET6)) {
    my $local_host = $family eq 'AF_INET' ? '127.0.0.1' : '::1';
    my %opts = (
        LocalHost => $local_host,
        LocalPort => $port,
        Proto     => 'tcp',
        Listen    => 5,
        ReuseAddr => 1,
    );
    if ($family eq 'AF_INET6') {
        $opts{V6Only} = 0;  # принимаем также IPv4 на Windows, если ОС позволяет
    }
    my $sock = IO::Socket::IP->new(%opts);
    if ($sock) {
        push @sockets, $sock;
        print "Listening on [$local_host]:$port\n";
    } else {
        warn "Cannot listen on $local_host:$port: $@\n";
    }
}

die "Cannot start server on port $port\n" unless @sockets;

my $select = IO::Select->new(@sockets);

while (my @ready = $select->can_read()) {
    for my $listener (@ready) {
        my $client = $listener->accept();
        next unless $client;
        handle_client($client);
    }
}

sub handle_client {
    my ($client) = @_;
    $client->autoflush(1);
    my $request = <$client>;
    return unless defined $request;

    my ($method, $raw_path) = $request =~ /^(\S+)\s+(\S+)\s+HTTP/i;
    $method ||= 'GET';
    $raw_path ||= '/';

    # Drain headers
    while (<$client>) { last if /^\r?\n$/; }

    if (uc($method) ne 'GET') {
        send_response($client, 405, 'Method Not Allowed', 'text/plain', '405 Method Not Allowed');
        close $client;
        return;
    }

    my $path = $raw_path;
    $path =~ s/\?.*$//;
    $path =~ s/%([0-9A-Fa-f]{2})/chr(hex($1))/ge;
    $path = '/site/index.html' if $path eq '/';

    my $full = File::Spec->rel2abs(File::Spec->catdir($root, $path));
    my $check = File::Spec->rel2abs($root);
    if (index($full, $check) != 0) {
        send_response($client, 403, 'Forbidden', 'text/plain', '403 Forbidden');
        close $client;
        return;
    }

    if (-d $full) {
        my $index = File::Spec->catfile($full, 'index.html');
        if (-f $index) { $full = $index; }
        else {
            send_response($client, 403, 'Forbidden', 'text/plain', 'Directory listing disabled');
            close $client;
            return;
        }
    }

    unless (-f $full) {
        send_response($client, 404, 'Not Found', 'text/plain', '404 Not Found');
        close $client;
        return;
    }

    open my $fh, '<:raw', $full or do {
        send_response($client, 500, 'Internal Server Error', 'text/plain', '500 Internal Server Error');
        close $client;
        return;
    };
    my $size = -s $fh;
    my $ext = '';
    if ($full =~ /\.([^.]+)$/) { $ext = lc($1); }
    my $type = $types{$ext} || 'application/octet-stream';

    print $client "HTTP/1.1 200 OK\r\n";
    print $client "Content-Type: $type\r\n";
    print $client "Content-Length: $size\r\n";
    print $client "Connection: close\r\n\r\n";

    my $buf;
    while (read($fh, $buf, 8192)) { print $client $buf; }
    close $fh;
    close $client;
}

sub send_response {
    my ($client, $code, $text, $type, $body) = @_;
    print $client "HTTP/1.1 $code $text\r\n";
    print $client "Content-Type: $type\r\n";
    print $client "Content-Length: " . length($body) . "\r\n";
    print $client "Connection: close\r\n\r\n";
    print $client $body;
}
