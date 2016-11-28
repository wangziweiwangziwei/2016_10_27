# -*- coding: utf-8 -*- 
from __future__ import division 
import wx
import time
import wx.aui 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from numpy import array, linspace,sin,cos,pi,short
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas 
from matplotlib.cm import jet 
from math import log10,sqrt,log10,atan
import scipy.signal as signal
import pyaudio
from src.Water.WaterFall import Water
from threading import Thread


class DrawPanel(wx.aui.AuiMDIChildFrame):
    def __init__(self,parent,fk,pk,angle,data,filePathList,am_fm_mode,file_mode):
        wx.aui.AuiMDIChildFrame.__init__(self,parent,-1,title=u"解调回放信号             ")
        self.parent=parent
       
        main_sp = wx.SplitterWindow(self,style=wx.SP_3D)
    
        self.menu = MenuSet(main_sp)
        draw_sp = wx.SplitterWindow(main_sp,style=wx.SP_3D)
        main_sp.SplitVertically(self.menu,draw_sp)
        main_sp.SetSashGravity(0.2)
         
        self.spec = IQ2_Spec(draw_sp,fk,pk,angle,filePathList,file_mode)
        self.wave = IQ2_Wave(draw_sp,data,filePathList,am_fm_mode)
        draw_sp.SplitHorizontally(self.spec,self.wave)
        draw_sp.SetSashGravity(0.56)
        
        
        
        #############以下是一个菜单 上下左右四个图的分割
#         left_sp = wx.SplitterWindow(main_sp)
#         self.menu = MenuSet(left_sp)
#         draw_sp = wx.SplitterWindow(left_sp,style=wx.SP_3D)
#         left_sp.SplitVertically(self.menu,draw_sp)
#         left_sp.SetSashGravity(0.3)
#  
#         self.sp1 = IQ2_Spec(draw_sp,fk,pk)
#         self.sp3 = IQ2_Wave(draw_sp,data)
#  
#         draw_sp.SplitHorizontally(self.sp1,self.sp3)
#         draw_sp.SetSashGravity(0.5)
#  
#           
#         right_sp = wx.SplitterWindow(main_sp,style=wx.SP_3D)
#         self.sp2 = IQ2_Water(right_sp,fk,pk)
#         self.sp4 = IQ2_Phase(right_sp,fk,angle) 
#         right_sp.SplitHorizontally(self.sp2,self.sp4)
#         right_sp.SetSashGravity(0.5)
#  
#          
#         main_sp.SplitVertically(left_sp,right_sp)
#         main_sp.SetSashGravity(0.6)

        ######################################### 

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(main_sp,1,wx.EXPAND|wx.ALL,5)
        self.SetSizer(sizer)
        self.Layout()
        
        self.Bind(wx.EVT_WINDOW_DESTROY,self.OnClose)
    
    
    def OnClose(self,event):
        self.parent.IQ2SpecFrame_test = None
        self.Close()    

class MenuSet(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
#         self.parent = parent
#         self.fk = fk
#         self.pk = pk
#         self.angle = angle
#         self.data = data

        pb_bSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.pl_chooseBtn = wx.Button(self,-1,u"选择进行回放的文件")
        
        self.pl_chooseFile = wx.TextCtrl(self,-1,u"")
#         Sizer1 = wx.BoxSizer(wx.HORIZONTAL)
#         Sizer1.Add(self.pl_chooseBtn,0,wx.ALL,5)
#         Sizer1.Add(self.drawBox,0,wx.ALL,5)
        pb_bSizer.Add(self.pl_chooseBtn,0,wx.ALL,5)
        pb_bSizer.Add(self.pl_chooseFile,0,wx.ALL|wx.EXPAND,5)
        pb_bSizer.Add((10,10))
        pb_bSizer.Add(wx.StaticLine(self),0,wx.EXPAND,5)
        
        self.filter_txt = wx.StaticText(self,-1,u"  设置音频低通滤波器参数：")
        pb_bSizer.Add(self.filter_txt,0,wx.ALL,5)
         
         
        self.pass_sideband_txt = wx.StaticText(self,-1,u"    通带边频")
        self.pass_sideband_f1 = wx.TextCtrl(self,-1,wx.EmptyString,wx.DefaultPosition,size=(40,-1))
        self.Hz_txt1 = wx.StaticText(self,-1,u"MHz")
        self.stop_sideband_txt = wx.StaticText(self,-1,u"    阻带边频")
        self.stop_sideband_f2 = wx.TextCtrl(self,-1,wx.EmptyString,wx.DefaultPosition,size=(40,-1))
        self.Hz_txt2 = wx.StaticText(self,-1,u"MHz")
        self.stop_att_txt = wx.StaticText(self,-1,u"    带外抑制")
        self.stop_att_A = wx.TextCtrl(self,-1,wx.EmptyString,wx.DefaultPosition,size=(40,-1))
        self.dB_txt = wx.StaticText(self,-1,u"dB")
 
        self.extract_txt = wx.StaticText(self,-1,u"    抽取倍率")
        self.extract_N = wx.TextCtrl(self,-1,wx.EmptyString,wx.DefaultPosition,size=(40,-1))
        self.extract_range = wx.StaticText(self,-1,u"(1-60)")
 
        f_gSizer1 = wx.GridSizer(5,3,0,0)
        f_gSizer1.Add(self.pass_sideband_txt,0,wx.EXPAND,5)
        f_gSizer1.Add(self.pass_sideband_f1,0,wx.ALL,5)
        f_gSizer1.Add(self.Hz_txt1,0,wx.EXPAND,5)
        
        f_gSizer1.Add(self.stop_sideband_txt,0,wx.EXPAND,5)
        f_gSizer1.Add(self.stop_sideband_f2,0,wx.ALL,5)
        f_gSizer1.Add(self.Hz_txt2,0,wx.EXPAND,5)
         
        f_gSizer1.Add(self.stop_att_txt,0,wx.EXPAND,5)
        f_gSizer1.Add(self.stop_att_A,0,wx.ALL,5)
        f_gSizer1.Add(self.dB_txt,0,wx.EXPAND,5)
        
        f_gSizer1.Add(self.extract_txt,0,wx.EXPAND,5)
        f_gSizer1.Add(self.extract_N,0,wx.ALL,5)
        f_gSizer1.Add(self.extract_range,0,wx.EXPAND,5)
        
        
        self.pl_txt = wx.StaticText(self,-1,u" 回放方式：")
        pl_mode = [u"声音回放"]
        self.pl_mode = wx.RadioBox(self,wx.ID_ANY,u"",wx.DefaultPosition,wx.DefaultSize,pl_mode,1,wx.RA_SPECIFY_ROWS)
        self.pl_mode.SetSelection(0)
        f_gSizer1.Add(self.pl_txt,0,wx.EXPAND,5)
        f_gSizer1.Add(self.pl_mode,0,wx.EXPAND,5)
        
        self.playback_set_Btn = wx.Button(self,-1,u"设置")
        self.playback_stop_Btn = wx.Button(self,-1,u"停止")
        f_gSizer2 = wx.GridSizer(1,2,0,0)
        f_gSizer2.Add(self.playback_set_Btn,0,wx.EXPAND,5)
        f_gSizer2.Add(self.playback_stop_Btn,0,wx.EXPAND,5)
        
        
        pb_bSizer.Add(f_gSizer1,0,wx.ALL,5)
        pb_bSizer.Add(f_gSizer2,0,wx.ALL,5)
        self.SetSizer(pb_bSizer)
        self.Layout()
        self.Centre(wx.BOTH)
        


        self.pl_chooseBtn.Bind(wx.EVT_BUTTON,self.pl_chooseFileClick)
        self.playback_set_Btn.Bind(wx.EVT_BUTTON,self.setPlaybackClick)
        self.playback_stop_Btn.Bind(wx.EVT_BUTTON,self.endPlayBackClick)
        
        
    def pl_chooseFileClick(self,evt):
        self.pl_chooseFileDlg = wx.FileDialog(None,u"选择进行回放的文件：",wildcard='*.wave2',style=wx.MULTIPLE)
        if self.pl_chooseFileDlg.ShowModal() == wx.ID_OK:
            for item in self.pl_chooseFileDlg.GetPaths():
                self.pl_chooseFile.AppendText(item)
                self.pl_chooseFile.AppendText(';')

        
    def setPlaybackClick(self,evt):
        f1 = float(self.pass_sideband_f1.GetValue())
        f2 = float(self.stop_sideband_f2.GetValue())
        A = float(self.stop_att_A.GetValue())
        
        
        order = int(log10(10**(A/10)-1)/(2*log10(f2/f1))) + 1 ####滤波器阶数向上取整
        rate_extr = int(self.extract_N.GetValue())
    

        for one_wave2_file_path in self.pl_chooseFileDlg.GetPaths(): 
            wave2_file = open(one_wave2_file_path, 'rb').readlines()
            sig_wave2 = []
            for line in wave2_file[11:-1]:
                sig_wave2.append(float(line.strip('\r\n')))
    
            bandwidth_rate = int(wave2_file[8])
            bw_3dB = f1 / (bandwidth_rate/2)

            b,a = signal.butter(order, bw_3dB, 'low')
            sig_filter = signal.filtfilt(b,a,sig_wave2)
            
            sig_extr = []
            if not rate_extr == 1:
                for i in range(len(sig_filter)//rate_extr):
                    sig_extr.append(sig_filter[i + rate_extr])
            else :
                sig_extr = sig_filter
                
            sig_fixed = []
            for i in range(len(sig_extr)):
                sig_fixed.append(int((2**15-1)*sig_extr[i]/max(sig_extr)))
                        
            self.OnSound(sig_fixed)
               
    def OnSound(self,sig):
        am_data = array(sig)
        wave_data=am_data.astype(short)
        data=wave_data.tostring()
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format = self.p.get_format_from_width(2),channels =2 ,rate = 40000,output = True)
        
        self.stream.write(data)
#         stream.close()
#         p.terminate()  
        
    def endPlayBackClick(self,evt):
        self.stream.close()
        self.p.terminate()
        
   
   

class IQ2_Spec(wx.Panel):
    def __init__(self,parent,fk,pk,angle,filePathList,file_mode):
        wx.Panel.__init__(self,parent)
        self.parent = parent
        self.fk = fk
        self.pk = pk
        self.angle = angle
        self.filePathList = filePathList
        self.file_mode = file_mode
        self.drawFlg = 1
        self.phaseFlg = 1
        self.CreatePanel()
        
        self.stayAveCount = 0
        
        self.pk_max = []
        self.pk_min = []
        self.pk_ave = []
        
        
                
    def CreatePanel(self):
        self.Figure = matplotlib.figure.Figure()
        self.axes=self.Figure.add_axes([0.1,0.1,0.8,0.8])
        self.FigureCanvas = FigureCanvas(self,-1,self.Figure)
        self.ID = wx.StaticText(self,-1,u'终端ID号')
        self.time_txt = wx.StaticText(self,-1,u'时间')
        self.lon = wx.StaticText(self,-1,u'经-纬-高')
        self.rbw = wx.StaticText(self,-1,u'RBW、VBW')
        self.centrFreq = wx.StaticText(self,-1,u"中心频率")
        self.rate = wx.StaticText(self,-1,u'采样率')
        self.zaibo = wx.StaticText(self,-1,u'载波频率')
        self.band = wx.StaticText(self,-1,u'带宽')
        self.xinzaobi = wx.StaticText(self,-1,u'信噪比')
        
        self.specBtn = wx.Button(self,-1,u'功率谱图')
        self.phaseBtn = wx.Button(self,-1,u'相位谱图')
        self.showList = [u"瞬时功率谱",u"最大保持",u"最小保持",u"迹线平均"]
        self.show_box = wx.ComboBox(self,-1,u"瞬时功率谱",choices = self.showList,style = wx.CB_DROPDOWN)
        self.show_box.SetSelection(0)
        self.Hz_txt = wx.StaticText(self,-1,u"MHz")
        self.Hz_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Min_X=wx.TextCtrl(self,-1,str('%0.1f'%self.fk[0]),size=(40,20),style=wx.TE_PROCESS_ENTER)
        self.Max_X=wx.TextCtrl(self,-1,str('%0.1f'%self.fk[-1]),size=(40,20),style=wx.TE_PROCESS_ENTER)
        
        #################################################################
        self.SetSizeHintsSz(wx.DefaultSize,wx.DefaultSize)
        m_bSizer = wx.BoxSizer(wx.VERTICAL)
        
        gSizer = wx.GridSizer(1,10,0,0)
        gSizer.Add(self.specBtn,0,wx.ALL|wx.ALIGN_BOTTOM,5)
        gSizer.Add(self.phaseBtn,0,wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_LEFT,5)
        
        gSizer1 = wx.GridSizer(3,1,0,0)
        gSizer1.Add(self.ID,0,wx.ALL,5)
        gSizer1.Add(self.time_txt,0,wx.ALL,5)
        gSizer1.Add(self.lon,0,wx.ALL,5)
        gSizer.Add(gSizer1,0,wx.ALL,5)
        gSizer.AddSpacer((10,10))
        
        gSizer2 = wx.GridSizer(3,1,0,0)
        gSizer2.Add(self.centrFreq,0,wx.ALL,5)
        gSizer2.Add(self.rate,0,wx.ALL,5)
        gSizer2.Add(self.rbw,0,wx.ALL,5)
        gSizer.Add(gSizer2,0,wx.ALL,5)
        gSizer.AddSpacer((10,10))
        
        gSizer3 = wx.GridSizer(3,1,0,0)
        gSizer3.Add(self.zaibo,0,wx.ALL,5)
        gSizer3.Add(self.band,0,wx.ALL,5)
        gSizer3.Add(self.xinzaobi,0,wx.ALL,5)
        gSizer.Add(gSizer3,0,wx.ALL,5)

        
        self.stopDrawBtn = wx.Button(self,-1,u'停止画图')
        gSizer.Add(self.show_box,0,wx.ALL,5)
        gSizer.Add(self.stopDrawBtn,0,wx.ALL,5)
        
        m_bSizer.Add(gSizer,0,wx.ALL|wx.EXPAND,5)
        
        bSizer = wx.BoxSizer(wx.VERTICAL)
        gSizer3 = wx.GridSizer(1,1,0,0)
        gSizer3.Add(self.FigureCanvas,1,wx.EXPAND,5)
        bSizer.Add(gSizer3,5,wx.EXPAND,5)
        m_bSizer.Add(bSizer,4,wx.EXPAND,5)
        
        gSizer4 = wx.GridSizer(1,3,0,0)
        gSizer4.Add(self.Min_X,0,wx.ALL,5)
        gSizer4.Add(self.Hz_txt,0,wx.ALIGN_CENTER,5)
        gSizer4.Add(self.Max_X,0,wx.ALIGN_RIGHT,5)
        m_bSizer.Add(gSizer4,0,wx.ALL|wx.EXPAND,5)
        

        
        self.SetSizer(m_bSizer)
        self.Layout()
        self.Centre(wx.BOTH)
        
        self.Min_X.Bind(wx.EVT_TEXT_ENTER,self.OnEnterMin_X)
        self.Max_X.Bind(wx.EVT_TEXT_ENTER,self.OnEnterMax_X)
        self.specBtn.Bind(wx.EVT_BUTTON,self.drawSpec)
        self.phaseBtn.Bind(wx.EVT_BUTTON,self.drawPhase)
        self.stopDrawBtn.Bind(wx.EVT_BUTTON,self.stopDraw)

        #####################################################################################
        
        self.xData = linspace(70,5995,2048)
        self.yData = [-45] * 2048
        self.lineSpec,=self.axes.plot(self.xData,self.yData,'y')
        self.axes.grid(True)
        
        self.ylabel('dBFS')
        
         
        xticks=linspace(70,5995,11)
        xticklabels = [str('%0.1f' % (i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation = 0)
        
        yticks=linspace(-120,0,9)
        yticklabels = [str('%0.1f' % (i)) for i in yticks]
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation = 0)

        
    def OnEnterMin_X(self,evt):
        self.change_Min_X=float(self.Min_X.GetValue())
        self.xlim(self.change_Min_X,float(self.Max_X.GetValue()))
        xticks=linspace(self.change_Min_X,float(self.Max_X.GetValue()),11)
        xticklabels = [str('%0.1f'%(i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation=0)
        self.FigureCanvas.draw() 

 
    def OnEnterMax_X(self,evt):
        self.change_Max_X=float(self.Max_X.GetValue())
        self.xlim(float(self.Min_X.GetValue()),self.change_Max_X)
        xticks=linspace(float(self.Min_X.GetValue()),self.change_Max_X,11)
        xticklabels = [str('%0.1f'%(i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation=0)
        self.FigureCanvas.draw()
    
    def stopDraw(self,evt):
        self.drawFlg = 0
        self.phaseFlg = 0
        self.phaseBtn.Enable(True)
        self.specBtn.Enable(True)
        self.show_box.Enable(True)
    
    def filePath(self,path):
        self.filePathList = path
        self.fileRealLen = len(self.filePathList)
        for item in self.filePathList:
            if item[-1] == '2':
                self.file_mode = 2
            elif item[-1] == 'q':
                self.file_mode = 1
                
        if self.file_mode==1:
            
            for path in self.filePathList:
                
                iq_file = open(path,'rb').read()
                iq_gps_centr = []
                for line in iq_file:
                    line = ord(line)
                    iq_gps_centr.append(line)
                
                freq_centr_int_h = iq_gps_centr[10] << 6
                freq_centr_int_l = iq_gps_centr[11] & 0x3F
                freq_centr_frac_h = (iq_gps_centr[11] >> 6)<< 8
                freq_centr_frac_l = iq_gps_centr[12]
                freq_centr_int = freq_centr_int_h + freq_centr_int_l
                freq_centr_frac = freq_centr_frac_h + freq_centr_frac_l
                freq_centr = freq_centr_int + freq_centr_frac / (10 ** len(str(freq_centr_frac)))
                freq_centr = float('%.4f' % freq_centr)
                
                    
                bandwidth = iq_gps_centr[13] >> 4
                if (bandwidth == 1) :
                    bandwidth_rate = 5
                elif (bandwidth == 2):
                    bandwidth_rate = 2.5
                elif (bandwidth == 3):
                    bandwidth_rate = 1.25
                elif (bandwidth == 4):
                    bandwidth_rate = 0.625
                elif (bandwidth == 5):
                    bandwidth_rate = 0.125
                    
            
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
                    

                    fk,pk,angle = self.ParseIQ(IData, QData, freq_centr, bandwidth_rate)
                    self.fk = fk
                    
        
        
        if self.file_mode==2:
            
        
            for i in self.filePathList:    

                iq2_gps_centr,IData,QData,freq_centr,bandwidth_rate = self.ParseIQ2(i)
                pk,fk,angle = self.fft_iq2(IData,QData,freq_centr,bandwidth_rate)
                self.fk_2 = fk
        
        self.filePathList = self.filePathList * 100  
        self.pk = pk      
    
    def drawSpec(self,evt):
        self.phaseBtn.Enable(False)
        self.pk_max = self.pk
        self.pk_min = self.pk
        self.pk_ave = self.pk

        self.drawFlg = 1
        self.ylabel(u'dBFS')
        
        if self.file_mode==2:
            self.xlim(self.fk_2[0], self.fk_2[-1])
            xticks=linspace(self.fk_2[0],self.fk_2[-1],11)
            self.ylim(-120,0)
            yticks = linspace(-120,0,9)  
        if self.file_mode==1:
            self.xlim(self.fk[0], self.fk[-1])
            xticks=linspace(self.fk[0],self.fk[-1],11)
            self.ylim(-150, 0)
            yticks = linspace(-150,0,11)
        
        yticklabels = [str(int(i)) for i in yticks]  
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation = 0)

        xticklabels = [str('%0.2f' % (i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation = 0)
        
        
        self.thread = Thread(target=self.drawSpecChild)
        self.thread.start()

        
    def drawSpecChild(self):
        
        try:
            
            if self.file_mode==2:
                
                for i in self.filePathList:    
                    if self.drawFlg==1:
                        
                        iq2_gps_centr,IData,QData,freq_centr,bandwidth_rate = self.ParseIQ2(i)
                        pk,fk,angle = self.fft_iq2(IData,QData,freq_centr,bandwidth_rate)
    
                        if self.show_box.GetSelection()==0:
                            self.setLbl_draw(fk, pk)
                        elif self.show_box.GetSelection()==1: ##最大保持
                            pk_max = self.findMax(pk)
                            self.setLbl_draw(fk, pk_max)
                        elif self.show_box.GetSelection()==2: ##最小保持
                            pk_min = self.findMin(pk)
                            self.setLbl_draw(fk, pk_min)
                        elif self.show_box.GetSelection()==3: ##迹线平均
                            pk_ave = self.findAve(pk)
                            self.setLbl_draw(fk, pk_ave)    
                            

                        time.sleep(0.3)   
                    if self.drawFlg==0:
                        break
                    
                
            if self.file_mode==1:
                for path in self.filePathList:
                    if self.drawFlg==1:
                        iq_file = open(path,'rb').read()
                        iq_gps_centr = []
                        for line in iq_file:
                            line = ord(line)
                            iq_gps_centr.append(line)
                        
                        freq_centr_int_h = iq_gps_centr[10] << 6
                        freq_centr_int_l = iq_gps_centr[11] & 0x3F
                        freq_centr_frac_h = (iq_gps_centr[11] >> 6)<< 8
                        freq_centr_frac_l = iq_gps_centr[12]
                        freq_centr_int = freq_centr_int_h + freq_centr_int_l
                        freq_centr_frac = freq_centr_frac_h + freq_centr_frac_l
                        freq_centr = freq_centr_int + freq_centr_frac / (10 ** len(str(freq_centr_frac)))
                        freq_centr = float('%.4f' % freq_centr)
                        
                            
                        bandwidth = iq_gps_centr[13] >> 4
                        if (bandwidth == 1) :
                            bandwidth_rate = 5
                        elif (bandwidth == 2):
                            bandwidth_rate = 2.5
                        elif (bandwidth == 3):
                            bandwidth_rate = 1.25
                        elif (bandwidth == 4):
                            bandwidth_rate = 0.625
                        elif (bandwidth == 5):
                            bandwidth_rate = 0.125
                            
                    
                        N = iq_gps_centr[14]
                        
                        
                        for j in range(N):
                            count = 0
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
                            
        
                            fk,pk,angle = self.ParseIQ(IData, QData, freq_centr, bandwidth_rate)
                            
                            if self.show_box.GetSelection()==0:
                                self.setLbl_draw(fk, pk)
                            elif self.show_box.GetSelection()==1: ##最大保持
                                pk_max = self.findMax(pk)
                                self.setLbl_draw(fk, pk_max)
                            elif self.show_box.GetSelection()==2: ##最小保持
                                pk_min = self.findMin(pk)
                                self.setLbl_draw(fk, pk_min)
                            elif self.show_box.GetSelection()==3: ##迹线平均
                                pk_ave = self.findAve(pk)
                                self.setLbl_draw(fk, pk_ave)   
                            
        
                            time.sleep(0.3)
                    
                    if self.drawFlg==0:
                        break    
        
        except Exception, e:
            print e

    def findMax(self,pk):
        for i in range(2048):
            if self.pk_max[i] < pk[i]:
                self.pk_max[i] = pk[i]
        return self.pk_max
    
    def findMin(self,pk):
        for i in range(2048):
            if self.pk_min[i] > pk[i]:
                self.pk_min[i] = pk[i]
        return self.pk_min
    
    def findAve(self,pk):
        self.stayAveCount += 1
        for i in range(2048):
            self.pk_ave[i]=(self.pk_ave[i] * self.stayAveCount + pk[i])/(self.stayAveCount+1)
        return self.pk_ave
                
    def drawPhase(self,evt):
        self.specBtn.Enable(False)
        self.show_box.Enable(False)
        self.phaseFlg = 1
        self.ylabel('angle')
        if self.file_mode==2:
            xticks=linspace(self.fk_2[0],self.fk_2[-1],11)
            self.ylim(-150,150)
            yticks = linspace(-150,150,11)  
        if self.file_mode==1:
            xticks=linspace(self.fk[0],self.fk[-1],11)
            self.ylim(-150, 150)
            yticks = linspace(-150,150,11)
            
        
        xticklabels = [str('%0.1f' % (i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation = 0)
        yticklabels = [str(int(i)) for i in yticks]  
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation = 0)
        
        self.thread = Thread(target=self.drawPhaseChild)
        self.thread.start()
        
#         self.filePathList = self.filePathList * 3
        
    def drawPhaseChild(self):
        
        try:
            if self.file_mode==2:
    
                
                for i in self.filePathList:
                    if self.phaseFlg:
                        count = 0
                        iq2_gps_centr,IData,QData,freq_centr,bandwidth_rate = self.ParseIQ2(i)
                        pk,fk,angle = self.fft_iq2(IData,QData,freq_centr,bandwidth_rate)
             
                         
                        self.setLbl_draw(fk, angle)
                         
                        time.sleep(0.3)
                    elif self.phaseFlg==0:
                        break
            
            if self.file_mode==1:
                for path in self.filePathList:
                    if self.phaseFlg:
                        iq_file = open(path,'rb').read()
                        iq_gps_centr = []
                        for line in iq_file:
                            line = ord(line)
                            iq_gps_centr.append(line)
                        
                        freq_centr_int_h = iq_gps_centr[10] << 6
                        freq_centr_int_l = iq_gps_centr[11] & 0x3F
                        freq_centr_frac_h = (iq_gps_centr[11] >> 6)<< 8
                        freq_centr_frac_l = iq_gps_centr[12]
                        freq_centr_int = freq_centr_int_h + freq_centr_int_l
                        freq_centr_frac = freq_centr_frac_h + freq_centr_frac_l
                        freq_centr = freq_centr_int + freq_centr_frac / (10 ** len(str(freq_centr_frac)))
                        freq_centr = float('%.4f' % freq_centr)
                        
                            
                        bandwidth = iq_gps_centr[13] >> 4
                        if (bandwidth == 1) :
                            bandwidth_rate = 5
                        elif (bandwidth == 2):
                            bandwidth_rate = 2.5
                        elif (bandwidth == 3):
                            bandwidth_rate = 1.25
                        elif (bandwidth == 4):
                            bandwidth_rate = 0.625
                        elif (bandwidth == 5):
                            bandwidth_rate = 0.125
                            
                    
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
                            
        
                            fk,pk,angle = self.ParseIQ(IData, QData, freq_centr, bandwidth_rate)
                            
                            self.setLbl_draw(fk, angle)
        
                            time.sleep(0.3)
                            
                    elif self.phaseFlg==0:
                        break
        
        except Exception, e:
            print e
    
    def ParseIQ(self,IData,QData,freq_centr,bandwidth_rate):
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
        
        return fk,pk,angle
    
    
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

    

    
    def set_txt(self,filename,lon,lat,hei,freq_centr,bandwidth_rate): 
        if filename[-2]=='-':
            id_txt = filename[-4:-2]
        else:
            id_txt = filename[-2:]

        
        self.ID.SetLabel(u'终端ID号：' + id_txt)
        self.time_txt.SetLabel(u'时间：' + filename[:19])
        self.lon.SetLabel(u'经-纬-高：'+str('%0.2f'%lon)+u'°'+'-'+str('%0.2f'%lat)+u'°'+'-'+str('%0.2f'%hei)+u'米')
        self.centrFreq.SetLabel(u'中心频率：' + str(freq_centr) + 'MHz')
        self.rate.SetLabel(u'采样率：' + str(bandwidth_rate) + 'MHz')
        self.rbw.SetLabel(u'RBW：' + str('%0.2f' % (float(bandwidth_rate*1000)/2048)) + 'kHz' + u'，' + u'VBW：' + str('%0.2f' % (float(bandwidth_rate*1000)/2048)) + 'kHz'+'')
        self.band.SetLabel(u'带宽：' + str(bandwidth_rate) + 'MHz')

        
        
    def setLbl_draw(self,fk,pk):
        
        self.lineSpec.set_xdata(array(fk))
        self.lineSpec.set_ydata(array(pk))
        self.FigureCanvas.draw()
        
        
    def xlim(self,x_min,x_max):  
        self.axes.set_xlim(x_min,x_max)  
  
    def ylim(self,y_min,y_max):  
        self.axes.set_ylim(y_min,y_max)

    def xlabel(self,XabelString="X"):   
        self.axes.set_xlabel(XabelString)  
  
    def ylabel(self,YabelString="Y"):  
        self.axes.set_ylabel(YabelString)
        


class IQ2_Wave(wx.Panel):

    def __init__(self,parent,data,filePathList,am_fm_mode):
        wx.Panel.__init__(self,parent)
        self.CreatePanel(data)
        self.filePathList = filePathList
        self.am_fm_mode = am_fm_mode
        self.drawFlg = 1

        
    def CreatePanel(self,data):
        self.Figure = matplotlib.figure.Figure()
        self.axes=self.Figure.add_axes([0.1,0.1,0.8,0.8])
        self.FigureCanvas = FigureCanvas(self,-1,self.Figure)
        self.waveBtn = wx.Button(self,-1,u"解调后归一化波形图")
#         self.title = wx.StaticText(self,-1,u"解调后归一化波形图")
#         self.title.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.angle_txt = wx.StaticText(self,-1,u"")
        self.Hz_txt = wx.StaticText(self,-1,u"")
        self.angle_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Hz_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Min_X=wx.TextCtrl(self,-1,str(0),size=(40,20),style=wx.TE_PROCESS_ENTER)
        self.Max_X=wx.TextCtrl(self,-1,str(2000),size=(40,20),style=wx.TE_PROCESS_ENTER)
        #################################################################
        self.SetSizeHintsSz(wx.DefaultSize,wx.DefaultSize)
        m_bSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.modeTxt = wx.StaticText(self,-1,u'解调方式：')
        gSizer = wx.GridSizer(1,5,0,0)
        gSizer.Add(self.waveBtn,0,wx.ALL|wx.ALIGN_BOTTOM,5)
        gSizer.AddSpacer(self.modeTxt,0,wx.ALL|wx.ALIGN_BOTTOM,5)
        gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
        gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
        self.stopDrawBtn = wx.Button(self,-1,u'停止画图')
        gSizer.Add(self.stopDrawBtn,0,wx.ALL|wx.ALIGN_BOTTOM,5)
        m_bSizer.Add(gSizer,0,wx.EXPAND,5)
        
        bSizer = wx.BoxSizer(wx.HORIZONTAL)
        gSizer2 = wx.GridSizer(1,1,0,0)
        gSizer2.Add(self.angle_txt,0,wx.ALIGN_CENTER|wx.ALL,5)
        gSizer3 = wx.GridSizer(1,1,0,0)
        gSizer3.Add(self.FigureCanvas,1,wx.EXPAND,5)
        bSizer.Add(gSizer2,0,wx.ALL|wx.ALIGN_CENTER,5)
        bSizer.Add(gSizer3,5,wx.EXPAND,5)
        m_bSizer.Add(bSizer,4,wx.EXPAND,5)
        
        
        gSizer4 = wx.GridSizer(1,3,0,0)
        gSizer4.Add(self.Min_X,0,wx.ALL,5)
        gSizer4.Add(self.Hz_txt,0,wx.ALIGN_CENTER,5)
        gSizer4.Add(self.Max_X,0,wx.ALIGN_RIGHT,5)
        m_bSizer.Add(gSizer4,0,wx.ALL|wx.EXPAND,5)
        
        self.SetSizer(m_bSizer)
        self.Layout()
        self.Centre(wx.BOTH)
        
        self.waveBtn.Bind(wx.EVT_BUTTON,self.drawWaveClick)  
        self.stopDrawBtn.Bind(wx.EVT_BUTTON,self.drawStop)
        self.Min_X.Bind(wx.EVT_TEXT_ENTER,self.OnEnterMin_X)
        self.Max_X.Bind(wx.EVT_TEXT_ENTER,self.OnEnterMax_X)  
        #####################################################################################
        self.xData = linspace(1,2000,2000)
        self.yData = [0] * 2000
        self.lineSpec,=self.axes.plot(self.xData,self.yData,'r')
        self.axes.grid(True)
        
        xticks = linspace(0,2000,11)
        xticklabels = [str(int(i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation = 0)
        
        yticks=linspace(-1,1,11)  
        yticklabels = [str('%0.1f' % (i)) for i in yticks]  
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation = 0)
        
        self.lineSpec.set_xdata([i for i in xrange(2000)])

    
    def filePath(self,path):
        self.filePathList = path
        
        for item in self.filePathList:
            if item[-1] == '2':
                self.file_mode = 2
            elif item[-1] == 'q':
                self.file_mode = 1
        
        self.filePathList = self.filePathList * 100
    
    def am_fm_mode_refresh(self,mode):
        self.am_fm_mode = mode

    
    def drawStop(self,evt):
        self.drawFlg = 0
        
    def drawWaveClick(self,evt):
        if self.am_fm_mode==0:
            mode_str = u'AM解调'
        elif self.am_fm_mode==1:
            mode_str = u'FM解调'
        self.modeTxt.SetLabel(u'解调方式：' + mode_str)
        self.drawFlg = 1
        self.thread = Thread(target=self.drawWaveChild)
        self.thread.start()

        
#         self.filePathList = self.filePathList * 5
    
    def drawWaveChild(self): 
         
        try:
            if self.file_mode == 2:
                
                
                for i in self.filePathList:
                    if self.drawFlg :          
        
                        iq2_gps_centr,IData,QData,freq_centr,bandwidth_rate = self.ParseIQ2(i)
                        if self.am_fm_mode == 0 : ###am
                            data = self.am_mode(IData, QData)
                        elif(self.am_fm_mode == 1 ): ###fm
                            data = self.fm_mode(IData, QData)
            
                        self.setLbl_draw(data)
                        time.sleep(0.3)
                        
                    elif self.drawFlg==0:
                        break
                    
            if self.file_mode==1:

                for path in self.filePathList:
                    if self.drawFlg:
                        iq_file = open(path,'rb').read()
                        iq_gps_centr = []
                        for line in iq_file:
                            line = ord(line)
                            iq_gps_centr.append(line)
                        
                        freq_centr_int_h = iq_gps_centr[10] << 6
                        freq_centr_int_l = iq_gps_centr[11] & 0x3F
                        freq_centr_frac_h = (iq_gps_centr[11] >> 6)<< 8
                        freq_centr_frac_l = iq_gps_centr[12]
                        freq_centr_int = freq_centr_int_h + freq_centr_int_l
                        freq_centr_frac = freq_centr_frac_h + freq_centr_frac_l
                        freq_centr = freq_centr_int + freq_centr_frac / (10 ** len(str(freq_centr_frac)))
                        freq_centr = float('%.4f' % freq_centr)
                        
                            
                        bandwidth = iq_gps_centr[13] >> 4
                        if (bandwidth == 1) :
                            bandwidth_rate = 5
                        elif (bandwidth == 2):
                            bandwidth_rate = 2.5
                        elif (bandwidth == 3):
                            bandwidth_rate = 1.25
                        elif (bandwidth == 4):
                            bandwidth_rate = 0.625
                        elif (bandwidth == 5):
                            bandwidth_rate = 0.125
                            
                    
                        N = iq_gps_centr[14]
                        
                        
                        for j in range(N):
                            count = 0
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
                            
                            
                            if self.am_fm_mode == 0 : ###am
                                data = self.am_mode(IData, QData)
                            elif(self.am_fm_mode == 1 ): ###fm
                                data = self.fm_mode(IData, QData)
                                
                            self.setLbl_draw(data)
        
                            time.sleep(0.3)
                    
                    elif self.drawFlg==0:
                        break
                            
        except Exception, e:
            print e,
                    
         
            
    def OnEnterMin_X(self,evt):
        self.change_Min_X=float(self.Min_X.GetValue())
        self.xlim(self.change_Min_X,float(self.Max_X.GetValue()))
        xticks=linspace(self.change_Min_X,float(self.Max_X.GetValue()),11)
        xticklabels = [str('%0.1f'%(i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation=0)
        self.FigureCanvas.draw() 

 
    def OnEnterMax_X(self,evt):
        self.change_Max_X=float(self.Max_X.GetValue())
        self.xlim(float(self.Min_X.GetValue()),self.change_Max_X)
        xticks=linspace(float(self.Min_X.GetValue()),self.change_Max_X,10)
        xticklabels = [str('%0.1f'%(i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation=0)
        self.FigureCanvas.draw()

        
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
    
        
    def am_mode(self,sigI,sigQ):  ####before
        sigI = [i * i for i in sigI]
        sigQ = [j * j for j in sigQ]
        mt1 = [sqrt(i + j) for i,j in zip(sigI,sigQ)]
        mean = sum(mt1) / len(mt1)
        data = [(i - mean) for i in mt1]
        data = data[0:len(data):1]
        abs_data=[abs(i) for i in data]
        data_max=max(abs_data)
        data=[float(i*1)/data_max for i in data]
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

        
    def setLbl_draw(self,data):

        self.lineSpec.set_ydata(array(data))
        self.FigureCanvas.draw()
        
    def xlim(self,x_min,x_max):  
        self.axes.set_xlim(x_min,x_max)  
  
    def ylim(self,y_min,y_max):  
        self.axes.set_ylim(y_min,y_max)

    def xlabel(self,XabelString="X"):   
        self.axes.set_xlabel(XabelString)  
  
    def ylabel(self,YabelString="Y"):  
        self.axes.set_ylabel(YabelString)
        
    
        
        
# class IQ2_Phase(wx.Panel):
#     def __init__(self,parent,fk,angle):
#         wx.Panel.__init__(self,parent)
#         self.CreatePanel(fk,angle)
# #         self.setLbl_draw(fk, pk)
#         
#     def CreatePanel(self,fk,pk):
#         self.Figure = matplotlib.figure.Figure()
#         self.axes=self.Figure.add_axes([0.1,0.1,0.8,0.8])
#         self.FigureCanvas = FigureCanvas(self,-1,self.Figure)
#         self.title = wx.StaticText(self,-1,u"相位谱图")
#         self.title.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
#         self.angle_txt = wx.StaticText(self,-1,u"度")
#         self.Hz_txt = wx.StaticText(self,-1,u"MHz")
#         self.angle_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
#         self.Hz_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
#         
#         #################################################################
#         self.SetSizeHintsSz(wx.DefaultSize,wx.DefaultSize)
#         m_bSizer = wx.BoxSizer(wx.VERTICAL)
#         
#         gSizer = wx.GridSizer(1,5,0,0)
#         gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
#         gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
#         gSizer.Add(self.title,0,wx.ALL,5)
#         m_bSizer.Add(gSizer,0,wx.ALL|wx.EXPAND,5)
#         
#         bSizer = wx.BoxSizer(wx.HORIZONTAL)
#         gSizer2 = wx.GridSizer(1,1,0,0)
#         gSizer2.Add(self.angle_txt,0,wx.ALIGN_CENTER|wx.ALL,5)
#         gSizer3 = wx.GridSizer(1,1,0,0)
#         gSizer3.Add(self.FigureCanvas,1,wx.EXPAND,5)
#         bSizer.Add(gSizer2,0,wx.ALL|wx.ALIGN_CENTER,5)
#         bSizer.Add(gSizer3,5,wx.EXPAND,5)
#         m_bSizer.Add(bSizer,4,wx.EXPAND,5)
#         
#         gSizer4 = wx.GridSizer(1,1,0,0)
#         gSizer4.Add(self.Hz_txt,0,wx.ALIGN_CENTER|wx.EXPAND,5)
#         m_bSizer.Add(gSizer4,0,wx.ALL|wx.ALIGN_CENTER,5)
#         
#         self.SetSizer(m_bSizer)
#         self.Layout()
#         self.Centre(wx.BOTH)
#             
#         #####################################################################################
#         self.xData = linspace(1,100,2048)
#         self.yData = [0] * 2048
#         self.lineSpec,=self.axes.plot(self.xData,self.yData,'b')
#         self.axes.grid(True)
#         
#         self.xlim(fk[0],fk[-1])
#         self.ylim(-200,200)
#         xticks=linspace(fk[0],fk[-1],9)
#         xticklabels = [str('%0.1f' % (i)) for i in xticks]
#         yticks=linspace(-200,200,11)  
#         yticklabels = [str(int(i)) for i in yticks]  
#         self.axes.set_xticks(xticks)
#         self.axes.set_xticklabels(xticklabels,rotation = 0)
#         self.axes.set_yticks(yticks)
#         self.axes.set_yticklabels(yticklabels,rotation = 0)
#         self.lineSpec.set_xdata(array(fk))
#         
#     def setLbl_draw(self,fk,angle):
#         xticks=linspace(fk[0],fk[-1],9)
#         xticklabels = [str('%0.1f' % (i)) for i in xticks]
#         self.axes.set_xticks(xticks)
#         self.axes.set_xticklabels(xticklabels,rotation = 0)
# 
#         self.lineSpec.set_ydata(array(angle))
#         self.FigureCanvas.draw()
#     
#     def xlim(self,x_min,x_max):  
#         self.axes.set_xlim(x_min,x_max)  
#   
#     def ylim(self,y_min,y_max):  
#         self.axes.set_ylim(y_min,y_max)
# 
#     def xlabel(self,XabelString="X"):   
#         self.axes.set_xlabel(XabelString)  
#   
#     def ylabel(self,YabelString="Y"):  
#         self.axes.set_ylabel(YabelString)
#         
# class IQ2_Water(wx.Panel):
#     def __init__(self,parent,fk,pk):
#         wx.Panel.__init__(self,parent )
# 
#         self.parent=parent
#         self.waterFirst=1
#         self.col=2048
#         self.row=1000
#         self.rowCpy=5
#         self.CreatePanel(fk,pk)
#         
#     def CreatePanel(self,fk,pk):
#         self.Figure = matplotlib.figure.Figure(figsize=(1,1))
#         self.axes=self.Figure.add_axes([0.1,0.1,0.8,0.8])
#         self.FigureCanvas = FigureCanvas(self,-1,self.Figure)
#         self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
#         bSizer = wx.BoxSizer(wx.VERTICAL)
#         self.title = wx.StaticText(self,-1,u"瀑布图")
#         self.title.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
#         gSizer = wx.GridSizer(1,5,0,0)
#         gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
#         gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
#         gSizer.Add(self.title,0,wx.ALL,5)
#         bSizer.Add(gSizer,0,wx.EXPAND,5)
#         bSizer.Add( self.FigureCanvas, 1, wx.EXPAND, 5 )
#         self.SetSizer( bSizer )
#         self.Layout()
#         
#         ####################################################################################
#         self.matrixFull = [[-120 for i in range(self.col)] for i in range(self.row)]
#         norm = matplotlib.colors.Normalize(vmin=-120, vmax=0)
#         self.image = self.axes.imshow(array(self.matrixFull),origin='lower',cmap=jet,norm=norm,interpolation='nearest')
#         cbar=self.Figure.colorbar(self.image)
#         ticks=linspace(-120,0,10)
#         cbar.set_ticks(ticks)
#         tick_labels=[str(int(i)) for i in ticks]
#         cbar.set_ticklabels(tick_labels)
#         self.FigureCanvas.draw()    
#         #####################################################################################
#         
# #         self.ylabel('Frame Number')
#         self.xlabel('MHz')
# 
#         xticks = linspace(0,self.col,9)
#         self.axes.set_xticks(xticks)
#         label = linspace(fk[0],fk[-1],9)
#         xticklabels = ['%0.1f' % i for i in label]
#         self.axes.set_xticklabels(xticklabels, rotation=0) 
#         intervalY = self.row / 10
#         yticks = range(0, self.row+1, intervalY)
#         yticklabels = [str(i) for i in yticks]
#         self.axes.set_yticks(yticks)
#         self.axes.set_yticklabels(yticklabels,rotation=0)  
#         
#     def setLbl_draw(self,pk):
# 
#         del self.matrixFull[self.row-self.rowCpy:self.row]
#         for i in range(self.rowCpy):
#             self.matrixFull.insert(0,pk)
#         self.image.set_data(array(self.matrixFull))
#         self.FigureCanvas.draw()
#         
#     def xlim(self,x_min,x_max):  
#         self.axes.set_xlim(x_min,x_max)  
#   
#     def ylim(self,y_min,y_max):  
#         self.axes.set_ylim(y_min,y_max)
# 
#     def xlabel(self,XabelString="X"):   
#         self.axes.set_xlabel(XabelString)  
#   
#     def ylabel(self,YabelString="Y"):  
#         self.axes.set_ylabel(YabelString)
