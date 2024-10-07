class EventData():
    def __init__(self,rawData: list, stripData: list):
        self.rawData=rawData 

        #the useful info produced
        self.stripAddresses=stripData #vector of length 16 of strips fired in each layer 
        self.xyHits=[] #vector of length 4 of hits in each XY sensor board
        self.uvHits=[] #vector of length 4 of hits in each UV sensor board
        self.moduleHits=[] #vector of length 4 of hits in each full module

        #currently missing
        #-- timing info

        #Geometry info
        self.maxYHeight=28.5
        self.nHitsPerLayer=4
        self.nLayersPerTracker=4
        self.nModules=4
        self.nXStrips=256
        self.nYStrips=252
        self.nXYStrips=self.nXStrips+self.nYStrips
        self.nUVStrips=256
        self.XYPitch=0.232
        self.UVPitch=0.223446
        self.layer0XPos=[
             -149.796 - 0.5*self.nXStrips*self.XYPitch  +0.5*self.XYPitch,
             -29.696 - 0.5*self.nXStrips*self.XYPitch  +0.5*self.XYPitch,
             90.404 - 0.5*self.nXStrips*self.XYPitch  +0.5*self.XYPitch,
        ]
        self.layer0YPos=[
            0.5*self.nYStrips*self.XYPitch  -0.5*self.XYPitch,
            0.5*self.nYStrips*self.XYPitch  -0.5*self.XYPitch,
            0.5*self.nYStrips*self.XYPitch  -0.5*self.XYPitch,
        ]
        self.layer1XPos=[
             -90.404 - 0.5*self.nXStrips*self.XYPitch  +0.5*self.XYPitch,
             29.696 - 0.5*self.nXStrips*self.XYPitch  +0.5*self.XYPitch,
             149.796 - 0.5*self.nXStrips*self.XYPitch  +0.5*self.XYPitch,
        ]
        self.layer1YPos=[
            0.5*self.nYStrips*self.XYPitch  -0.5*self.XYPitch,
            0.5*self.nYStrips*self.XYPitch  -0.5*self.XYPitch,
            0.5*self.nYStrips*self.XYPitch  -0.5*self.XYPitch,
        ]
        self.UVPos=[
             -147.929 -0.5*self.nUVStrips*self.UVPitch +0.5*self.UVPitch,
             -88.7571 -0.5*self.nUVStrips*self.UVPitch +0.5*self.UVPitch,
             -29.5857 -0.5*self.nUVStrips*self.UVPitch +0.5*self.UVPitch,
             29.5857 -0.5*self.nUVStrips*self.UVPitch +0.5*self.UVPitch,
             88.7571 -0.5*self.nUVStrips*self.UVPitch +0.5*self.UVPitch,
             147.929 -0.5*self.nUVStrips*self.UVPitch +0.5*self.UVPitch,
        ]

        #automatically calculate all interesting positions
        self.GetHits()


    def Print(self):
        print("Strips:",self.stripAddresses)
        print("XYHits",self.xyHits)
        print("UVHits:",self.uvHits)
        print("ModuleHits:",self.moduleHits)

    def GetHits(self):
        for i in range(self.nModules):

            #Get XYBoard Hits
            hits=[]
            for layer0Strip in self.stripAddresses[i*self.nLayersPerTracker]:
                waferLayer0,internalStripNo=divmod(layer0Strip,self.nXYStrips)
                layer0Pos=[None,None]
                if(internalStripNo<self.nXStrips):
                    layer0Pos[0]=self.layer0XPos[waferLayer0]+internalStripNo*self.XYPitch

                else:
                    internalStripNo-=self.nXStrips
                    layer0Pos[1]=self.layer0YPos[waferLayer0] - internalStripNo*self.XYPitch

                for layer1Strip in self.stripAddresses[i*self.nLayersPerTracker+1]:
                    waferLayer1,internalStripNo=divmod(layer1Strip,self.nXYStrips)
                    if(waferLayer0!=waferLayer1): #ignoring combinations from wafers that don't overlap
                        continue
                    layer1Pos=[None,None]
                    if(internalStripNo<self.nYStrips):
                        layer1Pos[1]=self.layer1YPos[waferLayer1]-internalStripNo*self.XYPitch
                    else:
                        internalStripNo-=self.nYStrips
                        layer1Pos[0]=self.layer1XPos[waferLayer1]+internalStripNo*self.XYPitch

                    #form hit
                    if layer0Pos[0] is not None and layer1Pos[1] is not None:
                        hits.append([layer0Pos[0],layer1Pos[1]])
                    elif layer1Pos[0] is not None and layer0Pos[1] is not None:
                        hits.append([layer1Pos[0],layer0Pos[1]])
                    #other cases don't matter as they won't have both an X and Y position available
            self.xyHits.append(hits)


            #Get UVBoard Hits
            hits=[]
            for uStrip in self.stripAddresses[i*self.nLayersPerTracker+2]:
                wafer,internalStripNo=divmod(uStrip,self.nUVStrips)
                xPosU=self.UVPos[wafer] + internalStripNo*self.UVPitch
                
                for vStrip in self.stripAddresses[i*self.nLayersPerTracker+3]:
                    wafer,internalStripNo=divmod(vStrip,self.nUVStrips)
                    xPosV=self.UVPos[wafer] + internalStripNo*self.UVPitch

                    #form hit and check it exists within the extent of the system
                    hitX=(xPosU+xPosV)/2
                    hitY=hitX-xPosU
                    if abs(hitY)<self.maxYHeight:
                        hits.append([hitX,hitY])
            self.uvHits.append(hits)


            #Combine XY and UV hits
            hits=[]
            #if(i==0): #UV module
            #    hits=self.uvHits[-1]
            #elif(i==1): #XY module
            #    hits=self.xyHits[-1]  
            #else: #4 layer modules
            for xyHit in self.xyHits[-1]:
                for uvHit in self.uvHits[-1]:
                    hits.append([(xyHit[0]+uvHit[0])/2, (xyHit[1]+uvHit[1])/2])
            self.moduleHits.append(hits)


  