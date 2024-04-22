#!/usr/bin/env bash

set -x

vpn_subnet="10.0.1"
cli_prov_subnet="176.16.1"
prov_vpc_subnet="100.10.0"

client="client1"
vpn="vpn1"
vpc="tfa1"

# Make VPN container and link namespace to host
docker_id=$(docker run -it -d --cap-add=NET_ADMIN --name ${vpn} ubuntu:23.10 bash)
docker exec -i ${vpn} bash <<EOF
apt-get -qq update
DEBIAN_FRONTEND=noninteractive apt install -yqq iproute2 iputils-ping vim wireguard iptables &>/dev/null
EOF
pid=$(docker inspect -f '{{.State.Pid}}' $docker_id)
sudo ln -sf /proc/$pid/ns/net /var/run/netns/${vpn}

# Add veth between VPC tfa1 and VPN container
sudo ip link add ve_${vpc}-${vpn} type veth peer name ve_${vpn}-${vpc}
sudo ip link set ve_${vpc}-${vpn} up netns tfa1
sudo ip link set ve_${vpn}-${vpc} up netns vpn1
sudo ip netns exec ${vpn} ip addr add ${vpn_subnet}.1/24 dev ve_${vpn}-${vpc}
sudo ip netns exec ${vpc} ip addr add ${vpn_subnet}.2/24 dev ve_${vpc}-${vpn}

# Make VPN client container and link namespace to host
docker_id=$(docker run -it -d --cap-add=NET_ADMIN --name ${client} ubuntu:23.10 bash)
docker exec -i ${client} bash <<EOF
apt-get -qq update
DEBIAN_FRONTEND=noninteractive apt-get install -yqq iproute2 iputils-ping vim wireguard iptables &>/dev/null
EOF
pid=$(docker inspect -f '{{.State.Pid}}' $docker_id)
sudo ln -sf /proc/$pid/ns/net /var/run/netns/${client}

# Add veth between provider network and client container
sudo ip link add ve_${client}-prov type veth peer name ve_prov-${client}
sudo ip link set ve_${client}-prov up netns ${client}
sudo ip link set ve_prov-${client} up netns Provider
sudo ip netns exec ${client} ip addr add ${cli_prov_subnet}.1/24 dev ve_${client}-prov
sudo ip netns exec Provider ip addr add ${cli_prov_subnet}.2/24 dev ve_prov-${client}

# On provider, add route
sudo ip netns exec Provider ip route add ${vpn_subnet}.0/24 via ${prov_vpc_subnet}.1 dev tfa1_pr

# On VPN, add route to VPC-Provider veth
sudo ip netns exec ${vpn} ip route add ${prov_vpc_subnet}.0/24 via ${vpn_subnet}.2

# On client, add route
sudo ip netns exec ${client} ip route add ${vpn_subnet}.0/24 via ${cli_prov_subnet}.2
sudo ip netns exec ${client} ip route add ${prov_vpc_subnet}.0/24 via ${cli_prov_subnet}.2

# On VPN, add route to an example VM
docker exec -i ${vpn} bash -c "ip route add 192.168.20.0/24 via ${vpn_subnet}.2"

# Generate Wireguard configs
vpn_privkey=$(docker exec -i ${vpn} bash -c "wg genkey")
vpn_pubkey=$(docker exec -i ${vpn} bash -c "echo $vpn_privkey | wg pubkey")
cli_privkey=$(docker exec -i ${client} bash -c "wg genkey")
cli_pubkey=$(docker exec -i ${client} bash -c "echo $cli_privkey | wg pubkey")

# Wireguard IPs
vpn_wgip="10.100.1.1"
cli_wgip="10.100.1.2"

docker exec -i ${vpn} bash <<EOF
echo \
'[Interface]
PrivateKey = ${vpn_privkey}
Address = ${vpn_wgip}/24
PostUp = iptables -A FORWARD -i %i -o ve_vpn1-tfa1 -j ACCEPT; iptables -A FORWARD -i ve_vpn1-tfa1 -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o ve_vpn1-tfa1 -s 10.100.1.0/24 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -o ve_vpn1-tfa1 -j ACCEPT; iptables -D FORWARD -i ve_vpn1-tfa1 -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o ve_vpn1-tfa1 -s 10.100.1.0/24 -j MASQUERADE
ListenPort = 51820

[Peer]
PublicKey = ${cli_pubkey}
AllowedIPs = ${cli_wgip}/32
' > /etc/wireguard/wg0.conf
wg-quick up wg0
EOF

docker exec -i ${client} bash <<EOF
echo \
'[Interface]
Address = ${cli_wgip}/32
PrivateKey = ${cli_privkey}

[Peer]
PublicKey = ${vpn_pubkey}
Endpoint = ${vpn_subnet}.1:51820
AllowedIPs = 0.0.0.0/0, ::/0
' > /etc/wireguard/wg0.conf
wg-quick up wg0
EOF
