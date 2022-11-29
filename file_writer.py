from datetime import date
import time
import numpy as np
filename = ""

#Function to write the header and top information for each file
def file_start(start_freq, end_freq, well_num):
    global filename
    
    t = time.localtime()
    current_time = time.strftime("%H_%M_%S", t)
    
    print("Starting file")
    filename = ("def_" + str(format(date.today())) + "_" + str(current_time) + ".txt")
    
    with open(filename, 'w', encoding = 'utf-8') as f:
        f.write("%Default Test:\n\n")
        f.write("%Start Frequency: " + str(start_freq))
        f.write('{:>28}' .format("End Frequency:") + str(end_freq) + "\n")
        f.write("%Wells Used: " + str(well_num) + "\n\n")

#Function that appends to the previously started file
#This function will accept the data arrays from the sweep and write them
#to a unique text file
def file_append(well_num, frequency_list, Xc_data, dut_cap_data, current_time_data, num_freq):
    global filename
    
    t = time.localtime()

    for x in range(0, well_num):
        with open(filename, 'a', encoding = 'utf-8') as f:
            f.write("%Well Number: " + str(x + 1) + "     Relative Time: " + str(current_time_data[x]) + "\n")
            f.write("%Frequency  Reactance  Capacitance\n\n")
        for y in range(0, num_freq):
            with open(filename, 'a', encoding = 'utf-8') as f:
                f.write(str(np.floor(frequency_list[y])) + ", " + str(Xc_data[x][y]) + ", " + str(dut_cap_data[x][y]) + "\n")
        with open(filename, 'a', encoding = 'utf-8') as f:
            f.write("\n")
