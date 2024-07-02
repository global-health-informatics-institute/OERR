#!/bin/sh

BASE_GPIO_PATH=/sys/class/gpio

PRINTERON=18

ON="1"
OFF="0"

filename=$(basename "$1")

exportPin() {
	if [ ! -e $BASE_GPIO_PATH/gpio18 ]; then
		echo "18" > $BASE_GPIO_PATH/export
	fi
}

setOutput()
{
	echo "out" > $BASE_GPIO_PATH/gpio18/direction
}

setPrinterState()
{
	echo $1 > $BASE_GPIO_PATH/gpio18/value
}

exportPin

setOutput

setPrinterState $ON
sleep 3

	ext="${filename##*.}"

	if [ "$ext" = "lbl" ]; then  

            echo "printing label $1" >> /tmp/print.log
            cat $1 > /dev/usblp0
	        
	fi;

	if [ "$ext" = "lbs" ]; then 
            echo "printing receipt $1" >> /tmp/print.log
            cat $1 > /dev/ttyUSB0  
	fi;

sleep 5
setPrinterState $OFF
rm $1