#required packages 
PyQt5
pyqtgraph
matplotlib
numpy

#Usage
python main.py  (tested with python 3.11 and 3.13 on both Windows and Linux)
Click select file to select an input binary file then hit run analysis to generate plots
Plots can be saved using File->SavePlots and selecting an appropriate directory
Options:
-Starting Event: pick the clock cycle you would like to start the analysis from (0= first event in file)
-Max events: total number of clock cycles to analyse. If left as zero will read the full file
-Update plots every N events: sets how often the plots are updated in terms of clock cycles. If set to 0 it will only generate plots after processing all data. It takes around ~0.1s to update all the plots so don't set this too low of it will slow everything down

#changes required depending on data format
Main:
-loadFile function currently assumes the inout file uses the ".bin" extension. If this is not the case then update the QFileDialog "filter" option (or simply remove it!)

Binary reader:
-Need to fill in the ReadHeader function
-Check this works on a real data set to make sure no errors in bit operations
-Need to check geometry mapping

