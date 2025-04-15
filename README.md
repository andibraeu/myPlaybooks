A collection of my ansible playbooks
=======

## Installing Requirements

Before you can run the playbooks, you need to install the required Ansible roles and collections:

```
ansible-galaxy install -r requirements.yaml
```

This command installs all needed dependencies:
- Collections: rvm_io.ruby, community.general, ansible.posix, community.postgresql
- Roles: jnv.debian-backports

## Basic setup
-------

* installs sudo
* adds a new admin user
* installs zsh as default shell

call via

```
ansible-playbook basic_setup.yaml -i $HOST_OR_IP, -u $INITIALUSERNAME -k -K --extra-vars="user=$USERNAME password=$CREATED WITH mkpasswd --method=sha-512"
```
