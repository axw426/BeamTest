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
-Update the data format- ultimately all that matters is that GetNextEvent contains a loop that reads in 1 clock cycle at a time, creates a 16 element array (one element per layer) where each element is a list of the non empty strip addresses for that layer, then passes this element to create an EventData object before performing a yield.
-If strip hits are seen but no hits are formed then it may be necessary to invert the strip addresses for some of the layers as I don't know what edge numbering starts at for each layer.

Event: 
-Double check geometry information is correct, in particular care should be taken to check how strips are numbered in XY layers. I've assumed they are numbered sequentially across the board, but potentially there are 4 empty addresses in each module as Y only has 252 channels instead of 256. This will only impact the XY hit maps and can probably be fixed by simply changing "nYStrips" to 256 and adding a fixed offset of 4*strip pitch to the layer0 and layer1 YPos arrays.
