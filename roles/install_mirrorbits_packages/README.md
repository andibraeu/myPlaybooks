# Mirrorbits Installation Role

This Ansible role installs and configures [Mirrorbits](https://github.com/etix/mirrorbits), a smart download redirector for software distribution.

## Features

- Installs Mirrorbits binary from GitHub releases
- Uses the official HTML templates included in the release package
- Sets up a system user and required directories
- Creates systemd service for automatic startup
- Configures Redis integration
- Installs and configures GeoIP databases
- Supports Redis Sentinel for high availability
- Supports multiple hashing algorithms
- Configurable fallbacks for regional mirrors

## Requirements

- Debian/Ubuntu system
- Redis server
- Internet connection for GeoIP database updates

## Role Variables

```yaml
# Mirrorbits version and installation paths
mirrorbits_version: "v0.6"  # Latest release version
mirrorbits_download_url: "https://github.com/etix/mirrorbits/releases/download/{{ mirrorbits_version }}/mirrorbits-linux-amd64.tar.gz"
mirrorbits_bin_path: "/usr/local/bin/mirrorbits"
mirrorbits_config_dir: "/etc/mirrorbits"

# Mirrorbits configuration options
mirrorbits_listen: "localhost:8080"
mirrorbits_repository_base_path: "/srv/repo"
mirrorbits_cache_dir: "/var/cache/mirrorbits"
mirrorbits_geoip_db_path: "/usr/share/GeoIP"
mirrorbits_output_mode: "auto"
mirrorbits_local_js_path: "https://cdnmaster.media.freifunk.net/mirrorbits/js"
mirrorbits_trace_file_location: "/mirrorbits/trace" 
mirrorbits_rpc_listen_address: "localhost:3390"

# Redis configuration
mirrorbits_redis_host: "127.0.0.1"
mirrorbits_redis_port: "6379"
mirrorbits_redis_password: ""
mirrorbits_redis_db: 0
mirrorbits_redis_use_sentinel: false
mirrorbits_redis_sentinel_master_name: "mirrorbits"
mirrorbits_redis_sentinels: []

# Hashing configuration
mirrorbits_use_multiple_hashes: true  # Use multiple hash algorithms
mirrorbits_hashing_algo: "sha256"  # Used when mirrorbits_use_multiple_hashes is false
mirrorbits_enable_sha256: true
mirrorbits_enable_sha1: true
mirrorbits_enable_md5: true

# Other settings
mirrorbits_enable_trace: true
mirrorbits_enable_logging: false
mirrorbits_weight_distribution_range: 1.5
mirrorbits_disable_on_missing_file: false
mirrorbits_max_link_headers: 10

# Fallbacks configuration
mirrorbits_fallbacks:
  - url: "https://cdnmaster.media.freifunk.net/"
    country_code: "fr"
    continent_code: "eu"

# GeoIP Configuration
geoip_account_id: "0"  # Change if you have a MaxMind account
geoip_license_key: "000000000000"  # Change if you have a MaxMind license
```

## Installation Details

The role performs the following tasks:
1. Enables the contrib repository for GeoIP packages
2. Installs required packages including Redis and GeoIP tools
3. Creates a dedicated system user and directories
4. Downloads the mirrorbits binary from GitHub releases
5. Installs the HTML templates to `/usr/share/mirrorbits/`
6. Configures mirrorbits with Redis connection settings
7. Configures and runs GeoIP database updates
8. Creates and enables a systemd service

## Example Usage

```yaml
- hosts: mirrors
  roles:
    - install_mirrorbits_packages
```

## Redis Sentinel Configuration

To enable Redis Sentinel for high availability:

```yaml
- hosts: mirrors
  vars:
    mirrorbits_redis_use_sentinel: true
    mirrorbits_redis_sentinel_master_name: "mirrorbits"
    mirrorbits_redis_sentinels:
      - "192.168.1.1:26379"
      - "192.168.1.2:26379"
      - "192.168.1.3:26379"
  roles:
    - install_mirrorbits_packages
```

## GeoIP Database

By default, this role uses the free GeoLite2 databases. If you have a MaxMind account and license, you can provide your account ID and license key:

```yaml
- hosts: mirrors
  vars:
    geoip_account_id: "your_account_id"
    geoip_license_key: "your_license_key"
  roles:
    - install_mirrorbits_packages
```

## Post-Installation

After installation, you may want to:

1. Configure your first mirror:
   ```
   mirrorbits add -http https://example.com/pub/ -rsync rsync://example.com/pub/ my-mirror
   ```

2. Enable the mirror:
   ```
   mirrorbits enable my-mirror
   ```

3. Scan the content:
   ```
   mirrorbits scan my-mirror
   ```

## License

This Ansible role is available under the MIT license. 