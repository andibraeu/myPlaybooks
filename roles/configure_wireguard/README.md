# configure_wireguard

Ansible role to configure WireGuard tunnels.

## Usage

This role installs and configures WireGuard for secure point-to-point connections,
e.g., for NFS traffic between NAS and Kubernetes nodes.

## Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `wireguard_address` | IP address with CIDR | `"10.200.0.1/24"` |
| `wireguard_private_key` | Private key (via vault!) | `"ABC123..."` |
| `wireguard_peers` | List of peers | see below |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `wireguard_interface` | `wg0` | Interface name |
| `wireguard_listen_port` | `51820` | Port (leave empty for clients) |
| `wireguard_enable_ip_forward` | `false` | Enable IP forwarding |
| `wireguard_postup` | - | PostUp command |
| `wireguard_postdown` | - | PostDown command |

## Example: NAS (Server)

```yaml
# host_vars/nas/vars.yaml
wireguard_address: "10.200.0.1/24"
wireguard_listen_port: 51820
wireguard_peers:
  - name: k3s-node1
    public_key: "{{ vault_wg_node1_pubkey }}"
    allowed_ips: "10.200.0.11/32"
  - name: k3s-node2
    public_key: "{{ vault_wg_node2_pubkey }}"
    allowed_ips: "10.200.0.12/32"
  - name: k3s-node3
    public_key: "{{ vault_wg_node3_pubkey }}"
    allowed_ips: "10.200.0.13/32"

# host_vars/nas/vault.yaml (encrypted with ansible-vault)
wireguard_private_key: "NAS_PRIVATE_KEY_HERE"
vault_wg_node1_pubkey: "NODE1_PUBLIC_KEY"
vault_wg_node2_pubkey: "NODE2_PUBLIC_KEY"
vault_wg_node3_pubkey: "NODE3_PUBLIC_KEY"
```

## Example: K3s Node (Client)

```yaml
# host_vars/k3s-node1/vars.yaml
wireguard_address: "10.200.0.11/24"
wireguard_listen_port: ""  # No listen port for clients
wireguard_peers:
  - name: nas
    public_key: "{{ vault_wg_nas_pubkey }}"
    allowed_ips: "10.200.0.1/32"
    endpoint: "192.168.1.100:51820"
    persistent_keepalive: 25

# host_vars/k3s-node1/vault.yaml
wireguard_private_key: "NODE1_PRIVATE_KEY_HERE"
vault_wg_nas_pubkey: "NAS_PUBLIC_KEY"
```

## Generating Keys

```bash
# Generate private key
wg genkey > private.key

# Derive public key
cat private.key | wg pubkey > public.key
```

## Switching to a Different Interface Later

To move the WireGuard endpoint to a different interface (e.g., eth1),
simply change the `endpoint` variable in the K3s node host_vars and
re-run the playbook.
