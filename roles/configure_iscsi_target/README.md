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

## CHAP-Authentifizierung

### Automatische Konfiguration (deaktiviert)

Die automatische CHAP-Konfiguration im Playbook ist aktuell **deaktiviert**, da die direkte Manipulation von `saveconfig.json` über Ansible problematisch sein kann. 

**Status:** Die Tasks `Set CHAP credentials in saveconfig.json` und `Restore iSCSI configuration` sind mit `- false` deaktiviert (siehe `tasks/main.yaml` Zeilen 100 und 113).

### Manuelle Konfiguration

#### Schritt 1: TPG-Attribute setzen (via Ansible)

Das Playbook setzt automatisch die notwendigen TPG-Attribute:
- `authentication=1` - Aktiviert CHAP-Authentifizierung
- `generate_node_acls=1` - Erlaubt automatische ACL-Generierung
- `cache_dynamic_acls=1` - Cached dynamisch generierte ACLs
- `demo_mode_write_protect=0` - Erlaubt Schreibzugriff

Diese werden automatisch gesetzt, wenn `iscsi_chap_username` und `iscsi_chap_password` definiert sind.

#### Schritt 2: CHAP-Credentials manuell setzen

**Option A: Mit dem bereitgestellten Python-Script (empfohlen)**

```bash
# Script auf das NAS kopieren
scp roles/configure_iscsi_target/scripts/set_chap_credentials.py nas:/tmp/

# Auf dem NAS ausführen
sudo python3 /tmp/set_chap_credentials.py \
  iqn.2026-01.local.s54:k3s-iscsi \
  k3s \
  "yP9cVmRevmZYLXQjRBNiVPam4gOwkGSh"
```

Das Script:
- Erstellt automatisch ein Backup von `saveconfig.json`
- Setzt die CHAP-Credentials
- Zeigt die nächsten Schritte an

**Option B: Manuell mit Python**

```bash
sudo python3 << 'PYEOF'
import json
config_file = '/etc/rtslib-fb-target/saveconfig.json'
target_iqn = 'iqn.2026-01.local.s54:k3s-iscsi'
new_password = 'yP9cVmRevmZYLXQjRBNiVPam4gOwkGSh'
new_userid = 'k3s'

# Backup erstellen
import shutil
from datetime import datetime
backup_file = f'{config_file}.backup.{datetime.now().strftime("%Y%m%d-%H%M%S")}'
shutil.copy2(config_file, backup_file)
print(f"Backup erstellt: {backup_file}")

# Config laden
with open(config_file, 'r') as f:
    config = json.load(f)

# CHAP-Credentials setzen
found = False
for target in config.get('targets', []):
    if target.get('wwn') == target_iqn:
        for tpg in target.get('tpgs', []):
            if isinstance(tpg, dict) and tpg.get('tag') == 1:
                tpg['chap_userid'] = new_userid
                tpg['chap_password'] = new_password
                found = True
                print(f"CHAP-Auth gesetzt für {target_iqn}/tpg1")
                break
        break

if not found:
    print(f"FEHLER: Target {target_iqn} nicht gefunden!")
    exit(1)

# Config speichern
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)
print("Config gespeichert.")
PYEOF
```

**Option C: Direkt mit einem Editor (nur für Experten)**

```bash
# Backup erstellen
sudo cp /etc/rtslib-fb-target/saveconfig.json /etc/rtslib-fb-target/saveconfig.json.backup.$(date +%Y%m%d-%H%M%S)

# Config bearbeiten
sudo nano /etc/rtslib-fb-target/saveconfig.json
# Suche nach dem Target und setze in tpg1:
#   "chap_userid": "k3s",
#   "chap_password": "yP9cVmRevmZYLXQjRBNiVPam4gOwkGSh"
```

#### Schritt 3: Config neu laden

Nach dem Setzen der CHAP-Credentials muss die Config neu geladen werden:

```bash
# Option 1: Via targetcli (empfohlen, wenn keine aktiven Sessions)
sudo targetcli restoreconfig

# Option 2: Service neu starten (unterbricht aktive Sessions)
sudo systemctl restart target
```

**WICHTIG:** `targetcli restoreconfig` kann aktive iSCSI-Sessions unterbrechen. Bei laufenden Kubernetes-Pods sollte `systemctl restart target` verwendet werden.

#### Schritt 4: Verifikation

```bash
# Prüfe ob CHAP-Credentials gesetzt sind
sudo cat /etc/rtslib-fb-target/saveconfig.json | python3 -m json.tool | \
  grep -A 30 '"wwn": "iqn.2026-01.local.s54:k3s-iscsi"' | \
  grep -E '(chap_userid|chap_password|authentication)'

# Prüfe Target-Status
sudo targetcli ls /iscsi/iqn.2026-01.local.s54:k3s-iscsi/tpg1

# Erwartete Ausgabe sollte zeigen:
# o- tpg1 ........................................................ [gen-acls, tpg-auth, 1-way auth]
```

### Troubleshooting

**Problem: Script findet Target nicht**
- Prüfe ob das Target existiert: `sudo targetcli ls /iscsi/`
- Prüfe den exakten IQN: `sudo cat /etc/rtslib-fb-target/saveconfig.json | python3 -m json.tool | grep wwn`

**Problem: CHAP-Auth funktioniert nicht**
- Stelle sicher, dass `authentication=1` im TPG gesetzt ist
- Prüfe ob `chap_userid` und `chap_password` in `saveconfig.json` vorhanden sind
- Prüfe ob die Config neu geladen wurde (`targetcli restoreconfig` oder Service-Restart)
- Prüfe die Logs: `sudo journalctl -u target -n 50`

**Problem: Config wird überschrieben**
- Stelle sicher, dass `targetcli saveconfig` nach manuellen Änderungen ausgeführt wird
- Oder verwende das Python-Script, das automatisch speichert

### Warum ist die automatische Konfiguration deaktiviert?

1. **Sicherheit:** Direkte Manipulation von `saveconfig.json` kann die Config beschädigen
2. **Kontrolle:** Manuelle Konfiguration gibt mehr Kontrolle über den Prozess
3. **Backup:** Das manuelle Script erstellt automatisch Backups
4. **Fehlerbehandlung:** Bessere Fehlerbehandlung und Validierung möglich

Die automatische Konfiguration kann reaktiviert werden, indem die `- false` Bedingungen in `tasks/main.yaml` entfernt werden (Zeilen 100 und 113).


