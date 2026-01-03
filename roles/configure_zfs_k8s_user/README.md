# configure_zfs_k8s_user

Diese Rolle erstellt einen dedizierten Benutzer für Democratic-CSI mit eingeschränkten sudo-Rechten für ZFS-Operationen und deaktiviert Root-Login per SSH.

## Was macht diese Rolle?

1. **Erstellt einen dedizierten Benutzer** (Standard: `zfs-k8s`)
2. **Richtet sudo-Regeln ein** - nur für ZFS/ZPool-Befehle, passwortlos
3. **Deaktiviert Root-Login per SSH** (konfigurierbar)
4. **Bereitet SSH-Verzeichnis vor** für den Benutzer

## Variablen

### Defaults (in `defaults/main.yml`):

```yaml
zfs_k8s_user: zfs-k8s
zfs_k8s_user_comment: "User for Democratic-CSI ZFS operations"
zfs_k8s_user_shell: /bin/bash
disable_root_ssh: true
```

### Überschreiben in `host_vars`:

```yaml
# host_vars/s54-k3s-nas/vars.yaml
zfs_k8s_user: zfs-k8s  # Optional: anderer Benutzername
disable_root_ssh: true  # Optional: Root-Login deaktivieren (Standard: true)
```

## Sudo-Konfiguration

Die Rolle erstellt `/etc/sudoers.d/zfs-k8s` mit folgendem Inhalt:

```
zfs-k8s ALL=(ALL) NOPASSWD: /usr/sbin/zfs, /usr/sbin/zpool, /usr/bin/zfs, /usr/bin/zpool
```

Dies ermöglicht dem Benutzer, nur ZFS- und ZPool-Befehle ohne Passwort auszuführen.

## Verwendung

Die Rolle wird automatisch vom `setup_nas.yaml` Playbook ausgeführt.

Nach der Ausführung:

1. SSH-Key für den Benutzer erstellen:
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/nas-democratic-csi -N ""
   ```

2. Öffentlichen Key auf NAS kopieren:
   ```bash
   ssh-copy-id -i ~/.ssh/nas-democratic-csi.pub zfs-k8s@<nas-ip>
   ```

3. Testen:
   ```bash
   ssh -i ~/.ssh/nas-democratic-csi zfs-k8s@<nas-ip>
   sudo zfs list  # Sollte funktionieren
   ```

## Democratic-CSI Konfiguration

In den HelmRelease-Dateien muss konfiguriert werden:

```yaml
driverConfig:
  zfs-generic-iscsi:
    zfsHostUser: "zfs-k8s"  # Statt root
    sudoEnabled: true  # Sudo aktivieren
    # ... rest der Konfiguration
```

## Sicherheit

- ✅ Root-Login per SSH ist deaktiviert
- ✅ Benutzer hat nur sudo-Rechte für ZFS-Befehle
- ✅ Keine vollständigen sudo-Rechte (nur `/usr/sbin/zfs`, `/usr/sbin/zpool`)
- ✅ Passwortloser sudo nur für ZFS-Befehle

