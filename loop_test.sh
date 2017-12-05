#!/bin/bash

hq=$1
port=$2

if [ "x$hq" = "x" ];then
    echo "loop_test.sh <ths, sina , leverfun, tencent or tdx> [port]"
    exit 1
fi

if [ "x$port" = "x" ];then
    base_url="http://127.0.0.1/stock/hq"
else
    base_url="http://127.0.0.1:$port/hq"
fi

url="$base_url/${hq}/hq?mcode=sz000002;sh600168&datatype=new,vol,money,pre,date,time,fromopen"


while true; do
    curl -s "$url"
    date
    sleep 1s
done

# vim: tabstop=4 shiftwidth=4 expandtab
