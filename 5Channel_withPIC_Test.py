################## FPGA_ver : 808
#ADC 1 -     

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
from readFPGA import read_FPGA_input, twos_complement_to_hex, proper_twos_complement
import matplotlib.pyplot as plt
import binascii
from datetime import datetime
import pandas as pd
from ch5_Parser import twos_complement, read_headerCCSDS, read_spectravals, read_xspectravals

# some set up parameters - used in signal generation
fs = 131072.                # sampling freq. in Hz
signal_freq0 = 60000         # signal freq. 1 in Hz
signal_freq1 = 60000         # signal freq. 1 in Hz
amp0 = 2**15-1                # amplitudes (in ADC units)
amp1 = 2**15-1                # amplitudes (in ADC units)
shift0 = 0                  # phase shift in radians
shift1 = 0                  # phase sift in radians
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

#Generate input signal from file or aribitrarily
fromFile = True
num = 1

if fromFile:
    inputs = 'Inputs/'
    
    amp = "hi"
    f = "_03khz"
    phase = "5deg"

    freq0 = "512hz"
    freq1 = "03khz"
    freq2 = "10khz"
    freq3 = "24khz" # broken
    freq4 = "33khz"

    file0 = inputs+amp+"_amp_"+freq0+'.txt'

    file1 = inputs+amp+"_amp_"+freq1+'.txt'
    
    file2 = inputs+amp+"_amp_"+freq2+'.txt'
    
    file3 = inputs+'signal_23000.txt'
    
    file4 = inputs+amp+"_amp_"+freq4+'.txt'

    # file0 = "D:\CANVAS_work\Canvas-Algorithm\Canvas_FPGA\Inputs\dummy_one.txt"
    # file1 = "D:\CANVAS_work\Canvas-Algorithm\Canvas_FPGA\Inputs\dummy_one.txt"
    # file2 = "D:\CANVAS_work\Canvas-Algorithm\Canvas_FPGA\Inputs\dummy_one.txt"
    # file3 = "D:\CANVAS_work\Canvas-Algorithm\Canvas_FPGA\Inputs\dummy_one.txt"
    # file4 = "D:\CANVAS_work\Canvas-Algorithm\Canvas_FPGA\Inputs\dummy_one.txt"

    channels0_td = read_FPGA_input(file0,signed=True,show_plots=False)
    channels1_td = read_FPGA_input(file1,signed=True,show_plots=False)
    channels2_td = read_FPGA_input(file2,signed=True,show_plots=False)
    channels3_td = read_FPGA_input(file3,signed=True,show_plots=False)
    channels4_td = read_FPGA_input(file4,signed=True,show_plots=False)

else:
    channels0_td = test_signal(fs, sample_len, signal_freq0, amp0, shift=shift0, channel_num=0, show_plots=False, save_output='both')
    channels1_td = test_signal(fs, sample_len, signal_freq1, amp1, shift=shift1, channel_num=1, show_plots=False, save_output='both')
if len(channels0_td) > 20480:
    num_samples = 20480#int(len(channels0_td)) # 1024 previoiusly
else:
    num_samples = int(len(channels0_td))
print(num_samples)

# test0 = list(range(1,1001)) # INCREMENT TEST
# test1 = list(range(1001,2001))
# test2 = list(range(2001,3001))
# test3 = list(range(3001,4001))
# test4 = list(range(4001,5001))

test0 = channels0_td[0:num_samples] # ORIGINAL
test1 = channels1_td[0:num_samples]
test2 = channels2_td[0:num_samples]
test3 = channels3_td[0:num_samples]
test4 = channels4_td[0:num_samples]

#initialize serial ports
pic_ser = serial.Serial("COM4",115200)
pic_ser1 = serial.Serial("COM10",115200)
pic_ser2 = serial.Serial("COM9",115200)
FPGA_ser = serial.Serial("COM7",115200) #Uncomment later

# testmode = ADC_And_Rotation

#reset FPGA
Siesta_cmd = b'\xC0\x51\xE5\x7A'
ser_write(FPGA_ser,Sync_Pat+Siesta_cmd,False)

#reset PIC
ser_write(pic_ser,ResetPIC+lf,True)
time.sleep(1)
response_check(pic_ser,initiated)
print('PIC Reset')
ser_write(pic_ser1,ResetPIC+lf,True)
time.sleep(1)
response_check(pic_ser1,initiated)
print('PIC1 Reset')
ser_write(pic_ser2,ResetPIC+lf,True)
time.sleep(1)
response_check(pic_ser2,initiated)
print('PIC2 Reset')

FPGA_ser.close()  #Uncomment later
time.sleep(0.5)   #Uncomment later
FPGA_ser.open()   #Uncomment later

#response_check(pic_ser,ack)
#print('Reset Received')

# response_check(pic_ser,initiated)
# print('PIC Reset')
# response_check(pic_ser1,initiated)
# print('PIC1 Reset')
# response_check(pic_ser2,initiated)
# print('PIC2 Reset')

########################## Buffering ###########################################

#Set number of samples to be buffered
to_Send = num_samples.to_bytes(4,'big',signed=False)
ser_write(pic_ser,SetLength+to_Send+lf)
response_check(pic_ser,ack) #Wait for acknowledge
print('Data Length Set')
#buffer data
t0=time.perf_counter()
var = 0
for i in range(len(test0)):
    val0 = test0[i].to_bytes(2,byteorder='big',signed=True)
    val1 = test1[i].to_bytes(2,byteorder='big',signed=True)
    ser_write(pic_ser,Data + val0 + delim + val1 + lf)
    if var%1000 == 0:
        print('buffering ', var)
    var = var+1
    #response_check(pic_ser,ack)
#check for complete from PIC
response_check(pic_ser,complete)
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
    val0 = test2[i].to_bytes(2,byteorder='big',signed=True)
    val1 = test3[i].to_bytes(2,byteorder='big',signed=True)
    ser_write(pic_ser1,Data + val0 + delim + val1 + lf)
    if var%1000 == 0:
        print('buffering ', var)
    var = var+1
    #response_check(pic_ser,ack)
response_check(pic_ser1,complete) #check for complete from PIC
del_t = time.perf_counter() - t0
print('PIC1 Data buffered after %f seconds', del_t)

#Set number of samples to be buffered on PIC2 
to_Send = num_samples.to_bytes(4,'big',signed=False)
ser_write(pic_ser2,SetLength+to_Send+lf)
# response_check(pic_ser2,ack) #Wait for acknowledge
print('Data Length Set')
#buffer data
t0=time.perf_counter()
var = 0
for i in range(len(test0)):
    val0 = test4[i].to_bytes(2,byteorder='big',signed=True)
    val1 = test4[i].to_bytes(2,byteorder='big',signed=True)
    ser_write(pic_ser2,Data + val0 + delim + val1 + lf)
    if var%1000 == 0:
        print('buffering ', var)
    var = var+1
    #response_check(pic_ser,ack)
#check for complete from PIC
# response_check(pic_ser,complete)
del_t = time.perf_counter() - t0
print('PIC2 Data buffered after %f seconds', del_t)
############################################################################

print('Calculating Rotation')
SCM_x00 = binascii.unhexlify(twos_complement_to_hex(1))
SCM_x01 = binascii.unhexlify(twos_complement_to_hex(0))
SCM_x02 = binascii.unhexlify(twos_complement_to_hex(0))
SCM_y10 = binascii.unhexlify(twos_complement_to_hex(0))
SCM_y11 = binascii.unhexlify(twos_complement_to_hex(1))
SCM_y12 = binascii.unhexlify(twos_complement_to_hex(0))
SCM_z20 = binascii.unhexlify(twos_complement_to_hex(0))
SCM_z21 = binascii.unhexlify(twos_complement_to_hex(0))
SCM_z22 = binascii.unhexlify(twos_complement_to_hex(1))
SCM_xoff = binascii.unhexlify(proper_twos_complement(0))
SCM_yoff = binascii.unhexlify(proper_twos_complement(0))
SCM_zoff = binascii.unhexlify(proper_twos_complement(0))

# ser_write(FPGA_ser,Sync_Pat+OpcodeSetMatrix+SCM_x00+SCM_x01+SCM_x02+SCM_y10+SCM_y11+SCM_y12+SCM_z20+SCM_z21+SCM_z22+SCM_xoff+SCM_yoff+SCM_zoff,False)
    
spec_core = b'\x01'
#configure and start FPGA
# print('FPGA Configured')
# time.sleep(0.5)
#ser_write(FPGA_ser,Sync_Pat+Config+spec_core+testmode,False)
#print('Set Test Mode')
#time.sleep(0.5)
# ser_write(FPGA_ser,Sync_Pat+Test_Enable,False)
# print('FPGA Started')
#time.sleep(10)
# Start FPGA

time.sleep(3)
Siesta_cmd = b'\xC0\x51\xE5\x7A'
ser_write(FPGA_ser,Sync_Pat+Siesta_cmd,False)
time.sleep(4)
Testmuxselect_cmd = b'\x7E\xF4'
Tm_adc1 = b'\x00\x01'  # data works but toggle weird
Tm_adc2 = b'\x00\x02'  # data works but toggle weird near the end
Tm_adc3 = b'\x00\x03'  # data works but toggle weird near the end
Tm_adc4 = b'\x00\x04'  # same as above
Tm_adc5 = b'\x00\x05'  # same as above
Tm_ef1 = b'\x00\x11'   # data works, the LA read wrong (eg.4)
Tm_ef2 = b'\x00\x12'   # data works fine
Tm_scm_x = b'\x00\x13' # same as above
Tm_scm_y = b'\x00\x14' # data works, the LA read wrong (eg.2004, 1998, 2006) 
Tm_scm_z = b'\x00\x15' # data works, the LA read wrong (eg.3008, 4, 3010)
Tm_All_ADC_In = b'\x00\x80'

Tm_Fifo_Write_Ch1 = b'\x00\x20' 
Tm_Fifo_Write_Ch2 = b'\x00\x21' 
Tm_Fifo_Write_Ch3 = b'\x00\x22' 
Tm_Fifo_Write_Ch4 = b'\x00\x23' 
Tm_Fifo_Write_Ch5 = b'\x00\x24' 
Tm_Fifo_Read_Ch1 = b'\x00\x30' 
Tm_Fifo_Read_Ch2 = b'\x00\x31' 
Tm_Fifo_Read_Ch3 = b'\x00\x32' 
Tm_Fifo_Read_Ch4 = b'\x00\x33' 
Tm_Fifo_Read_Ch5= b'\x00\x34' 

# ser_write(FPGA_ser,Sync_Pat+Testmuxselect_cmd+Tm_Fifo_Read_Ch1,False) #Keeps changing
# time.sleep(1)
Fiio_cmd = b'\xF1\x10\x80\x00'
ser_write(FPGA_ser,Sync_Pat+Fiio_cmd,False)
# time.sleep(1)
print('FPGA Configured')
Codeload_cmd = b'\xC0\xDE\x10\xAD'
ser_write(FPGA_ser,Sync_Pat+Codeload_cmd,False)
print('FPGA Started')

out_folder = 'HW-output'
FPGA_rev = "d723_"
readcon = 'none'
# to get timestamp
now = datetime.now()
date_time = now.strftime("_%m%d%Y_%H%M%S")
    
############ For parsing packets (2 bytes at a time)
# vals = readFPGA(FPGA_ser,readcon=readcon,num_read=num,outpath=out_folder+'/5-ch'+'/verify'+'/'+amp+'FPGA-' + FPGA_rev + amp + phase + f + '_iter' + date_time)
############ For parsing packets (1 byte at a time)
# vals = readFPGA(FPGA_ser,readcon=readcon,num_read=num,outpath=out_folder+'/5-ch'+'/verify'+'/'+amp+'FPGA-' + FPGA_rev + amp + phase + f + '_iter' + date_time)
############ For timing the Packets

vals = readFPGA(FPGA_ser, freq0, freq1, freq2, freq3, freq4,readcon=readcon,num_read=num,outpath=out_folder+'/5-ch'+'/verify'+'/'+amp+'FPGA-' + FPGA_rev + '_iter' + date_time , time_CCSDS=True, byte_type=2)
print("Packets saved")

# outpath='HW-output/5-ch/read_all'        
# name = outpath+ 'CCSDS_pkt' + date_time


##################### Parsing right after ########################

# Define Input and Output Location
outpath='HW-output/5-ch/01-31-24/read_all'
input_filename = outpath+ 'CCSDS_pkt' + date_time + '_' + freq0[0:3] + freq1[0:3] + freq2[0:3] + freq3[0:3] + freq4[0:3] + '.txt'
lines = open(input_filename).read().splitlines()
cnt = 0
now = datetime.now()
# date_time = now.strftime("_%m%d%Y_%H%M%S")
outpath='HW-output/parse/01-31-24/parse-'
name = outpath+ 'CCSDS_pkt' + date_time

# Looping till the end of the file - takes one line every iteration
for pkt in lines:
    # Checks for the Spectra header
    if pkt[:4] == '0AB0':
        print("Spectra")
        cnt+=1
        file_spec = open(name +'-SPECTRA_'+str(cnt)+'.txt','w')
        spectra_header = pkt[:34]
        spectra_vals = pkt[34:]
        file_spec.write("SPECTRA "+str(cnt)+"\n")
        read_headerCCSDS(file_spec, spectra_header)
        try:
            read_spectravals(file_spec, spectra_vals)
        except Exception:
            print("Incomplete")
            pass
        file_spec.close()
    # Checks for the Cross-Spectra A header
    elif pkt[:4] == '0AB4':
        print("Cross Spectra A")
        file_xspeca = open(name +'-XSPEC-A_'+str(cnt)+'.txt','w')
        xspeca_header = pkt[:34]
        xspeca_vals = pkt[34:]
        file_xspeca.write("CROSS-SPECTRA A "+str(cnt)+"\n")
        read_headerCCSDS(file_xspeca, xspeca_header)
        try:
            read_xspectravals(file_xspeca, xspeca_vals, 'A')
        except Exception:
            print("Incomplete")
            pass
        # try:
        #     read_xspectravals(file_xspeca, xspeca_vals, 'A')
        # except Exception:
        #     print("Incomplete")
        #     pass
        file_xspeca.close()
    # Checks for the Cross-Spectra B header
    elif pkt[:4] == '0AB5':
        print("Cross Spectra B")
        file_xspecb = open(name +'-XSPEC-B_'+str(cnt)+'.txt','w')
        xspecb_header = pkt[:34]
        xspecb_vals = pkt[34:]
        file_xspecb.write("CROSS-SPECTRA B "+str(cnt)+"\n")
        read_headerCCSDS(file_xspecb, xspecb_header)
        try:
            read_xspectravals(file_xspecb, xspecb_vals, 'B')
        except Exception:
            print("Incomplete")
            pass
        file_xspecb.close()
    # Checks for the Sync Pattern
    elif pkt == '1ACF  FC1D':
        print("Sync Pattern")
# Prints done, cuz why not :)
print("done")


