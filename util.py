#!/usr/bin/python
# coding: utf-8

""" ATEM switcher controller for Raspberry Pi (3-)
Copyright by Takumi DRIVE OU / Takumi Amano """

from typing import Dict, Any
import os
import sys
import json

class ReadConfig:
    def __init__(self):
        jsonfile = open("atemconfig.json", "r")
        self.configdic = json.load(jsonfile)["atem-config"]

    def getButton(self, _index):
        return self.configdic["buttons"][_index]

    def getButtonList(self, _attr) -> list:
        result_list = []
        for bt in self.configdic["buttons"]:
            if _attr in bt.keys():
                result_list.append(bt[_attr])
            else:
                result_list.append("")
        return result_list

    def getIpAddress(self) -> str:
        return self.configdic["ip-address"]

    def getConnectTimeout(self) -> float:
        return self.configdic["connect-timeout"]

if __name__ == "__main__":
    config = ReadConfig()
    print("ip address", config.getIpAddress())

    print("function : ",     config.getButtonList("function"))
    print("video sources: ", config.getButtonList("source"))
    print("display name : ", config.getButtonList("display-name"))
    
