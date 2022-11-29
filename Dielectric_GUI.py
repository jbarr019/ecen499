from guizero import App, Window, Text, Combo, Box, PushButton, TextBox, info, yesno, select_file, select_folder
import new_sweep as sweep
from timeit import default_timer as timer
import RPi.GPIO as GPIO

#Required for ADC library, declares that is MCP3204 and not MCP320X
pin_no = 4
#Pin number declarations using BCM pinouts
ADC_CS = 8
ADC_SCK = 11
ADC_MOSI = 10
ADC_MISO = 9
#Well Selector
MUX1_B0 = 2
MUX1_B1 = 3
MUX1_B2 = 4
#Feedback Capacitor Selector
MUX2_B0 = 0
MUX2_B1 = 5
MUX2_B2 = 6
#Switches to discharge the capacitors
SWITCH_1 = 13
SWITCH_2 = 19

#Setting up the GPIO pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ADC_CS, GPIO.OUT)
GPIO.setup(ADC_SCK, GPIO.OUT)
GPIO.setup(ADC_MOSI, GPIO.OUT)
GPIO.setup(ADC_MISO, GPIO.IN)
GPIO.setup(MUX1_B0, GPIO.OUT)
GPIO.setup(MUX1_B1, GPIO.OUT)
GPIO.setup(MUX1_B2, GPIO.OUT)
GPIO.setup(MUX2_B0, GPIO.OUT)
GPIO.setup(MUX2_B1, GPIO.OUT)
GPIO.setup(MUX2_B2, GPIO.OUT)
GPIO.setup(SWITCH_1, GPIO.OUT)
GPIO.setup(SWITCH_2, GPIO.OUT)

#Initializing global variables
page = 0
def_start_freq = None
def_end_freq = None
def_num_wells = None
def_num_freq = None

'''
Changes Window from main menu to desired function
'''
def main_window_change(main_menu_option):
    global page
    if (main_menu_option == "New Sweep"):
        page = 1
        app.hide()
        new_sweep_window.show()
    #Previous sweep window is not displayed because lack of functionality
    elif (main_menu_option == "Previous Sweeps"):
        page = 2
        #app.hide()
        #prev_sweep_window.show()
    elif (main_menu_option == "Manual Sweep"):
        page = 3
        app.hide()
        man_window.show()
    elif (main_menu_option == "Settings"):
        page = 4
        app.hide()
        set_window.show()
    else:
        page = 0
        app.show()

'''
Returns back to home page from any other page
'''
def back_to_home():
    global page
    if (page == 1):
        new_sweep_window.hide()
        app.show()
        app.focus()
    elif (page == 2):
        prev_sweep_window.hide()
        app.show()
        app.focus()
    elif (page == 3):
        man_window.hide()
        app.show()
        app.focus()
    elif (page == 4):
        set_window.hide()
        app.show()
        app.focus()
    else:
        page = 0
        app.show()
        
'''
Runs a new sweep
'''
def new_run():
    global page
    global def_start_freq
    global def_end_freq
    global def_num_wells
    global def_num_freq
    
    #New Sweep Page
    if (page == 1):
        textID = []
        textInputErr = False
        
        #Valid input checking
        try:
            dur_float = float(new_box1_dur0.value)
        except ValueError:
            #print("Invalid input:", new_box1_dur0.value)
            textInputErr = True
            textID.append(1)
        
        try:
            sweep_float = float(new_box2_sweep0.value)
        except ValueError:
            #print("Invalid input:", new_box2_sweep0.value)
            textInputErr = True
            textID.append(2)
        
        if (textInputErr):
            msg = "Error on the following inputs:\n"
            for i in range(0, len(textID)):
                msg = msg + "Input box:" + str(textID[i]) + "\n"
            info("New Sweep", msg)
        else:
            msg = "Run new sweep with following parameters?\n\n"
            msg = msg + "Start Frequency: " + str(def_start_freq) + " Hz\n"
            msg = msg + "End Frequency: " + str(def_end_freq) + " Hz\n"
            msg = msg + "Number of Wells: " + str(def_num_wells) + "\n"
            msg = msg + "Number of frequencies per sweep: " + str(def_num_freq) + "\n"
            msg = msg + "Total Test Duration: " + str(dur_float) + " Hrs\n"
            msg = msg + "Number of sweeps per hour: " + str(sweep_float) + " /hr\n"
            
            #Attempt to separate popup from calling the sweep function
            run_ = False
            if (yesno("New Sweep", msg)):
                print("Running sweep")
                run_ = True
            
            #Sends the default values to the sweep function in the low level code
            if (run_):
                starting_time = timer()
                sweep.run_sweep(start_freq=def_start_freq, end_freq=def_end_freq, well_num=def_num_wells,
                                num_freq=def_num_freq, Xc=0, dut_cap=0, total_duration=dur_float,
                                start_time=starting_time, sweeps_hr=sweep_float)
    #Manual Sweep Page
    elif (page == 3):        
        textID = []
        textInputErr = False
        
        #Valid input checking
        try:
            man_start_freq = float(man_box1_freq0.value)
        except ValueError:
            #print("Invalid input:", man_box1_freq0.value)
            textInputErr = True
            textID.append(1)
        
        try:
            man_end_freq = float(man_box2_freq0.value)
        except ValueError:
            #print("Invalid input:", man_box2_freq0.value)
            textInputErr = True
            textID.append(2)
            
        try:
            man_test_duration = float(man_box3_dur0.value)
        except ValueError:
            #print("Invalid input:", man_box3_dur0.value)
            textInputErr = True
            textID.append(3)
        
        try:
            man_num_freq = int(man_box4_numfreq0.value)
        except ValueError:
            #print("Invalid input:", man_box4_numfreq0.value)
            textInputErr = True
            textID.append(4)
        
        try:
            man_num_wells = int(man_box5_numwells0.value)
        except ValueError:
            #print("Invalid input:", man_box5_numwells0.value)
            textInputErr = True
            textID.append(5)
            
        try:
            man_sweep_hr = int(man_box6_sweephr0.value)
        except ValueError:
            #print("Invalid input:", man_box6_sweephr0.value)
            textInputErr = True
            textID.append(6)
        
        if (textInputErr):
            msg = "Error on the following inputs:\n"
            for i in range(0, len(textID)):
                msg = msg + "Input box:" + str(textID[i]) + "\n"
            info("Manual Sweep", msg)
        else:
            msg = "Run manual sweep with following parameters?\n\n"
            
            msg = msg + "Start Frequency: " + str(man_start_freq) + " Hz\n"
            msg = msg + "End Frequency: " + str(man_end_freq) + " Hz\n"
            msg = msg + "Number of Wells: " + str(man_num_wells) + "\n"
            msg = msg + "Number of frequencies per sweep: " + str(man_num_freq) + "\n"
            msg = msg + "Total Test Duration: " + str(man_test_duration) + " Hrs\n"
            msg = msg + "Number of sweeps per hour: " + str(man_sweep_hr) + " /hr\n"
            
            #Attempt to separate popup from calling the sweep function
            run_ = False
            if (yesno("Manual Sweep", msg)):
                print("Running sweep")
                run_ = True
                
            #Sends the manually inputted values to the sweep function in the low level code
            if (run_):
                starting_time = timer()
                sweep.run_sweep(start_freq=man_start_freq, end_freq=man_end_freq, well_num=man_num_wells,
                                num_freq=man_num_freq, Xc=0, dut_cap=0, total_duration=man_test_duration,
                                start_time=starting_time, sweeps_hr=man_sweep_hr)
    #Settings Page
    elif (page == 4):        
        textID = []
        textInputErr = False
        
        #Valid input checking
        try:
            set_start_freq = float(set_box1_freq0.value)
        except ValueError:
            #print("Invalid input:", set_box1_freq0.value)
            textInputErr = True
            textID.append(1)
        
        try:
            set_end_freq = float(set_box2_freq0.value)
        except ValueError:
            #print("Invalid input:", set_box2_freq0.value)
            textInputErr = True
            textID.append(2)
       
        try:
            set_num_freq = int(set_box4_numfreq0.value)
        except ValueError:
            #print("Invalid input:", set_box4_numfreq0.value)
            textInputErr = True
            textID.append(3)
        
        try:
            set_num_wells = int(set_box5_numwells0.value)
        except ValueError:
            #print("Invalid input:", set_box5_numwells0.value)
            textInputErr = True
            textID.append(4)
        
        if (textInputErr):
            msg = "Error on the following inputs:\n"
            for i in range(0, len(textID)):
                msg = msg + "Input box:" + str(textID[i]) + "\n"
            info("Settings", msg)
        else:
            msg = "Save the following settings?\n\n"
            
            msg = msg + "Start Frequency: " + str(set_start_freq) + " Hz\n"
            msg = msg + "End Frequency: " + str(set_end_freq) + " Hz\n"
            msg = msg + "Number of Wells: " + str(set_num_wells) + "\n"
            msg = msg + "Number of frequencies per sweep: " + str(set_num_freq) + "\n"
            
            if (yesno("Settings", msg)):
                #Saves the inputted settings to the default values
                print("Saving settings")
                def_start_freq = set_start_freq
                def_end_freq = set_end_freq
                def_num_wells = set_num_wells
                def_num_freq = set_num_freq
                '''
                Here is where the file writer code would overwrite the settings text file
                '''
#Prompts the user to select a file, returns the path
def get_file():
    filename = select_file()
    print(filename)
    prev_file_btn.text = filename
    
'''

GUI WIDGETS AND PROPERTIES

'''
#Creates a GUI app/object
app = App(title="", layout="auto", width=1000, height=750)

'''
HOME WINDOW
This will be the main window that will load different windows depending
on the selected function
'''
#Header Text
main_header = Text(app, text="Dielectric Spectroscopy", align="top", size=18)
#Padding for spacing between header and dropdown
main_pad1 = Box(app, align="top", width="fill", height=100)
#Dropdown that controls which function/page to go to
main_dropdown = Combo(app, align="top", options=["Please select an option...", "New Sweep",# "Previous Sweeps",
                                                 "Manual Sweep", "Settings"], width=25, command=main_window_change)

'''
NEW SWEEP WINDOW
This is the New Sweep window that will take in a custom duration and sample amount
while using the default paramater values to generate a frequency sweep.
'''
new_sweep_window = Window(app, title="Dielectric Spectroscopy", width=1000, height=750, visible=False)
#Header Text
new_header = Text(new_sweep_window, text="New Sweep", align="top", size=18)
#Padding for spacing between header and text boxes
new_pad1 = Box(new_sweep_window, align="top", width="fill", height=100)

#GUI Box for the first text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
new_box1 = Box(new_sweep_window, align="top", width="fill", height=80)
#Left padding in box
new_box1_lpad = Text(new_box1, align="left", width=40, text=" ")
#Textbox to enter duration
new_box1_dur0 = TextBox(new_box1, width=20, align="left")
#Displays duration text
new_box1_dur1 = Text(new_box1, text="Test Duration (hr)", width="fill", align="left", size=18)
#Right padding in box
new_box1_rpad = Text(new_box1, align="left", width=40, text=" ")

#GUI Box for the second text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
new_box2 = Box(new_sweep_window, align="top", width="fill", height=80)
#Left padding in box
new_box2_lpad = Text(new_box2, align="left", width=40, text=" ")
#Textbox to enter sample number
new_box2_sweep0 = TextBox(new_box2, width=20, align="left")
#Displays sampling text
new_box2_sweep1 = Text(new_box2, text="Sweeps/hr", width="fill", align="left", size=18)
#Right padding in box
new_box2_rpad = Text(new_box2, align="left", width=40, text=" ")

#Padding for spacing between text boxes and push buttons
new_pad2 = Box(new_sweep_window, align="top", width="fill", height=80)

#GUI Box for push buttons (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
new_box3 = Box(new_sweep_window, align="top", width="fill", height=120)
#Left padding in box
new_box3_lpad = Text(new_box3, align="left", width=20, text="  ")
#Push button to run the sweep
new_box3_run = PushButton(new_box3, align="left", width=35, height="fill", text="RUN",
                          command=new_run)
#Padding for spacing between two push buttons
new_box3_cpad = Text(new_box3, align="left", width=3, text=" ")
#Push button to return to home page
new_box3_back = PushButton(new_box3, align="left", width=35, height="fill", text="BACK",
                            command=back_to_home)
#Right padding in box
new_box3_rpad = Text(new_box3, align="left", width=20, text="  ")

'''
PREVIOUS SWEEP WINDOW
This window will have a dropdown with different dates to select the Previous Sweeps
that the user would like to view. It will show several values from that sweep at a glance
and then run a graph to show all the data points and detailed values.

Currently hidden because of lack of functionality
'''

prev_sweep_window = Window(app, title="Dielectric Spectroscopy", width=1000, height=750, visible=False)
#Header Text
prev_header = Text(prev_sweep_window, text="Previous Sweeps", align="top", size=18)
#Padding for spacing between header and dropdown
prev_pad1 = Box(prev_sweep_window, align="top", width="fill", height=100)
prev_file_btn = PushButton(prev_sweep_window, align="top", text="Please Select a File",
                            width=25, command=get_file)
#Padding for spacing between dropdown and text boxes
prev_pad2 = Box(prev_sweep_window, align="top", width="fill", height=100)

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
prev_box1 = Box(prev_sweep_window, width="fill", align="top")
#Left padding in box
prev_box1_lpad = Text(prev_box1, align="left", width=40, text=" ")
prev_box1_param0 = Text(prev_box1, width="fill", align="left", text="None", size=18)
prev_box1_param1 = Text(prev_box1, width="fill", align="left", text="Parameter 1", size=18)
prev_box1_param0.tk.configure(background="light gray")
#Right padding in box
prev_box1_rpad = Text(prev_box1, align="left", width=40, text=" ")

#Padding in between the two parameter boxes
prev_pad3 = Box(prev_sweep_window, align="top", width="fill", height=20)

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
prev_box2 = Box(prev_sweep_window, width="fill", align="top")
#Left padding in box
prev_box2_lpad = Text(prev_box2, align="left", width=40, text=" ")
prev_box2_param0 = Text(prev_box2, width="fill", align="left", text="None", size=18)
prev_box2_param1 = Text(prev_box2, width="fill", align="left", text="Parameter 2", size=18)
prev_box2_param0.tk.configure(background="light gray")
#Right padding in box
prev_box2_rpad = Text(prev_box2, align="left", width=40, text=" ")

#Padding for spacing between text boxes and push buttons
prev_pad4 = Box(prev_sweep_window, align="top", width="fill", height=80)

#GUI Box for push buttons (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
prev_box3 = Box(prev_sweep_window, align="top", width="fill", height=120)
#Left padding in box
prev_box3_lpad = Text(prev_box3, align="left", width=20, text="  ")
#Push button to graph the sweep
prev_box3_run = PushButton(prev_box3, align="left", width=35, height="fill", text="GRAPH")
#Padding for spacing between two push buttons
prev_box3_cpad = Text(prev_box3, align="left", width=3, text=" ")
#Push button to return to home page
prev_box3_back = PushButton(prev_box3, align="left", width=35, height="fill", text="BACK",
                           command=back_to_home)
#Right padding in box
prev_box3_rpad = Text(prev_box3, align="left", width=20, text="  ")

'''
MANUAL SWEEP WINDOW
'''
#Manual Sweep
man_window = Window(app, title="Dielectric Spectroscopy", width=1000, height=750, visible=False)
#Header Text
man_header = Text(man_window, text="Manual Sweep", align="top", size=18)
#Padding for spacing between header and text boxes
man_pad1 = Box(man_window, align="top", width="fill", height=60)

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
man_box1 = Box(man_window, align="top", width="fill", height=80)
#Left padding in box
man_box1_lpad = Text(man_box1, align="left", width=40, text="  ")
#Textbox to enter starting frequency
man_box1_freq0 = TextBox(man_box1, align="left", width="fill")
#Displays start frequency text
man_box1_freq1 = Text(man_box1, align="left", width="fill", text="Start Frequency", size=18)
#Right padding in box
man_box1_rpad = Text(man_box1, align="left", width=40, text="  ")

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
man_box2 = Box(man_window, align="top", width="fill", height=80)
#Left padding in box
man_box2_lpad = Text(man_box2, align="left", width=40, text="  ")
#Textbox to enter ending frequency
man_box2_freq0 = TextBox(man_box2, align="left", width="fill")
#Displays end frequency text
man_box2_freq1 = Text(man_box2, align="left", width="fill", text="End Frequency", size=18)
#Right padding in box
man_box2_rpad = Text(man_box2, align="left", width=40, text="  ")

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
man_box3 = Box(man_window, align="top", width="fill", height=80)
#Left padding in box
man_box3_lpad = Text(man_box3, align="left", width=40, text="  ")
#Textbox to enter duration number
man_box3_dur0 = TextBox(man_box3, align="left", width="fill")
man_box3_dur1 = Text(man_box3, align="left", width="fill", text="Test Duration (hr)", size=18)
#Right padding in box
man_box3_rpad = Text(man_box3, align="left", width=40, text="  ")

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
man_box4 = Box(man_window, align="top", width="fill", height=80)
#Left padding in box
man_box4_lpad = Text(man_box4, align="left", width=40, text="  ")
#Textbox to enter number of frequencies to sweep through
man_box4_numfreq0 = TextBox(man_box4, align="left", width="fill")
man_box4_numfreq1 = Text(man_box4, align="left", width="fill", text="Number of Freq./sweep", size=18)
#Right padding in box
man_box4_rpad = Text(man_box4, align="left", width=40, text="  ")

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
man_box5 = Box(man_window, align="top", width="fill", height=80)
#Left padding in box
man_box5_lpad = Text(man_box5, align="left", width=40, text="  ")
#Textbox to enter default number of wells
man_box5_numwells0 = TextBox(man_box5, align="left", width="fill")
man_box5_numwells1 = Text(man_box5, align="left", width="fill", text="Number of Wells", size=18)
#Right padding in box
man_box5_rpad = Text(man_box5, align="left", width=40, text="  ")

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
man_box6 = Box(man_window, align="top", width="fill", height=80)
#Left padding in box
man_box6_lpad = Text(man_box6, align="left", width=40, text="  ")
#Text that displays estimated run time
man_box6_sweephr0 = TextBox(man_box6, align="left", width="fill")
man_box6_sweephr1 = Text(man_box6, align="left", width="fill", text="Sweeps/hr", size=18)
#Right padding in box
man_box6_rpad = Text(man_box6, align="left", width=40, text="  ")

#Padding for spacing between text boxes and push buttons
man_pad2 = Box(man_window, align="top", width="fill", height=40)

#GUI Box for push buttons (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
man_box6 = Box(man_window, align="top", width="fill", height=120)
#Left padding in box
man_box6_lpad = Text(man_box6, align="left", width=20, text="  ")
#Push button to run the sweep
man_box6_run = PushButton(man_box6, align="left", width=35, height="fill", text="RUN", command=new_run)
#Padding for spacing between two push buttons
man_box6_cpad = Text(man_box6, align="left", width=3, text=" ")
#Push button to return to home page
man_box6_back = PushButton(man_box6, align="left", width=35, height="fill", text="BACK",
                           command=back_to_home)
#Right padding in box
man_box6_rpad = Text(man_box6, align="left", width=20, text="  ")

'''
SETTINGS WINDOW
'''
#Settings Window
set_window = Window(app, title="Dielectric Spectroscopy", width=1000, height=750, visible=False)
#Header Text
set_header = Text(set_window, text="Settings", align="top", size=18)
#Padding for spacing between header and text boxes
set_pad1 = Box(set_window, align="top", width="fill", height=100)

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
set_box1 = Box(set_window, align="top", width="fill", height=80)
#Left padding in box
set_box1_lpad = Text(set_box1, align="left", width=40, text="  ")
#Textbox to enter default starting frequency
set_box1_freq0 = TextBox(set_box1, align="left", width="fill")
set_box1_freq1 = Text(set_box1, align="left", width="fill", text="Default Start Frequency", size=18)
#Right padding in box
set_box1_rpad = Text(set_box1, align="left", width=40, text="  ")

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
set_box2 = Box(set_window, align="top", width="fill", height=80)
#Left padding in box
set_box2_lpad = Text(set_box2, align="left", width=40, text="  ")
#Textbox to enter default ending frequency
set_box2_freq0 = TextBox(set_box2, align="left", width="fill")
set_box2_freq1 = Text(set_box2, align="left", width="fill", text="Default End Frequency", size=18)
#Right padding in box
set_box2_rpad = Text(set_box2, align="left", width=40, text="  ")

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
set_box4 = Box(set_window, align="top", width="fill", height=80)
#Left padding in box
set_box4_lpad = Text(set_box4, align="left", width=40, text="  ")
#Textbox to enter default number of frequencies to sweep through
set_box4_numfreq0 = TextBox(set_box4, align="left", width="fill")
set_box4_numfreq1 = Text(set_box4, align="left", width="fill", text="Default Number of Freq./sweep", size=18)
#Right padding in box
set_box4_rpad = Text(set_box4, align="left", width=40, text="  ")

#GUI Box for text box and text widget (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
set_box5 = Box(set_window, align="top", width="fill", height=80)
#Left padding in box
set_box5_lpad = Text(set_box5, align="left", width=40, text="  ")
#Textbox to enter default number of wells
set_box5_numwells0 = TextBox(set_box5, align="left", width="fill")
set_box5_numwells1 = Text(set_box5, align="left", width="fill", text="Default Number of Wells", size=18)
#Right padding in box
set_box5_rpad = Text(set_box5, align="left", width=40, text="  ")

#Padding for spacing between text boxes and push buttons
set_pad2 = Box(set_window, align="top", width="fill", height=80)

#GUI Box for push buttons (for alignment purposes)
#Box is aligned with window and widgets in box have left alignment
set_box6 = Box(set_window, align="top", width="fill", height=120)
#Left padding in box
set_box6_lpad = Text(set_box6, align="left", width=20, text="  ")
#Push button to save the settings
set_box6_run = PushButton(set_box6, align="left", width=35, height="fill", text="SAVE", command=new_run)
#Padding for spacing between two push buttons
set_box6_cpad = Text(set_box6, align="left", width=3, text=" ")
#Push button to return to home page
set_box6_back = PushButton(set_box6, align="left", width=35, height="fill", text="BACK",
                           command=back_to_home)
#Right padding in box
set_box6_rpad = Text(set_box6, align="left", width=20, text="  ")

'''
DEFAULT VALUES
Right now it is hardcoded. Everytime the GUI initially launches these will be loaded into the settings.
Next step: Saving to a text file and pulling from text file on launch
'''
set_box1_freq0.value = "1000"
set_box2_freq0.value = "1000000"
set_box4_numfreq0.value = "50"
set_box5_numwells0.value = "8"

def_start_freq = float(set_box1_freq0.value)
def_end_freq = float(set_box2_freq0.value)
def_num_wells = int(set_box5_numwells0.value)
def_num_freq = int(set_box4_numfreq0.value)


#Main GUI loop that constantly checks for updated widgets
app.display()