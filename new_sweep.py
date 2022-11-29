from timeit import default_timer as timer
from datetime import date
import time
import math
import numpy as np
import adc_3204 as adc
import ad9833_python as ad
import file_writer as f
import RPi.GPIO as GPIO
import gpiozero

#Redundant setups in the event that they are not
#run when the GUI is enabled
pin_no = 4
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
#Delays for frequency and switch changing
delay_freq = 0.001
delay_sw = 0.001

##Declaring an Object for the Sine wave generator
sinegen = ad.AD9833(17, 27, 22)
#        MOSI, SCK, CS

#Global variables that will contain data being written to the text file
Xc_data = []
dut_cap_data = []
V_ch0_data = []
V_ch1_data = []
current_time_data = []

#Low level code to run a sweep of frequencies for each DUT
def run_sweep(start_freq, end_freq, sweeps_hr, num_freq,
              well_num, Xc, dut_cap, total_duration, start_time):
    global delay_sw
    
    f.file_start(start_freq, end_freq, well_num)
    #Capacitors in use: 6.8pF           20pF          150pF
    base_caps =[0.0000000000068, 0.00000000002, 0.00000000015]
    #Indicating if circuit is saturated and if we need to move to
    #other capacitor
    low_volt_range = 0.1
    high_volt_range = 5
    in_volt = False
    high_volt = False
    low_volt = False
    
    #Initially, the 20pF capacitor is selected
    GPIO.output(MUX2_B2, GPIO.LOW)
    GPIO.output(MUX2_B1, GPIO.LOW)
    GPIO.output(MUX2_B0, GPIO.LOW)
    base_cap_index = 1
        
    #This will calculate a  logarithmically spaced list of frequencies including
    #the start and end frequencies
    freq_list = np.logspace(np.log10(start_freq), np.log10(end_freq), num=num_freq,
                                endpoint=True, base=10, dtype=None, axis=0)
    #print("Freq List:\n", freq_list)
    
    #These are used to control how long the test will run and to calculate the delay time
    #between sweeps in order to hit the desired # of sweeps/hr
    total_duration = total_duration * 60.0 * 60
    #How often sweeps should occur every hour
    samples_hr = 3600.0/sweeps_hr
    elapsed_time = 0
    time_sweep_start = 0
    time_sweep_end = 0
    #print("Total Duration:", round(total_duration))
    #print("Samples/hr:", samples_hr)
    
    #Will continue loops through sweeps until the elapsed time is equal to or greater than
    #the user's inputted test duration
    while (elapsed_time < total_duration):
        #When each sweep starts
        time_sweep_start = timer()
        #This loop will go through each well under test
        #Currently, the max num of wells is 8
        for x in range(1, well_num+1):
            #Creates new lists of data for each well
            Xc_list = []
            dut_cap_list = []
            V_ch0_list = []
            V_ch1_list = []
            #Adds the time that each sweep was done to its list
            current_time_data.append(timer())
            
            #These if statements control MUX1 and will select the correct
            #well depending on which one is being tested in the loop
            if (x == 2):
                GPIO.output(MUX1_B2, GPIO.LOW)
                GPIO.output(MUX1_B1, GPIO.LOW)
                GPIO.output(MUX1_B0, GPIO.HIGH)
            
            elif (x == 3):
                GPIO.output(MUX1_B2, GPIO.LOW)
                GPIO.output(MUX1_B1, GPIO.HIGH)
                GPIO.output(MUX1_B0, GPIO.LOW)
            
            elif (x == 4):
                GPIO.output(MUX1_B2, GPIO.LOW)
                GPIO.output(MUX1_B1, GPIO.HIGH)
                GPIO.output(MUX1_B0, GPIO.HIGH)
            
            elif (x == 5):
                GPIO.output(MUX1_B2, GPIO.HIGH)
                GPIO.output(MUX1_B1, GPIO.LOW)
                GPIO.output(MUX1_B0, GPIO.LOW)
            
            elif (x == 6):
                GPIO.output(MUX1_B2, GPIO.HIGH)
                GPIO.output(MUX1_B1, GPIO.LOW)
                GPIO.output(MUX1_B0, GPIO.HIGH)
            
            elif (x == 7):
                GPIO.output(MUX1_B2, GPIO.HIGH)
                GPIO.output(MUX1_B1, GPIO.HIGH)
                GPIO.output(MUX1_B0, GPIO.LOW)
            
            elif (x == 8):
                GPIO.output(MUX1_B2, GPIO.HIGH)
                GPIO.output(MUX1_B1, GPIO.HIGH)
                GPIO.output(MUX1_B0, GPIO.HIGH)                
                
            else: #(MUX defaults to well 1)
                GPIO.output(MUX1_B2, GPIO.LOW)
                GPIO.output(MUX1_B1, GPIO.LOW)
                GPIO.output(MUX1_B0, GPIO.LOW)
                
            for i in range(0, num_freq):
                # Sets the frequency and waits for the sine wave and the circuitry
                # to settle
                present_freq = np.floor(freq_list[i])
                sinegen.set_freq(present_freq)
                
                if (present_freq <= 500):
                    time.sleep(0.03)
                    delay_sw = 0.03
                else:
                    delay_sw = 0.001
                
                # Turns the switch to discharge capacitors
                GPIO.output(SWITCH_1, GPIO.HIGH)
                GPIO.output(SWITCH_2, GPIO.HIGH)
                time.sleep(delay_sw)
                GPIO.output(SWITCH_1, GPIO.LOW)
                GPIO.output(SWITCH_2, GPIO.LOW)
                time.sleep(delay_sw)
                    
                #Sample the data in channel 0 three times
                data0_1 = adc.read_adc(0)
                data0_2 = adc.read_adc(0)
                data0_3 = adc.read_adc(0)
                #Uses the average for voltage 0
                avg_data0 = (data0_1 + data0_2 + data0_3) / 3                  
                voltage0 = avg_data0 * 4.96 / 4095.0
                
                #Sample the data in channel 1 three times
                data1_1 = adc.read_adc(1)
                data1_2 = adc.read_adc(1)
                data1_3 = adc.read_adc(1)
                #Uses the average for voltage 0
                avg_data1 = (data1_1 + data1_2 + data1_3) / 3
                voltage1 = avg_data1 * 4.96 / 4095.0
                    
                #If the voltage is too low!
                if (voltage1 <= low_volt_range):
                    low_volt = True
                    #Switch to the next lower capacitor. If its at the lowest, it remains at the lowest
                    #capacitor
                    if (base_cap_index == 2):
                        base_cap_index = 1
                        GPIO.output(MUX2_B2, GPIO.LOW)
                        GPIO.output(MUX2_B1, GPIO.LOW)
                        GPIO.output(MUX2_B0, GPIO.LOW)
                    else:
                        base_cap_index = 0
                        GPIO.output(MUX2_B2, GPIO.LOW)
                        GPIO.output(MUX2_B1, GPIO.LOW)
                        GPIO.output(MUX2_B0, GPIO.HIGH)
                        
                    #Repeat with new capacitor
                    if (present_freq <= 500):
                        time.sleep(0.03)
                        delay_sw = 0.03
                    else:
                        delay_sw = 0.001
                    
                    GPIO.output(SWITCH_1, GPIO.HIGH)
                    GPIO.output(SWITCH_2, GPIO.HIGH)
                    time.sleep(delay_sw)
                    GPIO.output(SWITCH_1, GPIO.LOW)
                    GPIO.output(SWITCH_2, GPIO.LOW)
                    time.sleep(delay_sw)
                    
                    data1_1 = adc.read_adc(1)
                    data1_2 = adc.read_adc(1)
                    data1_3 = adc.read_adc(1)
                    avg_data1 = (data1_1 + data1_2 + data1_3) / 3
                    voltage1 = avg_data1 * 4.96 / 4095.0
                    
                    #Voltage is still too low!
                    if (voltage1 <= low_volt_range):
                        #Cant read that value
                        #Resets capacitor back to 20pF capacitor
                        base_cap_index = 1
                        GPIO.output(MUX2_B2, GPIO.LOW)
                        GPIO.output(MUX2_B1, GPIO.LOW)
                        GPIO.output(MUX2_B0, GPIO.LOW)
                        
                        #Add error values to data lists
                        Xc_list.append(-1)
                        dut_cap_list.append(-1)
                        V_ch0_list.append(voltage0)
                        V_ch1_list.append(voltage1)
                        #print("Data cannot be calculated for:")
                        #print("Frequency:", present_freq)
                        #print("Capacitor:", base_caps[base_cap_index]
                        #print("V1 Low:", voltage1)
                    
                    #Voltage was too low but is now in the acceptable range
                    else:
                        #Calculates the impedance
                        Xc = (avg_data0 * 1 / ( 2 * math.pi * present_freq * base_caps[base_cap_index])) / avg_data1
                        #Calculates the capacitance
                        dut_cap = 1 / (2 * math.pi * present_freq * Xc)
                        
                        #Appends data to this well's and this sweep's list
                        Xc_list.append(Xc)
                        dut_cap_list.append(dut_cap)
                        V_ch0_list.append(voltage0)
                        V_ch1_list.append(voltage1)
                    
                #If voltage is too high!
                elif (voltage1 >= high_volt_range):
                    #Switch to the next higher capacitor. If its at the highest, it remains at the highest
                    #capacitor
                    if (base_cap_index == 0):
                        base_cap_index = 1
                        GPIO.output(MUX2_B2, GPIO.LOW)
                        GPIO.output(MUX2_B1, GPIO.LOW)
                        GPIO.output(MUX2_B0, GPIO.LOW)
                    else:
                        base_cap_index = 2
                        GPIO.output(MUX2_B2, GPIO.LOW)
                        GPIO.output(MUX2_B1, GPIO.HIGH)
                        GPIO.output(MUX2_B0, GPIO.LOW)
                    
                    #Repeat with new capacitor
                    if (present_freq <= 500):
                        time.sleep(0.03)
                        delay_sw = 0.03
                    else:
                        delay_sw = 0.001
                    
                    GPIO.output(SWITCH_1, GPIO.HIGH)
                    GPIO.output(SWITCH_2, GPIO.HIGH)
                    time.sleep(delay_sw)
                    GPIO.output(SWITCH_1, GPIO.LOW)
                    GPIO.output(SWITCH_2, GPIO.LOW)
                    time.sleep(delay_sw)
                    
                    data1_1 = adc.read_adc(1)
                    data1_2 = adc.read_adc(1)
                    data1_3 = adc.read_adc(1)
                    avg_data1 = (data1_1 + data1_2 + data1_3) / 3
                    voltage1 = avg_data1 *4.96 / 4095.0
                    
                    #Voltage is still too high!                    
                    if (voltage1 >= high_volt_range):
                        #Cant read that value
                        #Resets capacitor back to 20pF capacitor
                        base_cap_index = 1
                        GPIO.output(MUX2_B2, GPIO.LOW)
                        GPIO.output(MUX2_B1, GPIO.LOW)
                        GPIO.output(MUX2_B0, GPIO.LOW)
                        
                        
                        #Add error values to data lists
                        Xc_list.append(-1)
                        dut_cap_list.append(-1)
                        V_ch0_list.append(voltage0)
                        V_ch1_list.append(voltage1)
                        #print("Data cannot be calculated for:")
                        #print("Frequency:", present_freq)
                        #print("Capacitor:", base_caps[base_cap_index])
                        #print("V1 High2:", voltage1)
                    
                    #Voltage was too high but is now in the acceptable range
                    else:
                        #Calculates the impedance
                        Xc = (avg_data0 * 1 / ( 2 * math.pi * present_freq * base_caps[base_cap_index])) / avg_data1
                        #Calculates the capacitance
                        dut_cap = 1 / (2 * math.pi * present_freq * Xc)
                        
                        #Appends data to this well's and this sweep's list
                        Xc_list.append(Xc)
                        dut_cap_list.append(dut_cap)
                        V_ch0_list.append(voltage0)
                        V_ch1_list.append(voltage1)
                        
                #Voltage is in the acceptable range with the current capacitor        
                else:
                    #Calculates the impedance
                    Xc = (avg_data0 * 1 / ( 2 * math.pi * present_freq * base_caps[base_cap_index])) / avg_data1
                    #Calculates the capacitance
                    dut_cap = 1 / (2 * math.pi * present_freq * Xc)
                    
                    #Appends data to this well's and this sweep's list
                    Xc_list.append(Xc)
                    dut_cap_list.append(dut_cap)
                    V_ch0_list.append(voltage0)
                    V_ch1_list.append(voltage1)
                    
            #Appends the entire list from this well and its frequency sweep
            #to the data lists
            Xc_data.append(Xc_list)
            dut_cap_data.append(dut_cap_list)
            V_ch0_data.append(V_ch0_list)
            V_ch1_data.append(V_ch1_list)
            
        #Displays the total data lists on the shell
        print("Xc Data:\n", Xc_data)
        print("Cap Data:\n", dut_cap_data)
        print("V0 Data:\n", V_ch0_data)
        print("V1 Data:\n", V_ch1_data)
        #Writes data lists to the file
        f.file_append(well_num, freq_list, Xc_data, dut_cap_data,
                     current_time_data, num_freq)
        #print("Freq List:\n", freq_list)
        
        #Time that the sweep ended
        time_sweep_end = timer()
        #Calculates the elapsed time after the sweep is done
        #This is to help control when test is done
        elapsed_time = (timer() - start_time)
        print("Elapsed:", elapsed_time)
        #This calculates the delay that should occur between each sweep
        #based on the sweeps/hr given by the user and the time the program took
        #to finish the last sweep
        print("Sweep time:", (time_sweep_end - time_sweep_start), "Sweep/hr:", sweeps_hr,
              "Samples/hr:", samples_hr)
        print("Delay:", samples_hr - (time_sweep_end - time_sweep_start))
        if (elapsed_time < total_duration):
            time.sleep(samples_hr - (time_sweep_end - time_sweep_start))        
        
        #Clears all the data lists for new sweep
        Xc_data.clear()
        dut_cap_data.clear()
        V_ch0_data.clear()
        V_ch1_data.clear()
    print("DONE WITH TEST")