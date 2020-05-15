#!/bin/bash


raiz=$(pwd)
pasta=$(ls -d */)
cen=1
aux=1

for dir in $pasta
do 
    cd $dir 
    ins=$(ls | cut -d' ' -f 9)

    for sub in $ins
    do
        FILE=$raiz/ifstat.$cen.$aux.txt
        if [ ! -f $FILE ]; then
            touch $FILE
            echo "eth0-in,eth0-out,eth1-in,eth1-out" > $FILE
        fi

        cat $sub/https/1/client_ifstat.txt | sed '/KB\/s/g' | sed '/Clie/d' | awk -v OFS="," '$1=$1' >> $FILE
        aux=$((aux+1))
    done
    cen=$((cen+1))
    aux=1
    cd $raiz
done
