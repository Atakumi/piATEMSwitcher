#!/bin/bash

# turn off power save on WiFi adapter on raspberry pi. No need to do this if you're using wired LAN
sudo iw dev wlan0 set power_save off

LOCALDIR=/home/<your home directory>/piATEMSwitcher
cd $LOCALDIR

sleep 7
while true; do
  python3 ${LOCALDIR}/main.py
  EXITCODE=$?
  EXITCODE=$?

  case $EXITCODE in
    0)
      exit 0
      ;;
    1)
      sudo halt
      ;;
    3)
      sudo reboot
  esac
  sleep 3
  echo Restarting the main program
done
