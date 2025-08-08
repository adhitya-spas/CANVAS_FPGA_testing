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
#import datetime
from datetime import datetime, timedelta, timezone

# Third-party libraries
import pyvisa
import pathlib

# Custom libraries
from longtermtest_FPGA import init_FPGA, reset_PIC_FPGA, config_FPGA
from Shutdown_Signal_Generator import shutdown_cmd
# from serialfcns import readFPGA, ser_write, response_check

Ch1 = "Ch1" #EF1
Ch2 = "Ch2" #EF2
Ch3 = "Ch3" #BF1
Ch4 = "Ch4" #BF2
Ch5 = "Ch5" #BF3
All = "All"

sine = "sine"

# --------------------------------------------------------------------------------------------------
### MACROS for Testing (1 -> True, 0 -> False)
FIXED_FREQ  = 3#2                 # Set to 1 if you want to set frequencies || Set to 0 if you want random frequencies || Set to 2 if you want a step-wise frequency change (with an ordered change, overwrites FIXED_AMP)
FIXED_AMP   = 3                 # Set to 1 if you want to set amplitude || Set to 0 if you want random amplitude || Set to 2 if you want a step-wise amplitude change
FIXED_PHASE = 1                 # Set to 1 if you want to set phase || Set to 0 if you want random phase

RAW_DATA    = 1                 # Set to 1 if you want packets saved with "\n" || Set to 0 if you want raw data
# --------------------------------------------------------------------------------------------------
### DEFINE Constants
start_freq  = 192       # Hz
end_freq    = 42432     # Hz
step_freq   = 1         # Hz
set_freq    = [512, 512, 512, 512, 512, 512]    # [Ch1, Ch2, Ch3, Ch4, Ch5] || FOR FIXED FREQ, line 75

# hi_amp      = 60* 10**-3     #Vpp    # max amplitude of VHDL sims (27345)
# mid_amp     = 10* 10**-3     #Vpp
# low_amp     = 4*  10**-3     #Vpp
# step_amp    = 1*  10**-3     #Vpp   
# set_amp     = [low_amp, low_amp, low_amp, low_amp, low_amp]      # [Ch1, Ch2, Ch3, Ch4, Ch5] || FOR FIXED AMP, line 100

# Splitting Amplitude ranges into BF and EF ranges
hi_amp_bf      = 1200* 10**-3     #Vpp 
mid_amp_bf     = 600*   10**-3     #Vpp
low_amp_bf     = 15*    10**-3     #Vpp
step_amp_bf    = 5*22*    10**-3     #Vpp   

hi_amp_ef      = 60* 10**-3     #Vpp 
mid_amp_ef     = 10* 10**-3     #Vpp
low_amp_ef     = 4*  10**-3     #Vpp
step_amp_ef    = 5*1*  10**-3     #Vpp   

set_amp     = [low_amp_ef, low_amp_ef, low_amp_bf, low_amp_bf, low_amp_bf]      # [Ch1, Ch2, Ch3, Ch4, Ch5] || FOR FIXED AMP, line 100

start_phase = 0         # deg
end_phase   = 180       # deg
step_phase  = 1         # deg
set_phase   = [0, 32, 46, 73, 16]     # [Ch1, Ch2, Ch3, Ch4, Ch5] || FOR FIXED PHASE, line 110

switch_time = 0.1      # seconds (prev 10 sec)
switch_count= 0         # A counter for FIXED_FREQ=2; when to switch between testing sets 
counter_f     = 0         # A counter for FIXED_FREQ=2; when to stop each set
counter_a   = 0         # A counter for FIXEWD_AMP=2; to switch between different amplitudes
title_print = 0         # A check to print the title of the test set in logs
amp_switch  = 0         # 0-> Low | 1-> Mid | 2-> High
freq_switch = 0         # 0-> Ch 1 | 1-> Ch 2 | 2-> Ch 3 | 3-> Ch 4 | 4-> Ch 5 |
message     = ""
systicks    = 0

epoch_start = datetime(1999, 12, 31, 16, 0, 0)   #Start epoch date
utc_start   = datetime(1999, 12, 31, 22, 0, 0)   #Start utc date
start_datetime = datetime.now()
# Available frequencies (Hz)
freq_list = np.arange(start = start_freq, stop = end_freq, step = step_freq).tolist()

# Available Amplitudes (Vpp)
bf_amp_list = np.arange(start =low_amp_bf, stop = hi_amp_bf, step = step_amp_bf).tolist()
ef_amp_list = np.arange(start =low_amp_ef, stop = hi_amp_ef, step = step_amp_ef).tolist()

# Frequencies in No-No list (Edge cases) (Hz)
edge_freq = [192, 320, 448, 576, 704, 832, 960, 1088, 1216, 1344, 1472, 1600, 1728, 1856, 1984, 2112, 2240, 2368, 2496, 2752, 3008, 3264, 3520, 3776, 4032, 4288, 4544, 4800, 5056, 5568, 6080, 6592, 7104, 7616, 8128, 8640, 9152, 9664, 10688, 11712, 12736, 13760, 14784, 15808, 16832, 17856, 18880, 19904, 21952, 24000, 26048, 28096, 30144, 32192, 34240, 36288, 38336, 42432]

center_bin_freq = [
    0, 128, 256, 384, 512, 640, 768, 896, 1024, 1152, 1280, 1408, 1536, 1664, 1792, 1920,
    2048, 2176, 2304, 2432, 2560, 2688, 2816, 2944, 3072, 3200, 3328, 3456, 3584, 3712, 3840, 3968,
    4096, 4224, 4352, 4480, 4608, 4736, 4864, 4992, 5120, 5248, 5376, 5504, 5632, 5760, 5888, 6016,
    6144, 6272, 6400, 6528, 6656, 6784, 6912, 7040, 7168, 7296, 7424, 7552, 7680, 7808, 7936, 8064,
    8192, 8320, 8448, 8576, 8704, 8832, 8960, 9088, 9216, 9344, 9472, 9600, 9728, 9856, 9984, 10112,
    10240, 10368, 10496, 10624, 10752, 10880, 11008, 11136, 11264, 11392, 11520, 11648, 11776, 11904, 12032, 12160,
    12288, 12416, 12544, 12672, 12800, 12928, 13056, 13184, 13312, 13440, 13568, 13696, 13824, 13952, 14080, 14208,
    14336, 14464, 14592, 14720, 14848, 14976, 15104, 15232, 15360, 15488, 15616, 15744, 15872, 16000, 16128, 16256,
    16384, 16512, 16640, 16768, 16896, 17024, 17152, 17280, 17408, 17536, 17664, 17792, 17920, 18048, 18176, 18304,
    18432, 18560, 18688, 18816, 18944, 19072, 19200, 19328, 19456, 19584, 19712, 19840, 19968, 20096, 20224, 20352,
    20480, 20608, 20736, 20864, 20992, 21120, 21248, 21376, 21504, 21632, 21760, 21888, 22016, 22144, 22272, 22400,
    22528, 22656, 22784, 22912, 23040, 23168, 23296, 23424, 23552, 23680, 23808, 23936, 24064, 24192, 24320, 24448,
    24576, 24704, 24832, 24960, 25088, 25216, 25344, 25472, 25600, 25728, 25856, 25984, 26112, 26240, 26368, 26496,
    26624, 26752, 26880, 27008, 27136, 27264, 27392, 27520, 27648, 27776, 27904, 28032, 28160, 28288, 28416, 28544,
    28672, 28800, 28928, 29056, 29184, 29312, 29440, 29568, 29696, 29824, 29952, 30080, 30208, 30336, 30464, 30592,
    30720, 30848, 30976, 31104, 31232, 31360, 31488, 31616, 31744, 31872, 32000, 32128, 32256, 32384, 32512, 32640,
    32768, 32896, 33024, 33152, 33280, 33408, 33536, 33664, 33792, 33920, 34048, 34176, 34304, 34432, 34560, 34688,
    34816, 34944, 35072, 35200, 35328, 35456, 35584, 35712, 35840, 35968, 36096, 36224, 36352, 36480, 36608, 36736,
    36864, 36992, 37120, 37248, 37376, 37504, 37632, 37760, 37888, 38016, 38144, 38272, 38400, 38528, 38656, 38784,
    38912, 39040, 39168, 39296, 39424, 39552, 39680, 39808, 39936, 40064, 40192, 40320, 40448, 40576, 40704, 40832,
    40960, 41088, 41216, 41344, 41472, 41600, 41728, 41856, 41984, 42112, 42240, 42368, 42496
    #, 42624, 42752, 42880,
    #43008, 43136, 43264, 43392, 43520, 43648, 43776, 43904, 44032, 44160, 44288, 44416, 44544, 44672, 44800, 44928,
    #45056, 45184, 45312, 45440, 45568, 45696, 45824, 45952, 46080, 46208, 46336, 46464, 46592, 46720, 46848, 46976,
    #47104, 47232, 47360, 47488, 47616, 47744, 47872, 48000, 48128, 48256, 48384, 48512, 48640, 48768, 48896, 49024,
    #49152, 49280, 49408, 49536, 49664, 49792, 49920, 50048, 50176, 50304, 50432, 50560, 50688, 50816, 50944, 51072,
    #51200, 51328, 51456, 51584, 51712, 51840, 51968, 52096, 52224, 52352, 52480, 52608, 52736, 52864, 52992, 53120,
    #53248, 53376, 53504, 53632, 53760, 53888, 54016, 54144, 54272, 54400, 54528, 54656, 54784, 54912, 55040, 55168,
    #55296, 55424, 55552, 55680, 55808, 55936, 56064, 56192, 56320, 56448, 56576, 56704, 56832, 56960, 57088, 57216,
    #57344, 57472, 57600, 57728, 57856, 57984, 58112, 58240, 58368, 58496, 58624, 58752, 58880, 59008, 59136, 59264,
    #59392, 59520, 59648, 59776, 59904, 60032, 60160, 60288, 60416, 60544, 60672, 60800, 60928, 61056, 61184, 61312,
    #61440, 61568, 61696, 61824, 61952, 62080, 62208, 62336, 62464, 62592, 62720, 62848, 62976, 63104, 63232, 63360,
    #63488, 63616, 63744, 63872, 64000, 64128, 64256, 64384, 64512, 64640, 64768, 64896, 65024, 65152, 65280, 65408,
    #65536
]

# Phases in No-No list (Do not want typical cases) (deg)
no_no_phase = [0, 45, 90, 135, 180]

loop_no = 1
prev_amp_switch = -1
at_end = 1
# Change if communication error
# pic1_COM    = "COM4"
# pic2_COM    = "COM10"
# pic3_COM    = "COM9"
# FPGA_COM    = "COM3"

# --------------------------------------------------------------------------------------------------
### LOG FILE Initialization

## Making file name
dateString = time.strftime("%Y-%m-%d_%H%M")
filepath = "./log_data/" + dateString + "longlog_" + str(loop_no) +".csv"
#filepath = "CANVAS_git/CANVAS_FPGA_testing/log_data/" + dateString + "longlog_" + str(loop_no) +".csv"

## Creating csv file - printing header
with open(filepath, 'a') as f_object:
    writer_object = csv.writer(f_object)
    # writer_object.writerow(["Long Term Testing Log File","","","","-",time.strftime("%Y-%m-%d_%H%M%S")])
    writer_object.writerow(["UTC Time", "MT Time", "EPOCH", "Ch1_FREQ", "Ch1_AMP_gen_out", "Ch1_AMP_board_in", "Ch1_AMP_scale_ratio", "Ch1_PHASE", "Ch2_FREQ", "Ch2_AMP_gen_out", "Ch2_AMP_board_in", "Ch2_AMP_scale_ratio", "Ch2_PHASE", "Ch3_FREQ", "Ch3_AMP_gen_out", "Ch3_AMP_board_in", "Ch3_AMP_scale_ratio", "Ch3_PHASE", "Ch4_FREQ", "Ch4_AMP_gen_out", "Ch4_AMP_board_in", "Ch4_AMP_scale_ratio", "Ch4_PHASE", "Ch5_FREQ", "Ch5_AMP_gen_out", "Ch5_AMP_board_in", "Ch5_AMP_scale_ratio", "Ch5_PHASE", "Message"])

# --------------------------------------------------------------------------------------------------
while(True):
    message = "SIGNAL GENERATORS ARE SETUP"
    
    ### For chirps of frequency (up) and every up, increment amplitude
    if FIXED_AMP==3 and FIXED_FREQ ==3:
        #reset
        if at_end == 1:
            counter_f = 0
            counter_a +=1
            if counter_a >= len(ef_amp_list):
                counter_a = 0
            if freq_switch < 3:
                freq_switch += 1
            else:
                freq_switch = 0
            at_end = 0 
            
        #set freq    
        if freq_switch == 0:               
            freq1 = center_bin_freq[counter_f]
            freq2 = freq1
            freq3 = set_freq[2]
            freq4 = set_freq[3]
            freq5 = set_freq[4]
        elif freq_switch == 1:               
            freq1 = set_freq[0]
            freq2 = set_freq[1]
            freq3 = center_bin_freq[counter_f]
            freq4 = freq3
            freq5 = set_freq[4]
        elif freq_switch == 2:               
            freq1 = set_freq[0]
            freq2 = set_freq[1]
            freq3 = set_freq[2]
            freq4 = set_freq[3]
            freq5 = center_bin_freq[counter_f]
        
        #set amp
        amp1=ef_amp_list[counter_a]
        amp2=ef_amp_list[counter_a]
        amp3=bf_amp_list[counter_a]
        amp4=bf_amp_list[counter_a]
        amp5=bf_amp_list[counter_a]
        
        #increment
        counter_f +=1
        if counter_f >= len(center_bin_freq):
            at_end = 1
         
    
    if FIXED_AMP == 2:
        amp1=ef_amp_list[counter_a]
        amp2=ef_amp_list[counter_a]
        amp3=bf_amp_list[counter_a]
        amp4=bf_amp_list[counter_a]
        amp5=bf_amp_list[counter_a]

        counter_a+=1
    if counter_a>len(bf_amp_list)-2:
        counter_a = 0

    ### Transition between Different Frequency Changes
    if FIXED_FREQ == 2:
        # (1) Preset Frequency at Low, Mid and Hi amplitudes

        # Start with first preset frequency as defined in Line 41 set_freq
        if switch_count==0:         
            if title_print==0:
                # with open(filepath, 'a') as f_object:
                #     writer_object = csv.writer(f_object)
                #     writer_object.writerow(["","","","","","","", "", "", "", "", "", "STARTING TEST SET "+str(switch_count+1)+": PRESET FREQ & AMP ("+str(amp_switch+1)+"/3)"])
                message = "STARTING TEST SET "+str(switch_count+1)+": PRESET FREQ & AMP ("+str(amp_switch+1)+"/3)"
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
                # with open(filepath, 'a') as f_object:
                #     writer_object = csv.writer(f_object)
                #     writer_object.writerow(["","","","","","","", "", "", "", "", "", "STARTING TEST SET "+str(switch_count+1)+": RND FREQ and AMP "])
                message = "STARTING TEST SET "+str(switch_count+1)+": RND FREQ and AMP "
                title_print=1 
                FIXED_AMP = 0
            if counter< 5:    
                # Available frequencies (Hz)
                freq_list = np.arange(start = start_freq, stop = end_freq, step = step_freq).tolist()              # Change if you want more time for this
                # Choosing Frequencies (Hz)
                freq1 = random.choice([ele for ele in freq_list if ele != edge_freq])
                freq2 = freq1
                freq3 = random.choice([ele for ele in freq_list if ele != edge_freq])
                freq4 = freq3
                freq5 = random.choice([freq1,freq3])

            else:
                counter=-1
                amp_switch+=1
                title_print=0
                if amp_switch > 0:
                    switch_count+=1
                    amp_switch=0
                    up = 0

        # Next case is going up the freq ladder and down
        elif switch_count==2:
            if title_print==0:
                switch_time = 10     # Reducing switch time to get a good transition
                if up == 0:
                    counter=0
                    up = 0
                    freq_list = np.arange(start = start_freq, stop = end_freq, step = 100).tolist()
                if up == 1:
                    counter=0
                    up = 1
                    freq_list = np.arange(start = end_freq, stop = start_freq, step = -100).tolist()
                # with open(filepath, 'a') as f_object:
                #     writer_object = csv.writer(f_object)
                #     writer_object.writerow(["","","","","","","", "", "", "", "", "", "STARTING TEST SET "+str(switch_count+1)+": STEP UP AND DOWN FREQ and AMP: "+str(amp_switch)])
                message = "STARTING TEST SET "+str(switch_count+1)+": STEP UP AND DOWN FREQ and AMP: "+str(amp_switch)
                title_print=1
                FIXED_AMP = 0
            
            if counter< len(freq_list):  
                if freq_switch == 0:               
                    freq1 = freq_list[counter]
                    freq2 = freq1
                    freq3 = set_freq[2]
                    freq4 = set_freq[3]
                    freq5 = set_freq[4]
                # elif freq_switch == 1:               
                #     freq1 = set_freq[0]
                #     freq2 = freq_list[counter]
                #     freq3 = set_freq[2]
                #     freq4 = set_freq[3]
                #     freq5 = set_freq[4]
                elif freq_switch == 1:               
                    freq1 = set_freq[0]
                    freq2 = set_freq[1]
                    freq3 = freq_list[counter]
                    freq4 = freq3
                    freq5 = set_freq[4]
                # elif freq_switch == 3:               
                #     freq1 = set_freq[0]
                #     freq2 = set_freq[1]
                #     freq3 = set_freq[2]
                #     freq4 = freq_list[counter]
                #     freq5 = set_freq[4]
                elif freq_switch == 2:               
                    freq1 = set_freq[0]
                    freq2 = set_freq[1]
                    freq3 = set_freq[2]
                    freq4 = set_freq[3]
                    freq5 = freq_list[counter]
            else:
                if up == 0:
                    counter=-1
                    up = 1
                    #freq_list = np.arange(start = end_freq, stop = start_freq, step = 100).tolist()
                    title_print=0
                elif up == 1:
                    counter=-1
                    amp_switch+=1
                    title_print=0
                    up = 0
                    if amp_switch > 2:
                        freq_switch+=1
                        if freq_switch > 2:
                            switch_count=0
                            amp_switch=0
                            loop_no += 1
                            filepath = "./log_data/" + dateString + "longlog_" + str(loop_no) +".csv"
                            #filepath = "CANVAS_git/CANVAS_FPGA_testing/log_data/" + dateString + "longlog_" + str(loop_no) +".csv"
                            if loop_no % 3 == 0:
                                ## Creating csv file - printing header
                                with open(filepath, 'a') as f_object:
                                    writer_object = csv.writer(f_object)
                                    # writer_object.writerow(["Long Term Testing Log File","","","","-",time.strftime("%Y-%m-%d_%H%M%S")])
                                    writer_object.writerow(["UTC_Time", "MT_Time", "EPOCH", "Ch1_FREQ", "Ch1_AMP_gen_out", "Ch1_AMP_board_in", "Ch1_AMP_scale_ratio", "Ch1_PHASE", "Ch2_FREQ", "Ch2_AMP_gen_out", "Ch2_AMP_board_in", "Ch2_AMP_scale_ratio", "Ch2_PHASE", "Ch3_FREQ", "Ch3_AMP_gen_out", "Ch3_AMP_board_in", "Ch3_AMP_scale_ratio", "Ch3_PHASE", "Ch4_FREQ", "Ch4_AMP_gen_out", "Ch4_AMP_board_in", "Ch4_AMP_scale_ratio", "Ch4_PHASE", "Ch5_FREQ", "Ch5_AMP_gen_out", "Ch5_AMP_board_in", "Ch5_AMP_scale_ratio", "Ch5_PHASE", "Message"])
        
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
        amp_list_bf = np.arange(start = low_amp_bf, stop = hi_amp_bf, step = step_amp_bf).tolist()
        amp_list_ef = np.arange(start = low_amp_ef, stop = hi_amp_ef, step = step_amp_ef).tolist()
        
        if switch_count == 2:
            if prev_amp_switch != amp_switch:
                # Choosing Amplitudes (Vpp)
                amp1 = random.choice(amp_list_ef)
                amp2 = random.choice(amp_list_ef)
                amp3 = random.choice(amp_list_bf)
                amp4 = random.choice(amp_list_bf)
                amp5 = random.choice(amp_list_bf)
        else:                                  
            # Choosing Amplitudes (Vpp)
            amp1 = random.choice(amp_list_ef)
            amp2 = random.choice(amp_list_ef)
            amp3 = random.choice(amp_list_bf)
            amp4 = random.choice(amp_list_bf)
            amp5 = random.choice(amp_list_bf)

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

    ## Amplitude calculations
    b_in_amp1 = amp1/10
    b_in_amp2 = amp2/10
    b_in_amp3 = amp3
    b_in_amp4 = amp4
    b_in_amp5 = amp5

    sr_amp1 = amp1/(60*(10**-3))
    sr_amp2 = amp2/(60*(10**-3))
    sr_amp3 = amp3/(1.5)
    sr_amp4 = amp4/(1.5)
    sr_amp5 = amp5/(1.5)

    ## Writing Values into log file - printing frequency and amplitude
    with open(filepath, 'a') as f_object:
        writer_object = csv.writer(f_object)
        #writer_object.writerow([""])
        # writer_object.writerow([time.strftime("%Y-%m-%d_%H%M%S"),str((datetime.datetime.now() - epoch_start).total_seconds()), str(freq1), str(freq2), str(freq3), str(freq4), str(freq5)])
        # writer_object.writerow([time.strftime("%Y-%m-%d_%H%M%S"),str((datetime.datetime.now() - epoch_start).total_seconds()), "", "","","", "AMP", str(amp1), str(amp2), str(amp3), str(amp4), str(amp5)])
        # writer_object.writerow([time.strftime("%Y-%m-%d_%H%M%S"),str((datetime.datetime.now() - epoch_start).total_seconds()), "", "","","", "PHASE", str(phase1), str(phase2), str(phase3), str(phase4), str(phase5)])
        writer_object.writerow([
            datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S"),
            time.strftime("%Y-%m-%d_%H%M%S"), 
            str((datetime.now() - epoch_start).total_seconds()),
            str(freq1),
            str(amp1), str(b_in_amp1), str(sr_amp1),
            str(phase1),
            str(freq2),
            str(amp2), str(b_in_amp2), str(sr_amp2),
            str(phase2),
            str(freq3),
            str(amp3), str(b_in_amp3), str(sr_amp3),
            str(phase3),
            str(freq4),
            str(amp4), str(b_in_amp4), str(sr_amp4),
            str(phase4),
            str(freq5),
            str(amp5), str(b_in_amp5), str(sr_amp5),
            str(phase5),
            message
        ]) 
    #--------------------------------------------------------------------------------------------------
    ## Starting Signal Generator

    # Initialize resource manager

    rm = pyvisa.ResourceManager()

    # List all connected resources
    # print("Resources detected\n{}\n".format(rm.list_resources()))

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
    # with open(filepath, 'a') as f_object:
    #     writer_object = csv.writer(f_object)
    #     writer_object.writerow([time.strftime("%Y-%m-%d_%H%M%S"),"", "", "", "", "", "", "", "", "", "", "", "SIGNAL GENERATORS ARE SETUP"])
    # message = "SIGNAL GENERATORS ARE SETUP"


    #--------------------------------------------------------------------------------------------------
    ## FPGA and PIC controls

    # Initialising FPGA - define COM ports in DEFINE line 51
    #FPGA_ser = init_FPGA(FPGA_COM)

    # Reset PIC and FPGA
    #FPGA_ser = reset_FPGA(FPGA_ser)

    # Buffering? ????????
    #???????

    # Writing Confirmation of FPGA starting
    #with open(filepath, 'a') as f_object:
    #    writer_object = csv.writer(f_object)
    #    writer_object.writerow([time.strftime("%Y-%m-%d_%H%M"), "", "", "", "", "", "", "", "", "", "", "PIC & FPGA Initialized - STARTING FPGA"])

    # Start FPGA
    #config_FPGA(FPGA_ser, freq1, freq2, freq3, freq4, freq5, time.strftime("%Y-%m-%d_%H%M"), RAW_DATA)

    #--------------------------------------------------------------------------------------------------
    ## Wait time for next signal transition
    time.sleep(switch_time)     # switch_time can be set up in the MACRO SECTION in Line 53
    #with open(filepath, 'a') as f_object:
    #    writer_object = csv.writer(f_object)
    #    writer_object.writerow(["","","","","","", "", "", "", "", "", "Sswitch_time "+str(switch_time)])
    # systicks+=1
    # if systicks>2000:
    if datetime.now() >= (start_datetime + timedelta(hours=16)):
        shutdown_cmd()
    

# SG2025_1.write("C1:OUTP OFF")
