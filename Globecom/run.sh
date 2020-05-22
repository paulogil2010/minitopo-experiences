#!/bin/bash


# QUIC
cd quic/HL_1-5-Result
begin=$(date '+%d/%m/%Y %H:%M:%S')


sudo ./quic.py
./2-flows-quic.sh
./if-stat.sh

cd ../../
end=$(date '+%d/%m/%Y %H:%M:%S')

echo -e "Iniciou - $begin\nTerminou - $end" > quic_HL_1-5-Result-time.txt

# TCP
cd tcp/HL_1-5-Result
begin=$(date '+%d/%m/%Y %H:%M:%S')

sudo ./tcp.py
./2-flows-tcp.sh
./if-stat.sh

cd../../
end=$(date '+%d/%m/%Y %H:%M:%S')

echo -e "Iniciou - $begin\nTerminou - $end" > tcp_HL_1-5-Result-time.txt
