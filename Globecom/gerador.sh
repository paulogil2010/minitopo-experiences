#!/bin/bash
if [ -e perdas.txt ]
then
    rm perdas.txt
else
    touch perdas.txt
fi

for i in {1..5}
do
    cA=$(shuf -i 90-100 -n 1)
    cB=$(shuf -i 90-100 -n 1)
    unA=$(shuf -i 0-9 -n 1)
    deA=$(shuf -i 0-9 -n 1)
    unB=$(shuf -i 0-9 -n 1)
    deB=$(shuf -i 0-9 -n 1)
    echo "$cA.$unA$deA% $cB.$unB$deB%" >> perdas.txt
    echo "$cB.$unB$deB% $cA.$unA$deA%" >> perdas.txt
done
