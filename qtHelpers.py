from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QComboBox, QFileDialog, QMenu, QFrame, QScrollArea, QGridLayout, QLineEdit, QPushButton, QHBoxLayout, QSpacerItem, QVBoxLayout, QApplication, QMainWindow, QWidget, QAction, QTabWidget, QLabel
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui
from PyQt5.QtCore import QFile, QTextStream, pyqtSignal
import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np

#this file is simply used to create handy classes for grouping visual elements

class LabelledEdit:
    def __init__(self, label, defaultText="",maxWidth=200,minWidth=400):
        self.label = QLabel(f'<b>{label}</b>')
        #self.label.setMaximumWidth(300)
        self.value = QLineEdit(defaultText)
        self.value.setMaximumWidth(maxWidth)
        self.value.setMinimumWidth(minWidth)

        self.layout=QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value)

    def GetValue(self):
        return self.value.text()
    
    def SetValue(self,newText):
        self.value.setText(newText)

class LabelledCombo:
    def __init__(self, label, options,maxWidth=200,minWidth=400):
        self.label = QLabel(f'<b>{label}</b>')
        #self.label.setMaximumWidth(300)
        self.value = QComboBox()
        for entry in options:
                self.value.addItem(entry)
        self.value.setProperty("ID",0)
        #self.featComboBoxList[-1].currentIndexChanged.connect(self.setFeats)
        #self.featComboBoxList[-1].setInsertPolicy(QComboBox.NoInsert)

        self.value.setMaximumWidth(maxWidth)
        self.value.setMinimumWidth(minWidth)

        self.layout=QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value)
        self.layout.addStretch(1)

    def GetValue(self):
        return self.value.currentText()

class StripPlotObject():
    def __init__(self,xLabel="",yLabel="",showMean=False):
        self.xData=[]
        self.yData=[]
        self.showMean=showMean

        self.plot_graph = pg.PlotWidget()
        if(xLabel!=""):
            self.plot_graph.plotItem.getAxis("bottom").setLabel(xLabel)
        if(yLabel!=""):
            self.plot_graph.plotItem.getAxis("left").setLabel(yLabel)
        #self.plot_graph.setMaximumHeight(250)


    def Plot(self,data):
        self.plot_graph.clear()
        self.plot_graph.plot(data[0],data[1],stepMode=True)
        if self.showMean: 
            mean=np.mean(data[1])
            self.text = pg.TextItem(f"Mean= {mean: .2f}")
            self.plot_graph.addItem(self.text)
            self.text.setPos(0,9)


    def Save(self,directory,layer,label):
        exporter = pg.exporters.ImageExporter(self.plot_graph.plotItem)
        
        # set export parameters if needed
        exporter.parameters()['width'] = 1000   # (note this also affects height parameter)

        # save to file
        exporter.export(f"{directory}/{label}_Layer{layer}.png")

class ModulePlotObject():
    def __init__(self,name):
        self.xData=[]
        self.yData=[]

        #self.label=QLabel(name)

        self.plot=pg.PlotItem()
        self.plot.getAxis("bottom").setLabel("X","cm")
        self.plot.getAxis("left").setLabel("Y","cm")
        self.plot_graph = pg.ImageView(view=self.plot)
        self.plot_graph.view.invertY(False)
        self.plot_graph.view.setLimits(xMin = -180, yMin = -30,xMax=180,yMax=30)
        # Set a small padding to avoid the number form cutting off the edge
        #self.plot_graph.view.setXRange(-180,180, padding= 0.02)
        #self.plot_graph.view.setYRange(-30,30,padding=0.02)
        self.plot_graph.view.setTitle(name)

        self.plot_graph.ui.roiBtn.hide()
        self.plot_graph.ui.menuBtn.hide()
        cm = pg.colormap.get('CET-L9')
        self.plot_graph.setColorMap(cm)
        #self.plot_graph.setMaximumHeight(250)

        meanText=QLabel("<b>Mean:</b>")
        self.means=QLineEdit()
        stdText=QLabel("<b>Std:</b>")
        self.std=QLineEdit()

        self.layout=QGridLayout()
        #self.layout.addWidget(self.label,0,0)
        self.layout.addWidget(self.plot_graph,1,0,1,20)
        self.layout.addWidget(meanText,2,8)
        self.layout.addWidget(self.means,2,9)
        self.layout.addWidget(stdText,2,10)
        self.layout.addWidget(self.std,2,11)
        self.layout.setRowStretch(0,1)
        self.layout.setRowStretch(100,10)

    def Plot(self,data):

        self.plot_graph.clear()

        if data is not None:
            histData=data[0]

            x0, x1 = (-180, 180)
            y0, y1 = (-30, 30)
            xscale = (x1-x0)/histData[0].shape[0]
            yscale = (y1-y0)/histData[0].shape[1]
            self.plot_graph.setImage(histData[0],pos=[x0,y0], scale=[xscale, yscale])

            self.means.setText(f"x={data[1]: .3f}, y={data[2]: .3f}")
            self.std.setText(f"x={data[3]: .3f}, y={data[4]: .3f}")

        else:
            self.means.setText("Data is empty")
            self.std.setText("Data is empty")            

    def Save(self,directory,module):
        exporter = pg.exporters.ImageExporter(self.plot)
        
        # set export parameters if needed
        exporter.parameters()['width'] = 1000   # (note this also affects height parameter)

        # save to file
        exporter.export(f"{directory}/ModuleHits_Module{module}.png")