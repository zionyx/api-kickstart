#!/bin/bash
RESULT=$1

if [[ ! $RESULT -eq 0 ]]
then
   printf "${YELLOW}Result: ${RED}FAILED${RESET}\n\n"
else
   printf "${YELLOW}Result: ${GREEN}OK${RESET}\n\n"
fi
