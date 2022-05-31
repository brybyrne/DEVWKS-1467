#! /usr/bin/env python3

"""

Copyright (c) 2018 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Bryan Byrne <brybyrne@cisco.com>"
__contributors__ = [
    "Hank Preston <hapresto@cisco.com>",
]
__copyright__ = "Copyright (c) 2018 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"



from ncclient import manager, xml_
from jinja2 import Template
import yaml
import time
from argparse import ArgumentParser


# Setup and parse command line arguments for passing in hostname to CSR
parser = ArgumentParser("Setting the Router Hostname")
parser.add_argument(
    "-hn", "--hostname", help="This is the the hostname assigneed to the CSR", required=False, default="Router",
)

# Set up hostname variable to be used in NETCONF template
args = parser.parse_args()
rtr_hostname = args.hostname

# Read in the command_sets.yml file
# with open("provision/command_sets_16_9.yml") as f:
#    commands = yaml.safe_load(f.read())["commands"]
#    initial_config = commands["initial_config"]
#    nat_vpg_config = commands["nat_config"]

# Read in the entire YAML file for use in various templates
print("Reading in Device Device Details")
with open("provision/device_details.yml") as f:
    device_details = yaml.safe_load(f.read())

# Create the NETCONF template for creating interfaces
print("Setting Up NETCONF Templates")
with open("provision/templates/netconf_interface_template.j2") as f:
    interface_template = Template(f.read())

# Create the NETCONF template for configuring hostname
# The 'netconf_configs' directory must exist prior to running the script
with open("provision/templates/netconf_hostname_template.j2") as f:
    hostname_template = Template(f.read())

# Creating various .xml configuraitons
print("Creating Device Configurations")
for device in device_details["devices"]:
    print("Device: {}".format(device["name"]))

    # Creates interface .xml configuration
    print("Creating Interface Configurations from Templates")
    with open("provision/netconf_configs/{}_layer3.cfg".format(device["name"]), "w") as f:
        int_config = interface_template.render(interfaces=device["interfaces"])
        f.write(int_config)

    # Creates hostname .xml configuration
    with open("provision/netconf_configs/{}_hostname.cfg".format(device["name"]), "w") as f:
        hostname_config = hostname_template.render(hostname=rtr_hostname)
        f.write(hostname_config)

# Creating session details to be used by Netmiko. The intention is to reuse 'ch' for calling Netmiko sessions.
for device in device_details["devices"]:
    print("Defining netmiko session details on DEVICE: {}".format(device["name"]))

    with manager.connect(host=device["ip"],
                         username=device["username"],
                         password=device["password"],
                         port=device["netconf_port"],
                         allow_agent=False,
                         look_for_keys=False,
                         hostkey_verify=False) as m:

        # Sending hostname configurations to the router via NETCONF
        print("Sending hostname Configuration with Ncclient")
        hostname_resp = m.edit_config(hostname_config, target='running')

        # Sending interface configurations to the router via NETCONF
        print("Sending Interface Configuration with Ncclient")
        interface_resp = m.edit_config(int_config, target = 'running')

        # Without this sleep timer the remote device kicks back a an RPC error
        print("Pausing 5 seconds for Ncclient")
        time.sleep(5)

        # Send the RPC to save device configuraiton
        save_body = '<cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>'
        save_rpc = m.dispatch(xml_.to_ele(save_body))

        # Confirm Config Save
        print('**************************************************')
        print()
        print(save_rpc)
        print()
        print('**************************************************')








