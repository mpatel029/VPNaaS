#!/usr/bin/env bash

set -x

vpn="vpn1"
client="client1"

docker container rm --force ${vpn} ${client}
sudo ip netns del ${vpn} ${client}
