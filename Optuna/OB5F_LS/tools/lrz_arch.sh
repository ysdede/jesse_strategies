#!/bin/bash
lrzdir=$1; tar cvf $lrzdir.tar $lrzdir; lrzip -Ubvvp `nproc` -S .bzip2-lrz -L 9 $lrzdir.tar; rm -fv $lrzdir.tar; unset lrzdir

