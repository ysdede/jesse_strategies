#!/bin/bash
sudo -u postgres /usr/lib/postgresql/14/bin/pg_ctl -D /tmp/ramdisk/db/ stop
sleep 5
ps aux | grep postgresql
read -rsp $'Press any key to continue...\n' -n1 key

lrzdir=$1; lrunzip -cdivvp `nproc` -o $lrzdir.tar $lrzdir.tar.bzip2-lrz; tar xvf $lrzdir.tar; rm -vf $lrzdir.tar
sudo chmod 0700 -R /tmp/ramdisk/db
sudo chown -R postgres:postgres /tmp/ramdisk/db
