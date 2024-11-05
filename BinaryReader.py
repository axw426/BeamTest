import struct
import sys
from Event import EventData

class FileReader:

    def __init__(self,fileName: str, nSkip: int):
        self.fname=fileName

        #define the expected length for each data entry 
        self.nTrackers=4
        self.nHitsPerLayer=4 # number of hits in each line- will be padded with -1 if less tha this
        self.nLayersPerTracker=4
        nCaloBins=28

        nInts=(self.nHitsPerLayer*self.nTrackers*self.nLayersPerTracker)
        self.lengthOfEntry=2*(nInts)+2*(nCaloBins)+4*3+4
        
        self.event=0

        self.dataStructure="h"*nInts +"fff"+"H"*nCaloBins+"f"

        #Open file, read header, then skip to first event of interest
        print("Reading File: ", self.fname)
        self.data = open(self.fname,"rb")#.read()
        self.ReadHeader()
        self.data.seek(nSkip*self.lengthOfEntry,1) 


    def ReadHeader(self):
        print("Reading header")

    def GetNextEvent(self):
        while True:

            entry=self.data.read(self.lengthOfEntry)
            if not entry:
                break

            self.rawData=struct.unpack(self.dataStructure,entry)
            #extract strip data
            allStrips=[]
            for layer in range(16):
                strips=self.rawData[layer*self.nHitsPerLayer:(layer+1)*self.nHitsPerLayer]
                strips=[x for x in strips if x!=-1] #remove empty address
                allStrips.append(strips)
            
            #the important bit: EventData object takes an array of 16 arrays each containing the valid strip addresses for each of the 16 layers
            self.event=EventData(allStrips) 
            yield 

    def PrintEvent(self) -> None:
        print("Printing raw data")
        print(self.rawData)
        self.event.Print()
    


    

  
