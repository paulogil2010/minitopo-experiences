#!/bin/bash

cd quic/HO-Result
sudo ./quic.py
cd ../../tcp/HO-Result
sudo ./tcp.py
hora=$(date +%H:%M:%S)
echo $hora > acabou.txt
