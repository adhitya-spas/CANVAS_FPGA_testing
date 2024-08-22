# --------------------------------------------------------------------------------------------------
# Import libraries
import serial
import time
from time import sleep
import sys
import os
import csv
import random
import numpy as np

# Third-party libraries
import pyvisa
import pathlib

# Custom libraries
from longtermtest_FPGA import init_FPGA, reset_PIC_FPGA, config_FPGA
# from serialfcns import readFPGA, ser_write, response_check

Ch1 = "Ch1"
Ch2 = "Ch2"
Ch3 = "Ch3"
Ch4 = "Ch4"
Ch5 = "Ch5"
All = "All"

sine = "sine"

# --------------------------------------------------------------------------------------------------
### MACROS for Testing (1 -> True, 0 -> False)
FIXED_FREQ  = 1#2                 # Set to 1 if you want to set frequencies || Set to 0 if you want random frequencies || Set to 2 if you want a step-wise frequency change
FIXED_AMP   = 1#2                 # Set to 1 if you want to set amplitude || Set to 0 if you want random amplitude
FIXED_PHASE = 1#0                 # Set to 1 if you want to set phase || Set to 0 if you want random phase

RAW_DATA    = 1                 # Set to 1 if you want packets saved with "\n" || Set to 0 if you want raw data
# --------------------------------------------------------------------------------------------------
### DEFINE Constants
start_freq  = 192       # Hz
end_freq    = 42432     # Hz
step_freq   = 1         # Hz
set_freq    = [512, 3000, 10000, 23000, 33000]     # [Ch1, Ch2, Ch3, Ch4, Ch5] || FOR FIXED FREQ, line 75

hi_amp      = 80* 10**-3     #Vpp    # max amplitude of VHDL sims (27345)
mid_amp     = 10* 10**-3     #Vpp
low_amp     = 4*  10**-3     #Vpp
step_amp    = 1*  10**-3     #Vpp   
set_amp     = [low_amp, low_amp, low_amp, low_amp, low_amp]      # [Ch1, Ch2, Ch3, Ch4, Ch5] || FOR FIXED AMP, line 100

start_phase = 0         # deg
end_phase   = 180       # deg
step_phase  = 1         # deg
set_phase   = [0, 32, 46, 73, 16]     # [Ch1, Ch2, Ch3, Ch4, Ch5] || FOR FIXED PHASE, line 110

switch_time = 10        # seconds
switch_count= 0         # A counter for FIXED_FREQ=2; when to switch between testing sets 
counter     = 0         # A counter for FIXED_FREQ=2; when to stop each set
title_print = 0         # A check to print the title of the test set in logs
amp_switch  = 0         # 0-> Low | 1-> Mid | 2-> High
freq_switch = 0         # 0-> Ch 1 | 1-> Ch 2 | 2-> Ch 3 | 3-> Ch 4 | 4-> Ch 5 |

# Available frequencies (Hz)
freq_list = np.arange(start = start_freq, stop = end_freq, step = step_freq).tolist()

# Frequencies in No-No list (Edge cases) (Hz)
edge_freq = [192, 320, 448, 576, 704, 832, 960, 1088, 1216, 1344, 1472, 1600, 1728, 1856, 1984, 2112, 2240, 2368, 2496, 2752, 3008, 3264, 3520, 3776, 4032, 4288, 4544, 4800, 5056, 5568, 6080, 6592, 7104, 7616, 8128, 8640, 9152, 9664, 10688, 11712, 12736, 13760, 14784, 15808, 16832, 17856, 18880, 19904, 21952, 24000, 26048, 28096, 30144, 32192, 34240, 36288, 38336, 42432]

# Phases in No-No list (Do not want typical cases) (deg)
no_no_phase = [0, 45, 90, 135, 180]

# Change if communication error
# pic1_COM    = "COM4"
# pic2_COM    = "COM10"
# pic3_COM    = "COM9"
# FPGA_COM    = "COM3"

# --------------------------------------------------------------------------------------------------
### LOG FILE Initialization

## Making file name
dateString = time.strftime("%Y-%m-%d_%H%M")
filepath = "./log_data/" + dateString + "longlog.csv"

## Creating csv file - printing header
with open(filepath, 'a') as f_object:
    writer_object = csv.writer(f_object)
    writer_object.writerow(["Long Term Testing Log File","","","-",time.strftime("%Y-%m-%d_%H%M%S")])
    writer_object.writerow(["Time","","","","","Param", "Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5", "Message"])

# --------------------------------------------------------------------------------------------------
while(True):

    if FIXED_AMP == 2:
        if amp_switch==0:
            amp1 = low_amp
            amp2 = low_amp
            amp3 = low_amp
            amp4 = low_amp
            amp5 = low_amp
        elif amp_switch==1:
            amp1 = mid_amp
            amp2 = mid_amp
            amp3 = mid_amp
            amp4 = mid_amp
            amp5 = mid_amp
        elif amp_switch==2:
            amp1 = hi_amp
            amp2 = hi_amp
            amp3 = hi_amp
            amp4 = hi_amp
            amp5 = hi_amp

    ### Transition between Different Frequency Changes
    if FIXED_FREQ == 2:
        # (1) Preset Frequency at Low, Mid and Hi amplitudes

        # Start with first preset frequency as defined in Line 41 set_freq
        if switch_count==0:         
            if title_print==0:
                with open(filepath, 'a') as f_object:
                    writer_object = csv.writer(f_object)
                    writer_object.writerow(["","","","","","", "", "", "", "", "", "STARTING TEST SET "+str(switch_count+1)+": PRESET FREQ & AMP ("+str(amp_switch+1)+"/3)"])
                title_print=1
                FIXED_AMP = 2               # Forcing AMP to be fixed
            if counter< 3:                  # Change if you want more time for this
                freq1 = set_freq[0]
                freq2 = set_freq[1]
                freq3 = set_freq[2]
                freq4 = set_freq[3]
                freq5 = set_freq[4]
            else:
                counter=-1
                amp_switch+=1
                title_print=0
                if amp_switch > 2:
                    switch_count+=1
                    amp_switch=0

        # Second, run random frequencies for a while
        elif switch_count==1:         
            if title_print==0:
                with open(filepath, 'a') as f_object:
                    writer_object = csv.writer(f_object)
                    writer_object.writerow(["","","","","","", "", "", "", "", "", "STARTING TEST SET "+str(switch_count+1)+": RND FREQ and AMP "])
                title_print=1
                FIXED_AMP = 0               # Forcing AMP to be fixed random
            if counter< 5:                  # Change if you want more time for this
                # Choosing Frequencies (Hz)
                freq1 = random.choice([ele for ele in freq_list if ele != edge_freq])
                freq2 = random.choice([ele for ele in freq_list if ele != edge_freq])
                freq3 = random.choice([ele for ele in freq_list if ele != edge_freq])
                freq4 = random.choice([ele for ele in freq_list if ele != edge_freq])
                freq5 = random.choice([ele for ele in freq_list if ele != edge_freq])

            else:
                counter=-1
                amp_switch+=1
                title_print=0
                if amp_switch > 0:
                    switch_count+=1
                    amp_switch=0

        # Next case is going up the freq ladder and down
        elif switch_count==2:
            if title_print==0:
                # Available frequencies (Hz)
                freq_list = np.arange(start = start_freq, stop = end_freq, step = step_freq).tolist()
                counter = 0
                switch_time = 5     # Reducing switch time to get a good transition
                up = 1

                with open(filepath, 'a') as f_object:
                    writer_object = csv.writer(f_object)
                    writer_object.writerow(["","","","","","", "", "", "", "", "", "STARTING TEST SET "+str(switch_count+1)+": STEP UP AND DOWN FREQ and AMP: "+str(amp_switch)])
                title_print=1
            
            if counter< len(freq_list):  
                if freq_switch == 0:               
                    freq1 = freq_list[counter]
                    freq2 = set_freq[1]
                    freq3 = set_freq[2]
                    freq4 = set_freq[3]
                    freq5 = set_freq[4]
                elif freq_switch == 1:               
                    freq1 = set_freq[0]
                    freq2 = freq_list[counter]
                    freq3 = set_freq[2]
                    freq4 = set_freq[3]
                    freq5 = set_freq[4]
                elif freq_switch == 2:               
                    freq1 = set_freq[0]
                    freq2 = set_freq[1]
                    freq3 = freq_list[counter]
                    freq4 = set_freq[3]
                    freq5 = set_freq[4]
                elif freq_switch == 3:               
                    freq1 = set_freq[0]
                    freq2 = set_freq[1]
                    freq3 = set_freq[2]
                    freq4 = freq_list[counter]
                    freq5 = set_freq[4]
                elif freq_switch == 4:               
                    freq1 = set_freq[0]
                    freq2 = set_freq[1]
                    freq3 = set_freq[2]
                    freq4 = set_freq[3]
                    freq5 = freq_list[counter]
            else:
                if up == 1:
                    counter=-1
                    up = 0
                    freq_list = np.arange(start = end_freq, stop = start_freq, step = step_freq).tolist()
                elif up == 0:
                    counter=-1
                    amp_switch+=1
                    title_print=0
                    up = 1
                    if amp_switch > 2:
                        freq_switch+=1
                        if freq_switch > 4:
                            switch_count=0
                            amp_switch=0
        
        # Counter to change test sets
        counter+=1

    ### Initializing Parameters: Frequency and Amplitude

    ## Random Frequency Generator
    if FIXED_FREQ == 0:
        # Available frequencies (Hz)
        freq_list = np.arange(start = start_freq, stop = end_freq, step = step_freq).tolist()

        # Frequencies in No-No list (Edge cases) (Hz)
        edge_freq = [192, 320, 448, 576, 704, 832, 960, 1088, 1216, 1344, 1472, 1600, 1728, 1856, 1984, 2112, 2240, 2368, 2496, 2752, 3008, 3264, 3520, 3776, 4032, 4288, 4544, 4800, 5056, 5568, 6080, 6592, 7104, 7616, 8128, 8640, 9152, 9664, 10688, 11712, 12736, 13760, 14784, 15808, 16832, 17856, 18880, 19904, 21952, 24000, 26048, 28096, 30144, 32192, 34240, 36288, 38336, 42432]

        # Choosing Frequencies (Hz)
        freq1 = random.choice([ele for ele in freq_list if ele != edge_freq])
        freq2 = random.choice([ele for ele in freq_list if ele != edge_freq])
        freq3 = random.choice([ele for ele in freq_list if ele != edge_freq])
        freq4 = random.choice([ele for ele in freq_list if ele != edge_freq])
        freq5 = random.choice([ele for ele in freq_list if ele != edge_freq])

    if FIXED_FREQ == 1:
        # Manually set frequency in Line 41
        freq1 = set_freq[0]
        freq2 = set_freq[1]
        freq3 = set_freq[2]
        freq4 = set_freq[3]
        freq5 = set_freq[4]


    ## Random Amplitude Generator
    if FIXED_AMP == 0:

        # Available Amplitudes
        amp_list = np.arange(start = low_amp, stop = hi_amp, step = step_amp).tolist()
        
        if switch_count == 2:
            if counter == -1:
                # Choosing Amplitudes (Vpp)
                amp1 = random.choice(amp_list)
                amp2 = random.choice(amp_list)
                amp3 = random.choice(amp_list)
                amp4 = random.choice(amp_list)
                amp5 = random.choice(amp_list)
            else:
                # Choosing Amplitudes (Vpp)
                amp1 = random.choice(amp_list)
                amp2 = random.choice(amp_list)
                amp3 = random.choice(amp_list)
                amp4 = random.choice(amp_list)
                amp5 = random.choice(amp_list)

    if FIXED_AMP == 1:
        # Manually set amplitude in Line 41
        amp1 = set_amp[0]
        amp2 = set_amp[1]
        amp3 = set_amp[2]
        amp4 = set_amp[3]
        amp5 = set_amp[4]


    ## Random Phase Generator
    if FIXED_PHASE == 0:
        # Available Amplitudes
        phase_list = np.arange(start = start_phase, stop = end_phase, step = step_phase).tolist()

        # Choosing Phase (deg)
        phase1 = random.choice([ele for ele in phase_list if ele != no_no_phase])
        phase2 = random.choice([ele for ele in phase_list if ele != no_no_phase])
        phase3 = random.choice([ele for ele in phase_list if ele != no_no_phase])
        phase4 = random.choice([ele for ele in phase_list if ele != no_no_phase])
        phase5 = random.choice([ele for ele in phase_list if ele != no_no_phase])

    if FIXED_PHASE == 1:
        # Manually set phase in Line 46
        phase1 = set_phase[0]
        phase2 = set_phase[1]
        phase3 = set_phase[2]
        phase4 = set_phase[3]
        phase5 = set_phase[4]


    ## Writing Values into log file - printing frequency and amplitude
    with open(filepath, 'a') as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow([""])
        writer_object.writerow([time.strftime("%Y-%m-%d_%H%M%S"), "", "","","", "FREQ", str(freq1), str(freq2), str(freq3), str(freq4), str(freq5)])
        writer_object.writerow([time.strftime("%Y-%m-%d_%H%M%S"), "", "","","", "AMP", str(amp1), str(amp2), str(amp3), str(amp4), str(amp5)])
        writer_object.writerow([time.strftime("%Y-%m-%d_%H%M%S"), "", "","","", "PHASE", str(phase1), str(phase2), str(phase3), str(phase4), str(phase5)])

    # --------------------------------------------------------------------------------------------------
    ### Starting Signal Generator

    ## Initialize resource manager
    rm = pyvisa.ResourceManager()

    # List all connected resources
    print("Resources detected\n{}\n".format(rm.list_resources()))

    ## Based on Resource List, open three signal generator
    # 'USB0::0xF4ED::0xEE3A::SDG10GA2162677::INSTR',  Top one
    # 'USB0::0xF4ED::0xEE3A::SDG10GAQ1R1236::INSTR',  Middle one
    # 'USB0::0xF4ED::0xEE3A::SDG10GAX1R0601::INSTR',  Bottom one
    # 'USB0::0xF4EC::0x1430::SPD3XJFQ7R5455::INSTR', 
    # 'ASRL1::INSTR', 
    # 'ASRL10::INSTR'

    ## Open Signal Generator 1 (The top of the stack)
    print("Setting up Signal Generator 1")
    SG2025_1 = rm.open_resource('USB0::0xF4ED::0xEE3A::SDG10GA2162677::INSTR') # confirm parameters

    # Configure to measure DC current
    SG2025_1.write("*rst")
    SG2025_1.write("*idn?") 

    # Configure to output sine wave
    time.sleep(0.1)
    print("Setting up Channel 1")
    SG2025_1.write("C1:BSWV WVTP,SINE")
    time.sleep(0.1)
    SG2025_1.write("C1:BSWV FRQ,",str(freq1))
    time.sleep(0.1)
    SG2025_1.write("C1:BSWV AMP,",str(amp1))
    time.sleep(0.1)
    SG2025_1.write("C1:BSWV PHSE,",str(phase1))
    SG2025_1.write("C1:OUTP ON")
    print("\t : COMPLETED")

    time.sleep(0.1)
    print("Setting up Channel 2")
    SG2025_1.write("C2:BSWV WVTP,SINE")
    time.sleep(0.1)
    SG2025_1.write("C2:BSWV FRQ,",str(freq2))
    time.sleep(0.1)
    SG2025_1.write("C2:BSWV AMP,",str(amp2))
    time.sleep(0.1)
    SG2025_1.write("C2:BSWV PHSE,",str(phase2))
    SG2025_1.write("C2:OUTP ON")
    print("\t : COMPLETED")

    
    ## Open Signal Generator 2 (In the middle of the stack)
    print("Setting up Signal Generator 2")
    SG2025_2 = rm.open_resource('USB0::0xF4ED::0xEE3A::SDG10GAQ1R1236::INSTR') # confirm parameters

    # Configure to measure DC current
    SG2025_2.write("*rst")
    SG2025_2.write("*idn?") 

    # Configure to output sine wave
    time.sleep(0.1)
    print("Setting up Channel 3")
    SG2025_2.write("C1:BSWV WVTP,SINE")
    time.sleep(0.1)
    SG2025_2.write("C1:BSWV FRQ,",str(freq3))
    time.sleep(0.1)
    SG2025_2.write("C1:BSWV AMP,",str(amp3))
    time.sleep(0.1)
    SG2025_2.write("C1:BSWV PHSE,",str(phase3))
    SG2025_2.write("C1:OUTP ON")
    print("\t : COMPLETED")

    time.sleep(0.1)
    print("Setting up Channel 4")
    SG2025_2.write("C2:BSWV WVTP,SINE")
    time.sleep(0.1)
    SG2025_2.write("C2:BSWV FRQ,",str(freq4))
    time.sleep(0.1)
    SG2025_2.write("C2:BSWV AMP,",str(amp4))
    time.sleep(0.1)
    SG2025_2.write("C2:BSWV PHSE,",str(phase4))
    SG2025_2.write("C2:OUTP ON")
    print("\t : COMPLETED")


    ## Open Signal Generator 3 (The bottom of the stack)
    print("Setting up Signal Generator 3")
    SG2025_3 = rm.open_resource('USB0::0xF4ED::0xEE3A::SDG10GAX1R0601::INSTR') # confirm parameters

    # Configure to measure DC current
    SG2025_3.write("*rst")
    SG2025_3.write("*idn?") 

    # Configure to output sine wave
    time.sleep(0.1)
    print("Setting up Channel 5")
    SG2025_3.write("C1:BSWV WVTP,SINE")
    time.sleep(0.1)
    SG2025_3.write("C1:BSWV FRQ,",str(freq5))
    time.sleep(0.1)
    SG2025_3.write("C1:BSWV AMP,",str(amp5))
    time.sleep(0.1)
    SG2025_3.write("C1:BSWV PHSE,",str(phase5))
    SG2025_3.write("C1:OUTP ON")
    print("\t : COMPLETED")
    print("\n Signal Generators Setup")

    ## Writing Confirmation into Log File
    with open(filepath, 'a') as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow([time.strftime("%Y-%m-%d_%H%M%S"), "", "", "", "", "", "", "", "", "", "", "SIGNAL GENERATORS ARE SETUP"])

    # --------------------------------------------------------------------------------------------------
    ### FPGA and PIC controls

    ## Initialising FPGA - define COM ports in DEFINE line 51
    # FPGA_ser = init_FPGA(FPGA_COM)

    ## Reset PIC and FPGA
    # FPGA_ser = reset_FPGA(FPGA_ser)

    ## Buffering? ????????
    # ???????

    ## Writing Confirmation of FPGA starting
    # with open(filepath, 'a') as f_object:
    #     writer_object = csv.writer(f_object)
    #     writer_object.writerow([time.strftime("%Y-%m-%d_%H%M"), "", "", "", "", "", "", "", "", "", "", "PIC & FPGA Initialized - STARTING FPGA"])

    ## Start FPGA
    # config_FPGA(FPGA_ser, freq1, freq2, freq3, freq4, freq5, time.strftime("%Y-%m-%d_%H%M"), RAW_DATA)

    # --------------------------------------------------------------------------------------------------
    ### Wait time for next signal transition
    time.sleep(switch_time)     # switch_time can be set up in the MACRO SECTION in Line 53

# SG2025_1.write("C1:OUTP OFF")