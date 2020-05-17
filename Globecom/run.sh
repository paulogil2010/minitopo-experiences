#!/bin/bash


# QUIC
cd quic/BL_1-5-Result
start=$(date +%H:%M:%S)

sudo ./quic.py
./2-flows-quic.sh
./if-stat.sh

cd ../../
end=$(date +%H:%M:%S)

echo "Iniciou - $start\nTerminou - $end" > quic_BL_1-5-Result-time.txt

# TCP
cd tcp/BL_1-5-Result
start=$(date +%H:%M:%S)

sudo ./tcp.py
./2-flows-tcp.sh
./if-stat.sh

cd../../
end=$(date +%H:%M:%S)

echo "Iniciou - $start\nTerminou - $end" > tcp_BL_1-5-Result-time.txt
