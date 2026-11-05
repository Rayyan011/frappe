#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y docker.io docker-compose-v2 unattended-upgrades
install -d -m 0755 /etc/docker
cat >/etc/docker/daemon.json <<'JSON'
{"log-driver":"json-file","log-opts":{"max-size":"10m","max-file":"3"},"live-restore":true}
JSON
if ! swapon --show=NAME --noheadings | grep -q /swapfile; then
  fallocate -l 4G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi
echo 'vm.swappiness=10' >/etc/sysctl.d/90-opcloud.conf
echo 'vm.overcommit_memory=1' >>/etc/sysctl.d/90-opcloud.conf
sysctl -p /etc/sysctl.d/90-opcloud.conf
systemctl enable --now docker
systemctl restart docker
usermod -aG docker ubuntu
install -d -m 0700 -o ubuntu -g ubuntu /opt/stackable-opcloud
cat >/etc/ssh/sshd_config.d/90-opcloud.conf <<'SSH'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
SSH
sshd -t
systemctl reload ssh
