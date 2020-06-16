#!/usr/bin/env bash
# 1. 拉代码到 /var/www/pl_bbs
# 2. 执行 bash deploy.sh

set -ex

# 系统设置
apt-get install -y curl ufw
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 465
ufw default deny incoming
ufw default allow outgoing
ufw status verbose
ufw -f enable

# redis 需要 ipv6
sysctl -w net.ipv6.conf.all.disable_ipv6=0
# 安装过程中选择默认选项，这样不会弹出 libssl 确认框
export DEBIAN_FRONTEND=noninteractive
# 完全卸载 nginx
#sudo apt-get remove --purge nginx
#sudo apt-get autoremove --purge
# 装依赖
apt-get install -y git supervisor nginx python3-pip mysql-server redis-server apache2-utils
#apt-get install -y git supervisor nginx python3-pip mysql-server apache2-utils
pip3 install jinja2 flask gevent gunicorn pymysql flask_sqlalchemy flask_mail marrow.mailer redis Celery
#pip3 install jinja2 flask gevent gunicorn pymysql flask_sqlalchemy flask_mail marrow.mailer

# 删除测试用户和测试数据库
# 删除测试用户和测试数据库并限制关闭公网访问
mysql -u root -p... -e "DELETE FROM mysql.user WHERE User='';"
mysql -u root -p... -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -u root -p... -e "DROP DATABASE IF EXISTS test;"
mysql -u root -p... -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
# 设置密码并切换成密码验证
mysql -u root -p... -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '...';"

# 删掉 nginx default 设置
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-available/default
# 不要再 sites-available 里面放任何东西
cp /var/www/pl_bbs/pl_bbs.nginx /etc/nginx/sites-enabled/pl_bbs
chmod -R o+rwx /var/www/pl_bbs

cp pl_bbs.service /etc/systemd/system/pl_bbs.service
cp pl_bbs-message-queue.service /etc/systemd/system/pl_bbs-message-queue.service


# 初始化
cd /var/www/pl_bbs
python3 reset.py

# 重启服务器
systemctl daemon-reload
systemctl restart pl_bbs
systemctl restart pl_bbs-message-queue
systemctl restart nginx

echo 'succsss'
echo 'ip'
hostname -I
curl http://localhost
