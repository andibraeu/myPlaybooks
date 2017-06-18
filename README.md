A collection of my ansible playbooks
=======

Basic setup
-------

* installs sudo
* adds a new admin user
* installs zsh as default shell

call via

```
ansible-playbook basic_setup.yaml -i 77.87.49.9, -u $INITIALUSERNAME -k -K --extra-vars="user=$USERNAME password=$CREATED WITH mkpasswd --method=sha-512"
```
