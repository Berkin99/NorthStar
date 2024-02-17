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
#!/usr/bin/env python
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


__all__ = ["NorthBuffer"]


class NorthBuffer(): # NORTH BUFFER lIFO
    
    def __init__(self, size=30):

        self.rxbuffer = []
        for i in range(size+1):self.rxbuffer.append("")

        self.rxsize = size+1
        self.index = 1
        self.mutex = False
        self.sp = 0

    def _waitMutex(self):
        time.sleep(0.001)
        while self.mutex == True:
            time.sleep(0.001)
    
    def append(self,msg):
        self._waitMutex()
        self.mutex = True
        self.index += 1
        if self.index >= self.rxsize: self.index = 0
        if self.index == self.sp: self.sp += 1
        if self.sp == self.rxsize: self.sp = 0

        self.rxbuffer[self.index] = msg

        self.mutex = False
            
    def read(self):
        if not self.isAvailable(): return None
        self._waitMutex()
        self.mutex = True
        msg = self.rxbuffer[self.index]
        self.index -= 1
        if self.index < 0: self.index = self.rxsize-1
        self.mutex = False
        return msg
    
    def isAvailable(self):
        dif = self.index - self.sp
        if dif == 0: return 0
        return abs(dif) 
    
    def getBuffer(self):
        return self.rxbuffer