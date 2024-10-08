import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import subprocess
from pathlib import Path
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)

window = tk.Tk()
#root.state("zoomed")
w, h = window.maxsize()
window.geometry(f'{w}x{h}+0+0')
window.title("OPTIma Beam Test") 

#create tabs
tabControl = ttk.Notebook(window)
root = ttk.Frame(tabControl)
stripHitsTab = ttk.Frame(tabControl)

tabControl.add(root, text='Configure')
tabControl.add(stripHitsTab, text='Strip Hit Plots')
tabControl.pack(expand=1, fill="both")

#globals
plotScale=11


def open_file_dialog():
    runButton.config(bg="red")
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("Binary File", "*.bin"), ("All files", "*.*")])
    if file_path:
        print("FilePath=",file_path)
        fileValue.config(text=file_path)
        UpdatePlots(0)

def analyseData():
    runButton.config(bg="orange")
    runStatusLabel.config(text="Running...")
    runStatusLabel.config(text="Running")

    maxEvents=maxEventsValue.get("1.0","end-1c")
    nSkips=skipEventsValue.get("1.0","end-1c")
    print(fileValue["text"],maxEvents,nSkips)

    myProcess=subprocess.run(['python', 'ProcessData.py', "-f", fileValue["text"], "-max",maxEvents,"-s",nSkips],capture_output=True)
    if myProcess.returncode==0:
        runStatusLabel.config(text="Finished!")
        runButton.config(bg="green")
        UpdatePlots(0)

    else:
        runStatusLabel.config(text="FAILED")
        runButton.config(bg="red")


def UpdateChoices(i):
    if i==1:
        index=plotTypeValue1.current()
        plotChoiceValue1["values"]=choices[index]
        plotChoiceValue1.current(0)
    elif i==2:
        index=plotTypeValue2.current()
        plotChoiceValue2["values"]=choices[index]
        plotChoiceValue2.current(0)
    elif i==3:
        index=plotTypeValue3.current()
        plotChoiceValue3["values"]=choices[index]
        plotChoiceValue3.current(0)

def UpdatePlots(args):
    baseName=Path(fileValue["text"]).stem

    type=plotTypeNames[plotTypeValue1.current()]
    choice=plotChoiceValue1.current()
    newPlotFile=f"./Plots/{baseName}/{type}{choice}.png"
    newPlot=tk.PhotoImage(file=newPlotFile)
    newPlot=newPlot.subsample(plotScale)
    plot1.configure(image=newPlot)
    plot1.image=newPlot

    type=plotTypeNames[plotTypeValue2.current()]
    choice=plotChoiceValue2.current()
    newPlotFile=f"./Plots/{baseName}/{type}{choice}.png"
    newPlot=tk.PhotoImage(file=newPlotFile)
    newPlot=newPlot.subsample(plotScale)
    plot2.configure(image=newPlot)
    plot2.image=newPlot

    type=plotTypeNames[plotTypeValue3.current()]
    choice=plotChoiceValue3.current()
    newPlotFile=f"./Plots/{baseName}/{type}{choice}.png"
    newPlot=tk.PhotoImage(file=newPlotFile)
    newPlot=newPlot.subsample(plotScale)
    plot3.configure(image=newPlot)
    plot3.image=newPlot

#top left: settings
settingsY=20
settingsX=5
settingsLabel=tk.Label(root,text="Settings",font='Helvetica 18 bold')
settingsLabel.place(x=settingsX+0,y=settingsY-20)

#select file
file_path=""
openButton = tk.Button(root, text="Select File", command=open_file_dialog)
fileValue=tk.Label(root,text=file_path,background="white", width=40)
openButton.place (x=settingsX+0,y=settingsY+30)
fileValue.place(x=settingsX+120,y=settingsY+32)

#set maximum entries
maxEventsLabel=tk.Label(root,text="Maximum N Cycles")
maxEventsValue=tk.Text(root, height=1, width=29)
maxEventsValue.insert(tk.END,"10000")
maxEventsLabel.place (x=settingsX+0,y=settingsY+80)
maxEventsValue.place(x=settingsX+172,y=settingsY+80)

#set events to skip
skipEventsLabel=tk.Label(root,text="N Cycles To Skip")
skipEventsValue=tk.Text(root, height=1, width=29)
skipEventsValue.insert(tk.END,"0")
skipEventsLabel.place (x=settingsX+00,y=settingsY+120)
skipEventsValue.place(x=settingsX+172,y=settingsY+120)

#run analysis
runButton = tk.Button(root,
    text="Analyse File",
    width=10,
    height=1,
    bg="red",
    fg="black",
    activebackground="orange",
    command=analyseData
)
runButton.place(x=settingsX+175,y=settingsY+162)
runStatusLabel=tk.Label(root,text="")
runStatusLabel.place(x=settingsX+300,y=settingsY+162)

####### Plots #########
plotsY=220
plotsX=35
plotsLabel=tk.Label(root,text="Plots",font='Helvetica 18 bold')
plotsLabel.place(x=settingsX+0,y=settingsY+0)
plotsLabel.place(x=plotsX-30,y=plotsY)

plotTypes=["Strip Hits","XY Hit Map","UV Hit Map","Module Hit Map"]
plotTypeNames=["StipHits_","HitMap_XY_","HitMap_UV_","HitMap_Module_"]
choices=[]
choices.append([i for i in range(16)])
choices.append([i for i in range(4)])
choices.append([i for i in range(4)])
choices.append([i for i in range(4)])

defaultPhoto = tk.PhotoImage(file=r'./Plots/noScintillator_output/StipHits_0.png')
#defaultPhoto=defaultPhoto.zoom(2)
defaultPhoto=defaultPhoto.subsample(plotScale)

#Plot 1
plotTypeLabel1=tk.Label(root,text="Plot Type")
typeValue1 = tk.StringVar() 
plotTypeValue1=ttk.Combobox(root,width=30,textvariable=typeValue1 )
plotTypeValue1.bind("<<ComboboxSelected>>", lambda x: UpdateChoices(1))
plotTypeValue1["values"]=plotTypes
plotTypeValue1.current(0)

plotChoiceLabel1=tk.Label(root,text="Layer/Module")
choiceValue1=tk.StringVar()
plotChoiceValue1=ttk.Combobox(root,width=30,textvariable=choiceValue1)
plotChoiceValue1.bind("<<ComboboxSelected>>", UpdatePlots)
plotChoiceValue1["values"]=choices[0]
plotChoiceValue1.current(12)

plotTypeLabel1.place(x=plotsX+0,y=plotsY+60)
plotTypeValue1.place(x=plotsX+120,y=plotsY+60)
plotChoiceLabel1.place(x=plotsX+0,y=plotsY+100)
plotChoiceValue1.place(x=plotsX+120,y=plotsY+100)

plot1 = tk.Label(root, image=defaultPhoto)
plot1.place(x=plotsX+0,y=plotsY+160)

#plot2
plotTypeLabel2=tk.Label(root,text="Plot Type")
typeValue2 = tk.StringVar() 
plotTypeValue2=ttk.Combobox(root,width=30,textvariable=typeValue2 )
plotTypeValue2.bind("<<ComboboxSelected>>", lambda x: UpdateChoices(2))
plotTypeValue2["values"]=plotTypes
plotTypeValue2.current(1)

plotChoiceLabel2=tk.Label(root,text="Layer/Module")
choiceValue2=tk.StringVar()
plotChoiceValue2=ttk.Combobox(root,width=30,textvariable=choiceValue2)
plotChoiceValue2.bind("<<ComboboxSelected>>", UpdatePlots)
plotChoiceValue2["values"]=choices[0]
plotChoiceValue2.current(3)

plotTypeLabel2.place(x=plotsX+620,y=plotsY+60)
plotTypeValue2.place(x=plotsX+740,y=plotsY+60)
plotChoiceLabel2.place(x=plotsX+620,y=plotsY+100)
plotChoiceValue2.place(x=plotsX+740,y=plotsY+100)

plot2 = tk.Label(root, image=defaultPhoto)
plot2.place(x=plotsX+620,y=plotsY+160)

#plot3
plotTypeLabel3=tk.Label(root,text="Plot Type")
typeValue3 = tk.StringVar() 
plotTypeValue3=ttk.Combobox(root,width=30,textvariable=typeValue3 )
plotTypeValue3.bind("<<ComboboxSelected>>", lambda x: UpdateChoices(3))
plotTypeValue3["values"]=plotTypes
plotTypeValue3.current(3)

plotChoiceLabel3=tk.Label(root,text="Layer/Module")
choiceValue3=tk.StringVar()
plotChoiceValue3=ttk.Combobox(root,width=30,textvariable=choiceValue3)
plotChoiceValue3.bind("<<ComboboxSelected>>", UpdatePlots)
plotChoiceValue3["values"]=choices[0]
plotChoiceValue3.current(3)

plotTypeLabel3.place(x=plotsX+1240,y=plotsY+60)
plotTypeValue3.place(x=plotsX+1360,y=plotsY+60)
plotChoiceLabel3.place(x=plotsX+1240,y=plotsY+100)
plotChoiceValue3.place(x=plotsX+1360,y=plotsY+100)

plot3 = tk.Label(root, image=defaultPhoto)
plot3.place(x=plotsX+1240,y=plotsY+160)


def UpdateStripHits():
    pass

#stripHitPlots
stripHitLabel=tk.Label(stripHitsTab,text="Strip Hits",font='Helvetica 18 bold')
stripHitChoice=tk.Label(stripHitsTab,text="Module")
choiceValue=tk.StringVar()
stripChoiceValue=ttk.Combobox(stripHitsTab,width=30,textvariable=choiceValue)
stripChoiceValue.bind("<<ComboboxSelected>>", UpdateStripHits)
stripChoiceValue["values"]=choices[1]
stripChoiceValue.current(0)

stripHitPlots=[]
for i in range(4):
    stripHitPlots.append(tk.Label(stripHitsTab, image=defaultPhoto))

stripHitLabel.place(x=5,y=0)
stripHitChoice.place(x=120,y=15)
stripChoiceValue.place(x=190,y=15)

imageWidth=defaultPhoto.width()
xShift=(w-10)/(4)
print(w,imageWidth,xShift)
stripHitPlots[0].place(x=5,y=120)
stripHitPlots[1].place(x=5+xShift,y=120)
stripHitPlots[2].place(x=5+2*xShift,y=120)
stripHitPlots[3].place(x=5+3*xShift,y=120)



window.mainloop()