useradd -m zhuxu
passwd zhuxu
getent group sudo
sudo apt install git -y
bash <(curl -L https://github.com/crazypeace/xray-vless-reality/raw/main/install.sh)
# addons.mozilla.org

iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
iptables -F

apt-get purge netfilter-persistent

# crontab -e
# 0 1 * * * /usr/bin/systemctl restart xray

echo "hill" | s-nail -s "hill" -a ~/_vless_reality_url_  1077246@qq.com