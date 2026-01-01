# configure_zfs_datasets

Diese Rolle verwaltet ZFS-Datasets nach der Pool-Erstellung.

## Verwendung

### In einem Playbook oder host_vars

**host_vars/s54-k3s-nas/vars.yaml:**
```yaml
zfs_pool_name: tank
zfs_datasets:
  - name: k8s-unencrypted
  - name: k8s-encrypted
    encryption: true
    encryption_algorithm: aes-256-gcm
    encryption_keyformat: hex  # Default ist 'hex', alternativ 'raw' oder 'passphrase'
zfs_dataset_properties:
  - dataset: k8s-encrypted
    property: quota
    value: 2T
  - dataset: k8s-unencrypted
    property: quota
    value: 1T
```

**host_vars/s54-k3s-nas/vault.yaml:**
```yaml
# Verschlüsselungsschlüssel für k8s-encrypted Dataset
# Für hex-Format: 64 Zeichen (32 Bytes)
# Generieren mit: openssl rand -hex 32
zfs_datasets_encryption_keys:
  k8s-encrypted: "dein-64-zeichen-langer-hex-schluessel-hier"
```

**Oder direkt in zfs_datasets:**
```yaml
zfs_datasets:
  - name: k8s-encrypted
    encryption: true
    encryption_key: "{{ zfs_datasets_encryption_keys.k8s-encrypted }}"
```

### Variablen

- `zfs_pool_name` (default: `tank`): Name des ZFS-Pools
- `zfs_datasets`: Liste von Datasets, die erstellt werden sollen
- `zfs_dataset_properties`: Liste von Eigenschaften, die auf Datasets gesetzt werden sollen

## Voraussetzungen

- Ubuntu/Debian-System mit ZFS
- **ZFS-Utilities müssen installiert sein** (`zfsutils-linux`, `zfs-zed`)
  - Werden automatisch von `setup_nas.yaml` installiert
  - Oder manuell: `apt install zfsutils-linux zfs-zed`
- ZFS-Pool muss bereits existieren (wird manuell erstellt)
- Root-Zugriff

## Was wird konfiguriert?

- Erstellung von ZFS-Datasets (verschlüsselt und unverschlüsselt)
- Setzen von Dataset-Eigenschaften (Quotas, Compression, etc.)

## Verschlüsselte Datasets

Für verschlüsselte Datasets wird ein **Keyfile** verwendet:
- Keyfile wird in `/etc/zfs/keys/` gespeichert (nur root lesbar)
- Der Schlüssel sollte in `vault.yaml` gespeichert werden
- Empfohlen: 32 Zeichen langer zufälliger String

**Schlüssel generieren:**
```bash
# Für hex-Format (empfohlen, 64 Zeichen):
openssl rand -hex 32

# Für raw-Format (32 Bytes, muss genau 32 Bytes sein):
openssl rand 32
```

## Hinweis

**WICHTIG:** Der ZFS-Pool muss manuell erstellt werden, bevor diese Rolle ausgeführt wird. Diese Rolle verwaltet nur Datasets innerhalb eines bestehenden Pools.


