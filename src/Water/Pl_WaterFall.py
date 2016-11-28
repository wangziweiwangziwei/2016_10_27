# -*- coding: utf-8 -*-
from __future__ import division 
import wx
from numpy import array, linspace
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas 
from matplotlib.cm import jet 
import wx.aui 
import time
from math import log10,sqrt,log10,atan
import scipy.signal as signal
import numpy as np
from threading import Thread

class IQ2_Water(wx.aui.AuiMDIChildFrame):
    def __init__(self,parent,fk,pk,filePath,fileMode):
        wx.aui.AuiMDIChildFrame.__init__(self,parent,-1,title=u"回放文件瀑布图")
 
        self.parent=parent
        self.waterFirst=1
        self.col=2048
        self.row=1000
        self.rowCpy=5
        self.CreatePanel(fk,pk)
        self.filePath = filePath
        self.drawFlg = 1
        self.file_mode = fileMode
        
        self.Bind(wx.EVT_WINDOW_DESTROY,self.OnClose)
         
    def CreatePanel(self,fk,pk):
        
        self.ID = wx.StaticText(self,-1,u'终端ID号')
        self.time_txt = wx.StaticText(self,-1,u'时间')
        self.lon = wx.StaticText(self,-1,u'经-纬-高')
        self.rbw = wx.StaticText(self,-1,u'RBW、VBW')
        self.centrFreq = wx.StaticText(self,-1,u"中心频率")
        self.rate = wx.StaticText(self,-1,u'采样率')
        
        self.Figure = matplotlib.figure.Figure(figsize=(1,1))
        self.axes=self.Figure.add_axes([0.1,0.1,0.8,0.8])
        self.FigureCanvas = FigureCanvas(self,-1,self.Figure)
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        
        self.drawBtn = wx.Button(self,-1,u'开始画图')
        self.drawStopBtn = wx.Button(self,-1,u'停止画图')
        bSizer = wx.BoxSizer(wx.VERTICAL)
        gSizer = wx.GridSizer(1,7,0,0)
        gSizer.Add(self.drawBtn,0,wx.ALL,5)
        gSizer.Add(self.drawStopBtn,0,wx.ALL|wx.ALIGN_LEFT,5)
        
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

        
        bSizer.Add(gSizer,0,wx.ALL,5)

        bSizer.Add( self.FigureCanvas, 1, wx.EXPAND, 5 )
        self.SetSizer( bSizer )
        self.Layout()
        
        self.drawBtn.Bind(wx.EVT_BUTTON,self.drawClick)
        self.drawStopBtn.Bind(wx.EVT_BUTTON,self.drawStopClick) 
        ####################################################################################
        self.matrixFull = [[-120 for i in range(self.col)] for i in range(self.row)]
        norm = matplotlib.colors.Normalize(vmin=-120, vmax=0)
        self.image = self.axes.imshow(array(self.matrixFull),origin='lower',cmap=jet,norm=norm,interpolation='nearest')
        cbar=self.Figure.colorbar(self.image)
        ticks=linspace(-120,0,10)
        cbar.set_ticks(ticks)
        tick_labels=[str(int(i)) for i in ticks]
        cbar.set_ticklabels(tick_labels)
        self.FigureCanvas.draw()    
        #####################################################################################
         
        self.ylabel('Frame Number')
        self.xlabel('MHz')
 
        xticks = linspace(0,self.col,9)
        self.axes.set_xticks(xticks)
        label = linspace(fk[0],fk[-1],9)
        xticklabels = ['%0.1f' % i for i in label]
        self.axes.set_xticklabels(xticklabels, rotation=0) 
        intervalY = self.row // 10
        yticks = range(0, self.row+1, intervalY)
        yticklabels = [str(i) for i in yticks]
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation=0)  
        
    def fileDraw(self,path):
        self.filePath = path
        self.filePath = self.filePath * 100
        
    
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
#         self.band.SetLabel(u'带宽：' + str(bandwidth_rate) + 'MHz')    
    
    def drawClick(self,evt):

        self.drawFlg = 1
        self.thread = Thread(target=self.drawChild)
        self.thread.start()
        
    def drawChild(self):
        
        try :
            if self.file_mode==2:
                
                for i in self.filePath:

                    if self.drawFlg:
                        iq2_gps_centr,IData,QData,freq_centr,bandwidth_rate = self.ParseIQ2(i)
                        pk,fk,angle = self.fft_iq2(IData,QData,freq_centr,bandwidth_rate)
                        self.setLbl_draw(fk,pk)
                    elif self.drawFlg==0:
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
                            self.setLbl_draw(fk,pk)
                    elif self.drawFlg==0:
                        break
                                
        except Exception,e:
            print e,
    
    def drawStopClick(self,evt):
        self.drawFlg=0
    
    
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

    

             
    def setLbl_draw(self,fk,pk):
        
        label = linspace(fk[0],fk[-1],9)
        xticklabels = ['%0.1f' % i for i in label]
        self.axes.set_xticklabels(xticklabels, rotation=0) 
 
        del self.matrixFull[self.row-self.rowCpy:self.row]
        for i in range(self.rowCpy):
            self.matrixFull.insert(0,pk)
        self.image.set_data(array(self.matrixFull))
        self.FigureCanvas.draw()
         
    def xlim(self,x_min,x_max):  
        self.axes.set_xlim(x_min,x_max)  
   
    def ylim(self,y_min,y_max):  
        self.axes.set_ylim(y_min,y_max)
 
    def xlabel(self,XabelString="X"):   
        self.axes.set_xlabel(XabelString)  
   
    def ylabel(self,YabelString="Y"):  
        self.axes.set_ylabel(YabelString)
        
    
    def OnClose(self,event):
        self.parent.WaterFrame=None
        self.Close()