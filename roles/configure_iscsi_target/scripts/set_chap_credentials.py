#!/usr/bin/env python3
"""
Manuelles Script zum Setzen von CHAP-Credentials in saveconfig.json

Dieses Script sollte verwendet werden, wenn die automatische CHAP-Konfiguration
im Ansible-Playbook nicht funktioniert oder wenn manuelle Kontrolle gewünscht ist.

Verwendung:
    sudo python3 set_chap_credentials.py <TARGET_IQN> <CHAP_USERNAME> <CHAP_PASSWORD>

Beispiel:
    sudo python3 set_chap_credentials.py iqn.2026-01.local.s54:k3s-iscsi k3s "yP9cVmRevmZYLXQjRBNiVPam4gOwkGSh"

Nach dem Ausführen:
    1. Backup der saveconfig.json wird automatisch erstellt
    2. CHAP-Credentials werden in saveconfig.json gesetzt
    3. Manuell ausführen: sudo targetcli restoreconfig
    4. Oder Service neu starten: sudo systemctl restart target
"""

import json
import sys
import shutil
from datetime import datetime
from pathlib import Path

CONFIG_FILE = '/etc/rtslib-fb-target/saveconfig.json'
BACKUP_DIR = '/etc/rtslib-fb-target/backups'


def create_backup(config_file):
    """Erstellt ein Backup der saveconfig.json"""
    backup_dir = Path(BACKUP_DIR)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_file = backup_dir / f'saveconfig.json.backup.{timestamp}'
    
    shutil.copy2(config_file, backup_file)
    print(f"✓ Backup erstellt: {backup_file}")
    return backup_file


def set_chap_credentials(target_iqn, username, password):
    """Setzt CHAP-Credentials für das angegebene Target"""
    # Backup erstellen
    create_backup(CONFIG_FILE)
    
    # Config laden
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"FEHLER: {CONFIG_FILE} nicht gefunden!")
        print("Stelle sicher, dass targetcli bereits konfiguriert wurde.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"FEHLER: Ungültiges JSON in {CONFIG_FILE}: {e}")
        sys.exit(1)
    
    # Target finden und CHAP-Credentials setzen
    found = False
    for target in config.get('targets', []):
        if target.get('wwn') == target_iqn:
            for tpg in target.get('tpgs', []):
                if isinstance(tpg, dict) and tpg.get('tag') == 1:
                    old_password = tpg.get('chap_password', '')
                    old_userid = tpg.get('chap_userid', '')
                    
                    tpg['chap_userid'] = username
                    tpg['chap_password'] = password
                    found = True
                    
                    print(f"\n✓ CHAP-Auth gesetzt für {target_iqn}/tpg1")
                    print(f"  Benutzername:")
                    print(f"    Alt: {repr(old_userid)}")
                    print(f"    Neu: {repr(username)}")
                    print(f"  Passwort:")
                    print(f"    Alt: {repr(old_password)} (Länge: {len(old_password)})")
                    print(f"    Neu: {repr(password)} (Länge: {len(password)})")
                    break
            break
    
    if not found:
        print(f"\nFEHLER: Target {target_iqn} nicht gefunden in saveconfig.json!")
        print("\nVerfügbare Targets:")
        for target in config.get('targets', []):
            print(f"  - {target.get('wwn')}")
        sys.exit(1)
    
    # Config speichern
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\n✓ Config gespeichert: {CONFIG_FILE}")
    except Exception as e:
        print(f"\nFEHLER beim Speichern: {e}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("NÄCHSTE SCHRITTE:")
    print("="*70)
    print("1. Prüfe die Config:")
    print(f"   sudo cat {CONFIG_FILE} | python3 -m json.tool | grep -A 30 '\"wwn\": \"{target_iqn}\"' | grep -E '(chap_userid|chap_password|authentication)'")
    print("\n2. Lade die Config neu:")
    print("   sudo targetcli restoreconfig")
    print("   # ODER")
    print("   sudo systemctl restart target")
    print("\n3. Prüfe ob es funktioniert:")
    print(f"   sudo targetcli ls /iscsi/{target_iqn}/tpg1")
    print("="*70)


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    
    target_iqn = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    
    # Validierung
    if not target_iqn.startswith('iqn.'):
        print(f"WARNUNG: {target_iqn} sieht nicht wie ein gültiger IQN aus!")
        response = input("Trotzdem fortfahren? (j/N): ")
        if response.lower() != 'j':
            sys.exit(1)
    
    if len(password) < 12:
        print(f"WARNUNG: Passwort ist sehr kurz ({len(password)} Zeichen)!")
        response = input("Trotzdem fortfahren? (j/N): ")
        if response.lower() != 'j':
            sys.exit(1)
    
    set_chap_credentials(target_iqn, username, password)


if __name__ == '__main__':
    main()

