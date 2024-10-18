import argparse
from BinaryReader import FileReader
from Plotter import PlotHandler
from pathlib import Path

class DataProcessor():
    def __init__(self,fname,start=0,maxEvents=0,debug=False):
        self.fName=fname
        self.start=0
        self.maxEvents=maxEvents
        self.debug=debug

    def ProcessData(self):

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

            counter+=1
            if(self.maxEvents>0 and counter>self.maxEvents):
                break

        #Extract Useful Info
        self.plotHandler.GetMeanValues()


        '''
        #Plot Hit Maps
        for section in ["XY","UV","Module"]:
            for module in range(4):
                self.plotHandler.PlotHitPos(section,module)
                self.plotHandler.PlotHitsPerClock(section,module)

        
        import time
        start=time.time()
        plotHandler.PlotStripData()

        for layer in range(16):
            plotHandler.PlotStripsPerClock(layer)

        print("This took ",time.time()-start)
        '''