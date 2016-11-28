# -*- coding: utf-8 -*- 
from __future__ import division 
import time
import datetime
import wx
import pyaudio
import numpy as np
import scipy.signal as signal
from math import sqrt,log10,atan
from src.CommonUse.staticVar import  staticVar
from src.Package.package import RecordStartSet,RecorderEndSet,FrameHeader,FrameTail
from src.Thread import thread_recv_recorder
from src.Spectrum.IQ2_Spectrum_test import DrawPanel,MenuSet
from src.Water.Pl_WaterFall import IQ2_Water
 
class dialog_recorder ( wx.Dialog ):
    def __init__(self,parent):
        wx.Dialog.__init__(self,parent,-1,u"录音回放",wx.DefaultPosition,wx.Size(408,400))
        
        ##############硬件通信###############
        self.id = staticVar.getid()
        self.lowid = self.id & 0x00FF
        self.highid = self.id >> 8
        self.tail = FrameTail(0,0,0xAA)
        self.outPoint = staticVar.outPoint
        ##################################
        self.wave2_head_flag = 1
        self.count_last = 0
        self.time_val_last = 0
        self.save_wave2_flg = 1
        self.file_path_last = u''
        self.choosefilemode = 2
        self.iq_file_flg = 1
#         self.drawFlag = 1

        ##################################
        
        self.parent = parent
        self.CreatePanel()
        self.Layout()
        
        
#         self.SetFont(wx.Font(10, wx.ROMAN, wx.NORMAL, wx.LIGHT, underline=False, faceName=u"微软雅黑",
#                                         encoding=wx.FONTENCODING_DEFAULT))
    def CreatePanel(self):

        self.m_gSizer = wx.GridSizer(1,1,0,0)
        self.m_notebook = wx.Notebook(self,wx.ID_ANY,wx.DefaultPosition,wx.DefaultSize)
        
        
        ################# 录音模式  #######################
        self.start_pnl = wx.Panel(self.m_notebook,-1)
        s_bSizer = wx.BoxSizer(wx.VERTICAL)
        
        s_bSizer.Add((10,10))
        s_bSizer.Add((10,10))
        s_bSizer.Add((10,10))
        s_gSizer = wx.GridSizer(3,3,0,0)
        
        self.txt_recvgain = wx.StaticText(self.start_pnl,wx.ID_ANY,u"  接收增益",wx.DefaultPosition,wx.DefaultSize)     
        self.slider_recvgain = wx.Slider(self.start_pnl,wx.ID_ANY,7,-1,73,pos=wx.DefaultPosition,size=(130,-1),style=wx.SL_HORIZONTAL|wx.SL_LABELS|wx.SL_SELRANGE)
        self.sta_txt_recvg = wx.StaticText(self.start_pnl,wx.ID_ANY,u"dB",wx.DefaultPosition,wx.DefaultSize)
        s_gSizer.Add(self.txt_recvgain,0,wx.EXPAND,5)
        s_gSizer.Add(self.slider_recvgain,0,wx.EXPAND,5)
        s_gSizer.Add(self.sta_txt_recvg,0,wx.EXPAND,5)
        
        self.txt_centr_freq = wx.StaticText(self.start_pnl,wx.ID_ANY,u"  中心频率",wx.DefaultPosition,wx.DefaultSize)
        self.txt_ctrl_freq = wx.TextCtrl( self.start_pnl,wx.ID_ANY,wx.EmptyString,wx.DefaultPosition,size=(130,-1))
        self.sta_txt_freq = wx.StaticText(self.start_pnl,wx.ID_ANY,u"MHz",wx.DefaultPosition,wx.DefaultSize)
        s_gSizer.Add(self.txt_centr_freq,0,wx.EXPAND,5)
        s_gSizer.Add(self.txt_ctrl_freq,0,wx.ALL,5)
        s_gSizer.Add(self.sta_txt_freq,0,wx.EXPAND,5)
        
        self.band_data = wx.StaticText(self.start_pnl,wx.ID_ANY,u"  IQ 带宽/数据率",wx.DefaultPosition,wx.DefaultSize)
        self.bw_list = [ u"5", u"2.5", u"1.25", u"0.625", u"0.125" ]
        self.band_data_choice = wx.Choice(self.start_pnl,wx.ID_ANY,wx.DefaultPosition,wx.Size(130,-1),self.bw_list)
        self.band_data_choice.SetSelection(0)
        self.band_data_txt = wx.StaticText(self.start_pnl,wx.ID_ANY,u"MHz",wx.DefaultPosition,wx.DefaultSize)
        s_gSizer.Add(self.band_data,0,wx.EXPAND,5)
        s_gSizer.Add(self.band_data_choice,0,wx.ALL,5)
        s_gSizer.Add(self.band_data_txt,0,wx.EXPAND,5)
        
        # self.dtime_txt = wx.StaticText(self.start_pnl,wx.ID_ANY,u'  延迟时间',wx.DefaultPosition,wx.DefaultSize)
        # self.dtime = wx.TextCtrl( self.start_pnl,wx.ID_ANY,wx.EmptyString,wx.DefaultPosition,size=(130,-1))
        # self.dtime_unit = wx.StaticText(self.start_pnl,wx.ID_ANY,u'S',wx.DefaultPosition,wx.DefaultSize)
        # s_gSizer.Add(self.dtime_txt,0,wx.EXPAND,5)
        # s_gSizer.Add(self.dtime,0,wx.ALL,5)
        # s_gSizer.Add(self.dtime_unit,0,wx.EXPAND,5)
        
        s_bSizer.Add(s_gSizer,0,wx.ALL,5)

        curTime = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        Year = int(curTime[0:4])
        Month = int(curTime[4:6])
        Day = int(curTime[6:8])
        Hour = int(curTime[8:10])
        Min = int(curTime[10:12]) 
        Sec = int(curTime[12:14])
         
        self.StartTimeYear = wx.ComboBox(self.start_pnl,-1,str(Year),choices=["2016","2017","2018","2019"])
        self.StartTimeMonth = wx.ComboBox(self.start_pnl, -1, str(Month),
                                          choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])
        self.StartTimeDay = wx.TextCtrl(self.start_pnl,-1,str(Day),size=(50, 25))
        self.StartTimeHour = wx.TextCtrl(self.start_pnl,-1,str(Hour),size=(50, 25))
        self.StartTimeMinute = wx.TextCtrl(self.start_pnl,-1,str(Min),size=(50, 25))
        self.StartTimeSecond = wx.TextCtrl(self.start_pnl,-1,str(Sec),size=(45, 25))
         
        self.txt_time = wx.StaticText(self.start_pnl,wx.ID_ANY,u"  起始时间（年-月-日-时-分-秒）",wx.DefaultPosition,wx.DefaultSize)
        s_bSizer.Add(self.txt_time,0,wx.EXPAND,5)
         
        time_sizer=wx.BoxSizer(wx.HORIZONTAL)
        time_sizer.Add(self.StartTimeYear,0,wx.LEFT,20)
        time_sizer.Add(wx.StaticText(self.start_pnl,-1,"-"),0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.ALIGN_BOTTOM,5)
        time_sizer.Add(self.StartTimeMonth,0,wx.EXPAND)
        time_sizer.Add(wx.StaticText(self.start_pnl,-1,"-"),0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.ALIGN_BOTTOM,5)
        time_sizer.Add(self.StartTimeDay,0,wx.EXPAND)
        time_sizer.Add(wx.StaticText(self.start_pnl,-1,"-"),0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.ALIGN_BOTTOM,5)
        time_sizer.Add(self.StartTimeHour,0,wx.EXPAND)
        time_sizer.Add(wx.StaticText(self.start_pnl,-1,"-"),0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.ALIGN_BOTTOM,5)
        time_sizer.Add(self.StartTimeMinute,0,wx.EXPAND)
        time_sizer.Add(wx.StaticText(self.start_pnl,-1,"-"),0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.ALIGN_BOTTOM,5)
        time_sizer.Add(self.StartTimeSecond,0,wx.EXPAND)
         
        s_bSizer.Add(time_sizer,0,wx.ALL,5)
        
        self.sta_btn = wx.Button(self.start_pnl,-1,u"启动",wx.DefaultPosition,wx.DefaultSize)
        self.end_btn = wx.Button(self.start_pnl,-1,u"结束",wx.DefaultPosition,wx.DefaultSize)
        
        btn_Sizer = wx.GridSizer(1,4,0,0)
        btn_Sizer.AddSpacer((0,0),1,wx.EXPAND,5)
        btn_Sizer.Add(self.sta_btn,0,wx.ALL,5)
        btn_Sizer.Add(self.end_btn,0,wx.ALL,5)
        s_bSizer.Add(btn_Sizer)
        
        c_Sizer = wx.GridSizer(1,5,0,0)
        self.count_iq2_txt = wx.StaticText(self.start_pnl,-1,u"已录音文件总数：")
        self.count_iq2 = wx.StaticText(self.start_pnl,-1,u"")
        c_Sizer.Add(self.count_iq2_txt,0,wx.ALL,5)
        c_Sizer.Add(self.count_iq2,0,wx.ALL,5)
        s_bSizer.Add(c_Sizer)
        
        self.start_pnl.SetSizer(s_bSizer)
    
        
        self.m_notebook.AddPage(self.start_pnl,u"录音模式",True)
        
        ############ 回放模式 ##############################
        self.playback_pnl = wx.Panel(self.m_notebook,-1)
        pb_bSizer = wx.BoxSizer(wx.VERTICAL)
        
        bSizer1 = wx.GridSizer(1,2,0,0)
        self.file_path = wx.TextCtrl(self.playback_pnl,-1,u"",wx.DefaultPosition,wx.Size(170,-1))
        self.chooseBtn = wx.Button(self.playback_pnl,-1,u"选择进行解调的文件")
        bSizer1.Add(self.chooseBtn,0,wx.ALL,5)
        bSizer1.Add(self.file_path,0,wx.ALL|wx.ALIGN_BOTTOM,5)
        pb_bSizer.Add(bSizer1,0,wx.ALL,5)
        
        self.show_mode = wx.StaticText(self.playback_pnl,-1,u" 显示方式：")
        self.spec_mode = wx.CheckBox(self.playback_pnl,-1,u'功率谱图，相位谱图，解调后归一化波形')
        self.water_mode = wx.CheckBox(self.playback_pnl,-1,u'瀑布图')

        show_bSizer = wx.GridSizer(2,2,0,0)
        show_bSizer.Add(self.show_mode,0,wx.ALL,5)
        show_bSizer.AddSpacer((10,10))
        show_bSizer.Add(self.spec_mode,0,wx.ALL,5)
        show_bSizer.Add(self.water_mode,0,wx.ALL,5)
        pb_bSizer.Add(show_bSizer,0,wx.ALL,5)
        
        h_bSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.am_fm_mode_txt = wx.StaticText(self.playback_pnl,-1,u" 解调方式：")
        am_fm_mode = [u"AM解调",u"FM解调"]
        self.am_fm_mode = wx.RadioBox(self.playback_pnl,wx.ID_ANY,u"",wx.DefaultPosition,wx.DefaultSize,am_fm_mode,1,wx.RA_SPECIFY_ROWS)
        self.am_fm_mode.SetSelection(0)
        self.showBtn = wx.Button(self.playback_pnl,-1,u"确定")
        h_bSizer.Add(self.am_fm_mode_txt,0,wx.ALL,5)
        h_bSizer.Add(self.am_fm_mode,0,wx.ALL,5)
#         h_bSizer.Add((10,10))
#         h_bSizer.Add((10,10))
        h_bSizer.Add(self.showBtn,0,wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_LEFT,5)
        pb_bSizer.Add(h_bSizer,0,wx.ALL,5)
                
        self.playback_pnl.SetSizer(pb_bSizer)
        self.m_notebook.AddPage(self.playback_pnl,u"回放模式",False)
        
        
        ############ 设置主Sizer ##############################
        self.m_gSizer.Add(self.m_notebook,0,wx.ALL,5)
        self.SetSizer(self.m_gSizer)
        self.Center(wx.BOTH)
        
        ############# 事件 ##########################################
        self.sta_btn.Bind(wx.EVT_BUTTON,self.startReClick)
        self.end_btn.Bind(wx.EVT_BUTTON,self.endReClick)
        self.chooseBtn.Bind(wx.EVT_BUTTON,self.chooseFileClick)
#         self.pl_chooseBtn.Bind(wx.EVT_BUTTON,self.pl_chooseFileClick)
#         self.playback_set_Btn.Bind(wx.EVT_BUTTON,self.setPlaybackClick)
#         self.playback_stop_Btn.Bind(wx.EVT_BUTTON,self.endPlayBackClick)
        self.showBtn.Bind(wx.EVT_BUTTON,self.showPlaybackClick)
        
    def startReClick(self,evt):
        
        gain = int(self.slider_recvgain.GetValue())
        centr_freq = float(self.txt_ctrl_freq.GetValue())
        bandwidth = int(self.band_data_choice.GetSelection())
        
        recordStart = RecordStartSet()
        recordStart.CommonHeader = FrameHeader(0x55,0x34,self.lowid,self.highid)
        recordStart.CommonTail = self.tail
        
        recordStart.RecvGain = gain + 2
        recordStart.FreqArray = self.FreqToByte(centr_freq)
        recordStart.BandWidth = bandwidth + 1
        recordStart.DataRate = bandwidth + 1
        
        Year = self.StartTimeYear.GetValue()
        Month = self.StartTimeMonth.GetValue()
        Day = self.StartTimeDay.GetValue()
        Hour = self.StartTimeHour.GetValue()
        Minute = self.StartTimeMinute.GetValue()
        Hour = self.StartTimeHour.GetValue()
        Sec = self.StartTimeSecond.GetValue()
        
        #########将读取的时间转换为UTC时间下发给硬件###########
        time_set = Year + '-' + Month + '-' + Day + ' ' + Hour + ':' + Minute+ ':' + Sec
        time_set_stamp = time.mktime(time.strptime(time_set,"%Y-%m-%d %H:%M:%S"))
        time_utc = datetime.datetime.utcfromtimestamp(time_set_stamp)
        ############################################
        
        Year_utc = int(str(time_utc)[0:4])
        Month_utc = int(str(time_utc)[5:7])
        Day_utc = int(str(time_utc)[8:10])
        Hour_utc = int(str(time_utc)[11:13])
        Minute_utc = int(str(time_utc)[14:16])
        Sec_utc = int(str(time_utc)[17:19])
        
        startTime = (Year_utc,Month_utc,Day_utc,Hour_utc,Minute_utc,Sec_utc)
        
        recordStart.HighYear = startTime[0] >> 4
        recordStart.LowYear = startTime[0] & 0xF
        recordStart.Month = startTime[1]
        recordStart.Day = startTime[2]
        recordStart.HighHour = startTime[3] >> 2
        recordStart.Minute = startTime[4]
        recordStart.LowHour = startTime[3] & 0x3
        recordStart.Second = startTime[5] 
        
        
        self.outPoint.write(bytearray(recordStart))
        

            

        thread = thread_recv_recorder.ReceiveRecorderDataThread(self.parent)
        thread.start()
        
        self.count_iq2.SetLabel(str(thread_recv_recorder.ReceiveRecorderDataThread(self.parent).count_iq2_file))
        print thread_recv_recorder.ReceiveRecorderDataThread(self.parent).count_iq2_file
        
    
    def endReClick(self,evt):
        gain = int(self.slider_recvgain.GetValue())
        
        recordEnd = RecorderEndSet()
        recordEnd.CommonHeader = FrameHeader(0x55,0x35,self.lowid,self.highid)
        recordEnd.CommonTail = self.tail
        recordEnd.RecvGain = gain + 2
        
        freq_s = self.parent.FreqMin
        freq_e = self.parent.FreqMax
        
        array = self.SweepSection(freq_s, freq_e)
        recordEnd.StartSectionNo = array[0]
        recordEnd.EndSectionNo = array[1]
        recordEnd.HighStartFreq = array[2]
        recordEnd.LowStartFreq = array[3]
        recordEnd.HighEndFreq = array[4]
        recordEnd.LowEndFreq = array[5]
        
        self.outPoint.write(bytearray(recordEnd))
        
        
    def chooseFileClick(self,evt):
        self.chooseFileDlg = wx.FileDialog(None,u"选择进行解调的文件：",wildcard="(*.iq2)|*.iq2|(*iq)|*.iq", style=wx.MULTIPLE)
        if self.chooseFileDlg.ShowModal() == wx.ID_OK:
            for item in self.chooseFileDlg.GetPaths():
                self.file_path.AppendText(item)
                self.file_path.AppendText(';')
                
                if item[-1] == '2':
                    self.choosefilemode = 2
                elif item[-1] == 'q':
                    self.choosefilemode = 1
                        
    def showPlaybackClick(self,evt):  
        self.Close()
        if self.choosefilemode == 2 :
            self.iq2_file()

            
        elif self.choosefilemode == 1:
            self.iq_file()

        

            
    def iq_file(self):
        


        for path in self.chooseFileDlg.GetPaths():
            iq_file = open(path,'rb').read()
            iq_gps_centr = []
            for line in iq_file:
                line = ord(line)
                iq_gps_centr.append(line)
            

            wave1_list = []
                    
            wave1_list.append('Start')
            wave1_list.append(iq_gps_centr[1])
            
            longtitude_int = iq_gps_centr[2]
            longtitude_frac_high = iq_gps_centr[3] << 8
            longtitude_frac_low = iq_gps_centr[4]
            longtitude_frac = longtitude_frac_high + longtitude_frac_low
            longtitude = longtitude_int + longtitude_frac / (10 ** len(str(longtitude_frac))) 
            longtitude = float('%.6f' % longtitude)
            wave1_list.append(longtitude)
            
            wave1_list.append(iq_gps_centr[5] >> 7)
            
            latitude_int = iq_gps_centr[5] & 0x7F
            latitude_frac_high = iq_gps_centr[6] << 8
            latitude_frac_low = iq_gps_centr[7]
            latitude_frac = latitude_frac_high + latitude_frac_low
            latitude = latitude_int + latitude_frac / (10 ** len(str(latitude_frac)))
            latitude = float('%.6f' % latitude)
            wave1_list.append(latitude)
            
            height_flag = iq_gps_centr[8] >> 7
            height_high = (iq_gps_centr[8] & 0x7F) << 8
            height_low = iq_gps_centr[9]
            height = height_high + height_low
            if height_flag == 1 :
                height = - height
            wave1_list.append(height)
            
            
            
            freq_centr_int_h = iq_gps_centr[10] << 6
            freq_centr_int_l = iq_gps_centr[11] & 0x3F
            freq_centr_frac_h = (iq_gps_centr[11] >> 6)<< 8
            freq_centr_frac_l = iq_gps_centr[12]
            freq_centr_int = freq_centr_int_h + freq_centr_int_l
            freq_centr_frac = freq_centr_frac_h + freq_centr_frac_l
            freq_centr = freq_centr_int + freq_centr_frac / (10 ** len(str(freq_centr_frac)))
            freq_centr = float('%.4f' % freq_centr)

            wave1_list.append(freq_centr)
            
            bandwidth = iq_gps_centr[13] >> 4
            if (bandwidth == 1) :
                bandwidth_rate = 5
                wave1_list.append(5)
                wave1_list.append(5)
            elif (bandwidth == 2):
                bandwidth_rate = 2.5
                wave1_list.append(2.5)
                wave1_list.append(2.5)
            elif (bandwidth == 3):
                bandwidth_rate = 1.25
                wave1_list.append(1.25)
                wave1_list.append(1.25)
            elif (bandwidth == 4):
                bandwidth_rate = 0.625
                wave1_list.append(0.625)
                wave1_list.append(0.625)
            elif (bandwidth == 5):
                bandwidth_rate = 0.125
                wave1_list.append(0.125)
                wave1_list.append(0.125)
            
            wave1_list.append(iq_gps_centr[14])
            wave1_list.append('')
            
            # print wave1_list
            # print len(wave1_list)
            a = path.index('IQ')
            filename = path[(a + 3) : -3]
            
            
            wave1_file = open(r'./LocalData/Wave2/' + filename  + '.wave2','w')
            for i in range(len(wave1_list)):
                wave1_file.write(str(wave1_list[i]) + '\n')
            wave1_file.close() 
            
          
            N = iq_gps_centr[14]
            
            for j in range(N):
                IData = []
                QData = []
                for i in range(2000):
                    HighI1 = ((iq_gps_centr[6001 * (j + 1) - 5985 + i * 3]) >> 4) << 8
                    LowI1 = iq_gps_centr[6001 * (j + 1) - 5984 + i * 3]
                    if (HighI1 >= 2048):
                        I1 = -(2 ** 12 - HighI1 - LowI1)
                    else :
                        I1 = (HighI1 + LowI1)
                    IData.append(I1)
            
                    HighQ1 = ((iq_gps_centr[6001 * (j + 1) - 5985 + i * 3]) & 0x0F) << 8
                    LowQ1 = iq_gps_centr[6001 * (j + 1) - 5983 + i * 3]
                    if (HighQ1 >= 2048):
                        Q1 = -(2 ** 12 - HighQ1 - LowQ1)
                    else :
                        Q1 = (HighQ1 + LowQ1)
                    QData.append(Q1)

            
                IQData = []
                for i in range(2000):
                    data1 = complex(IData[i]/2047,-QData[i]/2047)
                    IQData.append(data1)
                for i in range(48):
                    IQData.append(0)
                    
                n = 2048 
                y = IQData[:]
                w = signal.blackmanharris(n) 
                y = y*w
                y_fft = np.fft.fft(y)
                y_fftshift = np.fft.fftshift(y_fft)
                yk = (1 / sqrt(sum(abs(w * w))/ 2048)) * y_fftshift 
                pk = [] ##### pk:相对平均功率谱
                fk = [] ##### fk:对应的实际频率值
                angle = [] #### angle:对应的相位谱
        
                
                for k in range(-1024,1024):
                    fk.append(freq_centr + k * bandwidth_rate / 2048)
                    
                
                for i in range(len(yk)):
                    pk.append(-57.206 + 20 * log10(abs(yk[i])))
                    
                    if (yk[i].real == 0)and(yk[i].imag > 0) :
                        angle.append(90)
                    elif (yk[i].real == 0)and(yk[i].imag < 0) :
                        angle.append(-90)
                    elif (yk[i].real == 0)and(yk[i].imag == 0) :
                        angle.append(0)
                    else :
                        angle.append(57.3 * atan(yk[i].imag / yk[i].real))
                    angle[i] = '%.2f' % angle[i]
                
                if self.am_fm_mode.GetSelection() == 0 : ###am
                    data = self.am_mode(IData, QData)
                elif(self.am_fm_mode.GetSelection() == 1 ): ###fm
                    data = self.fm_mode(IData, QData)  #### data:解调后对应的值
                
                

                if self.spec_mode.GetValue(): 
                    if(self.parent.IQ2SpecFrame_test == None):    
                        self.parent.IQ2SpecFrame_test = DrawPanel(self.parent,fk,pk,angle,data,self.chooseFileDlg.GetPaths(),self.am_fm_mode.GetSelection(),self.choosefilemode)
                        self.parent.IQ2SpecFrame_test.Activate()
                    
                        
                    self.parent.IQ2SpecFrame_test.spec.set_txt(filename, longtitude, latitude, height, freq_centr, bandwidth_rate)
#                     self.parent.IQ2SpecFrame_test.spec.setLbl_draw(fk,pk)
                    self.parent.IQ2SpecFrame_test.spec.filePath(self.chooseFileDlg.GetPaths())
                    self.parent.IQ2SpecFrame_test.wave.filePath(self.chooseFileDlg.GetPaths())
                    self.parent.IQ2SpecFrame_test.wave.am_fm_mode_refresh(self.am_fm_mode.GetSelection())

                    
                if self.water_mode.GetValue():
                    if(self.parent.WaterFrame_pl == None):
                        self.parent.WaterFrame_pl = IQ2_Water(self.parent,fk,pk,self.chooseFileDlg.GetPaths(),self.choosefilemode)
                        self.parent.WaterFrame_pl.Activate()
                    self.parent.WaterFrame_pl.set_txt(filename, longtitude, latitude, height, freq_centr, bandwidth_rate)
                    self.parent.WaterFrame_pl.fileDraw(self.chooseFileDlg.GetPaths())
                    self.parent.WaterFrame_pl.setLbl_draw(fk,pk)
            
                
                wave1_file = open(r'./LocalData/Wave2/' + filename + '.wave2','a')
                for i in range(2000):
                    wave1_file.write(str('%.4f' % data[i]) + '\n')
                wave1_file.close() 
            
             
            wave1_file = open(r'./LocalData/Wave2/' + filename + '.wave2','a')
            wave1_file.write('end')
            wave1_file.close()

                 
                    
        
    def iq2_file(self):
        
        if not self.chooseFileDlg.GetPaths() == self.file_path_last:
            self.save_wave2_flg = 1
            self.wave2_head_flag = 1
            self.wave2_file_path = None
#             self.data = None
            self.data_last = None
            self.filename_last = None
        
#         self.Close()

        
        if (not self.file_path == None):
  
            
            if len(self.chooseFileDlg.GetPaths()) == 1:

                for one_iq2_file_path in self.chooseFileDlg.GetPaths():
                    iq2_gps_centr,IData,QData,freq_centr,bandwidth_rate = self.ParseIQ2(one_iq2_file_path)
                    pk,fk,angle = self.fft_iq2(IData,QData,freq_centr,bandwidth_rate) 

#                     print '----'
                    
                    if self.am_fm_mode.GetSelection() == 0 : ###am
                        data = self.am_mode(IData, QData)
                    elif(self.am_fm_mode.GetSelection() == 1 ): ###fm
                        data = self.fm_mode(IData, QData)
                        
                    self.lon,self.lat,self.hei,filename = self.save_iq2_to_wave1(one_iq2_file_path,iq2_gps_centr,freq_centr,data)
                    
                    if self.spec_mode.GetValue():    
                        if(self.parent.IQ2SpecFrame_test == None):
                            self.parent.IQ2SpecFrame_test = DrawPanel(self.parent,fk,pk,angle,data,self.chooseFileDlg.GetPaths(),self.am_fm_mode.GetSelection(),self.choosefilemode)
                            self.parent.IQ2SpecFrame_test.Activate()
    
                        self.parent.IQ2SpecFrame_test.spec.set_txt(filename, self.lon, self.lat, self.hei, freq_centr, bandwidth_rate)
#                         self.parent.IQ2SpecFrame_test.spec.setLbl_draw(fk,pk)
                        self.parent.IQ2SpecFrame_test.spec.filePath(self.chooseFileDlg.GetPaths())
                        self.parent.IQ2SpecFrame_test.wave.filePath(self.chooseFileDlg.GetPaths())
                        self.parent.IQ2SpecFrame_test.wave.am_fm_mode_refresh(self.am_fm_mode.GetSelection())
#                         self.parent.IQ2SpecFrame_test.wave.setLbl_draw(data)
                        
                    if self.water_mode.GetValue():
                        if(self.parent.WaterFrame_pl == None):
                            self.parent.WaterFrame_pl = IQ2_Water(self.parent,fk,pk,self.chooseFileDlg.GetPaths(),self.choosefilemode)
                            self.parent.WaterFrame_pl.Activate()
                        self.parent.WaterFrame_pl.set_txt(filename, self.lon, self.lat, self.hei, freq_centr, bandwidth_rate)
                        self.parent.WaterFrame_pl.fileDraw(self.chooseFileDlg.GetPaths())
                        self.parent.WaterFrame_pl.setLbl_draw(fk,pk)




            elif len(self.chooseFileDlg.GetPaths()) > 1:

                for one_iq2_file_path in self.chooseFileDlg.GetPaths():
                     
                    iq2_gps_centr,IData,QData,freq_centr,bandwidth_rate = self.ParseIQ2(one_iq2_file_path)
                    pk,fk,angle = self.fft_iq2(IData,QData,freq_centr,bandwidth_rate)                     
    
                    
                    if self.am_fm_mode.GetSelection() == 0 : ###am
                        data = self.am_mode(IData, QData)
                    elif(self.am_fm_mode.GetSelection() == 1 ): ###fm
                        data = self.fm_mode(IData, QData)
                    
                    if self.save_wave2_flg:
                        self.lon,self.lat,self.hei,filename = self.save_iq2_to_wave1(one_iq2_file_path,iq2_gps_centr,freq_centr,data)
                    
                    if self.spec_mode.GetValue(): 
                        if(self.parent.IQ2SpecFrame_test == None):    
                            self.parent.IQ2SpecFrame_test = DrawPanel(self.parent,fk,pk,angle,data,self.chooseFileDlg.GetPaths(),self.am_fm_mode.GetSelection(),self.choosefilemode)
                            self.parent.IQ2SpecFrame_test.Activate()
                            
                        self.parent.IQ2SpecFrame_test.spec.set_txt(self.filename_last, self.lon, self.lat, self.hei, freq_centr, bandwidth_rate)
#                         self.parent.IQ2SpecFrame_test.spec.setLbl_draw(fk,pk)
                        self.parent.IQ2SpecFrame_test.spec.filePath(self.chooseFileDlg.GetPaths())
                        self.parent.IQ2SpecFrame_test.wave.filePath(self.chooseFileDlg.GetPaths())
                        self.parent.IQ2SpecFrame_test.wave.am_fm_mode_refresh(self.am_fm_mode.GetSelection())
                        
                    if self.water_mode.GetValue():
                        if(self.parent.WaterFrame_pl == None):
                            self.parent.WaterFrame_pl = IQ2_Water(self.parent,fk,pk,self.chooseFileDlg.GetPaths(),self.choosefilemode)
                            self.parent.WaterFrame_pl.Activate()
                        self.parent.WaterFrame_pl.set_txt(filename, self.lon, self.lat, self.hei, freq_centr, bandwidth_rate)
                        self.parent.WaterFrame_pl.fileDraw(self.chooseFileDlg.GetPaths())
                        self.parent.WaterFrame_pl.setLbl_draw(fk,pk)
                        
                    
                    

                                      
                            
                if self.save_wave2_flg:
                    a = open(self.wave2_file_path,'a')
                    for i in range(len(self.data_last)):
                        a.write(str(self.data_last[i]) + '\n')
                    a.write('end')
                    a.close()
                    self.save_wave2_flg = 0
            
                
        self.file_path_last = self.chooseFileDlg.GetPaths()

                            
        
    def save_iq2_to_wave1(self,one_iq2_file_path,iq2_gps_centr,freq_centr,data):
        wave1_list = []
        
        wave1_list.append('Start')
        wave1_list.append(iq2_gps_centr[1])
        
        longtitude_int = iq2_gps_centr[2]
        longtitude_frac_high = iq2_gps_centr[3] << 8
        longtitude_frac_low = iq2_gps_centr[4]
        longtitude_frac = longtitude_frac_high + longtitude_frac_low
        longtitude = longtitude_int + longtitude_frac / (10 ** len(str(longtitude_frac))) 
        longtitude = float('%.6f' % longtitude)
        wave1_list.append(longtitude)
        
        wave1_list.append(iq2_gps_centr[5] >> 7)
        
        latitude_int = iq2_gps_centr[5] & 0x7F
        latitude_frac_high = iq2_gps_centr[6] << 8
        latitude_frac_low = iq2_gps_centr[7]
        latitude_frac = latitude_frac_high + latitude_frac_low
        latitude = latitude_int + latitude_frac / (10 ** len(str(latitude_frac)))
        latitude = float('%.6f' % latitude)
        wave1_list.append(latitude)
        
        height_flag = iq2_gps_centr[8] >> 7
        height_high = (iq2_gps_centr[8] & 0x7F) << 8
        height_low = iq2_gps_centr[9]
        height = height_high + height_low
        if height_flag == 1 :
            height = - height
        wave1_list.append(height)
        
        wave1_list.append(freq_centr)
        
        bandwidth = iq2_gps_centr[13] >> 4
        if (bandwidth == 1) :
            wave1_list.append(5)
            wave1_list.append(5)
            time_count = 20000 #####硬件时间计数块
            time_count_d = 100 #####硬件时间计数块允许的误差
        elif (bandwidth == 2):
            wave1_list.append(2.5)
            wave1_list.append(2.5)
            time_count = 40000
            time_count_d = 200
        elif (bandwidth == 3):
            wave1_list.append(1.25)
            wave1_list.append(1.25)
            time_count = 80000
            time_count_d = 400
        elif (bandwidth == 4):
            wave1_list.append(0.625)
            wave1_list.append(0.625)
            time_count = 160000
            time_count_d = 800
        elif (bandwidth == 5):
            wave1_list.append(0.125)
            wave1_list.append(0.125)
            time_count = 800000
            time_count_d = 4000
        
        wave1_list.append('')
        wave1_list.append('')

        for i in range(len(data)):
            data[i] = '%.4f' % data[i]
            data[i] = float(data[i])        
            wave1_list.append(data[i])
        
        wave1_list.append('end')
        # print wave1_list,'-----',len(wave1_list)
        
        path = one_iq2_file_path
        if path[-1] == '2':
            a = path.index('IQ2')
            filename = path[(a + 4) : -4]
        elif path[-1] == 'q':
            a = path.index('IQ')
            filename = path[(a + 3) : -3]
        
        wave1_file = open(r'./LocalData/Wave1/' + filename + '.wave1','w')
        for i in range(len(wave1_list)):
            wave1_file.write(str(wave1_list[i]) + '\n')
        wave1_file.close()     
        
        count = int(filename[20 : -3])
        
        minute = filename[14:16]
        sec = filename[17:19]
        time_val = int(minute + sec)
        
        ############# 判断计数值是否连续 #################
        if cmp(count, self.count_last) == -1 :
            d = self.count_last - count
            if cmp(d, time_count) == -1:
                if time_count - d < time_count_d :
                    self.count_flg = 1
                else:
                    self.count_flg = 0
            elif cmp(d, time_count) == 1:
                if d - time_count < time_count_d :
                    self.count_flg = 1
                else :
                    self.count_flg = 0
            elif cmp(d, time_count)==0 :
                self.count_flg = 1
        elif cmp(count, self.count_last) == 1 :
            d = count - self.count_last
            if cmp(d, time_count) == -1:
                if time_count - d < time_count_d :
                    self.count_flg = 1
                else :
                    self.count_flg = 0
            elif cmp(d, time_count) == 1:
                if d - time_count < time_count_d :
                    self.count_flg = 1
                else :
                    self.count_flg = 0
            elif cmp(d, time_count)==0 :
                self.count_flg = 1
        elif cmp(count, self.count_last) == 0:
            self.count_flg = 0
        
        ############# 判断时间是否连续 #################
        if cmp(time_val,self.time_val_last) == -1 :
            if ((50000000 - time_count - count)< time_count_d) and (self.count_last < time_count_d):
                self.time_flg = 1
            elif (count < (50000000 - time_count_d)) and (self.count_last < time_count + time_count_d):
                self.time_flg = 1
            else :
                self.time_flg = 0
        
        elif cmp(time_val,self.time_val_last) == 1 :
            if ((50000000 - time_count - self.count_last)< time_count_d) and (count < time_count_d):
                self.time_flg = 1
            elif (self.count_last < (50000000 - time_count_d)) and (count < time_count + time_count_d):
                self.time_flg = 1
            else :
                self.time_flg = 0
        elif cmp(time_val,self.time_val_last) == 0 :
            self.time_flg = 1        
        
        ##########################################
        head = []
        for i in range(11):
            head.append(wave1_list[i])

        #########################################

        if self.time_flg and self.count_flg :
            if self.wave2_head_flag == 1 :
                if (self.filename_last == None) :
                    self.filename_last = filename
#                 if (self.data_last == None):
#                     self.data_last = data
                    
                wave2_file = open(r'./LocalData/Wave2/' + self.filename_last + '.wave2', 'w')
                for i in range(len(self.head_last)):
                    wave2_file.write(str(self.head_last[i]) + '\n')
                self.wave2_file_path = r'./LocalData/Wave2/' + self.filename_last + '.wave2'
                wave2_file.close()
                self.wave2_head_flag = 0
            
            if not (self.data_last == None):
                
                self.wave2_file = open(self.wave2_file_path,'a')
                self.save_wave1_to_wave2(self.wave2_file, self.data_last)
        
        #########################################
        
        self.filename_last = filename
        self.head_last = head
        self.data_last = data
        self.count_last = count 
        self.time_val_last = time_val   
        
        return longtitude,latitude,height,filename

                
    def save_wave1_to_wave2(self,wave2_file,data):
                
        for i in range(2000):
            data[i] = '%.4f' % data[i]
            data[i] = float(data[i]) 
            wave2_file.write(str(data[i]) + '\n')  
        wave2_file.close()  

    
    def ParseIQ2(self,iq2_file_path):
        iq2_file = open(iq2_file_path, 'rb').read()
        iq2_gps_centr = []
        for line in iq2_file:
            i = ord(line)
            iq2_gps_centr.append(i)
        
        
        ############## 取出中心频率#################### 
        freq_centr_int_h = iq2_gps_centr[10] << 6
        freq_centr_int_l = iq2_gps_centr[11] & 0x3F
        freq_centr_frac_h = (iq2_gps_centr[11] >> 6)<< 8
        freq_centr_frac_l = iq2_gps_centr[12]
        freq_centr_int = freq_centr_int_h + freq_centr_int_l
        freq_centr_frac = freq_centr_frac_h + freq_centr_frac_l
        freq_centr = freq_centr_int + freq_centr_frac / (10 ** len(str(freq_centr_frac)))
        freq_centr = float('%.4f' % freq_centr)
        
        ############## 取出数据率 ####################
        bw_byte = iq2_gps_centr[13] >> 4
        if bw_byte == 1:
            bandwidth_rate = 5
        elif bw_byte == 2 :
            bandwidth_rate = 2.5
        elif bw_byte == 3:
            bandwidth_rate = 1.25
        elif bw_byte == 4:
            bandwidth_rate = 0.625
        elif bw_byte == 5 :
            bandwidth_rate = 0.125

        ############## 取出IQ信号 ####################    
        IData = []
        QData = []
        for i in range(2000):
            if ((18 + i * 3) < (len(iq2_gps_centr) - 1)):
                HighI1 = ((iq2_gps_centr[16 + i * 3]) >> 4) << 8
                LowI1 = iq2_gps_centr[17 + i * 3]
                if (HighI1 >= 2048):
                    I1 = -(2 ** 12 - HighI1 - LowI1)
                else:
                    I1 = (HighI1 + LowI1)
                IData.append(I1)
                
                HighQ1 = ((iq2_gps_centr[16 + i * 3]) & 0x0F) << 8
                LowQ1 = iq2_gps_centr[18 + i * 3]
                if (HighQ1 >= 2048):
                    Q1 = -(2 ** 12 - HighQ1 - LowQ1)
                else:
                    Q1 = (HighQ1 + LowQ1)
                QData.append(Q1)
                
        return iq2_gps_centr,IData,QData,freq_centr,bandwidth_rate
    
        
    def fft_iq2(self,IData,QData,freq_centr,bandwidth_rate):
        ############### 进行加窗FFT变换 #############################
        IQData = []
        for i in range(2000):
            data = complex(IData[i]/2047,-QData[i]/2047)
            IQData.append(data)
        for i in range(48):
            IQData.append(0)
            
        n = 2048 
        y = IQData[:]
        w = signal.blackmanharris(n) 
        y = y*w
        y_fft = np.fft.fft(y)
        y_fftshift = np.fft.fftshift(y_fft)
        yk = (1 / sqrt(sum(abs(w * w))/ 2048)) * y_fftshift 
        pk = [] ##### pk:相对平均功率谱
        fk = [] ##### fk:对应的实际频率值
        angle = [] #### angle:对应的相位谱

        
        for k in range(-1024,1024):
            fk.append(freq_centr + k * bandwidth_rate / 2048)
            
        
        for i in range(len(yk)):
            pk.append(-57.206 + 20 * log10(abs(yk[i])))
            
            if (yk[i].real == 0)and(yk[i].imag > 0) :
                angle.append(90)
            elif (yk[i].real == 0)and(yk[i].imag < 0) :
                angle.append(-90)
            elif (yk[i].real == 0)and(yk[i].imag == 0) :
                angle.append(0)
            else :
                angle.append(57.3 * atan(yk[i].imag / yk[i].real))
            angle[i] = '%.2f' % angle[i]
        
        return pk,fk,angle

    
    def am_mode(self,sigI,sigQ):  ####before
        sigI = [i * i for i in sigI]
        sigQ = [j * j for j in sigQ]
        mt1 = [sqrt(i + j) for i,j in zip(sigI,sigQ)]
        mean = sum(mt1) / len(mt1)
        data = [(i - mean) for i in mt1]
        data = data[0:len(data):1]
        abs_data=[abs(i) for i in data]
        data_max=max(abs_data)
        data=[float(i*1.25)/data_max for i in data]
        return data
    
    def fm_mode(self,sigI,sigQ):
        data = []
        for i in range(1,2000):
            data.append(sigI[i-1] * sigQ[i] - sigQ[i-1]*sigI[i])
        data.append(0)
        sum = 0
        for i in range(2000):
            sum += data[i]
        mean = sum/2000
        for i in range(2000):
            data[i]=data[i]-mean
        abs_data = [abs(i) for i in data]
        data_max = max(abs_data)
        data = [float(i) / data_max for i in data]
        return data
    

    def FreqToByte(self,freq):
        freqInt = int(freq)
        freqFloat = freq - freqInt
        freqF = int(freqFloat * 2 ** 10)
        highFreqInt = freqInt >> 6
        lowFreqInt = freqInt & 0x003F
        highFreqFrac = freqF >> 8
        lowFreqFrac = freqF & 0x0FF
        return (highFreqInt,highFreqFrac,lowFreqInt,lowFreqFrac)


    def SweepSection(self,freqStart,freqEnd):
        startK = (freqStart - 70) // 25
        endK = (freqEnd - 70) // 25
        startNum = int(float(freqStart - (startK * 25 + 70)) * 1024 // 25)
        endNum = int(float(freqEnd - (endK * 25 + 70)) * 1024 // 25)
        startKth = startK + 1
        endKth = endK + 1 
        if ((freqEnd - 70) % 25 == 0):
            endKth = endK 
            endNum = 1023
        startf_h = startNum >> 8
        startf_l = startNum & 0x0FF
        endf_h = endNum >> 8
        endf_l = endNum & 0x0FF
        return (startKth, endKth, startf_h, startf_l, endf_h, endf_l)      
    
      
