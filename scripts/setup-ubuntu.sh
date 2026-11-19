#!/usr/bin/env bash
# Prepare a fresh Ubuntu 22.04 / 24.04 server (or Debian 12) for the deploy kit. Run once, as root:
#     curl -fsSL <raw url>/setup-ubuntu.sh | sudo bash        or      sudo bash deploy/setup-ubuntu.sh
# Does: Docker (official apt repo), firewall (only SSH, 80, 443), automatic security updates, a swap file on small machines.
# Does NOT: touch SSH settings, create users, or deploy anything. SKIP_FIREWALL=1 / SKIP_SWAP=1 skip those parts.
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "run as root: sudo bash $0"; exit 1; }
. /etc/os-release
case "$ID" in ubuntu|debian) ;; *) echo "this script is for Ubuntu or Debian (found: $ID)"; exit 1 ;; esac
export DEBIAN_FRONTEND=noninteractive

echo "== packages"
apt-get update -qq
apt-get install -y -qq ca-certificates curl git gnupg unattended-upgrades >/dev/null

echo "== Docker"
if ! command -v docker >/dev/null; then
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL "https://download.docker.com/linux/$ID/gpg" -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/$ID $VERSION_CODENAME stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin >/dev/null
fi
command -v systemctl >/dev/null && systemctl enable --now docker >/dev/null 2>&1 || true
[ -n "${SUDO_USER:-}" ] && usermod -aG docker "$SUDO_USER" && echo "added $SUDO_USER to the docker group (log out and in once)"

echo "== automatic security updates"
echo 'APT::Periodic::Update-Package-Lists "1"; APT::Periodic::Unattended-Upgrade "1";' > /etc/apt/apt.conf.d/20auto-upgrades

if [ "${SKIP_FIREWALL:-0}" != "1" ]; then
  echo "== firewall (SSH, 80, 443 only)"
  apt-get install -y -qq ufw >/dev/null
  ufw default deny incoming >/dev/null
  ufw default allow outgoing >/dev/null
  ufw allow OpenSSH >/dev/null || ufw allow 22/tcp >/dev/null   # SSH first, so enabling cannot lock you out
  ufw allow 80/tcp >/dev/null
  ufw allow 443/tcp >/dev/null
  ufw --force enable >/dev/null
  # note: Docker publishes ports through its own iptables rules and bypasses ufw; the compose file only publishes 80 and 443 for that reason
fi

if [ "${SKIP_SWAP:-0}" != "1" ] && [ "$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo)" -lt 6000 ] && ! swapon --show | grep -q .; then
  echo "== 2 GB swap file (this machine has under 6 GB RAM)"
  fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile >/dev/null && swapon /swapfile
  grep -q /swapfile /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo
docker --version && docker compose version
echo "RAM: $(awk '/MemTotal/{printf "%.1f GB", $2/1048576}' /proc/meminfo), disk free: $(df -h / | awk 'NR==2{print $4}')"
echo "Next: git clone this repo, then follow DEPLOYMENT.md step 3"
