#!/bin/bash

cd quic/LO-Result
sudo ./quic.py
cd ../../tcp/LO-Result
sudo ./tcp.py
hora=$(date +%H:%M:%S)
echo $hora > acabou.txt
