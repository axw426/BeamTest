
import sys
import time
import os

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QFileDialog, QMenu, QFrame, QGridLayout, QLineEdit, QPushButton, QHBoxLayout, QSpacerItem, QVBoxLayout, QApplication, QMainWindow, QWidget, QAction, QTabWidget, QLabel
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui
from PyQt5.QtCore import QFile, QTextStream, pyqtSignal

from qtHelpers import *
from BinaryReader import FileReader
from Plotter import PlotHandler
from pathlib import Path

class BeamTestUi(QMainWindow):

    def __init__(self):
        """View initializer."""
        super().__init__()

        # Set main window's properties
        self.setWindowTitle('OPTIma Beam Test')
        #self.setWindowIcon(QtGui.QIcon("Images/Optima.png"))
        
        # Set up the central widget 
        self.widget = QWidget()                 
        self.widget.setMaximumWidth(QApplication.primaryScreen().size().width()) #set maximum display width to be screen size to avoid scrolling

        #create tabs
        self.tabs = QTabWidget()
        self.stripsTab = QWidget()
        self.moduleTab = QWidget()
        self.timingTab = QWidget() 
        self.otherTab = QWidget() 

        # Add tabs
        self.tabs.addTab(self.stripsTab,"Strip Hits")
        self.tabs.addTab(self.moduleTab,"Module Hits")
        self.tabs.addTab(self.timingTab,"Timing Info")
        self.tabs.addTab(self.otherTab,"Other")
  
        self.generalLayout = QGridLayout()
        self.widget.setLayout(self.generalLayout)
        self.stripTabLayout = QGridLayout()
        self.stripsTab.setLayout(self.stripTabLayout)
        self.moduleTabLayout = QGridLayout()
        self.moduleTab.setLayout(self.moduleTabLayout) 
        self.timingTabLayout = QGridLayout()
        self.timingTab.setLayout(self.timingTabLayout)
        self.otherTabLayout = QGridLayout()
        self.otherTab.setLayout(self.otherTabLayout)

        self.setCentralWidget(self.widget)
        
        #intialize variables
        self.fileName=""
        self.plotHandler=PlotHandler()

        # Create all sections
        self.CreateMenuBar()
        self.CreateOptions()
        self.CreateStripsTab()
        self.CreateModulesTab()
        self.CreateTimingTab()
        self.CreateOtherTab()

        self.generalLayout.addLayout(self.optionsLayout,0,0)
        self.generalLayout.addWidget(self.tabs,1,0)


        #Maximise the window
        self.showMaximized()
    
    def CreateMenuBar(self):
        
        #create menu bar
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        #create actions and add slots
        self.saveAction = QAction("&SavePlots...", self)
        self.saveAction.triggered.connect(self.savePlots)

        self.loadAction = QAction("&Open...", self)
        self.loadAction.triggered.connect(self.loadFile)
        
        #add actions to menu bar
        fileMenu.addAction(self.loadAction)
        fileMenu.addAction(self.saveAction)

    def SetStatus(self,colour,text=None):
        #Sets status colour and text
        self.analyseButtom.setStyleSheet(f"background-color: {colour};border : 2px solid black; padding-top: 15px; padding-bottom: 15px; padding-left: 5px; padding-right: 5px")
        if text is not None:
            self.outputStatus.setText(text)

    def CreateOptions(self):

        #create input options
        self.fileInput=LabelledEdit("File Name","")
        self.fileInput.value.textChanged.connect(lambda: self.SetStatus("orange","Options changed, hit run analysis..."))
        self.nEventsInFileLabel=QLabel("")
        self.startInput=LabelledEdit("Starting Event","0")
        self.startInput.value.textChanged.connect(lambda: self.SetStatus("orange","Options changed, hit run analysis..."))
        self.maxEventsInput=LabelledEdit("Max Events (0=no max)","0")
        self.maxEventsInput.value.textChanged.connect(lambda: self.SetStatus("orange","Options changed, hit run analysis..."))
        self.refreshRate=LabelledEdit("Update plots every N events (0=end)","1000")
        self.refreshRate.value.textChanged.connect(lambda: self.SetStatus("orange","Options changed, hit run analysis..."))
        self.selectFile=QPushButton("Select File",self)
        self.selectFile.setMaximumWidth(100)
        self.selectFile.clicked.connect(self.loadFile)

        self.outputStatus=QLabel("Please select an input file")
        self.outputStatus.setWordWrap(True)
        self.analyseButtom=QPushButton("Run Analysis",self)
        #newFont=QtGui.QFont(self.analyseButtom.font())
        #newFont.setPointSize(30)
        #self.analyseButtom.setFont(newFont)
        #self.analyseButtom.setMinimumSize(80,80)
        #self.analyseButtom.setMaximumWidth(100)
        self.SetStatus("red")
        self.analyseButtom.clicked.connect(self.analyseData)

        #set layout
        self.optionsLayout=QGridLayout()
        self.optionsLayout.addLayout(self.fileInput.layout,0,0)
        self.optionsLayout.addWidget(self.selectFile,0,1)
        self.optionsLayout.addWidget(self.nEventsInFileLabel,1,1)
        self.optionsLayout.addLayout(self.startInput.layout,1,0)
        self.optionsLayout.addLayout(self.maxEventsInput.layout,0,3)
        self.optionsLayout.addLayout(self.refreshRate.layout,1,3)
        self.optionsLayout.addWidget(self.analyseButtom,0,5,2,2)
        self.optionsLayout.addWidget(self.outputStatus,0,7,2,1)

        self.optionsLayout.setColumnMinimumWidth(2,80)
        self.optionsLayout.setColumnStretch(8,10)

    def CreateOtherTab(self):
        temp=QLabel("Will add things like subsampling info here")
        self.otherTabLayout.addWidget(temp,0,0)

    def CreateTimingTab(self):
        #Tab showing hits as a function of time for each layer

        #create plot objects
        self.timingPlots=[]
        for i in range(16):
            self.timingPlots.append(StripPlotObject(xLabel="Clock Cycle",showMean=True))

        #add labels
        for i in range(4):
            label=QLabel(f"<b>Module {i}</b>")
            label.setAlignment(Qt.AlignCenter)
            self.timingTabLayout.addWidget(label,0,i+1)

        for i,value in enumerate(["nHits\n XY","nHits\n YX","nHits\n U","nHits\n V"]):
            label=QLabel(f"<b>{value}</b>")
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignCenter)
            self.timingTabLayout.addWidget(label,i+1,0)

        #add objects to the layout
        for i in range(16):
            self.timingTabLayout.addWidget(self.timingPlots[i].plot_graph,i%4+1,(int)(i/4)+1)
     
    def CreateStripsTab(self):
        #creates histograms of strips hit

        #create plot objects
        self.stripPlots=[]
        for i in range(16):
            self.stripPlots.append(StripPlotObject(xLabel="Strip Number"))

        #add labels
        for i in range(4):
            label=QLabel(f"<b>Module {i}</b>")
            label.setAlignment(Qt.AlignCenter)
            self.stripTabLayout.addWidget(label,0,i+1)

        for i,value in enumerate(["nHits\n XY","nHits\n YX","nHits\n U","nHits\n V"]):
            label=QLabel(f"<b>{value}</b>")
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignCenter)
            self.stripTabLayout.addWidget(label,i+1,0)

        #add objects to the layout
        for i in range(16):
            self.stripTabLayout.addWidget(self.stripPlots[i].plot_graph,i%4+1,(int)(i/4)+1)

    def CreateModulesTab(self):
        #Shows hit map for each module (XY,UV, Full module)
        
        #create option dialogues
        self.hitTypeChoice=LabelledCombo("Hit Type",["Full Module","Full Module (2 layer hits allowed)","XY Only","UV Only"])
        self.hitTypeChoice.value.currentIndexChanged.connect(self.UpdatePlots)

        #create plot objects
        self.modulePlots=[]
        for i in range(4):
            self.modulePlots.append(ModulePlotObject(f"<b>Module {i}</b>"))
        
        #layout
        self.moduleTabLayout.addLayout(self.hitTypeChoice.layout,1,1,1,2)
        for i in range(4):
            self.moduleTabLayout.addLayout(self.modulePlots[i].layout,(int)(i/2)+3,i%2+1)
        self.moduleTabLayout.setRowStretch(0,2)
        self.moduleTabLayout.setRowStretch(2,2)
        self.moduleTabLayout.setRowStretch(3,10)
        self.moduleTabLayout.setRowStretch(4,10)
  
    def loadFile(self):
        self.fileName = QFileDialog.getOpenFileName(self, 'Open File',filter="Binary files (*.bin)")[0]
        self.fileInput.SetValue(self.fileName)

        fSize=os.path.getsize(self.fileName)
        headerSize=0
        lengthOfEntry=200
        self.nEventsInFile=(int)((fSize-headerSize)/lengthOfEntry)
        self.nEventsInFileLabel.setText(f"Events in File= {self.nEventsInFile}")

    
    def savePlots(self):
        self.outputDir=QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        for layer in range(16):
            self.stripPlots[layer].Save(self.outputDir,layer,"StripNumber")
            self.timingPlots[layer].Save(self.outputDir,layer,"HitsPerClockCycle")

        for module in range(4):
            self.modulePlots[module].Save(self.outputDir,module)

    def analyseData(self):

        start=time.time()
        #enclose in try loop to identify when analysis fails
        try:

            #set all parameters
            self.fName=self.fileInput.GetValue()
            self.start=(int)(self.startInput.GetValue())
            self.maxEvents=(int)(self.maxEventsInput.GetValue())
            refreshRateValue=(int)(self.refreshRate.GetValue())
            self.debug=False

            #update status
            self.SetStatus("orange",f"Running analysis, processed 0/{self.nEventsInFile-self.start}")

            #setup files and plot handler
            reader=FileReader(self.fName, self.start)
            self.plotHandler=PlotHandler()
            outputDir=Path(self.fName).stem
            self.plotHandler.SetOutputDirectory("Plots/"+outputDir)

            #loop over events
            counter=0
            for event in reader.GetNextEvent():
                
                if(self.debug):
                    print("Event",counter)
                    reader.event.Print()

                #update plot handler
                self.plotHandler.AddEvent(reader.event)
                counter+=1

                if(self.maxEvents>0 and counter>self.maxEvents):
                    break

                #update plots at user defined interval
                if refreshRateValue>0 and counter%refreshRateValue==0:
                    self.SetStatus("orange",f"Running analysis, processed {counter}/{self.nEventsInFile-self.start}")
                    self.plotHandler.GetMeanValues()
                    self.UpdatePlots()
                    QApplication.processEvents() #updates GUI while still executing the loop



            #Extract useful info and update plots
            self.plotHandler.GetMeanValues()
            print("Analysis took ",time.time()-start)
            self.UpdatePlots()

            self.SetStatus("green","Analysis complete!!")
        except Exception as error:
            print(error)
            self.SetStatus("red","Analysis failed! Please check options are valid")

    def UpdatePlots(self):
        #refreshes data for all plots in every tab

        start=time.time()
        for i in range(16):
            self.stripPlots[i].Plot(self.plotHandler.GetStripHistogram(i))
            self.timingPlots[i].Plot(self.plotHandler.GetTimingHistogram(i))

        for i in range(4):
            self.modulePlots[i].Plot(self.plotHandler.GetModuleData(i,self.hitTypeChoice.GetValue()))

        print("Updating plots took ",time.time()-start)

def main():
    """Main function."""
    # Create an instance of QApplication
    beamTest = QApplication(sys.argv)

    # Show the GUI
    view = BeamTestUi()
    view.show()


    # Execute the apps main loop
    sys.exit(beamTest.exec_())

if __name__ == '__main__':
    main() 
