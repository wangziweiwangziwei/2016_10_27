# -*- coding: utf-8 -*- 
import wx.aui 
import matplotlib
from numpy import array, linspace
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas 
import scipy.signal as signal
import numpy as np
from math import log10,sqrt,log10,atan
import time

class IQ2_Spec(wx.Panel):
    def __init__(self,parent,fk,pk,angle,filePathList,file_mode):
        wx.Panel.__init__(self,parent)
        self.parent = parent
        self.fk = fk
        self.pk = pk
        self.angle = angle
        self.filePathList = filePathList
        self.file_mode = file_mode
        self.CreatePanel()
        
                
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
        gSizer.AddSpacer((10,10))
        gSizer.Add(self.show_box,0,wx.ALL,5)
        m_bSizer.Add(gSizer,0,wx.ALL|wx.EXPAND,5)
        
        bSizer = wx.BoxSizer(wx.HORIZONTAL)
        gSizer3 = wx.GridSizer(1,1,0,0)
        gSizer3.Add(self.FigureCanvas,1,wx.EXPAND,5)
        bSizer.Add(gSizer3,5,wx.EXPAND,5)
        m_bSizer.Add(bSizer,4,wx.EXPAND,5)
          

        
        self.SetSizer(m_bSizer)
        self.Layout()
        self.Centre(wx.BOTH)
        
        self.specBtn.Bind(wx.EVT_BUTTON,self.drawSpec)
        self.phaseBtn.Bind(wx.EVT_BUTTON,self.drawPhase)
            
        #####################################################################################
        
        self.xData = linspace(1,100,2048)
        self.yData = [0] * 2048
        self.lineSpec,=self.axes.plot(self.xData,self.yData,'y')
        self.axes.grid(True)
    
    
    def filePath(self,path):
        item = path[0]
        if item[-1] == '2': 
            self.file_mode = 2  ###iq2
        elif item[-1] == 'q': 
            self.file_mode = 1  ####iq
        self.path = path
    
    def drawSpec(self,evt):
        self.ylabel('dBFS')
        path = self.path
        if self.file_mode==1:
            self.parseIQFile(path)
            self.ylim(-150,0)
            yticks = linspace(-150,0,11)
        
        if self.file_mode==2:
            self.parseIQ2File(path)
            self.ylim(-120,0)
            yticks = linspace(-120,0,11)
        
        yticklabels = [str(int(i)) for i in yticks] 
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation = 0)
           
            
    
    
    def drawPhase(self,evt):
        self.ylabel('angle')
        path = self.path
        if self.file_mode==1:
            self.ylim(-200, 200)
            yticks = linspace(-200,200,11)
        if self.file_mode==2:
            self.ylim(-150,150)
            yticks = linspace(-150,150,11)
            self.parseIQ2FilePhase(path)
        
        yticklabels = [str(int(i)) for i in yticks]  
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation = 0)
    
    def parseIQFilePhase(self,pathList):
        for path in pathList:
            iq_file = open(path,'rb').read()    
            iqList = []
            for line in iq_file:
                line = ord(line)
                iqList.append(line) 
            self.parseIQDataPhase(iqList)
            
    def parseIQDataPhase(self,iqList):
        freq_centr_int_h = iqList[10] << 6
        freq_centr_int_l = iqList[11] & 0x3F
        freq_centr_frac_h = (iqList[11] >> 6)<< 8
        freq_centr_frac_l = iqList[12]
        freq_centr_int = freq_centr_int_h + freq_centr_int_l
        freq_centr_frac = freq_centr_frac_h + freq_centr_frac_l
        freq_centr = freq_centr_int + freq_centr_frac / (10 ** len(str(freq_centr_frac)))
        freq_centr = float('%.4f' % freq_centr)
        
        bandwidth = iqList[13] >> 4
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
            
        N = iqList[14]
        
        for j in range(N):
            IData = []
            QData = []
            for i in range(2000):
                HighI1 = ((iqList[6001 * (j + 1) - 5985 + i * 3]) >> 4) << 8
                LowI1 = iqList[6001 * (j + 1) - 5984 + i * 3]
                if (HighI1 >= 2048):
                    I1 = -(2 ** 12 - HighI1 - LowI1)
                else :
                    I1 = (HighI1 + LowI1)
                IData.append(I1)
        
                HighQ1 = ((iqList[6001 * (j + 1) - 5985 + i * 3]) & 0x0F) << 8
                LowQ1 = iqList[6001 * (j + 1) - 5983 + i * 3]
                if (HighQ1 >= 2048):
                    Q1 = -(2 ** 12 - HighQ1 - LowQ1)
                else :
                    Q1 = (HighQ1 + LowQ1)
                QData.append(Q1)
            
            fk,pk,angle = self.parseIQ(IData, QData, freq_centr, bandwidth_rate)
            self.setLbl(fk, angle)
            self.draw(fk, angle)
            time.sleep(0.3)
            if not j==N:
                self.lineSpec.remove()
        
            
    def parseIQ2FilePhase(self,pathList):
        for path in pathList:
            count = 0
            iq2_gps_centr,IData,QData,freq_centr,bandwidth_rate = self.ParseIQ2(path)
            pk,fk,angle = self.fft_iq2(IData,QData,freq_centr,bandwidth_rate)
            
            self.setLbl(fk, angle)
            self.draw(fk, angle)
            if not len(pathList)==1 :
                count += 1
                if not count == len(pathList):
                    self.lineSpec.remove()
            if len(pathList)==1 :
                self.lineSpec.remove()    
        
    def parseIQ2File(self,pathList):
        for path in pathList:
            count = 0
            iq2_gps_centr,IData,QData,freq_centr,bandwidth_rate = self.ParseIQ2(path)
            pk,fk,angle = self.fft_iq2(IData,QData,freq_centr,bandwidth_rate)
            
            self.setLbl(fk, pk)
            self.draw(fk, pk)
            if not len(pathList)==1 :
                count += 1
                if not count == len(pathList):
                    self.lineSpec.remove()
            if len(pathList)==1 :
                self.lineSpec.remove()

        
    def parseIQFile(self,pathList):   
        for path in pathList:
            iq_file = open(path,'rb').read()    
            iqList = []
            for line in iq_file:
                line = ord(line)
                iqList.append(line) 
            self.parseIQData(iqList)
    
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

    
      
    def parseIQData(self,iqList):
        freq_centr_int_h = iqList[10] << 6
        freq_centr_int_l = iqList[11] & 0x3F
        freq_centr_frac_h = (iqList[11] >> 6)<< 8
        freq_centr_frac_l = iqList[12]
        freq_centr_int = freq_centr_int_h + freq_centr_int_l
        freq_centr_frac = freq_centr_frac_h + freq_centr_frac_l
        freq_centr = freq_centr_int + freq_centr_frac / (10 ** len(str(freq_centr_frac)))
        freq_centr = float('%.4f' % freq_centr)
        
        bandwidth = iqList[13] >> 4
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
            
        N = iqList[14]
        
        for j in range(N):
            IData = []
            QData = []
            for i in range(2000):
                HighI1 = ((iqList[6001 * (j + 1) - 5985 + i * 3]) >> 4) << 8
                LowI1 = iqList[6001 * (j + 1) - 5984 + i * 3]
                if (HighI1 >= 2048):
                    I1 = -(2 ** 12 - HighI1 - LowI1)
                else :
                    I1 = (HighI1 + LowI1)
                IData.append(I1)
        
                HighQ1 = ((iqList[6001 * (j + 1) - 5985 + i * 3]) & 0x0F) << 8
                LowQ1 = iqList[6001 * (j + 1) - 5983 + i * 3]
                if (HighQ1 >= 2048):
                    Q1 = -(2 ** 12 - HighQ1 - LowQ1)
                else :
                    Q1 = (HighQ1 + LowQ1)
                QData.append(Q1)
            
            fk,pk,angle = self.parseIQ(IData, QData, freq_centr, bandwidth_rate)
            self.setLbl(fk, pk)
            self.draw(fk, pk)
            time.sleep(0.3)
            if not j==N:
                self.lineSpec.remove()
                
    def parseIQ(self,IData,QData,freq_centr,bandwidth_rate):
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
        
    def setLbl(self,fk,pk):
        
        
        xticks=linspace(fk[0],fk[-1],10)
        xticklabels = [str('%0.1f' % (i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation = 0)
        
        
        
    def draw(self,fk,pk):
        self.lineSpec.set_xdata(array(fk))
        self.lineSpec.set_ydata(array(pk))
        self.lineSpec,=self.axes.plot(fk,pk,'y')
        self.FigureCanvas.draw()
    
    def set_txt(self,filename,lon,lat,hei,freq_centr,bandwidth_rate): 
        if filename[-2]=='-':
            id_txt = filename[-4:-2]
        else:
            id_txt = filename[-2:]

        
        self.ID.SetLabel(u'终端ID号：' + id_txt)
        self.time_txt.SetLabel(u'时间：' + filename[:19])
        self.lon.SetLabel(u'经-纬-高：'+str('%0.2f'%lon)+'-'+str('%0.2f'%lat)+'-'+str('%0.2f'%hei)+'')
        self.centrFreq.SetLabel(u'中心频率：' + str(freq_centr) + 'MHz')
        self.rate.SetLabel(u'采样率：' + str(bandwidth_rate) + 'MHz')
        self.rbw.SetLabel(u'RBW：' + str('%0.2f' % (float(bandwidth_rate*1000)/2048)) + 'kHz' + u'，' + u'VBW：' + str('%0.2f' % (float(bandwidth_rate*1000)/2048)) + 'kHz'+'')
        self.band.SetLabel(u'带宽：' + str(bandwidth_rate) + 'MHz')

        
    def xlim(self,x_min,x_max):  
        self.axes.set_xlim(x_min,x_max)  
  
    def ylim(self,y_min,y_max):  
        self.axes.set_ylim(y_min,y_max)

    def xlabel(self,XabelString="X"):   
        self.axes.set_xlabel(XabelString)  
  
    def ylabel(self,YabelString="Y"):  
        self.axes.set_ylabel(YabelString)
