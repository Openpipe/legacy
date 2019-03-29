#!/bin/sh
rm -f tmp.txt
set -eu
wget https://archive.org/download/stackexchange-snapshot-2018-03-14/academia.stackexchange.com.7z -O /tmp/academia.stackexchange.com.7z
mkdir -p /tmp/academia
cd /tmp/academia
7za x ../academia.stackexchange.com.7z
#gzip *.xml
