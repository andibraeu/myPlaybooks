# Caddy Setup Role for Mirrorbits

Diese Ansible-Rolle richtet Caddy als Webserver ein, um zwei Hauptfunktionen zu erfüllen:

1. Reverse Proxy für Mirrorbits auf der Domain `cdn.media.freifunk.net`
2. Direktes Bereitstellen von Dateien aus dem Repository-Verzeichnis auf der Domain `cdn-m1.media.freifunk.net`

## Features

- Installiert Caddy aus dem offiziellen Repository
- Konfiguriert Caddy als Reverse Proxy für Mirrorbits
- Stellt Dateien direkt aus dem Repository-Verzeichnis bereit
- Konfiguriert geeignete Sicherheitsheader

## Anforderungen

- Debian-basiertes System
- Mirrorbits läuft auf demselben Server (Standard: localhost:8080)
- Repository-Verzeichnis mit den bereitzustellenden Dateien (Standard: /var/lib/mirrorbits/repos)

## Rollen-Variablen

```yaml
# Caddy-Installation und Konfiguration
caddy_apt_key_url: "https://dl.cloudsmith.io/public/caddy/stable/gpg.key"
caddy_apt_repository: "deb [signed-by=/usr/share/keyrings/caddy-stable-archive-keyring.gpg] https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main"
caddy_keyring_path: "/usr/share/keyrings/caddy-stable-archive-keyring.gpg"

# Domain-Konfiguration
caddy_proxy_domain: "cdn.media.freifunk.net"  # Domain für Mirrorbits-Proxy
caddy_files_domain: "cdn-m1.media.freifunk.net"  # Domain für direkte Dateiauslieferung
caddy_admin_email: "admin@example.org"  # Für Let's Encrypt-Zertifikate

# Mirrorbits-Proxy-Konfiguration
mirrorbits_backend: "localhost:8080"

# Repository-Konfiguration
caddy_repository_path: "/var/lib/mirrorbits/repos"
```

## Verwendung

Füge diese Rolle in dein Playbook ein:

```yaml
- hosts: mirrors
  roles:
    - setup_caddy
```

## Anpassen der Konfiguration

Du kannst die Domains, E-Mail und Pfade anpassen, indem du die Variablen in deinem Playbook setzt:

```yaml
- hosts: mirrors
  vars:
    caddy_proxy_domain: "deine-mirror-domain.example.com"
    caddy_files_domain: "datei-mirror.example.com"
    caddy_admin_email: "deine-email@example.com"
    caddy_repository_path: "/pfad/zu/deinem/repository"
    mirrorbits_backend: "localhost:8081"  # Falls Mirrorbits auf einem anderen Port läuft
  roles:
    - setup_caddy
```

## Funktionsweise

1. Caddy leitet alle Anfragen an `caddy_proxy_domain` an Mirrorbits weiter
2. Anfragen an `caddy_files_domain` werden direkt aus dem Repository-Verzeichnis bedient
3. Sicherheitsheader werden allen Antworten hinzugefügt

## Hinweise

- Die Konfiguration beinhaltet automatisches HTTPS mit Let's Encrypt
- Logs werden in /var/log/caddy/ gespeichert
- Jede Domain hat ihre eigene Logdatei 