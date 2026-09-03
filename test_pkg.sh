echo "Testing apt..."
apt-get --version
echo "Testing apt lock..."
lsof /var/lib/dpkg/lock-frontend || true
