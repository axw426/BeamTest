import struct
import sys
from Event import EventData

class FileReader:

    def __init__(self,fileName: str, nSkip: int):
        self.fname=fileName

        #define the expected length for each data entry 
        self.fileHeaderSize=4096
        self.eventHeaderLength=2 #bytes
        self.layerDataLength=2 #bytes
        self.caloDataLength=2 #bytes 
        self.fullEventLength=52 #bytes
        self.nLayers=16

        self.event=0

        #Open file, read header, then skip to first event of interest
        print("Reading File: ", self.fname)
        self.data = open(self.fname,"rb")#.read()
        self.ReadHeader()
        self.Skip(nSkip)


    def ReadHeader(self):
        #print("Reading header")

        #until fixed, just take in the current size and skip it
        self.data.seek(self.fileHeaderSize,1) 

    def Skip(self,nSkip):
        #note, this needs changed based on the final data format
        #self.data.seek(nSkip*self.lengthOfEntry,1) 

        currentEvent=0
        while currentEvent<nSkip:

            #read header to find out number of events in this clock cycle
            entry=int.from_bytes(self.data.read(self.eventHeaderLength))  
            emptyClockCounter=entry & 0b111111111111
            eventCounter=(entry >> 12) & 0b1111
            if not entry:
                break
            
            #skip forward to end of clock cycle
            self.data.seek((eventCounter*self.fullEventLength)-self.eventHeaderLength)        

            currentEvent+=1

        

    def GetNextEvent(self):
        #note to self, if endianness is an issue, can just unpack each 16 bit piece of data into an unsigned int (H)

        while True:

            #get number of hits in this event
            entry=int.from_bytes(self.data.read(self.eventHeaderLength))
            emptyClockCounter=entry & 0b111111111111
            eventCounter=(entry >> 12) & 0b1111
            if not entry:
                break
            self.data.seek(-1*self.eventHeaderLength,1)

            #now read enough blocks for that number of events
            allStrips=[[] for x in range(self.nLayers)]
            rawSamples=[[] for x in range(self.nLayers)]
            for n in range(eventCounter):
                self.data.read(self.eventHeaderLength) #every event has this mini header
                for layer in range(self.nLayers):
                    entry=int.from_bytes(self.data.read(self.layerDataLength))
                    sample= entry & 0b11111111
                    channelAddress=(entry >> 8) & 0b11111111111
                    layerAddress=(entry >> 19) & 0b1111
                    controlBit=(entry >> 23) & 0b1
                    if(controlBit==1):
                        allStrips[layer].append(channelAddress)
                        rawSamples[layer].append(sample)

                self.data.read(self.caloDataLength) 


            #convert raw strip addresses to real addresses based on Daniels mapping

            
            #the important bit: EventData object takes an array of 16 arrays each containing the valid strip addresses for each of the 16 layers
            self.event=EventData(allStrips,rawSamples,emptyClockCounter) 

            yield 

    def PrintEvent(self) -> None:
        print("Printing raw data")
        print(self.rawData)
        self.event.Print()
    


    

  
