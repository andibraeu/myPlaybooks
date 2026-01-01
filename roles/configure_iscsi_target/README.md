# configure_iscsi_target

Diese Rolle konfiguriert einen iSCSI Target Server auf Ubuntu/Debian-Systemen.

## Verwendung

### In einem Playbook

```yaml
- hosts: nas
  roles:
    - configure_iscsi_target
  vars:
    iscsi_target_iqn: iqn.2024-01.local.nas:k8s-iscsi
    iscsi_portal_ip: 0.0.0.0
    iscsi_initiator_iqn: iqn.2024-01.local.k3s:*
    iscsi_chap_username: k8s
    iscsi_chap_password: "secure-password"
    iscsi_backstore_name: k8s-pool
    iscsi_backstore_device: /dev/zvol/tank/k8s
```

### Variablen

- `iscsi_target_iqn` (default: `iqn.2024-01.local.nas:k8s-iscsi`): IQN des iSCSI Targets
- `iscsi_portal_ip` (default: `0.0.0.0`): IP-Adresse, auf der der Target lauscht
- `iscsi_initiator_iqn` (default: `iqn.2024-01.local.k3s:*`): IQN der erlaubten Initiators (Wildcard für Kubernetes)
- `iscsi_chap_username`: CHAP-Benutzername (optional, aber empfohlen)
- `iscsi_chap_password`: CHAP-Passwort (optional, aber empfohlen)
- `iscsi_backstore_name`: Name des Backstores
- `iscsi_backstore_device`: Pfad zum Block-Device (z.B. ZFS-Zvol)

## Voraussetzungen

- Ubuntu/Debian-System
- Root-Zugriff
- ZFS-Pool und Zvol sollten bereits erstellt sein (wenn verwendet)

## Was wird konfiguriert?

- Installation von `targetcli-fb` und zugehörigen Paketen
- Erstellung eines iSCSI Targets
- Konfiguration von CHAP-Authentifizierung (optional)
- Start und Aktivierung des iSCSI Target Services

## Sicherheit

**WICHTIG:** Setze `iscsi_chap_username` und `iscsi_chap_password` in `host_vars` oder `group_vars`, nicht direkt im Playbook!


