# -*- coding: utf-8 -*- 
import wx
import wx.aui 
import matplotlib
import matplotlib.pyplot as plt
from numpy import array, linspace,sin,cos,pi,short
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas 
from matplotlib.cm import jet 
from math import log10,sqrt,log10
import scipy.signal as signal
import pyaudio





class DrawPanel(wx.aui.AuiMDIChildFrame):
    def __init__(self,parent,fk,pk,angle,data):
        wx.aui.AuiMDIChildFrame.__init__(self,parent,-1,title=u"解调回放信号             ")
        self.parent=parent
       
        main_sp = wx.SplitterWindow(self,style=wx.SP_3D)
        

         
#         menu_sp = wx.SplitterWindow(main_sp,style=wx.SP_3D)
#         self.menu = MenuSet(main_sp)
#         draw_sp = wx.SplitterWindow(main_sp,style=wx.SP_3D)
#         main_sp.SplitVertically(self.menu,draw_sp)
#         main_sp.SetSashGravity(0.2)
#         
#         self.spec = IQ2_Spec(draw_sp,fk,pk,data)
#         self.wave = IQ2_Wave(draw_sp,data)
#         draw_sp.SplitHorizontally(self.spec,self.wave)
#         draw_sp.SetSashGravity(0.55)
        
        
        
        #############以下是一个菜单 上下左右四个图的分割
        left_sp = wx.SplitterWindow(main_sp)
        self.menu = MenuSet(left_sp)
        draw_sp = wx.SplitterWindow(left_sp,style=wx.SP_3D)
        left_sp.SplitVertically(self.menu,draw_sp)
        left_sp.SetSashGravity(0.3)
 
        self.sp1 = IQ2_Spec(draw_sp,fk,pk)
        self.sp3 = IQ2_Wave(draw_sp,data)
 
        draw_sp.SplitHorizontally(self.sp1,self.sp3)
        draw_sp.SetSashGravity(0.5)
 
          
        right_sp = wx.SplitterWindow(main_sp,style=wx.SP_3D)
        self.sp2 = IQ2_Water(right_sp,fk,pk)
        self.sp4 = IQ2_Phase(right_sp,fk,angle) 
        right_sp.SplitHorizontally(self.sp2,self.sp4)
        right_sp.SetSashGravity(0.5)
 
         
        main_sp.SplitVertically(left_sp,right_sp)
        main_sp.SetSashGravity(0.6)

         

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(main_sp,1,wx.EXPAND|wx.ALL,5)
        self.SetSizer(sizer)
        self.Layout()
        

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
                self.pl_file_path.AppendText(item)
                self.pl_file_path.AppendText(';')

        
    def setPlaybackClick(self,evt):
        f1 = float(self.pass_sideband_f1.GetValue())
        f2 = float(self.stop_sideband_f2.GetValue())
        A = float(self.stop_att_A.GetValue())
        
#         bw_3dB = float(self.bandwidth.GetValue())
#         order = int(self.order.GetValue())
        
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
    def __init__(self,parent,fk,pk):
        wx.Panel.__init__(self,parent)
        self.parent = parent
        self.CreatePanel(fk,pk)
#         self.fk = fk
#         self.pk = pk
#         self.data = data
#         self.draw_change()
        
#         self.setLbl_draw(fk, pk)
        
    def CreatePanel(self,fk,pk):
        self.Figure = matplotlib.figure.Figure()
        self.axes=self.Figure.add_axes([0.1,0.1,0.8,0.8])
        self.FigureCanvas = FigureCanvas(self,-1,self.Figure)
        self.rbw = wx.StaticText(self,-1,u'RBW:')
        self.vbw = wx.StaticText(self,-1,u'VBW:')
        self.centrFreq = wx.StaticText(self,-1,u"中心频率:")
        self.drawList = [u"功率谱图",u"瀑布图",u"相位谱图"]
        self.drawBox = wx.ComboBox(self,-1,u"功率谱图",choices=self.drawList,style = wx.CB_DROPDOWN)
        self.drawBox.SetSelection(0)
        self.showList = [u"瞬时功率谱",u"最大保持",u"最小保持",u"迹线平均"]
        self.title = wx.StaticText(self,-1,u"功率谱图")
        self.title.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
#         self.stop_btn = wx.Button(self,-1,u"停止画图")
        self.show_box = wx.ComboBox(self,-1,u"瞬时功率谱",choices = self.showList,style = wx.CB_DROPDOWN)
#         self.dBFS_txt = wx.StaticText(self,-1,u"dBFS")
        self.Hz_txt = wx.StaticText(self,-1,u"MHz")
#         self.dBFS_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Hz_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        #################################################################
        self.SetSizeHintsSz(wx.DefaultSize,wx.DefaultSize)
        m_bSizer = wx.BoxSizer(wx.VERTICAL)
        
        gSizer = wx.GridSizer(1,3,0,0)
#         gSizer.AddSpacer((0,0),1,wx.ALL,5)
        gSizer.Add(self.drawBox,0,wx.ALL,5)
        gSizer.Add(self.title,0,wx.ALL,5)
#         gSizer.Add(self.stop_btn,0,wx.ALL,5)
#         gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
#         gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
#         gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
        gSizer.Add(self.show_box,0,wx.ALL,5)
        m_bSizer.Add(gSizer,0,wx.ALL|wx.EXPAND,5)
        
        bSizer = wx.BoxSizer(wx.HORIZONTAL)
#         gSizer2 = wx.GridSizer(1,1,0,0)
#         gSizer2.Add(self.dBFS_txt,0,wx.ALIGN_CENTER|wx.ALL,5)
        gSizer3 = wx.GridSizer(1,1,0,0)
        gSizer3.Add(self.FigureCanvas,1,wx.EXPAND,5)
#         bSizer.Add(gSizer2,0,wx.ALL|wx.ALIGN_CENTER,5)
        bSizer.Add(gSizer3,5,wx.EXPAND,5)
        m_bSizer.Add(bSizer,4,wx.EXPAND,5)
        
        gSizer4 = wx.GridSizer(1,1,0,0)
        gSizer4.Add(self.Hz_txt,0,wx.ALIGN_CENTER|wx.EXPAND,5)
        m_bSizer.Add(gSizer4,0,wx.ALL|wx.ALIGN_CENTER,5)
        
        gSizer5 = wx.GridSizer(1,3,0,0)
        gSizer5.Add(self.rbw,0,wx.ALL,5)
        gSizer5.Add(self.vbw,0,wx.ALL,5)
        gSizer5.Add(self.centrFreq,0,wx.ALL|wx.ALIGN_BOTTOM,5)
        m_bSizer.Add(gSizer5,0,wx.ALL,5)
        
        self.SetSizer(m_bSizer)
        self.Layout()
        self.Centre(wx.BOTH)
            
        #####################################################################################
        self.xData = linspace(1,100,2048)
        self.yData = [0] * 2048
        self.lineSpec,=self.axes.plot(self.xData,self.yData,'y')
        self.axes.grid(True)
        
        self.xlim(fk[0],fk[-1])
        self.ylim(-150,0)
        self.ylabel('dBFS')
#         self.xlabel('MHz')
        
        xticks=linspace(fk[0],fk[-1],9)
        xticklabels = [str('%0.1f' % (i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation = 0)
        
        yticks=linspace(-150,0,11)  
        yticklabels = [str(int(i)) for i in yticks]  
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation = 0)
    
    
#     def draw_change(self):
#         index = self.drawBox.GetSelection()
#         if index == 0 :
#             self.CreatePanel(self.fk, self.pk)    
#             self.setLbl_draw(self.fk, self.pk)
#         elif index == 2 :
#             self.CreatePanel(self.fk, self.data)
#             self.setLbl_draw(self.fk, self.data)
#             self.title.SetLabel(u'相位谱图')
    
    def set_rbw_centrFreq(self,freq_centr,bandwidth_rate):    
        self.rbw.SetLabel('rbw:' + str('%0.3f' % (float(bandwidth_rate*1000)/2048)) + 'kHz')
        self.vbw.SetLabel('vbw:' + str('%0.3f' % (float(bandwidth_rate*1000)/2048)) + 'kHz')
        self.centrFreq.SetLabel(u'中心频率:' + str(freq_centr) + 'MHz')
        
    def setLbl_draw(self,fk,pk):
        xticks=linspace(fk[0],fk[-1],9)
        xticklabels = [str('%0.1f' % (i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation = 0)
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
        
class IQ2_Phase(wx.Panel):
    def __init__(self,parent,fk,angle):
        wx.Panel.__init__(self,parent)
        self.CreatePanel(fk,angle)
#         self.setLbl_draw(fk, pk)
        
    def CreatePanel(self,fk,pk):
        self.Figure = matplotlib.figure.Figure()
        self.axes=self.Figure.add_axes([0.1,0.1,0.8,0.8])
        self.FigureCanvas = FigureCanvas(self,-1,self.Figure)
        self.title = wx.StaticText(self,-1,u"相位谱图")
        self.title.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.angle_txt = wx.StaticText(self,-1,u"度")
        self.Hz_txt = wx.StaticText(self,-1,u"MHz")
        self.angle_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Hz_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        #################################################################
        self.SetSizeHintsSz(wx.DefaultSize,wx.DefaultSize)
        m_bSizer = wx.BoxSizer(wx.VERTICAL)
        
        gSizer = wx.GridSizer(1,5,0,0)
        gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
        gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
        gSizer.Add(self.title,0,wx.ALL,5)
        m_bSizer.Add(gSizer,0,wx.ALL|wx.EXPAND,5)
        
        bSizer = wx.BoxSizer(wx.HORIZONTAL)
        gSizer2 = wx.GridSizer(1,1,0,0)
        gSizer2.Add(self.angle_txt,0,wx.ALIGN_CENTER|wx.ALL,5)
        gSizer3 = wx.GridSizer(1,1,0,0)
        gSizer3.Add(self.FigureCanvas,1,wx.EXPAND,5)
        bSizer.Add(gSizer2,0,wx.ALL|wx.ALIGN_CENTER,5)
        bSizer.Add(gSizer3,5,wx.EXPAND,5)
        m_bSizer.Add(bSizer,4,wx.EXPAND,5)
        
        gSizer4 = wx.GridSizer(1,1,0,0)
        gSizer4.Add(self.Hz_txt,0,wx.ALIGN_CENTER|wx.EXPAND,5)
        m_bSizer.Add(gSizer4,0,wx.ALL|wx.ALIGN_CENTER,5)
        
        self.SetSizer(m_bSizer)
        self.Layout()
        self.Centre(wx.BOTH)
            
        #####################################################################################
        self.xData = linspace(1,100,2048)
        self.yData = [0] * 2048
        self.lineSpec,=self.axes.plot(self.xData,self.yData,'b')
        self.axes.grid(True)
        
        self.xlim(fk[0],fk[-1])
        self.ylim(-200,200)
        xticks=linspace(fk[0],fk[-1],9)
        xticklabels = [str('%0.1f' % (i)) for i in xticks]
        yticks=linspace(-200,200,11)  
        yticklabels = [str(int(i)) for i in yticks]  
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation = 0)
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation = 0)
        self.lineSpec.set_xdata(array(fk))
        
    def setLbl_draw(self,fk,angle):
        xticks=linspace(fk[0],fk[-1],9)
        xticklabels = [str('%0.1f' % (i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation = 0)

        self.lineSpec.set_ydata(array(angle))
        self.FigureCanvas.draw()
    
    def xlim(self,x_min,x_max):  
        self.axes.set_xlim(x_min,x_max)  
  
    def ylim(self,y_min,y_max):  
        self.axes.set_ylim(y_min,y_max)

    def xlabel(self,XabelString="X"):   
        self.axes.set_xlabel(XabelString)  
  
    def ylabel(self,YabelString="Y"):  
        self.axes.set_ylabel(YabelString)
        
class IQ2_Water(wx.Panel):
    def __init__(self,parent,fk,pk):
        wx.Panel.__init__(self,parent )

        self.parent=parent
        self.waterFirst=1
        self.col=2048
        self.row=1000
        self.rowCpy=5
        self.CreatePanel(fk,pk)
        
    def CreatePanel(self,fk,pk):
        self.Figure = matplotlib.figure.Figure(figsize=(1,1))
        self.axes=self.Figure.add_axes([0.1,0.1,0.8,0.8])
        self.FigureCanvas = FigureCanvas(self,-1,self.Figure)
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        bSizer = wx.BoxSizer(wx.VERTICAL)
        self.title = wx.StaticText(self,-1,u"瀑布图")
        self.title.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        gSizer = wx.GridSizer(1,5,0,0)
        gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
        gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
        gSizer.Add(self.title,0,wx.ALL,5)
        bSizer.Add(gSizer,0,wx.EXPAND,5)
        bSizer.Add( self.FigureCanvas, 1, wx.EXPAND, 5 )
        self.SetSizer( bSizer )
        self.Layout()
        
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
        
#         self.ylabel('Frame Number')
        self.xlabel('MHz')

        xticks = linspace(0,self.col,9)
        self.axes.set_xticks(xticks)
        label = linspace(fk[0],fk[-1],9)
        xticklabels = ['%0.1f' % i for i in label]
        self.axes.set_xticklabels(xticklabels, rotation=0) 
        intervalY = self.row / 10
        yticks = range(0, self.row+1, intervalY)
        yticklabels = [str(i) for i in yticks]
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation=0)  
        
    def setLbl_draw(self,pk):

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

class IQ2_Wave(wx.Panel):

    def __init__(self,parent,data):
        wx.Panel.__init__(self,parent)
        self.CreatePanel(data)

        
    def CreatePanel(self,data):
        self.Figure = matplotlib.figure.Figure()
        self.axes=self.Figure.add_axes([0.1,0.1,0.8,0.8])
        self.FigureCanvas = FigureCanvas(self,-1,self.Figure)
        self.title = wx.StaticText(self,-1,u"解调后归一化波形图")
        self.title.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.angle_txt = wx.StaticText(self,-1,u"")
        self.Hz_txt = wx.StaticText(self,-1,u"")
        self.angle_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Hz_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        #################################################################
        self.SetSizeHintsSz(wx.DefaultSize,wx.DefaultSize)
        m_bSizer = wx.BoxSizer(wx.VERTICAL)
        
        gSizer = wx.GridSizer(1,5,0,0)
        gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
        gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
        gSizer.Add(self.title,0,wx.ALL,5)
        m_bSizer.Add(gSizer,0,wx.ALL|wx.EXPAND,5)
        
        bSizer = wx.BoxSizer(wx.HORIZONTAL)
        gSizer2 = wx.GridSizer(1,1,0,0)
        gSizer2.Add(self.angle_txt,0,wx.ALIGN_CENTER|wx.ALL,5)
        gSizer3 = wx.GridSizer(1,1,0,0)
        gSizer3.Add(self.FigureCanvas,1,wx.EXPAND,5)
        bSizer.Add(gSizer2,0,wx.ALL|wx.ALIGN_CENTER,5)
        bSizer.Add(gSizer3,5,wx.EXPAND,5)
        m_bSizer.Add(bSizer,4,wx.EXPAND,5)
        
        gSizer4 = wx.GridSizer(1,1,0,0)
        gSizer4.Add(self.Hz_txt,0,wx.ALIGN_CENTER|wx.EXPAND,5)
        m_bSizer.Add(gSizer4,0,wx.ALL|wx.ALIGN_CENTER,5)
        
        self.SetSizer(m_bSizer)
        self.Layout()
        self.Centre(wx.BOTH)
            
        #####################################################################################
        self.xData = linspace(1,2000,2000)
        self.yData = [0] * 2000
        self.lineSpec,=self.axes.plot(self.xData,self.yData,'r')
        self.axes.grid(True)
        
#         self.xlim(fk[0],fk[-1])
#         self.ylim(-200,200)
        xticks = linspace(0,2000,11)
        xticklabels = [str(int(i)) for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation = 0)
        
        yticks=linspace(-2,2,9)  
        yticklabels = [str('%0.1f' % (i)) for i in yticks]  
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation = 0)
        
        self.lineSpec.set_xdata([i for i in xrange(2000)])
#         self.lineSpec.set_xdata(array(fk))
        
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