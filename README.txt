Basic python script for visualizing data:

Currently run with python main.py -f <binary file name> -max <optional, maximum clock cycles to study> -s <optional,number of clock cycles to skip>

Main loop reads in one clock of data ("Event") at a time (can choose start point in data and set max events)
Event class converts raw data into all the useful info (Strips per layer, XY hits, UV hits, Module Hits)
Plotter collates data per event and plots




