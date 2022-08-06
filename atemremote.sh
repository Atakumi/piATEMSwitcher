#!/bin/bash

LOCALDIR=/home/takua/piATEMSwitcher
cd $LOCALDIR

sleep 10
while true; do
  python3 ${LOCALDIR}/main.py
  EXITCODE=$?
  echo Exit code - $EXITCODE
  if [ $EXITCODE -eq 1 ]; then
    sudo halt
  fi
  if [ $EXITCODE -eq 0 ]; then
    exit 0
  fi
  sleep 3
  echo Restarting the main program
done
