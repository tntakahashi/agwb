#!/bin/bash

TERMINAL=xterm

if ! command -v ${TERMINAL} > /dev/null; then
	echo ${TERMINAL} terminal not installed.
	exit 1
fi

set -e
rm -f /tmp/rdpipe /tmp/wrpipe
# Create the named pipes
mknod /tmp/rdpipe p
mknod /tmp/wrpipe p
# Run the python script in the other xterm
# Uncomment the line below to run the test that uses emulated IPbus
#${TERMINAL} -e "python3 python_ipbus/wb_test.py; echo 'press ENTER'; read" &
# Uncomment the line below to run the test that uses raw Python access
${TERMINAL} -e "python3 python_raw/wb_test.py; echo 'press ENTER'; read" &
make
