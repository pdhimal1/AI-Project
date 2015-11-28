'''
File:
	gui.py
Authors:
	Prakash Dhimal, Kevin Sanford
Description:
	Python source file to display a GUI for Predictor.py
'''
import subprocess
import predictor as pred
from Tkinter import *
import tkMessageBox
import Tkinter as tk
import sys

'''
Class to redirect stdout to the GUI
'''
class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        #self.widget.configure(state="disabled")


# Global variables
root            = tk.Tk()          # Creates the window pane for the GUI
tickerResponse  = StringVar()   # Creates a variable for string responses from GUI
daysResponse    = IntVar()      # Creates a variable for integer respones from GUI
text = tk.Text()
spreadV = IntVar()
volumeV = IntVar()
'''
Prints out the header

@param
    none
@return
    none
'''
def headerInfo():
    print "**************************************************"
    #print "*       Stock Predictor       *"
    #print "***************************************************"

'''
Executes the function to call predictor for either a specific stock or the DJIA list

@params
    - num
        Indicates whether the function calls for specific, DJIA, or an error has occurred
    - ticker
        The company's ticker information
    - days
        How many days the user wants to use as training data

@returns
    none
'''

def executeJob(ticker, days):
    subprocess.call('clear', shell = True)
    headerInfo()
    pred.gui_call(ticker, days, spreadV.get(), volumeV.get())

'''
Grabs just the days required to run the whole DJIA list

@params
    none
@returns
    none
'''
def grabDJIA():
    mDays = daysResponse.get()
    #print mDays

    if mDays >= 1:
        executeJob('DJIA', mDays)
    else:
        headerInfo()
        print "An error has occurred! Check inputs and try again!"


'''
Grabs information required to predict for a specific stock

@params
    none
@returns
    none
'''
def grabSpecific():
    # Flag to indicate if it's legal or we can pass
    legal = -1

    # Grabs responses for a specific stock
    mTicker = tickerResponse.get().upper()
    mDays = daysResponse.get()

    if not mTicker:
	headerInfo()
        print "An error has occurred! Check inputs and try again!"
    else:
	    # Checks legality for mDays
	    if mDays >= 1:
		executeJob(mTicker, mDays)
	    else:
		headerInfo()
        	print "An error has occurred! Check inputs and try again!"


def helpDisplay():
    HELP_TEXT = """Enter a company's ticker symbol and amount of days to train and hit the Prediction button.

Predictions for DJIA companies, enter amount of days to train, and hit DJIA button. """
    tkMessageBox.showinfo("HELP", HELP_TEXT)
    #mLabel3 = Label(text = "\nHELP:", font=("Arial", 11)).pack()
    #mLabel4 = Label(text = "Enter company's ticker symbol and amount of days to train and hit Predict button", font=("Arial", 10)).pack()
    #mLabel5 = Label(text = "Predictions for DJIA companies, enter amount of days to train, and hit DJIA button.", font=("Arial", 10)).pack()


'''


'''
def set_up_buttons(master):
	mLabelbutton = Label(master, text = "Pick features to use", font=("Arial", 11)).pack()

	c = Checkbutton(master, text = " Price Change", variable=spreadV, anchor='w', font=("Arial", 11))
	c.pack()
	c.var = spreadV
	
	v = Checkbutton(master, text = " Volume       ", variable=volumeV, anchor='w', font=("Arial", 11))
	v.pack()
	v.var = volumeV

	return spreadV, volumeV

'''
Sets up the GUI to display to user

@params
    The variable
'''

'''
Clears the screen and then destroys the window pane

@params
    none
@returns
    none
'''
def exitGUI():
    subprocess.call('clear', shell = True)
    root.destroy()

def setGUI(root):
    # Modify dimensions of root window
    root.title("Stock Predictor")
    #root.geometry("400x400")


    # Add Frames
    leftFrame = Frame(root, bd = 5)
    leftFrame.pack(side=LEFT)

    rightFrame = Frame(root, bd = 10)
    rightFrame.pack(side=RIGHT)

    spreadV, volumeV = set_up_buttons(rightFrame)

    #------------------------------------------------------------------------#
    #            code to make stdout appear in the GUI                       #
    
    text.configure(background='dimgrey')
    text.tag_configure("stdout", foreground="white", font=("Arial", 11))
    text.pack(fill = 'both', expand = 'True')
    sys.stdout = TextRedirector(text, "stdout")
    #sys.stderr = TextRedirector(text, "stderr")
    #------------------------------------------------------------------------#



    # Add Information for User Input
    mLabel  = Label(leftFrame, text = "Stock Ticker", fg='blue', font=("Arial", 11), anchor = 'n').pack()
    mEntry  = Entry(leftFrame, width=15, textvariable = tickerResponse, font=("Arial", 11)).pack()
    mLabel2 = Label(leftFrame, text = "Number of Days", fg='blue', font=("Arial", 11), anchor='n').pack()
    mEntry2 = Entry(leftFrame, width=15, textvariable = daysResponse, font=("Arial", 11)).pack()


    # Asks for DJIA or regular
    mbutton1 = Button(leftFrame, command = grabDJIA,     text = "  DJIA ", fg='red', anchor='s', font=("Arial", 11))
    mbutton2 = Button(leftFrame, command = grabSpecific, text = "Predict", fg='red', anchor='s', font=("Arial", 11))
    mbutton4 = Button(leftFrame, command = helpDisplay, text = " HELP ", fg='red', anchor='s', font=("Arial",11))
    mbutton3 = Button(leftFrame, command = exitGUI,      text = "  EXIT ", fg='red', anchor='s', font=("Arial", 11))
    mbutton2.pack()
    mbutton1.pack()
    mbutton4.pack()
    mbutton3.pack()

    

'''
Main function for the GUI. It sets up the GUI, clears screen, prints the header, activates the GUI loop

@param
    none
@returns
    none
'''
def main():
    # Set up the GUI
    setGUI(root)
    root.grid_propagate(False)

    # Clear Screen
    subprocess.call('clear', shell = True)

    # Calls Header
    #headerInfo()

    # Activate the GUI
    root.mainloop()

'''
Driver
'''

if __name__ == '__main__':
	main()
