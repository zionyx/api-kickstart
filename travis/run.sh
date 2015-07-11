#!/bin/bash
source colors.sh
./edgerc.s
for SCRIPT in ./enabled/*; 
do
	TEST=$(grep -F 'Test: ' ./available/run-user-admin.py | sed 's/# Test: //')
	printf "${YELLOW}TEST:${RESET} ${TEST}\n"
	echo "========================================================="
	$SCRIPT
	./result.sh $?
done ;
