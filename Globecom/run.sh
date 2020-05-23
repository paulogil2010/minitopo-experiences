#!/bin/bash


# QUIC
cd quic/HL_1-5-Result
begin=$(date '+%d/%m/%Y %H:%M:%S')

# 10-20
sudo ./quic-10-20.py
./2-flows-quic.sh
mkdir 10-20
mv https* 10-20
cd ../../
# 20-30
sudo ./quic-20-30.py
./2-flows-quic.sh
mkdir 20-30
mv https* 20-30
cd ../../
# 30-40
sudo ./quic-30-40.py
./2-flows-quic.sh
mkdir 30-40
mv https* 30-40
cd ../../
# 40-50
sudo ./quic-40-50.py
./2-flows-quic.sh
mkdir 40-50
mv https* 40-50
cd ../../
# 50-60
sudo ./quic-50-60.py
./2-flows-quic.sh
mkdir 50-60
mv https* 50-60
cd ../../
# 60-70
sudo ./quic-60-70.py
./2-flows-quic.sh
mkdir 60-70
mv https* 60-70
cd ../../
# 70-80
sudo ./quic-70-80.py
./2-flows-quic.sh
mkdir 70-80
mv https* 70-80
cd ../../
# 80-90
sudo ./quic-80-90.py
./2-flows-quic.sh
mkdir 80-90
mv https* 80-90
cd ../../
# 90-100
sudo ./quic-90-100.py
./2-flows-quic.sh
mkdir 90-100
mv https* 90-100
cd ../../


end=$(date '+%d/%m/%Y %H:%M:%S')

echo -e "Iniciou - $begin\nTerminou - $end" > quic_LO-10-100.txt

# # TCP
# cd tcp/HL_1-5-Result
# begin=$(date '+%d/%m/%Y %H:%M:%S')

# sudo ./tcp.py
# ./2-flows-tcp.sh
# ./if-stat.sh

# cd../../
# end=$(date '+%d/%m/%Y %H:%M:%S')
# cd ../../
# echo -e "Iniciou - $begin\nTerminou - $end" > tcp_HL_1-5-Result-time.txt
