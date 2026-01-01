# configure_nfs_server

Diese Rolle konfiguriert einen NFS-Server auf Ubuntu/Debian-Systemen.

## Verwendung

### In einem Playbook

```yaml
- hosts: nas
  roles:
    - configure_nfs_server
  vars:
    nfs_export_path: /mnt/k8s-storage
    nfs_allowed_networks: 10.0.0.0/8
    nfs_domain: local
```

### Variablen

- `nfs_export_path` (default: `/mnt/k8s-storage`): Pfad, der über NFS exportiert werden soll
- `nfs_allowed_networks` (default: `10.0.0.0/8`): Erlaubte Netzwerke in CIDR-Notation
- `nfs_domain` (default: `local`): NFSv4 Domain

## Voraussetzungen

- Ubuntu/Debian-System
- Root-Zugriff
- Der Export-Pfad sollte existieren oder wird erstellt

## Was wird konfiguriert?

- Installation von `nfs-kernel-server` und `nfs-common`
- Konfiguration von `/etc/exports`
- Aktivierung von NFSv4
- Start und Aktivierung des NFS-Services


