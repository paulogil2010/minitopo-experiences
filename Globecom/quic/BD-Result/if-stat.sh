#!/bin/bash


raiz=$(pwd)
pasta=$(ls -d */)
saida="$raiz/ifstat"
cen=1
aux=1

if [! -d "$saida"]; then
    mkdir $saida
else
    rm -rf $saida/*
fi


for dir in $pasta
do
    cd $dir
    ins=$(ls | cut -d' ' -f 9)

    for sub in $ins
    do
        FILE=$saida/ifstat.$cen.$aux.txt
        if [ ! -f $FILE ]; then
            touch $FILE
            echo "eth0-in,eth0-out,eth1-in,eth1-out" > $FILE
        fi

        cat $sub/quic/1/client_ifstat.txt | sed '/KB\/s/g' | sed '/Clie/d' | awk -v OFS="," '$1=$1' >> $FILE
        aux=$((aux+1))
    done
    cen=$((cen+1))
    aux=1
    cd $raiz
done
