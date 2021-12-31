#!/bin/bash
sudo mkdir /tmp/ramdisk
sudo chmod 777 /tmp/ramdisk
sudo mount -t tmpfs -o size=8G ramdisk /tmp/ramdisk
mount | tail -n 1
sudo service postgresql stop
mkdir /tmp/ramdisk/db
sudo chmod 0700 -R /tmp/ramdisk/db
sudo chown -R postgres:postgres /tmp/ramdisk/db

sudo -u postgres tar -xvf /home/ysdede/jesse-projects/databases/fresh_db.tar.bz2 -C /tmp/ramdisk/

# sudo systemctl stop postgresql
# sudo service postgresql stop  # WSL2
#sudo killall postgresql

sudo -u postgres /usr/lib/postgresql/14/bin/pg_ctl -D /tmp/ramdisk/db -w start
