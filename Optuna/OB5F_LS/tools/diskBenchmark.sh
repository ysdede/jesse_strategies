sync; dd if=/dev/zero of=/tmp/ramdisk/ bs=1M count=1024; sync
dd: failed to open '/tmp/ramdisk/': Is a directory
ysdede@instance-1:~/jesse-projects/git/jesse_strategies/Optuna/OttBands5minFixedOttOptuna1Test$ sync; dd if=/dev/zero of=/tmp/ramdisk/benchfile bs=1M count=1024; sync
1024+0 records in
1024+0 records out
1073741824 bytes (1.1 GB, 1.0 GiB) copied, 0.360476 s, 3.0 GB/s
ysdede@instance-1:~/jesse-projects/git/jesse_strategies/Optuna/OttBands5minFixedOttOptuna1Test$ dd if=/tmp/ramdisk/benchfile of=/dev/null bs=1M count=1024
1024+0 records in
1024+0 records out
1073741824 bytes (1.1 GB, 1.0 GiB) copied, 0.178526 s, 6.0 GB/s

