# DNS Setup

Following https://docs.fedoraproject.org/en-US/fedora-server/administration/dnsmasq/#_basic_configuration

## Installation

    # apt install dnsmasq

## Configuration

1. Activation config for the dnsmasq NetworkManager plugin:

```
# /etc/NetworkManager/conf.d/00-use-dnsmasq.conf #
# This enabled the dnsmasq plugin.
[main]
dns=dnsmasq
```

2. Configuration of the name resolution

```
# /etc/NetworkManager/dnsmasq.d/01-DNS-example-lan.conf
# This file sets up DNS for the private local net domain example.lan
local=/example.lan/
# file where to find the list of IP - hostname mapping
addn-hosts=/etc/dnsmasq.hosts
domain-needed
bogus-priv
# Automatically add <domain> to simple names in a hosts-file.
expand-hosts
# interfaces to listen on
interface=lo
interface=enp2s0
# in case of a bridge don't use the attached server virtual ethernet interface
# The below defines a Wildcard DNS Entry.
#address=/.localnet/10.10.10.zzz
# Upstream public net DNS server (max.three)
no-poll
server=8.8.8.8
```

Note: I decided to use `8.8.8.8` as a public net DNS server, not sure if it does anything.

3. Add test file `/etc/dnsmasq.hosts`
```
127.0.0.1 test-dns
```

4. Restart `NetworkManager`

```
# systemctl restart NetworkManager
```

Current error:

    vmadm@lnVM15:~$ ping test-dns
    ping: test-dns: Name or service not known
