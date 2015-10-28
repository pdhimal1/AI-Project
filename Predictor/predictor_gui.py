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
import djia
from Tkinter import *

# Global variables
root            = Tk()          # Creates the window pane for the GUI
tickerResponse  = StringVar()   # Creates a variable for string responses from GUI
daysResponse    = IntVar()      # Creates a variable for integer respones from GUI

'''
Prints out the header

@param
    none
@return
    none
'''
def headerInfo():
    print "*******************************"
    print "*       Stock Predictor       *"
    print "*******************************"

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
def executeJob(num, ticker, days):
    subprocess.call('clear', shell = True)
    if num == 0:
	headerInfo()
	pred.process_company(ticker, days)
    elif num == 1:
	headerInfo()
        tickers = djia.get_djia_list()
	for i in range(len(tickers)):
		pred.process_company(tickers[i], days)
    else:
	headerInfo()
        print "An error has occurred! Check inputs and try again!"

'''
Grabs just the days required to run the whole DJIA list

@params
    none
@returns
    none
'''
def grabDJIA():
    mDays = daysResponse.get()
    print mDays

    if mDays >= 1:
        executeJob(1, None, mDays)
    else:
        executeJob(-1, None, None)  # Illegal days entered


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

    # Checks legality for mDays
    if mDays >= 1:
        legal = 0   # Tells next function that we're predicting a specific stock
    else:
        legal = -1

    #Execute specific commands
    executeJob(legal, mTicker, mDays)


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
    leftFrame = Frame(root)
    leftFrame.pack(side=LEFT)

    rightFrame = Frame(root)
    rightFrame.pack(side=RIGHT)

    # Add Information for User Input
    mLabel  = Label(leftFrame, text = "Stock Ticker").pack()
    mEntry  = Entry(leftFrame, textvariable = tickerResponse).pack()
    mLabel2 = Label(leftFrame, text = "Days").pack()
    mEntry2 = Entry(leftFrame, textvariable = daysResponse).pack()
    mLabel3 = Label(leftFrame, text = "Enter a stock ticker and amount of days to train").pack()
    mLabel4 = Label(leftFrame, text = "or for DJIA, enter amount of days to train.").pack()

    # Asks for DJIA or regular
    mbutton1 = Button(rightFrame, command = grabDJIA,     text = "DJIA")
    mbutton2 = Button(rightFrame, command = grabSpecific, text = "SPECIFIC")
    mbutton3 = Button(rightFrame, command = exitGUI,      text = "EXIT")
    mbutton1.pack()
    mbutton2.pack()
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
    headerInfo()

    # Activate the GUI
    root.mainloop()

'''
Driver
'''
if __name__ == '__main__':
	main()
