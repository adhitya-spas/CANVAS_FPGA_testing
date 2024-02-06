from doctest import testmod
from encodings import utf_8
from multiprocessing.connection import wait
import os
import sys
from urllib import response
sys.path.append("..\Canvas-Algorithm") #import functions from parent directory
import serial #import serial library
import time
import numpy as np
from numpy import random
#custom function imports
from saveas import save_output_txt
from serialfcns import readFPGA, ser_write, response_check
from inputstimulus import test_signal
from readFPGA import read_FPGA_input, twos_complement_to_hex, proper_twos_complement, twos_complement
import matplotlib.pyplot as plt
import binascii
from datetime import datetime
import pandas as pd

# Things to do still:
# => Parser Verify
# => Design such that model data and the CCSDS packet can be interchanged
# => Make edits to the channels taken in
# => Change FPGA_rev everywhere
# => Solve the overwriting issue with the output
# => Compare with model and give results right away
# => Reduce number of tests in test file of 3-Ch

############################################################################### PARAMETER SETUP #############################################################################################

# some set up parameters - used in signal generation
fs = 131072.                # sampling freq. in Hz
signal_freq0 = 60000         # signal freq. 1 in Hz
signal_freq1 = 60000         # signal freq. 1 in Hz
amp0 = 2**15-1                # amplitudes (in ADC units)
amp1 = 2**15-1                # amplitudes (in ADC units)
shift0 = 0                  # phase shift in radians
shift1 = 0                  # phase shift in radians
sample_len = 0.5             # seconds
xspec_test = True

#misc PIC commands
ack = b'\x06\x0A'
lf = b'\x0A'
delim = b'\x2C'
complete = b'Ready.\n'
initiated = b'\nInitiating.\n'

#define pic packet headers
SetConfig = b'\x01'
Data = b'\x02'
ResetPIC = b'\x03' #Just this, need to wait ~2 seconds after sending command
StartFPGA = b'\x04'
StopFPGA = b'\x05'
SetLength = b'\x06' #takes payload of uint32

#define pic SetConfig payloads
Ingress_Write = b'\x00'
Ingress_Read = b'\x01'
Ch_0_Pkt_Gen = b'\x02'
ADC_And_Rotation = b'\x03'
FFT_Results = b'\x04'
FFT_Power = b'\x05'
Spec_to_X_Spec_IF = b'\x06'
Spectra_Results = b'\x07'
Power_RAM_port_A = b'\x08'
Power_RAM_port_B = b'\x09'
Real_RAM_port_A = b'\x0A'
Real_RAM_port_B = b'\x0B'
X_Spec_Real_Results = b'\x0C'
Imaginary_RAM_port_A = b'\x0D'
Imaginary_RAM_port_B = b'\x0E'
X_Spec_Imaginary_Results = b'\x0F'

#GSE Commands to FPGA
Sync_Pat = b'\x1A\xCF\xFC\x1D'
Test_Enable = b'\x7E\x57\xBA\x11'
SW_Reset = b'\x7E\x57\xDE\xAD'
Config = b'\x7E\x57\xCF\x16'
OpcodeSetMatrix = b'\x7E\x57\x00\x00'

############################################################################### INPUT INIT #############################################################################################
# class Science_Packet:
#     pkt_ver_num = ""
#     pkt_type = ""
#     sec_hdr_flag = ""
#     app_id = ""
#     seq_flag = ""
#     seq_cnt = ""
#     pkt_data_len = ""
#     coarse_time = ""
#     fine_time = ""
#     payload_data = ""

#     def __init__(self, pkt_ver_num, pkt_type, sec_hdr_flag, app_id, seq_flag, seq_cnt, pkt_data_len, coarse_time, fine_time, payload_data):  
#         self.name = personName  
#         self.age = personAge 

# # Assume input packet is placed in array

# CCSDS_data = []

# i=0
# for channel_no in range(0,5):
#     while CCSDS_data[i]!="0xCC":
#         if CCSDS_data[i]+CCSDS_data[i+1]+CCSDS_data[i+2]+CCSDS_data[i+3] == "0x1A0xCF0xFC0x1D":

#             Pkt_Ver_num = CCSDS_data[i:i+3]       # Packet Version Number

#             Pkt_Type = CCSDS_data[i+3:i+4]          # Packet Type
#             Sec_Hdr_Flag = CCSDS_data[i+4:i+5]      # Secondary Header Flag
#             App_id = CCSDS_data[i+5:i+16]           # App ID

#             Seq_Flag = CCSDS_data[i+16:i+18]        # Sequence Flags
#             Seq_Cnt = CCSDS_data[i+18:i+32]         # Sequence Count

#             Pkt_Data_len = CCSDS_data[i+32:i+48]    # Packet Data Length

#             Coarse_Time = CCSDS_data[i+48:i+80]     # Coarse Time
#             Fine_Time = CCSDS_data[i+80:i+96]       # Fine Time

#             Payload_Data = CCSDS_data[i+96:i+int(twos_complement(str(Pkt_Data_len)))]
#             i+=96+int(twos_complement(str(Pkt_Data_len)))
#         i+=1
#     if channel_no == 1:
#         Packet1 = Science_Packet()


#Generate input signal from file or aribitrarily
fromFile = True
num = 1

if fromFile:
    inputs = 'Inputs/'
    
    amp = "mid" # "low" "mid" "hi"
    phase = "5deg"
    f = "_03khz"
    #file0 = inputs+amp+"0deg"+f+'.txt'
    #file0 = 'Inputs/Increment_counter_input.txt'
    #file1 = 'Inputs/Increment_counter_input.txt'
    #file1 = inputs+amp+phase+f+'.txt' 
    #file2 = inputs+amp+phase+f+'.txt' 
    phase0 = "03khz"
    file0 = inputs+amp+"_amp_"+phase0+'.txt'
    phase1 = "10khz"
    file1 = inputs+amp+"_amp_"+phase1+'.txt'
    phase2 = "24khz"
    file2 = inputs+amp+"_amp_"+phase2+'.txt'
    phase3 = "10khz"
    file3 = inputs+amp+"_amp_"+phase3+'.txt'
    phase4 = "24khz"
    file4 = inputs+amp+"_amp_"+phase4+'.txt'
    channels0_td = read_FPGA_input(file0,signed=True,show_plots=False)
    channels1_td = read_FPGA_input(file1,signed=True,show_plots=False)
    channels2_td = read_FPGA_input(file2,signed=True,show_plots=False)
    channels3_td = read_FPGA_input(file3,signed=True,show_plots=False)
    channels4_td = read_FPGA_input(file4,signed=True,show_plots=False)
else:
    channels0_td = test_signal(fs, sample_len, signal_freq0, amp0, shift=shift0, channel_num=0, show_plots=False, save_output='both')
    channels1_td = test_signal(fs, sample_len, signal_freq1, amp1, shift=shift1, channel_num=1, show_plots=False, save_output='both')
    channels2_td = test_signal(fs, sample_len, signal_freq1, amp1, shift=shift1, channel_num=1, show_plots=False, save_output='both')
    channels3_td = test_signal(fs, sample_len, signal_freq1, amp1, shift=shift1, channel_num=1, show_plots=False, save_output='both')
    channels4_td = test_signal(fs, sample_len, signal_freq1, amp1, shift=shift1, channel_num=1, show_plots=False, save_output='both')
if len(channels0_td) > 20480:
    num_samples = 1024  #Adjust for sample size
else:
    num_samples = int(len(channels0_td))
print(num_samples)

test0 = channels0_td[0:num_samples]
test1 = channels1_td[0:num_samples]
test2 = channels2_td[0:num_samples]
test3 = channels3_td[0:num_samples]
test4 = channels4_td[0:num_samples]

#initialize serial ports (in_... for ease of changing in main test) -- MAKE SURE COM# IS RIGHT
in_pic_ser = serial.Serial("COM5",115200) # Contains 1,2
in_pic_ser1 = serial.Serial("COM4",115200) # Contains 3,4
in_pic_ser2 = serial.Serial("COM4",115200) # Contains 5, dummy
in_FPGA_ser = serial.Serial("COM6",115200)

############################################################################### 1CH TEST SETUP #############################################################################################
# Number of Tests: 5 - each channel once
print("1-Channel Test Begin")
ch = 0
while ch < 5:

    FPGA_ser = in_FPGA_ser
    if ch == 0:
        pic_ser = in_pic_ser
        test = test0
    elif ch == 1:
        pic_ser = in_pic_ser
        test = test1
    elif ch == 2:
        pic_ser = in_pic_ser1
        test = test2
    elif ch == 3:
        pic_ser = in_pic_ser1
        test = test3
    elif ch == 4:
        pic_ser = in_pic_ser2
        test = test4
    
    #reset PIC
    time.sleep(0.5)
    ser_write(pic_ser,ResetPIC+lf,True)
    time.sleep(0.5)
    #response_check(pic_ser,ack)
    #print('Reset Received')
    response_check(pic_ser,initiated)
    print('PIC Reset')

    #configure PIC
    ser_write(pic_ser,SetConfig+testmode+lf)

    #Wait for acknowledge
    response_check(pic_ser,ack)
    print('FPGA Configured')

    #Set number of samples to be buffered
    to_Send = num_samples.to_bytes(4,'big',signed=False)
    ser_write(pic_ser,SetLength+to_Send+lf)

    #Wait for acknowledge
    response_check(pic_ser,ack)
    print('Data Length Set')

    #buffer data
    t0=time.perf_counter()
    var = 0
    for i in test:
        val = i.to_bytes(2,byteorder='big',signed=True)
        ser_write(pic_ser,Data + val + delim + val + lf)
        if var%1000 == 0:
            print('buffering ', var)
        var = var+1
        #response_check(pic_ser,ack)

    #check for complete from PIC
    response_check(pic_ser,complete)

    t1 = time.perf_counter()
    del_t = t1-t0
    print('Data buffered after %f seconds', del_t)

############################################################################### 1CH TEST MAIN #############################################################################################
    #start
    ser_write(pic_ser,StartFPGA+lf)
    testmode = Spectra_Results

    #Wait for acknowledge
    response_check(pic_ser,ack)
    print('FPGA Started')

    out_folder = 'HW-output/5-ch/ch-1'
    FPGA_rev = "Rev14p1_"


    vals,bits = readFPGA(FPGA_ser,readcon="none",num_read=num,outpath=out_folder+'/FPGA-' + FPGA_rev + amp + f + '_' + ch)

    if testmode == ADC_And_Rotation:
        adc3r = vals[:,0]
        adc2r = vals[:,1]
        adc1r = vals[:,2]
        adc3 = vals[:,3]
        adc2 = vals[:,4]
        adc1 = vals[:,5]

        out_path = out_folder+'/FPGA-'+FPGA_rev+'_ADC_And_Rotation'+f+'_'+ch

        save_output_txt(adc3r,out_path+'adc3r','both',bits)
        save_output_txt(adc2r,out_path+'adc2r','both',bits)
        save_output_txt(adc1r,out_path+'adc1r','both',bits)
        save_output_txt(adc3,out_path+'adc3','both',bits)
        save_output_txt(adc2,out_path+'adc2','both',bits)
        save_output_txt(adc1,out_path+'adc1','both',bits)

    elif testmode == FFT_Results:
        bin= vals[:,0]
        re = vals[:,1]
        im = vals[:,2]

        out_path = out_folder+'/FPGA-'+FPGA_rev+'_FFT'+f+'_'+ch


    elif testmode == FFT_Power:
        bin = vals[:,0]
        pwr = vals[:,1]

        out_path = out_folder+'/FPGA-'+FPGA_rev+'_FFT_PWR'+f+'_'+ch

    elif testmode == Spectra_Results:
        bin = vals[:,0] 
        comp_rst= vals[:,1] 
        uncomp_rst = vals[:,2] 

        out_path = out_folder+'/FPGA-'+FPGA_rev+'_Spectra_Result'+f+'_'+ch

    print('End of channel #',ch)
    ch+=1

print("End of 1-Ch Test")

############################################################################### 2CH TEST SETUP #############################################################################################
# Number of Tests: 10 - (1,2) (1,3) (1,4) (1,5) (2,3) (2,4) (2,5) (3,4) (3,5) (4,5)

print("2-Channel Test Begin")
ch = 0
while ch < 10: # Change according to number of tests
    #initialize serial ports - Change configs based on how to split the tests
    FPGA_ser = in_FPGA_ser
    if ch == 0:     # (1,2)
        pic_ser = in_pic_ser
        test = test0
        pic_ser1 = in_pic_ser
        test_1 = test1
    elif ch == 1:   # (1,3)
        pic_ser = in_pic_ser
        test = test0
        pic_ser1 = in_pic_ser1
        test_1 = test2
    elif ch == 2:   # (1,4)
        pic_ser = in_pic_ser
        test = test0
        pic_ser1 = in_pic_ser1
        test_1 = test3
    elif ch == 3:   # (1,5)
        pic_ser = in_pic_ser
        test = test0
        pic_ser1 = in_pic_ser2
        test_1 = test4
    elif ch == 4:   # (2,3)
        pic_ser = in_pic_ser
        test = test1
        pic_ser1 = in_pic_ser1
        test_1 = test2
    elif ch == 5:   # (2,4)
        pic_ser = in_pic_ser
        test = test1
        pic_ser1 = in_pic_ser1
        test_1 = test3
    elif ch == 6:   # (2,5)
        pic_ser = in_pic_ser
        test = test1
        pic_ser1 = in_pic_ser2
        test_1 = test4
    elif ch == 7:   # (3,4)
        pic_ser = in_pic_ser1
        test = test2
        pic_ser1 = in_pic_ser1
        test_1 = test3
    elif ch == 8:   # (3,5)
        pic_ser = in_pic_ser1
        test = test2
        pic_ser1 = in_pic_ser2
        test_1 = test4
    elif ch == 9:   # (4,5)
        pic_ser = in_pic_ser1
        test = test3
        pic_ser1 = in_pic_ser2
        test_1 = test4

############################################################################### 2CH TEST MAIN #############################################################################################

    while iterate < 2:    
        #main loop
        spec_core = b'\x01'
        iterate = 0

        #set test mode
        if xspec_test:
            if iterate == 0:
                testmode = X_Spec_Real_Results #change to ADC_And_Rotation for feedback test
                readcon = 'none'
                mode = 'xspec_real'
            else: 
                #testmode = X_Spec_Imaginary_Results
                testmode = X_Spec_Imaginary_Results #For testing, change this testmode
                readcon = 'none' #valid options are 'all' or 'none'. All dumps all data to a file, none proceeds with normal mode
                mode = 'xspec_imaginary'
        else:
            iterate+=1
            testmode = Spectra_Results
            readcon = 'none'
            mode = ''

        #reset FPGA
        ser_write(FPGA_ser,Sync_Pat+SW_Reset,False)
        print('FPGA Reset')

        #reset PIC and flush FPGA Serial Port
        ser_write(pic_ser,ResetPIC+lf,True)
        ser_write(pic_ser1,ResetPIC+lf,True)

        FPGA_ser.close()
        time.sleep(0.5)
        FPGA_ser.open()

        #response_check(pic_ser,ack)
        #print('Reset Received')
        response_check(pic_ser,initiated)
        print('PIC0 Reset')
        response_check(pic_ser1,initiated)
        print('PIC1 Reset')

        #Set number of samples to be buffered on PIC0 (2 Channels - A1 and A2)
        to_Send = num_samples.to_bytes(4,'big',signed=False)
        ser_write(pic_ser,SetLength+to_Send+lf)
        response_check(pic_ser,ack) #Wait for acknowledge
        print('Data Length Set')

        #buffer data
        t0=time.perf_counter()
        var = 0
        for i in range(len(test0)):
            val0 = test[i].to_bytes(2,byteorder='big',signed=True)
            val1 = test[i].to_bytes(2,byteorder='big',signed=True)
            ser_write(pic_ser,Data + val0 + delim + val1 + lf)
            if var%1000 == 0:
                print('buffering ', var)
            var = var+1
            #response_check(pic_ser,ack)
        response_check(pic_ser,complete) #check for complete from PIC
        del_t = time.perf_counter() - t0
        print('PIC0 Data buffered after %f seconds', del_t)

        #Set number of samples to be buffered on PIC1 (1 Channel - A3)
        to_Send = num_samples.to_bytes(4,'big',signed=False)
        ser_write(pic_ser1,SetLength+to_Send+lf)
        response_check(pic_ser1,ack) #Wait for acknowledge
        print('Data Length Set')

        #buffer data
        t0=time.perf_counter()
        var = 0
        for i in range(len(test0)):
            val0 = test_1[i].to_bytes(2,byteorder='big',signed=True)
            val1 = test_1[i].to_bytes(2,byteorder='big',signed=True)
            ser_write(pic_ser1,Data + val0 + delim + val1 + lf)
            if var%1000 == 0:
                print('buffering ', var)
            var = var+1
            #response_check(pic_ser,ack)
        response_check(pic_ser1,complete) #check for complete from PIC
        del_t = time.perf_counter() - t0
        print('PIC1 Data buffered after %f seconds', del_t)


        #configure and start FPGA
        ser_write(FPGA_ser,Sync_Pat+Config+spec_core+testmode,False)
        print('FPGA Configured')
        ser_write(FPGA_ser,Sync_Pat+Test_Enable,False)
        print('FPGA Started')
    
        out_folder = 'HW-output/5-ch/ch-2'
        FPGA_rev = "60220713_"

        vals = readFPGA(FPGA_ser,readcon=readcon,num_read=num,outpath=out_folder+'/FPGA-' + FPGA_rev + amp + phase + f)

        v=int(vals[0][0])
        print('First Entry: ',v) #Let's look at the first datum
        iterate+=1
    print("End of iteration #",ch)
    ch+=1

print("End of 2-Ch Test")

############################################################################### 3CH TEST SETUP #############################################################################################
# Number of Tests: 10 

# Which 3 serial ports to use for the 3 channel test?
pic_ser = in_pic_ser1
pic_ser1 = in_pic_ser2
FPGA_ser = in_FPGA_ser

spec_core = b'\x01'
iterate = 0
#set test mode
testmode = ADC_And_Rotation #change to ADC_And_Rotation for feedback test
readcon = 'none'
mode = 'ADC_Rot'

### Read Text File
df = pd.read_csv("3_test_cmds.txt", sep="\t")
angle_vals = df.Rot[:]
test_number = df.Test[:]

print("2-Channel Test Begin")
ch = 0
while ch < 10: # Change according to number of tests

    #initialize serial ports - Change configs based on how to split the tests
    FPGA_ser = in_FPGA_ser
    if ch == 0:
        pic_ser = in_pic_ser
        test = test0
    elif ch == 1:
        pic_ser = in_pic_ser
        test = test1
    elif ch == 2:
        pic_ser = in_pic_ser1
        test = test2
    elif ch == 3:
        pic_ser = in_pic_ser1
        test = test3

    while iterate < len(test_number):
        
        # Initialize rotation 
        rot_num = 0
        ### Create initial unit matrix
        final_matrix = np.array( [ [1,             0,              0], 
                                [0,             1,             0], 
                                [0,             0,             1] ] )

        ### Creating Model Matrix
        model_matrix = np.zeros([len(test1),3])
        model_matrix[:,0] = test2
        model_matrix[:,1] = test3
        model_matrix[:,2] = test4

        matrix_model_mul = np.array( [ [1,             0,              0], 
                                [0,             1,             0], 
                                [0,             0,             1] ] )

        #reset FPGA
        ser_write(FPGA_ser,Sync_Pat+SW_Reset,False)
        print('FPGA Reset')

        #reset PIC and flush FPGA Serial Port
        ser_write(pic_ser,ResetPIC+lf,True)
        ser_write(pic_ser1,ResetPIC+lf,True)

        FPGA_ser.close()
        time.sleep(0.5)
        FPGA_ser.open()

        #response_check(pic_ser,ack)
        #print('Reset Received')
        response_check(pic_ser,initiated)
        print('PIC0 Reset')
        response_check(pic_ser1,initiated)
        print('PIC1 Reset')

        #Set number of samples to be buffered on PIC0 (2 Channels - A1 and A2)
        to_Send = num_samples.to_bytes(4,'big',signed=False)
        ser_write(pic_ser,SetLength+to_Send+lf)
        response_check(pic_ser,ack) #Wait for acknowledge
        print('Data Length Set')

        #buffer data
        t0=time.perf_counter()
        var = 0
        for i in range(len(test0)):
            val0 = test2[i].to_bytes(2,byteorder='big',signed=True)
            val1 = test3[i].to_bytes(2,byteorder='big',signed=True)
            ser_write(pic_ser,Data + val0 + delim + val1 + lf)
            if var%1000 == 0:
                print('buffering ', var)
            var = var+1
            #response_check(pic_ser,ack)
        response_check(pic_ser,complete) #check for complete from PIC
        del_t = time.perf_counter() - t0
        print('PIC0 Data buffered after %f seconds', del_t)

        #Set number of samples to be buffered on PIC1 (1 Channel - A3)
        to_Send = num_samples.to_bytes(4,'big',signed=False)
        ser_write(pic_ser1,SetLength+to_Send+lf)
        response_check(pic_ser1,ack) #Wait for acknowledge
        print('Data Length Set')

        #buffer data
        t0=time.perf_counter()
        var = 0
        for i in range(len(test0)):
            val0 = test4[i].to_bytes(2,byteorder='big',signed=True)
            val1 = test4[i].to_bytes(2,byteorder='big',signed=True)
            ser_write(pic_ser1,Data + val0 + delim + val1 + lf)
            if var%1000 == 0:
                print('buffering ', var)
            var = var+1
            #response_check(pic_ser,ack)
        response_check(pic_ser1,complete) #check for complete from PIC
        del_t = time.perf_counter() - t0
        print('PIC1 Data buffered after %f seconds', del_t)


############################################################################### 3CH TEST MAIN #############################################################################################

        while rot_num < len(angle_vals[iterate]):

            ### Declaring theta
            if rot_num==0:
                theta = df.Angle1[iterate]
            elif rot_num==1:
                theta = df.Angle2[iterate]
            elif rot_num==2:
                theta = df.Angle3[iterate]
            model_theta = theta             # Change to 360 - theta

            # Convert to radian
            theta *= np.pi / 180
            model_theta *= np.pi / 180

            # Initializing xoff, yoff, zoff as 0
            xoff = 0
            yoff = 0
            zoff = 0

            ################
            # about X rotation
            ################
            if angle_vals[iterate][rot_num] == "X":
                about_x       = np.array( [ [1,             0,              0], 
                                        [0, np.cos(theta), -np.sin(theta)], 
                                        [0, np.sin(theta),  np.cos(theta)] ] )
                model_about_x = np.array( [ [1,             0,              0], 
                                        [0, np.cos(model_theta), -np.sin(model_theta)], 
                                        [0, np.sin(model_theta),  np.cos(model_theta)] ] )
                
                final_matrix = np.matmul(final_matrix,about_x)
                model_matrix = np.matmul(model_matrix,model_about_x)
                matrix_model_mul = np.matmul(matrix_model_mul,model_about_x)
            ################
            # about Y rotation
            ################
            elif angle_vals[iterate][rot_num] == "Y":
                about_y       = np.array( [ [ np.cos(theta),  0, np.sin(theta)], 
                                        [             0,  1,             0], 
                                        [-np.sin(theta),  0, np.cos(theta)] ] )
                model_about_y = np.array( [ [ np.cos(model_theta),  0, np.sin(model_theta)], 
                                        [             0,  1,             0], 
                                        [-np.sin(model_theta),  0, np.cos(model_theta)] ] )

                final_matrix = np.matmul(final_matrix,about_y)
                model_matrix = np.matmul(model_matrix,model_about_y)
                matrix_model_mul = np.matmul(matrix_model_mul,model_about_y)

            ################
            # about Z rotation
            ################
            elif angle_vals[iterate][rot_num] == "Z":
                about_z       = np.array( [ [np.cos(theta), -np.sin(theta), 0], 
                                        [np.sin(theta),  np.cos(theta), 0], 
                                        [            0,              0, 1] ] )
                model_about_z = np.array( [ [np.cos(model_theta), -np.sin(model_theta), 0], 
                                        [np.sin(model_theta),  np.cos(model_theta), 0], 
                                        [            0,              0, 1] ] )

                final_matrix = np.matmul(final_matrix,about_z) 
                model_matrix = np.matmul(model_matrix,model_about_z)
                matrix_model_mul = np.matmul(matrix_model_mul,model_about_z)

            #######
            # Offsets
            #######
            elif angle_vals[iterate][rot_num] == "x":
                xoff = df.Xoff[iterate]
            elif angle_vals[iterate][rot_num] == "y":
                yoff = df.Yoff[iterate]
            elif angle_vals[iterate][rot_num] == "z":
                zoff = df.Zoff[iterate]
            rot_num += 1

        # Model rotation matrix
        #model_matrix = np.matmul(model_matrix,final_matrix) #debug
        #model_matrix = np.matmul(model_matrix,matrix_model_mul)
        # FPGA rotation matrix
        SCM_x00 = binascii.unhexlify(twos_complement_to_hex(final_matrix[0][0]))
        SCM_x01 = binascii.unhexlify(twos_complement_to_hex(final_matrix[0][1]))
        SCM_x02 = binascii.unhexlify(twos_complement_to_hex(final_matrix[0][2]))
        SCM_y10 = binascii.unhexlify(twos_complement_to_hex(final_matrix[1][0]))
        SCM_y11 = binascii.unhexlify(twos_complement_to_hex(final_matrix[1][1]))
        SCM_y12 = binascii.unhexlify(twos_complement_to_hex(final_matrix[1][2]))
        SCM_z20 = binascii.unhexlify(twos_complement_to_hex(final_matrix[2][0]))
        SCM_z21 = binascii.unhexlify(twos_complement_to_hex(final_matrix[2][1]))
        SCM_z22 = binascii.unhexlify(twos_complement_to_hex(final_matrix[2][2]))
        SCM_xoff = binascii.unhexlify(proper_twos_complement(xoff))
        SCM_yoff = binascii.unhexlify(proper_twos_complement(yoff))
        SCM_zoff = binascii.unhexlify(proper_twos_complement(zoff))
        
        ser_write(FPGA_ser,Sync_Pat+OpcodeSetMatrix+SCM_x00+SCM_x01+SCM_x02+SCM_y10+SCM_y11+SCM_y12+SCM_z20+SCM_z21+SCM_z22+SCM_xoff+SCM_yoff+SCM_zoff,False)
        # ser_write(FPGA_ser,Sync_Pat+OpcodeSetMatrix+SCM_x00+SCM_y10+SCM_z20+SCM_x01+SCM_y11+SCM_z21+SCM_x02+SCM_y12+SCM_z22+SCM_xoff+SCM_yoff+SCM_zoff,False)
        
        print('FPGA Configured')
        time.sleep(0.5)
        ser_write(FPGA_ser,Sync_Pat+Config+spec_core+testmode,False)
        print('Set Test Mode')
        time.sleep(0.5)
        ser_write(FPGA_ser,Sync_Pat+Test_Enable,False)
        print('FPGA Started')

        out_folder = 'HW-output'
        FPGA_rev = "60220713_"
        # to get timestamp
        now = datetime.now()
        date_time = now.strftime("_%m%d%Y_%H%M%S")
        vals = readFPGA(FPGA_ser,readcon=readcon,num_read=num,outpath=out_folder+'/3-ch'+'/Looped_twice_all'+'/'+amp+'FPGA-' + FPGA_rev + amp + phase + f + '_iter' + str(iterate) + date_time)

        ## Writing into text file for verification of Model
        file = open(out_folder+'/3-ch'+'/Looped_twice_all'+'/'+amp+'Model-' + str(iterate) + date_time+ '.txt','w')
        file.write("R3"+"\t"+"R2"+"\t"+"R1"+"\t"+"A3"+"\t"+"A2"+"\t"+"A1"+"\n")
        for a in range(0,len(model_matrix[:,0])):
            file.write(str(int(model_matrix[a,2]))+"\t"+str(int(model_matrix[a,1]))+"\t"+str(int(model_matrix[a,0]))+"\t"+str(int(test2[a]))+"\t"+str(int(test1[a]))+"\t"+str(int(test0[a]))+"\n")
        file.close()

        ## Comparing the model values with FPGA values
        df1 = pd.read_csv(out_folder+'/3-ch'+'/Looped_twice_all'+'/'+amp+'FPGA-' + FPGA_rev + amp + phase + f + '_iter' + str(iterate) + date_time +'ADCLoopback_int'+'.txt', sep="\t")
        print(df1[0:5])

        df2 = pd.read_csv(out_folder+'/3-ch'+'/Looped_twice_all'+'/'+amp+'Model-' + str(iterate) + date_time+ '.txt', sep="\t")
        print(df2[0:5])

        diff_3 = abs(df1.R3 - df2.R3)
        diff_2 = abs(df1.R2 - df2.R2)
        diff_1 = abs(df1.R1 - df2.R1)

        ## Writing into text file for verification of Model
        file = open(out_folder+'/3-ch'+'/Looped_twice_all'+'/'+amp+'Verification-' + str(iterate) + date_time+ '.txt','w')
        file.write("R3_df"+"\t"+"R2_df"+"\t"+"R1_df"+"\n")  
        for a in range(0,len(df2.R1)):
            file.write(str(diff_3[a])+"\t"+str(diff_2[a])+"\t"+str(diff_1[a])+"\n")
        file.close()

        # v=int(vals[0][0])]
        # print('First Entry: ',v) #Let's look at the first datum   
        if iterate<28:
        ## Verifying if the difference is greater than what its supposed to be
            df_v = pd.read_csv(out_folder+'/3-ch'+'/Looped_twice_all'+'/'+amp+'Verification-' + str(iterate) + date_time+ '.txt', sep="\t")
            if not all(num<3 for num in df_v.R1_df):
                print("OVER THE LIMIT!!" * 10)
            elif not all(num<3 for num in df_v.R2_df):
                print("OVER THE LIMIT!!" * 10)
            elif not all(num<3 for num in df_v.R3_df):
                print("OVER THE LIMIT!!" * 10)
            # else:
            #     print("You're safe, for now")   
        iterate+=1
    print("End of iteration #",ch)
    ch+=1

print("End of 3-Ch Test")

############################################################################################################################################################################
print('Test Completed')