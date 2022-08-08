#!/bin/bash

# turn off power save on WiFi adapter on raspberry pi. No need to do this if you're using wired LAN
sudo iw dev wlan0 set power_save off

LOCALDIR=/home/<your home directory>/piATEMSwitcher
cd $LOCALDIR

sleep 7
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
