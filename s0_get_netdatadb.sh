#!/bin/bash

# d='20191006'

d=$1
nf="var/netdata-$d.db.gz"

if [ -z "$d" ]
then
    echo ERROR - Invoke as: ./s0_get_netdatadb.sh YYYYMMDD
    exit 1
fi

if [ -f "$nf" ]
then
    echo WARNING - File $nf already exists. Skipping download.
    echo WARNING - Please remove existing file to force re-downloading.
    exit 0
else
    echo Getting netdata for date $d

    wget -c --output-document="$nf" \
        http://trantor.labs.lacnic.net/carlos/netdata/netdata-$d.db.gz

    cd var
    gunzip netdata-$d.db.gz
fi 

# linking to latest
ln -sf netdata-$d.db netdata-latest.db 

exit 0