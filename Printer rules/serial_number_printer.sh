#!/bin/bash
# Define the fixed prefix
PREFIX="202502"

# Loop from 001 to 050 using seq with -w to pad numbers with zeros
for i in $(seq -w 1 50); do
  # Create the label command string and send it to the printer
  cat <<EOF > /dev/usb/lp0
N
q406
Q203,027
ZT
B100,40,0,1,2,4,100,T,"${PREFIX}${i}"
A100,150,0,3,1,1,N,"S/N:""${PREFIX}${i}"
P2
EOF
done
