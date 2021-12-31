#!/bin/bash
/usr/lib/postgresql/14/bin/pg_ctl -D /tmp/ramdisk/db/ stop
sleep 5
ps aux | grep postgresql
read -rsp $'Press any key to continue...\n' -n1 key

lrzdir=$1; tar cvf $lrzdir.tar $lrzdir; lrzip -Ubvvp `nproc` -S .bzip2-lrz -L 4 $lrzdir.tar; rm -fv $lrzdir.tar; unset lrzdir
