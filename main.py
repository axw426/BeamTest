
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

        # Set some main window's properties
        self.setWindowTitle('OPTIma Beam Test')
        #self.setWindowIcon(QtGui.QIcon("Images/5eEmblem.png"))
        
        # Set up the central widget 
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.widget.setMaximumWidth(QApplication.primaryScreen().size().width()) #set maximum display width to be screen size to avoid scrolling

        self.fileName=""

        #create tabs
        self.tabs = QTabWidget()
        self.stripsTab = QWidget()
        self.moduleTab = QWidget()
        self.timingTab = QWidget() 

        # Add tabs
        self.tabs.addTab(self.stripsTab,"Strip Hits")
        self.tabs.addTab(self.moduleTab,"Module Hits")
        self.tabs.addTab(self.timingTab,"Timing Info")
  
        self.generalLayout = QGridLayout()
        self.widget.setLayout(self.generalLayout)
        self.timingTabLayout = QGridLayout()
        self.timingTab.setLayout(self.timingTabLayout)
        self.stripTabLayout = QGridLayout()
        self.stripsTab.setLayout(self.stripTabLayout)
        self.moduleTabLayout = QGridLayout()
        self.moduleTab.setLayout(self.moduleTabLayout) 

        self.setCentralWidget(self.widget)
        
        # Create all sections
        self.CreateMenuBar()
        self.CreateOptions()
        self.CreateTimingTab()
        self.CreateStripsTab()
        self.CreateModulesTab()


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
        #self.saveAction = QAction("&Save...", self)

        #create actions and add slots
        self.loadAction = QAction("&Open...", self)
        self.loadAction.triggered.connect(self.loadFile)
        
        #add actions to menu bar
        fileMenu.addAction(self.loadAction)

    def SetStatus(self,colour,text=None):
        self.analyseButtom.setStyleSheet(f"background-color: {colour}")
        if text is not None:
            self.outputStatus.setText(text)

    def CreateOptions(self):
        self.fileInput=LabelledEdit("File Name","")
        self.fileInput.value.textChanged.connect(lambda: self.SetStatus("orange","Options changed, hit run analysis..."))
        self.nEventsInFileLabel=QLabel("")
        self.startInput=LabelledEdit("Starting Event","0")
        self.startInput.value.textChanged.connect(lambda: self.SetStatus("orange","Options changed, hit run analysis..."))
        self.maxEventsInput=LabelledEdit("Max Events (0=no max)","0")
        self.maxEventsInput.value.textChanged.connect(lambda: self.SetStatus("orange","Options changed, hit run analysis..."))
        self.refreshRate=LabelledEdit("Update plots every N events (0=end)","0")
        self.refreshRate.value.textChanged.connect(lambda: self.SetStatus("orange","Options changed, hit run analysis..."))
        self.selectFile=QPushButton("Select File",self)
        self.selectFile.setMaximumWidth(100)
        self.selectFile.clicked.connect(self.loadFile)

        self.outputStatus=QLabel("Please select an input file")
        self.analyseButtom=QPushButton("Run Analysis",self)
        self.analyseButtom.setStyleSheet("border : 20px solid black;")
        #self.analyseButtom.setMinimumSize(80,80)
        #self.analyseButtom.setMaximumWidth(100)
        self.SetStatus("red")
        self.analyseButtom.clicked.connect(self.analyseData)

        spacer=QSpacerItem(2000,10)

        self.optionsLayout=QGridLayout()
        self.optionsLayout.addLayout(self.fileInput.layout,0,0)
        self.optionsLayout.addWidget(self.selectFile,0,1)
        self.optionsLayout.addWidget(self.nEventsInFileLabel,1,1)
        self.optionsLayout.addLayout(self.startInput.layout,1,0)
        self.optionsLayout.addLayout(self.maxEventsInput.layout,0,3)
        self.optionsLayout.addLayout(self.refreshRate.layout,1,3)
        self.optionsLayout.addWidget(self.analyseButtom,0,5,2,2)
        self.optionsLayout.addWidget(self.outputStatus,0,7,2,1)
        #self.optionsLayout.addItem(spacer,0,2)

        self.optionsLayout.setColumnMinimumWidth(2,80)
        self.optionsLayout.setColumnStretch(8,10)

    def CreateTimingTab(self):

        #want some timing plots
        #median number of hits as a function of time in  each module

        pass

        
    def CreateStripsTab(self):
        
        self.stripPlots=[]
        for i in range(16):
            self.stripPlots.append(StripPlotObject())

        for i in range(4):
            label=QLabel(f"<b>Module {i}</b>")
            label.setAlignment(Qt.AlignCenter)
            self.stripTabLayout.addWidget(label,0,i+1)

        for i,value in enumerate(["XY","YX","U","V"]):
            label=QLabel(f"<b>{value}</b>")
            label.setAlignment(Qt.AlignCenter)
            self.stripTabLayout.addWidget(label,i+1,0)


        for i in range(16):
            self.stripTabLayout.addWidget(self.stripPlots[i].plot_graph,i%4+1,(int)(i/4)+1)

    def CreateModulesTab(self):
        
        self.hitTypeChoice=LabelledCombo("Hit Type",["Full Module","XY Only","UV Only"])
        self.hitTypeChoice.value.currentIndexChanged.connect(self.UpdatePlots)

        self.modulePlots=[]
        for i in range(4):
            self.modulePlots.append(ModulePlotObject(f"<b>Module {i}</b>"))
        
        #layout
        self.moduleTabLayout.addLayout(self.hitTypeChoice.layout,0,1,1,2)
        for i in range(4):
            self.moduleTabLayout.addLayout(self.modulePlots[i].layout,(int)(i/2)+1,i%2+1)
        self.moduleTabLayout.setRowStretch(0,5)
        self.moduleTabLayout.setRowStretch(1,10)
        self.moduleTabLayout.setRowStretch(2,10)
  

    def loadFile(self):

        self.fileName = QFileDialog.getOpenFileName(self, 'Open File',filter="bin (*.bin);")[0]
        self.fileInput.SetValue(self.fileName)

        fSize=os.path.getsize(self.fileName)
        headerSize=0
        lengthOfEntry=200
        self.nEventsInFile=(int)((fSize-headerSize)/lengthOfEntry)
        self.nEventsInFileLabel.setText(f"Events in File= {self.nEventsInFile}")

        print("Selected",self.fileName)
    
    def analyseData(self):

        #print("Analysing Data")
        start=time.time()

        try:

            self.fName=self.fileInput.GetValue()
            self.start=(int)(self.startInput.GetValue())
            self.maxEvents=(int)(self.maxEventsInput.GetValue())
            refreshRateValue=(int)(self.refreshRate.GetValue())

            self.SetStatus("orange",f"Running analysis, processed 0/{self.nEventsInFile-self.start}")


            self.debug=False

            #setup files
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

                self.plotHandler.AddEvent(reader.event)

                if refreshRateValue>0 and counter%refreshRateValue==0:
                    self.SetStatus("orange",f"Running analysis, processed {counter}/{self.nEventsInFile-self.start}")
                    self.plotHandler.GetMeanValues()
                    self.UpdatePlots()
                    QApplication.processEvents() #updates GUI while in the loop

                counter+=1
                if(self.maxEvents>0 and counter>self.maxEvents):
                    break

            #Extract Useful Info
            self.plotHandler.GetMeanValues()

            print("Analysis took ",time.time()-start)
            self.UpdatePlots()

            self.SetStatus("green","Analysis complete!!")
        except Exception as error:
            print(error)
            self.SetStatus("red","Analysis failed! Please check options are valid")

    
    def UpdatePlots(self):
        
        start=time.time()
        for i in range(16):
            self.stripPlots[i].Plot(self.plotHandler.GetStripHistogram(i))

        for i in range(4):
            self.modulePlots[i].Plot(self.plotHandler.GetModuleData(i,self.hitTypeChoice.GetValue()))

        print("Updating plots took ",time.time()-start)

# Client code
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
