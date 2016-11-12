# -*- coding: utf-8 -*-
import threading
import time
import datetime
import usb
import struct
import cPickle as pickle
from src.CommonUse.staticVar import staticVar
from src.Package.package import IQ2UploadHeader,IQ2Block
 
class ReceiveRecorderDataThread(threading.Thread):
    def __init__(self,mainframe):
        threading.Thread.__init__(self)
        
        self.count_iq2_file = 0
        self.event = threading.Event()
        self.event.set()
        
        ###########################
        self.byte_to_package = mainframe.byte_to_package
        self.mainframe = mainframe
        
    def stop(self):
        self.event.clear()
        
    def run(self):
        
        count = 0
        while(count < 20):
            try:
                
                self.event.wait()
                recvRec = self.byte_to_package.ReceiveRecorderData()
                if (not recvRec == 0):
                    self.SaveIQ(recvRec)

            except usb.core.USBError,e:
                print "  IQ2 NO DATA"
                time.sleep(1)
                count += 1
                
    def SaveIQ(self,recvRec):
        
        self.IQ2List = []
        
        block = IQ2Block(recvRec.IQDataAmp)
        self.IQ2List.append(block)

        head = IQ2UploadHeader(0x00, recvRec.LonLatAlti, recvRec.ParamNoUp)
        block = IQ2Block(recvRec.IQDataAmp)

        ##### ���iq2�ļ� ################

        count = (recvRec.SecondCount[0] << 24) + \
                (recvRec.SecondCount[1] << 16) + \
                (recvRec.SecondCount[2] << 8) + \
                (recvRec.SecondCount[3])

        Time = recvRec.Time

        Year = (Time.HighYear << 4) + Time.LowYear
        Month = Time.Month
        Day = Time.Day
        Hour = (Time.HighHour << 2) + Time.LowHour 
        Minute = Time.Minute
        Second = Time.Second
        ID = staticVar.getid()

        ###########将读取的UTC时间转换为本地时间############
        time_recv_utc = str(Year) + '-' + str(Month) + '-' + str(Day) + ' ' + str(Hour) + ':' + str(Minute) + ':' + str(Second)
        time_recv_utc_stamp = time.mktime(time.strptime(time_recv_utc,"%Y-%m-%d %H:%M:%S"))
        time_utc = datetime.datetime.utcfromtimestamp(time_recv_utc_stamp)
        time_local = time_utc + datetime.timedelta(hours = 16)


        Year = str(time_local)[0:4]
        Month = str(time_local)[5:7]
        Day = str(time_local)[8:10]
        Hour = str(time_local)[11:13]
        Minute = str(time_local)[14:16]
        Second = str(time_local)[17:19]
        ############################################

        if(not Year == 2016):
            curTime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            Year = curTime[0:4]
            Month = curTime[4:6]
            Day = curTime[6:8]
            Hour = curTime[8:10]
            Minute = curTime[10:12]
            Second = curTime[12:14]


        fileName = Year + "-" + Month + "-" + Day + \
                   "-" + Hour + "-" + Minute +  \
                   "-" + Second + '-' + str(count) + '-' +  str(ID) + \
                   '.iq2'

        print fileName
        self.count_iq2_file = self.count_iq2_file + 1
        # print self.count_iq2_file 
        
        ########### SaveToLocal(tdoa方式存本地)####################
#         fid = open(".\LocalData\\IQ2\\" + fileName,'wb')
#         d = dict(head = head, block = block)
#         pickle.dump(d, fid)
#         fid.close()
        
        
        ############ SaveToLocal(iq方式存本地)#####################
        fid = open(".\LocalData\\IQ2\\" + fileName,'wb')
        fid.write(bytearray(head))
        for block in self.IQ2List:
            fid.write(bytearray(block))
        fid.write(struct.pack("!B", 0x00))
        fid.close()
        
        del self.IQ2List

