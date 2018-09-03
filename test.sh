#!/bin/bash

urlget='curl -s -S -L'

hq=$1
port=$2

if [ "x$hq" = "x" ];then
    echo "test.sh <ths, sian, leverfun, tencent or tdx> [port]"
    exit 1
fi

if [ "x$port" = "x" ];then
    base_url="http://127.0.0.1/stock/hq"
else
    base_url="http://127.0.0.1:$port/hq"
fi

ths_urls="      \
datatype/       \
datatype/pre    \
hqhost/         \
market/         \
code/           \
code/wka        \
hq?mcode=sz000002;sh600168&datatype=new,pre,date,time,fromopen  \
hq?mcode=sz000002;sh600168  \
"

sina_urls="      \
hq?mcode=sz000002;sh600168&datatype=new,pre,date,time,fromopen  \
hq?mcode=sz000002;sh600168  \
"

tdx_urls="      \
hq?mcode=sz000002;sh600168&datatype=new,pre,date,time,fromopen  \
hq?mcode=sz000002;sh600168  \
"

leverfun_urls="      \
hq?mcode=sz000002;sh600168&datatype=new,pre,date,time,fromopen  \
hq?mcode=sz000002;sh600168  \
"
tencent_urls="      \
hq?mcode=sz000002;sh600168&datatype=new,pre,date,time,fromopen  \
hq?mcode=sz000002;sh600168  \
"



echo " ================================ Test ${hq} ==================================="

hqurls=${hq}_urls

for url in ${!hqurls}; do
    cmd="$urlget ${base_url}/${hq}/${url}"
    echo "# $cmd"
    $cmd | json_pp
done



# vim: tabstop=4 shiftwidth=4 expandtab
