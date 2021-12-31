#!/bin/bash

# This script will create a postgresql database on ramdisk
# create jesse_db, jesse user, and grant privileges
# and download kline data from Binance Vision

# Stop postgresql service if it is running
start_time=$SECONDS

echo "Trying to stop Postgresql service gracefully, watch ps aux output for it..."
sudo systemctl stop postgresql
sudo service postgresql stop  # WSL2
sudo -u postgres /usr/lib/postgresql/14/bin/pg_ctl -D /tmp/ramdisk/db/ stop
sudo umount /tmp/ramdisk/
sleep 5

ps aux | grep postgresql
read -rsp $'Press any key to continue...\n' -n1 key

# Create ramdisk, mount it, set permissions
sudo mkdir /tmp/ramdisk
sudo chmod 777 /tmp/ramdisk
sudo mount -t tmpfs -o size=4G ramdisk /tmp/ramdisk
mount | tail -n 1
mkdir /tmp/ramdisk/db
sudo chmod 0700 -R /tmp/ramdisk/db
sudo chown -R postgres:postgres /tmp/ramdisk/db

# Initialize db directory as Postgresql database
sudo -u postgres /usr/lib/postgresql/14/bin/pg_ctl -D /tmp/ramdisk/db initdb

# Start Postgresql with custom directory
sudo -u postgres /usr/lib/postgresql/14/bin/pg_ctl -D /tmp/ramdisk/db -w start

# Create jesse_db, user and grant privileges
sudo -u postgres psql -c "CREATE DATABASE jesse_db;"
sudo -u postgres psql -c "CREATE USER jesse_user WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE jesse_db to jesse_user;"

# jesse make-project temp-project
# cd temp-project
# Warmup jesse_db
jesse import-candles Binance btc-usdt 2021-12-04 --skip-confirmation

# Batch import
jesse-tk bulk spot btc-usdt $1 --workers 5
jesse-tk bulk spot eth-usdt $1 --workers 5
jesse-tk bulk spot bnb-usdt $1 --workers 5

# 2nd pass with jesse import-candles to fill missing candles
jesse import-candles Binance btc-usdt $1 --skip-confirmation
jesse import-candles Binance eth-usdt $1 --skip-confirmation
jesse import-candles Binance bnb-usdt $1 --skip-confirmation

# Vacuum, analyze and reindex jesse_db
sudo -u postgres /usr/lib/postgresql/14/bin/vacuumdb  --analyze --verbose -d jesse_db -e -f
sudo -u postgres /usr/lib/postgresql/14/bin/reindexdb --verbose jesse_db

# cd ..
# rm -r temp-project
elapsed=$(( SECONDS - start_time ))
eval "echo Elapsed time: $(date -ud "@$elapsed" +'$((%s/3600/24)) days %H hr %M min %S sec')"
