#!/bin/bash

# This script will create a postgresql database on ramdisk

# Stop postgresql service if it is running
echo "Trying to stop Postgresql service gracefully, watch ps aux output for it..."
sudo systemctl stop postgresql
sudo service postgresql stop  # WSL2
sudo -u postgres /usr/lib/postgresql/14/bin/pg_ctl -D /tmp/ramdisk/db/ stop
sudo umount /tmp/ramdisk/
sleep 3

ps aux | grep postgresql
read -rsp $'Press any key to continue...\n' -n1 key

# Create ramdisk, mount it, set permissions
sudo mkdir /tmp/ramdisk
sudo chmod 777 /tmp/ramdisk
sudo mount -t tmpfs -o size=4G ramdisk /tmp/ramdisk
mount | tail -n 1

wget https://github.com/ysdede/jesse_dbs/releases/download/jesse/db-pigz.tar.gz -O /tmp/ramdisk/db-pigz.tar.gz

sudo apt install pigz -y

tar -I pigz -xvf /tmp/ramdisk/db-pigz.tar.gz -C /tmp/ramdisk/
rm /tmp/ramdisk/db-pigz.tar.gz

sudo chmod 0700 -R /tmp/ramdisk/db
sudo chown -R postgres:postgres /tmp/ramdisk/db

sudo -u postgres /usr/lib/postgresql/14/bin/pg_ctl -D /tmp/ramdisk/db -w start
sleep 2
jesse import-candles Binance btc-usdt 2021-12-01 --skip-confirmation
jesse import-candles Binance eth-usdt 2021-12-01 --skip-confirmation
jesse import-candles Binance bnb-usdt 2021-12-01 --skip-confirmation

sudo -u postgres /usr/lib/postgresql/14/bin/vacuumdb --analyze -d jesse_db -e -f
sudo -u postgres /usr/lib/postgresql/14/bin/reindexdb jesse_db
