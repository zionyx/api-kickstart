#!/usr/bin/env bash
CYAN="\033[36m"
BLUE="\033[34m"
GREEN="\033[32m"
RED="\033[31m"
RESET="\033[0m"

if [[ -z $BIN ]]; then
    BIN=$LANGUAGE
fi

FILES=(examples/${LANGUAGE}/*.${EXT})
for KEY in "${!FILES[@]}"
do
	if [[ `basename ${FILES[$KEY]}` == gen_edgerc* ]]; then
	    STATUSES[$KEY]=0
	else
		$BIN ${FILES[$KEY]} --verbose --debug
		STATUSES[$KEY]=$?
	fi
done

HAS_ERROR=0;
printf "\n\n\n${BLUE}======= SUMMARY =======${RESET}\n\n"

for KEY in "${!STATUSES[@]}"
do
	if [[ ${STATUSES[$KEY]} -ne 0 ]]; then
		HAS_ERROR=1
		echo -e "${CYAN} $(basename ${FILES[$KEY]})${RESET}... [${RED}FAIL${RESET}]"
	else
		echo -e "${CYAN} $(basename ${FILES[$KEY]})${RESET}... [${GREEN}OK${RESET}]"
	fi
done

if [[ $HAS_ERROR -eq 1 ]]; then
	exit 1
fi
