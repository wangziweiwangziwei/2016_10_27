# -*- coding: utf-8 -*- 
import wx.aui 
import matplotlib
from numpy import array, linspace
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas 


class IQ2_Spec(wx.aui.AuiMDIChildFrame):
    def __init__(self,parent):
        wx.aui.AuiMDIChildFrame.__init__(self,parent,-1,title=u"iq2功率谱图             ")
        self.parent=parent
        self.CreatePanel()
        
    def CreatePanel(self):
        self.Figure = matplotlib.figure.Figure()
        self.axes=self.Figure.add_axes([0.05,0.05,0.93,0.93])
        self.FigureCanvas = FigureCanvas(self,-1,self.Figure)
        self.rbw = wx.StaticText(self,-1,u'   RBW:_____')
        self.vbw = wx.StaticText(self,-1,u'   VBW:_____')
#         self.show_txt = wx.StaticText(self, -1, u'显示模式：')
        self.showList = [u"瞬时功率谱",u"最大保持",u"最小保持",u"迹线平均"]
        self.show_box = wx.ComboBox(self,-1,u"瞬时功率谱",choices = self.showList,style = wx.CB_DROPDOWN)
        self.dBFS_txt = wx.StaticText(self,-1,u"dBFS")
        self.Hz_txt = wx.StaticText(self,-1,u"Hz")
        self.dBFS_txt.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Hz_txt.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        #################################################################
        self.SetSizeHintsSz(wx.DefaultSize,wx.DefaultSize)
        m_bSizer = wx.BoxSizer(wx.VERTICAL)
        
        gSizer = wx.GridSizer(1,5,0,0)
        gSizer.Add(self.rbw,0,wx.ALL,5)
        gSizer.Add(self.vbw,0,wx.ALL,5)
        gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
        gSizer.AddSpacer((0,0),1,wx.EXPAND,5)
        gSizer.Add(self.show_box,0,wx.ALL,5)
        m_bSizer.Add(gSizer,0,wx.ALL|wx.EXPAND,5)
        
        bSizer = wx.BoxSizer(wx.HORIZONTAL)
        gSizer2 = wx.GridSizer(1,1,0,0)
        gSizer2.Add(self.dBFS_txt,0,wx.ALIGN_CENTER|wx.ALL,5)
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
        self.lineSpec,=self.axes.plot(self.xData,self.yData,'y')
        self.axes.grid(True)
        
    def setLbl_draw(self,fk,pk):
        self.xlim(fk[0],fk[-1])
        self.ylim(-100,100)
        xticks=linspace(fk[0],fk[-1],10)
        xticklabels = [str('%0.1f' % (i)) for i in xticks]
        yticks=linspace(-100,100,11)  
        yticklabels = [str(int(i)) for i in yticks]  
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels,rotation = 0)
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(yticklabels,rotation = 0)
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
