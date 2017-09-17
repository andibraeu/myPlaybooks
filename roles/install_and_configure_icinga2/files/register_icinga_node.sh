#!/bin/bash

# This generates and signs your required certificates. Please do not
# forget to install the Icinga 2 package and your desired monitoring
# plugins first:

ICINGA_PKI_DIR=/etc/icinga2/pki
ICINGA_USER=nagios
chown $ICINGA_USER $ICINGA_PKI_DIR

icinga2 pki new-cert --cn {{ inventory_hostname }} \
--key $ICINGA_PKI_DIR/{{ inventory_hostname }}.key \
--cert $ICINGA_PKI_DIR/{{ inventory_hostname }}.crt

icinga2 pki save-cert --key $ICINGA_PKI_DIR/{{ inventory_hostname }}.key \
--trustedcert $ICINGA_PKI_DIR/trusted-master.crt \
--host home.andi95.de

icinga2 pki request --host home.andi95.de \
--port 5665 \
--ticket {{ icinga2_ticket_number }} \
--key $ICINGA_PKI_DIR/{{ inventory_hostname }}.key \
--cert $ICINGA_PKI_DIR/{{ inventory_hostname }}.crt \
--trustedcert $ICINGA_PKI_DIR/trusted-master.crt \
--ca $ICINGA_PKI_DIR/ca.crt
