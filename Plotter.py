from Event import EventData
import statistics 
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib
import numpy as np

matplotlib.use('agg') 

#plots we want
# - histogram of strips fired in each layer -DONE
# - hit location in each sensor board -DONE
# - hit location in each module -DONE
# - distribution of number of hits per clock  -DONE
# - time of hit within subsample?
# - number of hits per clock cycle

#basic info
# - mean hit position per module- DONE
# - mean number of hits per layer/module- DONE

class PlotHandler():

    def __init__(self):
        self.stripAddresses=[[] for i in range (16)]
        self.xyHits=[[] for i in range (4)]
        self.uvHits=[[] for i in range (4)]
        self.moduleHits=[[] for i in range (4)]

        self.nStripHits=[[] for i in range (16)]
        self.nXYHits=[[] for i in range (4)]
        self.nUVHits=[[] for i in range (4)]
        self.nModuleHits=[[] for i in range (4)]

        self.meanStripsFiredPerLayer=[]
        self.meanXYHitsPerModule=[]
        self.meanUVHitsPerModule=[]
        self.meanHitsPerModule=[]

        self.meanXYHitPos=[]
        self.meanUVHitPos=[]
        self.meanModuleHitPos=[]

        self.nClocks=0
        
        self.outputDirectory="Plots"

        self.dpi=500
        self.imageSize=()
        self.imageWidth=400
        self.dpi=144*10
        self.figsize=(500*10/self.dpi, 500*10/self.dpi)

    def SetOutputDirectory(self,newPath):
        Path(newPath).mkdir(parents=True, exist_ok=True)
        self.outputDirectory=newPath
    
    def AddEvent(self,event: EventData):

        self.nClocks+=1

        #strip addresses
        for i,layer in enumerate(event.stripAddresses):
            self.nStripHits[i].append(len(layer))
            for hit in layer:
                self.stripAddresses[i].append(hit)

        #xy hits
        for i,module in enumerate(event.xyHits):
            self.nXYHits[i].append(len(module))
            for hit in module:
                self.xyHits[i].append(hit)

        #uv hits
        for i,module in enumerate(event.uvHits):
            self.nUVHits[i].append(len(module))
            for hit in module:
                self.uvHits[i].append(hit)

        #module hits
        for i,module in enumerate(event.moduleHits):
            self.nModuleHits[i].append(len(module))
            for hit in module:
                self.moduleHits[i].append(hit)


    def GetStripHistogram(self,layer):
        data=self.stripAddresses[layer]
        y,x = np.histogram(data, bins=[x-0.5 for x in range(1536)])
        return [x,y]
    
    def GetTimingHistogram(self,layer):
        y=self.nStripHits[layer]
        x=[i for i in range(len(y)+1)]
        return [x,y]
    
    def GetModuleData(self,module,hitType):
        if(hitType=="XY Only"):
            rawData=self.xyHits[module]
            xData=[data[0] for data in rawData]
            yData=[data[1] for data in rawData]
        elif(hitType=="UV Only"):
            rawData=self.uvHits[module]
            xData=[data[0] for data in rawData]
            yData=[data[1] for data in rawData]
        if(hitType=="Full Module"):
            rawData=self.moduleHits[module]
            xData=[data[0] for data in rawData]
            yData=[data[1] for data in rawData]

        hist= np.histogram2d(xData, yData, bins=[360,60], range=[[-180,180],[-30,30]], density=None, weights=None)

        if len(xData)>0:
            return [hist,np.mean(xData),np.mean(yData),np.std(xData),np.std(yData)]
        else:
            return None

    def GetMeanValues(self):
        
        for i,values in enumerate(self.nStripHits):
            self.meanStripsFiredPerLayer.append(statistics.fmean(values))
        
        for i in range(len(self.nXYHits)):
            self.meanXYHitsPerModule.append(statistics.fmean(self.nXYHits[i]))
            self.meanUVHitsPerModule.append(statistics.fmean(self.nUVHits[i]))
            self.meanHitsPerModule.append(statistics.fmean(self.nModuleHits[i]))

            if len(self.xyHits[i])>0:
                self.meanXYHitPos.append([statistics.fmean([x[0] for x in self.xyHits[i]]),statistics.fmean([x[1] for x in self.xyHits[i]])])
            else:
                self.meanXYHitPos.append([None,None])

            if len(self.uvHits[i])>0:
                self.meanUVHitPos.append([statistics.fmean([x[0] for x in self.uvHits[i]]),statistics.fmean([x[1] for x in self.uvHits[i]])])
            else:
                self.meanUVHitPos.append([None,None])

            if len(self.moduleHits[i])>0:
                self.meanModuleHitPos.append([statistics.fmean([x[0] for x in self.moduleHits[i]]),statistics.fmean([x[1] for x in self.moduleHits[i]])])
            else:
                self.meanModuleHitPos.append([None,None])

        '''
        print("MeanStripsFiredPerLayer")
        for i,value in enumerate(self.meanStripsFiredPerLayer):
            print(i,value)
        print("MeanHitsPerXYModule")
        for i,value in enumerate(self.meanXYHitsPerModule):
            print(i,value)
        print("MeanHitsPerUVModule")
        for i,value in enumerate(self.meanUVHitsPerModule):
            print(i,value)        
        print("MeanHitsPerModule")
        for i,value in enumerate(self.meanHitsPerModule):
            print(i,value)

        print("Mean Hit Position (XY Board)")
        for i,value in enumerate(self.meanXYHitPos):
            print(i,value)
        print("Mean Hit Position (UV Board)")
        for i,value in enumerate(self.meanUVHitPos):
            print(i,value)
        print("Mean Hit Position (Module)")
        for i,value in enumerate(self.meanModuleHitPos):
            print(i,value)
        '''

    def PlotStripData(self):
        fig=plt.figure(figsize=self.figsize,dpi=self.dpi)
        for layer in range(16):
            plt.hist(self.stripAddresses[layer],bins=[x-0.5 for x in range(1536)])
            fig.savefig(f'{self.outputDirectory}/StipHits_{layer}.pdf',dpi=self.dpi)   # save the figure to file
            plt.clf()
        plt.close(fig)
    
    def PlotHitPos(self,section:str,module:int):
        if section=="XY":
            data=self.xyHits[module]
        elif section=="UV":
            data=self.uvHits[module]
        elif section=="Module":
            data=self.moduleHits[module]    
        else:
            print("Unrecognised hit type:",section) 
            return 1
        
        xBins=range(-180,180,1)
        yBins=range(-180,180,1)
        fig=plt.figure(figsize=self.figsize,dpi=self.dpi)
        x=[i[0] for i in data]
        y=[i[1] for i in data]
        plt.hist2d(x,y,bins=[xBins,yBins])
        if(len(data)>0):
            plt.text(-150, 130, f"Mean ({statistics.fmean(x):.3f},{statistics.fmean(x):.3f})\nStdev ({statistics.stdev(x):.3f},{statistics.stdev(x):.3f})", color="white")
        plt.xlabel("Strip Address")
        plt.ylabel("Counts")
        fig.savefig(f'{self.outputDirectory}/HitMap_{section}_{module}.png',dpi=self.dpi)   # save the figure to file
        plt.close(fig)

    def PlotHitsPerClock(self,section:str,module:int):
        if section=="XY":
            data=self.nXYHits[module]
        elif section=="UV":
            data=self.nUVHits[module]
        elif section=="Module":
            data=self.nModuleHits[module]    
        else:
            print("Unrecognised hit type:",section) 
            return 1
    
        fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
        fig=plt.figure(figsize=self.figsize,dpi=self.dpi)
        plt.hist(data,bins=[x-0.5 for x in range(30)])
        fig.savefig(f'{self.outputDirectory}/HitsPerClock_{section}_{module}.png',dpi=self.dpi)   # save the figure to file
        plt.xlabel("X Position (mm)")
        plt.ylabel("Y Position (mm)")
        plt.close(fig)

    def PlotStripsPerClock(self,layer: int):

        fig=plt.figure(figsize=self.figsize,dpi=self.dpi)
        plt.hist(self.nStripHits[layer],bins=[x-0.5 for x in range(30)])
        fig.savefig(f'{self.outputDirectory}/StripsPerClock_{layer}.png',dpi=self.dpi)   # save the figure to file
        plt.close(fig)

       