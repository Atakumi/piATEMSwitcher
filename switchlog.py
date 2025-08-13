#!/usr/bin/python
# coding: utf-8

""" 
    File: switchlog.py
    Function: create and record log for ATEM switcher events
    ATEM switcher controller for Raspberry Pi (ZeroW, 3-)
    Copyright by Takumi DRIVE OU / Takumi Amano 
"""

import time

class switchlog:
    def __init__(self, _switcher):
        self.switcher = _switcher
        # Open local text file as 'switchlog.drp'
        self.log_file_path = f'switchlog-{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday}.drp'
        # get timecode for log entry
        timecode = self.switcher.lastStateChange.timeCode
        try:
            self.log_file = open(self.log_file_path, "a+")  # Open for reading and appending
            log_entry = f'{{"version":1,"masterTimecode":"{timecode}","videoMode":"1080p29.97"}}\n'
            self.log_file.write(log_entry)
            self.log_file.flush()
        except Exception as e:
            print(f"Error opening log file: {e}")
            self.log_file = None

    def log_event(self, source: int, index: int):
        if self.log_file:
            timecode = self.switcher.lastStateChange.timeCode
            log_entry = f'{{"masterTimecode":"{timecode}","mixEffectBlocks":[{{"source":{source},"_index_":{index}}}]}}\n'
            self.log_file.write(log_entry)
            self.log_file.flush()

    def close_log(self):
        if self.log_file:
            self.log_file.close()
            self.log_file = None
