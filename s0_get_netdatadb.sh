#!/bin/bash

# d='20191006'

d=$1

if [ -z "$d" ]
then
    echo Invoke as: ./s0_get_netdatadb.sh YYYYMMDD
    exit 1
fi

echo Getting netdata for date $d

wget -c --output-document=var/netdata-$d.db.gz \
    http://trantor.labs.lacnic.net/carlos/netdata/netdata-$d.db.gz

cd var

gunzip netdata-$d.db.gz

ln -sf netdata-$d.db netdata-latest.db 
