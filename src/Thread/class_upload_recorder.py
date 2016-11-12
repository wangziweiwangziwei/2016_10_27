# -*- coding: utf-8 -*-
import threading
import time
import wx
from src.Package.package import *
from src.Spectrum import Spectrum_1
import struct
from src.CommonUse.staticVar import staticVar
from src.CommonUse.staticFileUpMode import staticFileUp
import socket
import os
import cPickle as pickle

from src.Package.logg import Log
class SendRecorderFile():
    def __init__(self):


        self.FILE_PATH = os.getcwd() + "\\LocalData\\IQ2\\"
        self.indexOfNameList=0
        self.nameListIQ2 = []



    def send_recorder_data(self):
        if (self.nameListIQ2 == []):
            self.nameListIQ2 = os.listdir(self.FILE_PATH)

            if (len(self.nameListIQ2) >= 10):
                self.upload()
            else:
                self.nameListIQ2 = []

        else:
            self.upload()

    def upload(self):

        if (self.indexOfNameList == len(self.nameListIQ2)):
           
            self.indexOfNameList = 0
            self.nameListIQ2 = []


        else:
            #传输文件

            fileName = self.nameListIQ2[self.indexOfNameList]
            self.indexOfNameList += 1
            if(os.path.isfile(self.FILE_PATH + fileName)):
                    
            
#                 d = pickle.load(fid)
#                 fid.close()
# 
#                 LonLat= d['LonLat']
#                 count_ab= d['count_ab']
#                 list_for_ab=d['list_for_ab']
# 
# 
                fileNameLen=len(fileName)
#                 fileContentLen=sizeof(LonLat)+5*count_ab+3

                sockFile = staticVar.getSockFile()
                if(not sockFile==0):
                    try:
                        str1=struct.pack("!2BHQ",0x00,0xFF,fileNameLen,6017) ######服务器规定的格式
                        sockFile.sendall(str1+fileName)
                        # sockFile.sendall(struct.pack("!B", 0x00))
                        
                        print str1+fileName
                        f = open(".\LocalData\\IQ2\\" + fileName, 'rb').read()
                        for i in f:
                            sockFile.sendall(i)
                    
                        
#                         sockFile.sendall(bytearray(LonLat))
#                         sockFile.sendall(struct.pack("!B",  count_ab))
#                         sockFile.sendall(bytearray(list_for_ab))
#                         sockFile.sendall(struct.pack("!B",0x00))

                        print fileName
                        os.remove(self.FILE_PATH + fileName)
                        Log.getLogger().debug("send_iq2_file_ok:%s" % fileName)

                    except socket.error,e:
                        print 'socket error occur in send iq2 ',e
                        Log.getLogger().debug(" socket_error_found_in_send_iq2_file: %s" % e)
                        Log.getLogger().debug(" Cur socket sockFile=: %s" % staticVar.sockFile)

                        staticVar.sockFile=0