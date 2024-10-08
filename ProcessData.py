import argparse
from BinaryReader import FileReader
from Plotter import PlotHandler
from pathlib import Path

print("Processing Data")

#read command line options
parser=argparse.ArgumentParser(description="Script for reading OPTIma beam test data")
parser.add_argument("-f","--fileName",help="Name of input file",type=str,required=True)
parser.add_argument("-s","--skip",help="Number of entries to skip before reading",type=int,default=0)
parser.add_argument("-max","--maxEvents",help="Maximum number of entries to read",type=int,default=-1)
parser.add_argument("-d","--debug",help="Debug mode: prints all info to terminal", action='store_true')
args=parser.parse_args()
parser.print_help()
print(args)



#setup files
reader=FileReader(args.fileName, args.skip)
plotHandler=PlotHandler()
outputDir=Path(args.fileName).stem
plotHandler.SetOutputDirectory("Plots/"+outputDir)

#loop over events
counter=0
for event in reader.GetNextEvent():
    
    if(args.debug):
        print("Event",counter)
        reader.event.Print()

    plotHandler.AddEvent(reader.event)

    counter+=1
    if(args.maxEvents>0 and counter>args.maxEvents):
        break

#Extract Useful Info
plotHandler.GetMeanValues()

#Plot Hit Maps
for section in ["XY","UV","Module"]:
    for module in range(4):
        plotHandler.PlotHitPos(section,module)
        plotHandler.PlotHitsPerClock(section,module)


import time
start=time.time()
plotHandler.PlotStripData()

for layer in range(16):
    plotHandler.PlotStripsPerClock(layer)

print("This took ",time.time()-start)