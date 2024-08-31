#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  __  __ ____ _  __ ____ ___ __  __
#  \ \/ // __// |/ //  _// _ |\ \/ /
#   \  // _/ /    /_/ / / __ | \  / 
#   /_//___//_/|_//___//_/ |_| /_/  
# 
#   2024 Yeniay Uav Flight Control Systems
#   Research and Development Team

import sys
sys.path.append('./')

import time
import northlib.ntrp as radioManager
from   northlib.ntrp.northpipe import NorthPipe,NorthNRF
import northlib.ntrp.ntrp as ntrp
import northlib.ncmd.controller as ncmd
from   northlib.ncmd.northcom import NorthCOM
from   northlib.ncmd.nrxtable import NrxTableLog
import keyboard
import threading

"""
String to NRX Commands translator
Controller task auto start
str = [GET / SET][NRX NAME][VALUE]
"""
class NorthCMD(NorthCOM):
	def __init__(self, uri) -> None:
		super().__init__(uri)
		self.connect()        # Request ACK to sended MSG
		self.synchronize()    # Syncronize the NRX Table

		self.ctrl = ncmd.Controller(True) # Joystick controller
		self.ctrl.callBack = lambda x : self.txCMD(channels = x, force = True)

	def commandParser(self, string = str):
		parsed = string.split(' ')
		if(parsed[0] == "GET"):
			print(self.GET(parsed[1]))
		if(parsed[0] == "SET"):
			if(len(parsed) > 3):self.SET(parsed[1], parsed[2:])
			elif(len(parsed) == 3): self.SET(parsed[1], parsed[2])

if __name__ == '__main__':
	
	radioManager.radioSearch (baud=2000000) #Arduino DUE (USB Connection) has no Baudrate
	if not len(radioManager.availableRadios) > 0: sys.exit()

	uri = "radio:/0/76/2/E7E7E7E301"
	cmd = NorthCMD(uri)
	cmd.commandParser(input())

	while (cmd.radio.isRadioAlive()):
		cmd.commandParser(input())