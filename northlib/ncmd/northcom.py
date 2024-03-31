#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  __  __ ____ _  __ ____ ___ __  __
#  \ \/ // __// |/ //  _// _ |\ \/ /
#   \  // _/ /    /_/ / / __ | \  / 
#   /_//___//_/|_//___//_/ |_| /_/  
# 
#   2024 Yeniay Uav Flight Control Systems
#   Research and Development Team

import time
from northlib.ntrp.northpipe import NorthNRF
from northlib.ntrp.ntrpbuffer import NTRPBuffer
import northlib.ntrp.ntrp as ntrp
from northlib.ncmd.nrxtable import NrxTable

__author__ = 'Yeniay RD'
__all__ = ['NorthCOM']


class NorthCOM(NorthNRF):

    """ 
    NorthCommander Core Class
    Set URI : radio:/radioindex/ch/bandwidth/address

    Communicates with agent.
    Parameter, Function Syncronisation
    """

    CMD_PARAM_CONTENT    = 1
    CMD_FUNCTION_CONTENT = 2

    def __init__(self, uri="radio:/0/76/2/E7E7E7E301"):
        self.uri = uri
        part = uri.split('/')
        super().__init__(int(part[1]),int(part[2]),int(part[3]),part[4])
        
        self.setCallBack(ntrp.NTRPHeader_e.ACK,self.rxACK)
        self.setCallBack(ntrp.NTRPHeader_e.NAK,self.rxNAK)
        self.setCallBack(ntrp.NTRPHeader_e.SET,self.rxSET)
        self.setCallBack(ntrp.NTRPHeader_e.LOG,self.rxSET)
        self.setCallBack(ntrp.NTRPHeader_e.CMD,self.rxCMD)
        
        self.setRxHandleMode(self.RX_HANDLE_MODE_CALLBACK)
        self.txTRX()

        self.connection = False
        self.tableReady = False
        self.paramtable = NrxTable()

    def connect(self,timeout = 30):
        rettime = self.waitConnection(timeout)
        if rettime > 0 : 
            self.printID("connected in " + str(rettime) + " seconds.")
            self.connection = True
        else: self.connection = False

    def synchronize(self):
        self.setRxHandleMode(self.RX_HANDLE_MODE_BUFFER)
        i=0
        miss = 0
        self.rxbuffer.flush()
        while 1:
            self.txCMD(dataID=self.CMD_PARAM_CONTENT,channels=bytearray([i]))
            time.sleep(0.01)
            if self.rxbuffer.isAvailable()<1:
                miss+=1 
                if miss > 50: self.printID("Too much missing command! : " + str(miss))
                continue

            msg = self.rxbuffer.read()
            if (msg.header == ntrp.NTRPHeader_e.ACK): break
            if not (msg.header == ntrp.NTRPHeader_e.CMD) : continue
            if not (msg.dataID == self.CMD_PARAM_CONTENT): continue 
            self.paramtable.tableAppend(msg.data)
            i+=1

        self.tableReady = True
        self.setRxHandleMode(self.RX_HANDLE_MODE_CALLBACK)

    def rxHandler(self,msg = ntrp.NTRPMessage()):
        func = self.rxFunctions.get(msg.header)
        if func == None: self.printID("rxHandler Packet Error : Header Not Found")
        func(msg)

    def rxNAK(self,msg):
        self.printID('NAK')

    def rxACK(self,msg):
        self.printID('ACK')

    def rxCMD(self,msg=ntrp.NTRPMessage()):
        if msg.dataID == self.CMD_PARAM_CONTENT:
            self.paramtable.tableAppend(msg.data)

    def rxSET(self,msg=ntrp.NTRPMessage()):
        nx = self.paramtable.getByIndex(msg.dataID)
        if nx == None: 
            self.printID("rxSET Not found in the table : " + str(msg.dataID))
            return
        nx.setValue(msg.data)

