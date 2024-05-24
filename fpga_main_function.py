### importing libraries
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

from cmath import pi
from matplotlib.pyplot import show
import glob

### Importing custom libraries
from readFPGA import read_FPGA_input, proper_twos_complement
from saveas import save_output_txt
from win import get_win
from serialfcns import readFPGA, ser_write, response_check
from inputstimulus import test_signal
from readFPGA import read_FPGA_input, twos_complement_to_hex, proper_twos_complement
import matplotlib.pyplot as plt
import binascii
import pandas as pd
from ch5_Parser import twos_complement, read_headerCCSDS, read_spectravals, read_xspectravals
from fftcanvas import canvas_fft
from fftpwr import fft_spec_power, fft_xspec_power
from rebinacc import rebin_likefpga, acc_likefpga
from cfbinavg import rebin_canvas
from log2compress import spec_compress, xspec_compress


### Some PIC commands
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


def run_fpga_output(file_input, date_time, pic_ser,pic_ser1,pic_ser2,FPGA_ser):
    channels0_td = read_FPGA_input(file_input[0],signed=True,show_plots=False)
    channels1_td = read_FPGA_input(file_input[1],signed=True,show_plots=False)
    channels2_td = read_FPGA_input(file_input[2],signed=True,show_plots=False)
    channels3_td = read_FPGA_input(file_input[3],signed=True,show_plots=False)
    channels4_td = read_FPGA_input(file_input[4],signed=True,show_plots=False)
    
    num_samples = 20480 # 65535 # 20480

    test0 = channels0_td[0:num_samples] 
    test1 = channels1_td[0:num_samples]
    test2 = channels2_td[0:num_samples]
    test3 = channels3_td[0:num_samples]
    test4 = channels4_td[0:num_samples]
    
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
            
    ############ For parsing packets (2 bytes at a time)
    # vals = readFPGA(FPGA_ser,readcon=readcon,num_read=num,outpath=out_folder+'/5-ch'+'/verify'+'/'+amp+'FPGA-' + FPGA_rev + amp + phase + f + '_iter' + date_time)
    ############ For parsing packets (1 byte at a time)
    # vals = readFPGA(FPGA_ser,readcon=readcon,num_read=num,outpath=out_folder+'/5-ch'+'/verify'+'/'+amp+'FPGA-' + FPGA_rev + amp + phase + f + '_iter' + date_time)
    ############ For timing the Packets

    amp = "hi"
    freq0 = file_input[0][-10:-4]
    freq1 = file_input[1][-10:-4]
    freq2 = file_input[2][-10:-4]
    freq3 = file_input[3][-10:-4]
    freq4 = file_input[4][-10:-4]
    vals = readFPGA(FPGA_ser, freq0, freq1, freq2, freq3, freq4,readcon=readcon,num_read=1,outpath=out_folder+'/5-ch'+'/verify'+'/'+amp+'FPGA-' + FPGA_rev + '_iter' + date_time , time_CCSDS=True, byte_type=3)
    print("Packets saved")
    
##################### Parsing right after ########################
def parse_these_packets(file_input,date_time):
    
    amp = "hi"
    freq0 = file_input[0][-10:-4]
    freq1 = file_input[1][-10:-4]
    freq2 = file_input[2][-10:-4]
    freq3 = file_input[3][-10:-4]
    freq4 = file_input[4][-10:-4]

    # Define Input and Output Location
    outpath='HW-output/5-ch/test_trs_rest/read_all'
    input_filename = outpath+ 'CCSDS_pkt' + date_time + '_' + freq0[0:3] + freq1[0:3] + freq2[0:3] + freq3[0:3] + freq4[0:3] + '.txt'
    lines = open(input_filename).read().splitlines()
    cnt = 0
    # now = datetime.now()
    # date_time = now.strftime("_%m%d%Y_%H%M%S")
    outpath='HW-output/parse/test_trs_rest/parse-'
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
##################### Comparing Files ########################
def compare_these_packets(date_time):
    ## Comparing the model values with FPGA values
    df1 = pd.read_csv('model_trs_rest/Spec_vals_'+date_time+'.txt', skiprows=[0,1,2,3,4,5,6,7], sep="\t")
    int1_list = df1.iloc[1342:].values.tolist()     # convert specific range to list
    int1_vals = []
    for j in range(0,len(int1_list)):
        int1_vals.append([eval(i) for i in int1_list[:][j]])  # convert string to integer
    # print(df1[0:5])

    df2 = pd.read_csv('HW-output/parse/test_trs_rest/parse-'+'CCSDS_pkt' + date_time+'-SPECTRA_'+str(1)+'.txt', skiprows=[0,1,2,3,4,5,6,7,8,9,10,11,12,13], sep="\t")
    int2_list = df2.iloc[69:].values.tolist()       # convert specific range to list
    int2_vals = []
    for j in range(0,len(int2_list)):
        int2_vals.append([eval(i) for i in int2_list[:][j]])  # convert string to integer
    # print(df2[0:5])

    ## Find comparison size:
    if(len(int1_vals)<len(int2_vals)):
        size_val = len(int1_vals)
    else:
        size_val = len(int2_vals)

    ## Checking for difference > 1
    if(int1_vals[0:size_val]==int2_vals[0:size_val]):
        print("\n_______________________\nSUCCESS\n_______________________\n")
    else:
        diff = np.subtract(int1_vals[0:size_val],int2_vals[0:size_val])
        bad_loc = np.argwhere(np.absolute(diff)>3)
        file_readme = open('HW-output/parse/test_trs_rest/readme_'+str(date_time)+'.txt','w')
        for h in range(0,len(bad_loc)):
            file_readme.write("\nHere are the bad arrays (pos "+str(h)+" )=> "+str(int1_vals[bad_loc[h][0]])+" & "+str(int2_vals[bad_loc[h][0]])+"\n")
        file_readme.close()
##################### Generate Model ########################
def model_generation(file_input, date_time):
     
    # remove output files in path
    files = glob.glob('output/*')
    for f in files:
        os.remove(f)

    # some set up parameters
    hi_amp  = 27345             # max amplitude of VHDL sims
    mid_amp = 2**11
    low_amp = 2**6
    fs = 131072.                # sampling freq. in Hz

    signal_freq0 = 35e3         # signal freq. 1 in Hz %James - 24e3
    signal_freq1 = 35e3         # signal freq. 2 in Hz %James - 24e3
    amp0 = 2**15               # amplitudes (in ADC units) %James = hi_amp
    amp1 = 2**15              # amplitudes (in ADC units) %James = hi_amp
    shift0 = 0                  # phase shift in radians
    shift1 = 0    # phase shift in radians % James = 83 * np.pi/180 
    sample_len = 1024*256*2/fs            # 1/4 seconds %James = 0.5
    nFFT = 1024                 # length of FFT
    n_acc = 256                 # number of FFTs to accummulate %James = 8

    # STEP 1 -------------------- GENERATE INPUT ----------------------------- 
    
    channels0_td_pre = read_FPGA_input(file_input[0],signed=True,show_plots=False)
    channels1_td_pre = read_FPGA_input(file_input[1],signed=True,show_plots=False)
    channels2_td_pre = read_FPGA_input(file_input[2],signed=True,show_plots=False)
    channels3_td_pre = read_FPGA_input(file_input[3],signed=True,show_plots=False)
    channels4_td_pre = read_FPGA_input(file_input[4],signed=True,show_plots=False)
    
    num_samples = 20480 #65535 # 20480 #len(channels0_td_pre) #
    test0 = channels0_td_pre[0:num_samples]
    test1 = channels1_td_pre[0:num_samples]
    test2 = channels2_td_pre[0:num_samples]
    test3 = channels3_td_pre[0:num_samples]
    test4 = channels4_td_pre[0:num_samples]

    channels0_td = test0*128 
    channels1_td = test1*128 
    channels2_td = test2*128
    channels3_td = test3*128
    channels4_td = test4*128

    #print(max(channels0_td))
    # STEP 2 ----------------- GET HANNING WINDOW ----------------------------
    # get a window based on IDL code
    win = get_win(nFFT, show_plots=False, save_output=None)

    # STEP 3 ----------------------- TAKE FFT --------------------------------
    # take fft on each channel

    channel0_fd_real, channel0_fd_imag = canvas_fft(nFFT, fs, win, channels0_td, overlap=True,  channel_num=0, show_plots=False, save_output=None)
    channel1_fd_real, channel1_fd_imag = canvas_fft(nFFT, fs, win, channels1_td, overlap=True,  channel_num=1, show_plots=False, save_output=None)
    channel2_fd_real, channel2_fd_imag = canvas_fft(nFFT, fs, win, channels2_td, overlap=True,  channel_num=2, show_plots=False, save_output=None)
    channel3_fd_real, channel3_fd_imag = canvas_fft(nFFT, fs, win, channels3_td, overlap=True,  channel_num=3, show_plots=False, save_output=None)
    channel4_fd_real, channel4_fd_imag = canvas_fft(nFFT, fs, win, channels4_td, overlap=True,  channel_num=4, show_plots=False, save_output=None)

    # STEP 4 ----------------------- CALC PWR --------------------------------
    # calculate power, diff for spectra and x-spec
    #fpga_rev = "Rev14p1"
    #fpga_file_path_0 = "Data_compare/xspec_im_test/"+"0712_03khz_spec0_FFT_hex.txt"
    #fpga_file_path_1 = "Data_compare/xspec_im_test/"+"0712_03khz_spec1_FFT_hex.txt"

    #f_ar_0, f_ai_0 = read_FPGA_input_lines(fpga_file_path_0, 32, line_n=3, x=1, y=2)
    #f_ar_1, f_ai_1 = read_FPGA_input_lines(fpga_file_path_1, 32, line_n=3, x=1, y=2)

    spec_pwr0 = fft_spec_power(channel0_fd_real, channel0_fd_imag, channel_num=0, show_plots=False, save_output=None)
    spec_pwr1 = fft_spec_power(channel1_fd_real, channel1_fd_imag, channel_num=1, show_plots=False, save_output=None)
    spec_pwr2 = fft_spec_power(channel2_fd_real, channel2_fd_imag, channel_num=2, show_plots=False, save_output=None)
    spec_pwr3 = fft_spec_power(channel3_fd_real, channel3_fd_imag, channel_num=3, show_plots=False, save_output=None)
    spec_pwr4 = fft_spec_power(channel4_fd_real, channel4_fd_imag, channel_num=4, show_plots=False, save_output=None)

    xspec_pwr_r_01, xspec_pwr_i_01 = fft_xspec_power(channel0_fd_real, channel0_fd_imag, channel1_fd_real, channel1_fd_imag, channel_nums=[0,1], show_plots=False, save_output=None)
    xspec_pwr_r_02, xspec_pwr_i_02 = fft_xspec_power(channel0_fd_real, channel0_fd_imag, channel2_fd_real, channel2_fd_imag, channel_nums=[0,2], show_plots=False, save_output=None)
    xspec_pwr_r_03, xspec_pwr_i_03 = fft_xspec_power(channel0_fd_real, channel0_fd_imag, channel3_fd_real, channel3_fd_imag, channel_nums=[0,3], show_plots=False, save_output=None)
    xspec_pwr_r_04, xspec_pwr_i_04 = fft_xspec_power(channel0_fd_real, channel0_fd_imag, channel4_fd_real, channel4_fd_imag, channel_nums=[0,4], show_plots=False, save_output=None)
    xspec_pwr_r_12, xspec_pwr_i_12 = fft_xspec_power(channel1_fd_real, channel1_fd_imag, channel2_fd_real, channel2_fd_imag, channel_nums=[1,2], show_plots=False, save_output=None)
    xspec_pwr_r_13, xspec_pwr_i_13 = fft_xspec_power(channel1_fd_real, channel1_fd_imag, channel3_fd_real, channel3_fd_imag, channel_nums=[1,3], show_plots=False, save_output=None)
    xspec_pwr_r_14, xspec_pwr_i_14 = fft_xspec_power(channel1_fd_real, channel1_fd_imag, channel4_fd_real, channel4_fd_imag, channel_nums=[1,4], show_plots=False, save_output=None)
    xspec_pwr_r_23, xspec_pwr_i_23 = fft_xspec_power(channel2_fd_real, channel2_fd_imag, channel3_fd_real, channel3_fd_imag, channel_nums=[2,3], show_plots=False, save_output=None)
    xspec_pwr_r_24, xspec_pwr_i_24 = fft_xspec_power(channel2_fd_real, channel2_fd_imag, channel4_fd_real, channel4_fd_imag, channel_nums=[2,4], show_plots=False, save_output=None)
    xspec_pwr_r_34, xspec_pwr_i_34 = fft_xspec_power(channel3_fd_real, channel3_fd_imag, channel4_fd_real, channel4_fd_imag, channel_nums=[3,4], show_plots=False, save_output=None)


    #spec_pwr0 = fft_spec_power(f_ar_0, f_ai_0, channel_num=0, show_plots=False, save_output='both')
    #spec_pwr1 = fft_spec_power(f_ar_1, f_ai_1, channel_num=1, show_plots=False, save_output='both')
    #xspec_pwr_r, xspec_pwr_i = fft_xspec_power(f_ar_0, f_ai_0, f_ar_1, f_ai_1, channel_nums=[0, 1], show_plots=False,save_output='both')
    #xspec_pwr_r, xspec_pwr_i = fft_spec_power([channel0_fd_real], [channel0_fd_imag], [channel1_fd_real], [channel1_fd_imag], channel_nums=[0,1], show_plots=False, save_output='both')
    # STEP 5 -------------------- rebin and acc -------------------------------
    # functions written to rebin (avg in freq) and acc (avg in time)
    rebin_pwr0= rebin_likefpga(spec_pwr0, channel_num=0, show_plots=False, save_output=None)
    rebin_pwr1= rebin_likefpga(spec_pwr1, channel_num=1, show_plots=False, save_output=None)
    rebin_pwr2= rebin_likefpga(spec_pwr2, channel_num=2, show_plots=False, save_output=None)
    rebin_pwr3= rebin_likefpga(spec_pwr3, channel_num=3, show_plots=False, save_output=None)
    rebin_pwr4= rebin_likefpga(spec_pwr4, channel_num=4, show_plots=False, save_output=None)

    rebin_pwr_01_r= rebin_likefpga(xspec_pwr_r_01, channel_num=5, show_plots=False, save_output=None)
    rebin_pwr_01_i= rebin_likefpga(xspec_pwr_i_01, channel_num=6, show_plots=False, save_output=None)
    rebin_pwr_02_r= rebin_likefpga(xspec_pwr_r_02, channel_num=7, show_plots=False, save_output=None)
    rebin_pwr_02_i= rebin_likefpga(xspec_pwr_i_02, channel_num=8, show_plots=False, save_output=None)
    rebin_pwr_03_r= rebin_likefpga(xspec_pwr_r_03, channel_num=9, show_plots=False, save_output=None)
    rebin_pwr_03_i= rebin_likefpga(xspec_pwr_i_03, channel_num=10, show_plots=False, save_output=None)
    rebin_pwr_04_r= rebin_likefpga(xspec_pwr_r_04, channel_num=11, show_plots=False, save_output=None)
    rebin_pwr_04_i= rebin_likefpga(xspec_pwr_i_04, channel_num=12, show_plots=False, save_output=None)
    rebin_pwr_12_r= rebin_likefpga(xspec_pwr_r_12, channel_num=13, show_plots=False, save_output=None)
    rebin_pwr_12_i= rebin_likefpga(xspec_pwr_i_12, channel_num=14, show_plots=False, save_output=None)
    rebin_pwr_13_r= rebin_likefpga(xspec_pwr_r_13, channel_num=15, show_plots=False, save_output=None)
    rebin_pwr_13_i= rebin_likefpga(xspec_pwr_i_13, channel_num=16, show_plots=False, save_output=None)
    rebin_pwr_14_r= rebin_likefpga(xspec_pwr_r_14, channel_num=17, show_plots=False, save_output=None)
    rebin_pwr_14_i= rebin_likefpga(xspec_pwr_i_14, channel_num=18, show_plots=False, save_output=None)
    rebin_pwr_23_r= rebin_likefpga(xspec_pwr_r_23, channel_num=19, show_plots=False, save_output=None)
    rebin_pwr_23_i= rebin_likefpga(xspec_pwr_i_23, channel_num=20, show_plots=False, save_output=None)
    rebin_pwr_24_r= rebin_likefpga(xspec_pwr_r_24, channel_num=21, show_plots=False, save_output=None)
    rebin_pwr_24_i= rebin_likefpga(xspec_pwr_i_24, channel_num=22, show_plots=False, save_output=None)
    rebin_pwr_34_r= rebin_likefpga(xspec_pwr_r_34, channel_num=23, show_plots=False, save_output=None)
    rebin_pwr_34_i= rebin_likefpga(xspec_pwr_i_34, channel_num=24, show_plots=False, save_output=None)

    acc_pwr0 = acc_likefpga(rebin_pwr0, n_acc, channel_num=0, show_plots=False, save_output=None)
    acc_pwr1 = acc_likefpga(rebin_pwr1, n_acc, channel_num=1, show_plots=False, save_output=None)
    acc_pwr2 = acc_likefpga(rebin_pwr2, n_acc, channel_num=2, show_plots=False, save_output=None)
    acc_pwr3 = acc_likefpga(rebin_pwr3, n_acc, channel_num=3, show_plots=False, save_output=None)
    acc_pwr4 = acc_likefpga(rebin_pwr4, n_acc, channel_num=4, show_plots=False, save_output=None)

    acc_pwr01_r = acc_likefpga(rebin_pwr_01_r, n_acc, channel_num=5, show_plots=False, save_output=None)
    acc_pwr01_i = acc_likefpga(rebin_pwr_01_i, n_acc, channel_num=6, show_plots=False, save_output=None)
    acc_pwr02_r = acc_likefpga(rebin_pwr_02_r, n_acc, channel_num=7, show_plots=False, save_output=None)
    acc_pwr02_i = acc_likefpga(rebin_pwr_02_i, n_acc, channel_num=8, show_plots=False, save_output=None)
    acc_pwr03_r = acc_likefpga(rebin_pwr_03_r, n_acc, channel_num=9, show_plots=False, save_output=None)
    acc_pwr03_i = acc_likefpga(rebin_pwr_03_i, n_acc, channel_num=10, show_plots=False, save_output=None)
    acc_pwr04_r = acc_likefpga(rebin_pwr_04_r, n_acc, channel_num=11, show_plots=False, save_output=None)
    acc_pwr04_i = acc_likefpga(rebin_pwr_04_i, n_acc, channel_num=12, show_plots=False, save_output=None)
    acc_pwr12_r = acc_likefpga(rebin_pwr_12_r, n_acc, channel_num=13, show_plots=False, save_output=None)
    acc_pwr12_i = acc_likefpga(rebin_pwr_12_i, n_acc, channel_num=14, show_plots=False, save_output=None)
    acc_pwr13_r = acc_likefpga(rebin_pwr_13_r, n_acc, channel_num=15, show_plots=False, save_output=None)
    acc_pwr13_i = acc_likefpga(rebin_pwr_13_i, n_acc, channel_num=16, show_plots=False, save_output=None)
    acc_pwr14_r = acc_likefpga(rebin_pwr_14_r, n_acc, channel_num=17, show_plots=False, save_output=None)
    acc_pwr14_i = acc_likefpga(rebin_pwr_14_i, n_acc, channel_num=18, show_plots=False, save_output=None)
    acc_pwr23_r = acc_likefpga(rebin_pwr_23_r, n_acc, channel_num=19, show_plots=False, save_output=None)
    acc_pwr23_i = acc_likefpga(rebin_pwr_23_i, n_acc, channel_num=20, show_plots=False, save_output=None)
    acc_pwr24_r = acc_likefpga(rebin_pwr_24_r, n_acc, channel_num=21, show_plots=False, save_output=None)
    acc_pwr24_i = acc_likefpga(rebin_pwr_24_i, n_acc, channel_num=22, show_plots=False, save_output=None)
    acc_pwr34_r = acc_likefpga(rebin_pwr_34_r, n_acc, channel_num=23, show_plots=False, save_output=None)
    acc_pwr34_i = acc_likefpga(rebin_pwr_34_i, n_acc, channel_num=24, show_plots=False, save_output=None)


    # STEP 6 ---------------- average in time and freq -------------------------
    # import canvas bins correctly -- make sure you have this file
    fname = 'CANVAS_fbins/fbins.txt'                                 
    fbins_str = np.genfromtxt(fname, dtype='str') 
    fbins_dbl = [(float(f[0].replace(',','')),float(f[1].replace(',',''))) for f in fbins_str]
    c_fbins = [item for sublist in fbins_dbl for item in sublist]
    center_freqs = [fs/nFFT * ff for ff in np.arange(0, 512)]

    avg_pwr0 = rebin_canvas(acc_pwr0, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=0, show_plots=False, save_output=None)
    avg_pwr1 = rebin_canvas(acc_pwr1, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=1, show_plots=False, save_output=None)
    avg_pwr2 = rebin_canvas(acc_pwr2, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=2, show_plots=False, save_output=None)
    avg_pwr3 = rebin_canvas(acc_pwr3, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=3, show_plots=False, save_output=None)
    avg_pwr4 = rebin_canvas(acc_pwr4, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=4, show_plots=False, save_output=None)

    avg_pwr01_r = rebin_canvas(acc_pwr01_r, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=5, show_plots=False, save_output=None)
    avg_pwr01_i = rebin_canvas(acc_pwr01_i, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=6, show_plots=False, save_output=None)
    avg_pwr02_r = rebin_canvas(acc_pwr02_r, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=7, show_plots=False, save_output=None)
    avg_pwr02_i = rebin_canvas(acc_pwr02_i, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=8, show_plots=False, save_output=None)
    avg_pwr03_r = rebin_canvas(acc_pwr03_r, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=9, show_plots=False, save_output=None)
    avg_pwr03_i = rebin_canvas(acc_pwr03_i, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=10, show_plots=False, save_output=None)
    avg_pwr04_r = rebin_canvas(acc_pwr04_r, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=11, show_plots=False, save_output=None)
    avg_pwr04_i = rebin_canvas(acc_pwr04_i, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=12, show_plots=False, save_output=None)
    avg_pwr12_r = rebin_canvas(acc_pwr12_r, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=13, show_plots=False, save_output=None)
    avg_pwr12_i = rebin_canvas(acc_pwr12_i, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=14, show_plots=False, save_output=None)
    avg_pwr13_r = rebin_canvas(acc_pwr13_r, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=15, show_plots=False, save_output=None)
    avg_pwr13_i = rebin_canvas(acc_pwr13_i, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=16, show_plots=False, save_output=None)
    avg_pwr14_r = rebin_canvas(acc_pwr14_r, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=17, show_plots=False, save_output=None)
    avg_pwr14_i = rebin_canvas(acc_pwr14_i, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=18, show_plots=False, save_output=None)
    avg_pwr23_r = rebin_canvas(acc_pwr23_r, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=19, show_plots=False, save_output=None)
    avg_pwr23_i = rebin_canvas(acc_pwr23_i, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=20, show_plots=False, save_output=None)
    avg_pwr24_r = rebin_canvas(acc_pwr24_r, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=21, show_plots=False, save_output=None)
    avg_pwr24_i = rebin_canvas(acc_pwr24_i, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=22, show_plots=False, save_output=None)
    avg_pwr34_r = rebin_canvas(acc_pwr34_r, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=23, show_plots=False, save_output=None)
    avg_pwr34_i = rebin_canvas(acc_pwr34_i, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=24, show_plots=False, save_output=None)

    # STEP 7 ---------------- compress -------------------------
    # use spec compress or xspec compress for log2 compression
    cpmrs_val0 = spec_compress(avg_pwr0, channel_num=0, show_plots=False, save_output='both')
    cpmrs_val1 = spec_compress(avg_pwr1, channel_num=1, show_plots=False, save_output='both')
    cpmrs_val2 = spec_compress(avg_pwr2, channel_num=2, show_plots=False, save_output='both')
    cpmrs_val3 = spec_compress(avg_pwr3, channel_num=3, show_plots=False, save_output='both')
    cpmrs_val4 = spec_compress(avg_pwr4, channel_num=4, show_plots=False, save_output='both')

    cmprs_val_r01 = xspec_compress(avg_pwr01_r, channel_num=5, coefficient='r', show_plots=False, save_output='both')
    cmprs_val_i01 = xspec_compress(avg_pwr01_i, channel_num=6, coefficient='i', show_plots=False, save_output='both')
    cmprs_val_r02 = xspec_compress(avg_pwr02_r, channel_num=7, coefficient='r', show_plots=False, save_output='both')
    cmprs_val_i02 = xspec_compress(avg_pwr02_i, channel_num=8, coefficient='i', show_plots=False, save_output='both')
    cmprs_val_r03 = xspec_compress(avg_pwr03_r, channel_num=9, coefficient='r', show_plots=False, save_output='both')
    cmprs_val_i03 = xspec_compress(avg_pwr03_i, channel_num=10, coefficient='i', show_plots=False, save_output='both')
    cmprs_val_r04 = xspec_compress(avg_pwr04_r, channel_num=11, coefficient='r', show_plots=False, save_output='both')
    cmprs_val_i04 = xspec_compress(avg_pwr04_i, channel_num=12, coefficient='i', show_plots=False, save_output='both')
    cmprs_val_r12 = xspec_compress(avg_pwr12_r, channel_num=13, coefficient='r', show_plots=False, save_output='both')
    cmprs_val_i12 = xspec_compress(avg_pwr12_i, channel_num=14, coefficient='i', show_plots=False, save_output='both')
    cmprs_val_r13 = xspec_compress(avg_pwr13_r, channel_num=15, coefficient='r', show_plots=False, save_output='both')
    cmprs_val_i13 = xspec_compress(avg_pwr13_i, channel_num=16, coefficient='i', show_plots=False, save_output='both')
    cmprs_val_r14 = xspec_compress(avg_pwr14_r, channel_num=17, coefficient='r', show_plots=False, save_output='both')
    cmprs_val_i14 = xspec_compress(avg_pwr14_i, channel_num=18, coefficient='i', show_plots=False, save_output='both')
    cmprs_val_r23 = xspec_compress(avg_pwr23_r, channel_num=19, coefficient='r', show_plots=False, save_output='both')
    cmprs_val_i23 = xspec_compress(avg_pwr23_i, channel_num=20, coefficient='i', show_plots=False, save_output='both')
    cmprs_val_r24 = xspec_compress(avg_pwr24_r, channel_num=21, coefficient='r', show_plots=False, save_output='both')
    cmprs_val_i24 = xspec_compress(avg_pwr24_i, channel_num=22, coefficient='i', show_plots=False, save_output='both')
    cmprs_val_r34 = xspec_compress(avg_pwr34_r, channel_num=23, coefficient='r', show_plots=False, save_output='both')
    cmprs_val_i34 = xspec_compress(avg_pwr34_i, channel_num=24, coefficient='i', show_plots=False, save_output='both')
    print("Done! Freq: ",signal_freq0)
    
    freq0 = file_input[0][-10:-4]
    freq1 = file_input[1][-10:-4]
    freq2 = file_input[2][-10:-4]
    freq3 = file_input[3][-10:-4]
    freq4 = file_input[4][-10:-4]
    
    # STEP 8 ---- saving as meaningful data ----
    file_spec = open('model_trs_rest/Spec_vals_'+date_time+'.txt','w')
    file_spec.write("SPECTRA "+"\n")

    file_spec.write("Channal Frequency "+"\n")
    file_spec.write("0 -> "+freq0+"\n")
    file_spec.write("1 -> "+freq1+"\n")
    file_spec.write("2 -> "+freq2+"\n")
    file_spec.write("3 -> "+freq3+"\n")
    file_spec.write("4 -> "+freq4+"\n")

    spec_vals = []
    spec_vals.append(cpmrs_val0)
    spec_vals.append(cpmrs_val1)
    spec_vals.append(cpmrs_val2)
    spec_vals.append(cpmrs_val3)
    spec_vals.append(cpmrs_val4)

    # Writing spectra values into file
    file_spec.write("HEX\n("+"0)\t("+"1)\t("+"2)\t("+"3)\t("+"4)\n")
    for i in range(len(spec_vals[0])):
        file_spec.write(str(proper_twos_complement(spec_vals[0][i]))+"\t"+str(proper_twos_complement(spec_vals[1][i]))+"\t"+str(proper_twos_complement(spec_vals[2][i]))+"\t"+str(proper_twos_complement(spec_vals[3][i]))+"\t"+str(proper_twos_complement(spec_vals[4][i]))+"\n")
    file_spec.write("INT\n("+"0)\t("+"1)\t("+"2)\t("+"3)\t("+"4)\n")
    for i in range(len(spec_vals[0])):
        file_spec.write(str(spec_vals[0][i])+"\t"+str(spec_vals[1][i])+"\t"+str(spec_vals[2][i])+"\t"+str(spec_vals[3][i])+"\t"+str(spec_vals[4][i])+"\n")

    file_spec.close()

    file_xspeca = open('model_trs_rest/Xspec_A_vals_'+date_time+'.txt','w')
    file_xspeca.write("CROSS-SPECTRA A (Real) "+"\n")
    type = 'A'

    file_xspeca.write("Channal Frequency "+"\n")
    file_xspeca.write("0 -> "+freq0+"\n")
    file_xspeca.write("1 -> "+freq1+"\n")
    file_xspeca.write("2 -> "+freq2+"\n")
    file_xspeca.write("3 -> "+freq3+"\n")
    file_xspeca.write("4 -> "+freq4+"\n")

    # Combining Real values
    xspec_real = []
    xspec_real.append(cmprs_val_r01)
    xspec_real.append(cmprs_val_r02)
    xspec_real.append(cmprs_val_r03)
    xspec_real.append(cmprs_val_r04)
    xspec_real.append(cmprs_val_r12)
    xspec_real.append(cmprs_val_r13)
    xspec_real.append(cmprs_val_r14)
    xspec_real.append(cmprs_val_r23)
    xspec_real.append(cmprs_val_r24)
    xspec_real.append(cmprs_val_r34)

    # Writing Real values into file
    file_xspeca.write("HEX\n("+type+"r01)\t("+type+"r02)\t("+type+"r03)\t("+type+"r04)\t("+type+"r12)\t("+type+"r13)\t("+type+"r14)\t("+type+"r23)\t("+type+"r24)\t("+type+"34)\n")
    for i in range(len(xspec_real[0])):
        file_xspeca.write(str(proper_twos_complement(xspec_real[0][i]))+"\t"+str(proper_twos_complement(xspec_real[1][i]))+"\t"+str(proper_twos_complement(xspec_real[2][i]))+"\t"+str(proper_twos_complement(xspec_real[3][i]))+"\t"+str(proper_twos_complement(xspec_real[4][i]))+"\t"+str(proper_twos_complement(xspec_real[5][i]))+"\t"+str(proper_twos_complement(xspec_real[6][i]))+"\t"+str(proper_twos_complement(xspec_real[7][i]))+"\t"+str(proper_twos_complement(xspec_real[8][i]))+"\t"+str(proper_twos_complement(xspec_real[9][i]))+"\n")
    file_xspeca.write("INT\n("+type+"r01)\t("+type+"r02)\t("+type+"r03)\t("+type+"r04)\t("+type+"r12)\t("+type+"r13)\t("+type+"r14)\t("+type+"r23)\t("+type+"r24)\t("+type+"34)\n")
    for i in range(len(xspec_real[0])):
        file_xspeca.write(str(xspec_real[0][i])+"\t"+str(xspec_real[1][i])+"\t"+str(xspec_real[2][i])+"\t"+str(xspec_real[3][i])+"\t"+str(xspec_real[4][i])+"\t"+str(xspec_real[5][i])+"\t"+str(xspec_real[6][i])+"\t"+str(xspec_real[7][i])+"\t"+str(xspec_real[8][i])+"\t"+str(xspec_real[9][i])+"\n")

    file_xspeca.close()

    # Doing it again for 'B'
    file_xspecb = open('model_trs_rest/Xspec_B_vals_'+date_time+'.txt','w')
    file_xspecb.write("CROSS-SPECTRA B (Imaginary) "+"\n")
    type = 'B'

    file_xspecb.write("Channal Frequency "+"\n")
    file_xspecb.write("0 -> "+freq0+"\n")
    file_xspecb.write("1 -> "+freq1+"\n")
    file_xspecb.write("2 -> "+freq2+"\n")
    file_xspecb.write("3 -> "+freq3+"\n")
    file_xspecb.write("4 -> "+freq4+"\n") 

    # Combining Imaginary values
    xspec_im = []
    xspec_im.append(cmprs_val_i01)
    xspec_im.append(cmprs_val_i02)
    xspec_im.append(cmprs_val_i03)
    xspec_im.append(cmprs_val_i04)
    xspec_im.append(cmprs_val_i12)
    xspec_im.append(cmprs_val_i13)
    xspec_im.append(cmprs_val_i14)
    xspec_im.append(cmprs_val_i23)
    xspec_im.append(cmprs_val_i24)
    xspec_im.append(cmprs_val_i34)

    # Writing Imaginary values into file
    file_xspecb.write("HEX\n("+type+"i01)\t("+type+"r02)\t("+type+"r03)\t("+type+"r04)\t("+type+"r12)\t("+type+"r13)\t("+type+"r14)\t("+type+"r23)\t("+type+"r24)\t("+type+"34)\n")
    for i in range(len(xspec_im[0])):
        file_xspecb.write(str(proper_twos_complement(xspec_im[0][i]))+"\t"+str(proper_twos_complement(xspec_im[1][i]))+"\t"+str(proper_twos_complement(xspec_im[2][i]))+"\t"+str(proper_twos_complement(xspec_im[3][i]))+"\t"+str(proper_twos_complement(xspec_im[4][i]))+"\t"+str(proper_twos_complement(xspec_im[5][i]))+"\t"+str(proper_twos_complement(xspec_im[6][i]))+"\t"+str(proper_twos_complement(xspec_im[7][i]))+"\t"+str(proper_twos_complement(xspec_im[8][i]))+"\t"+str(proper_twos_complement(xspec_im[9][i]))+"\n")
    file_xspecb.write("INT\n("+type+"r01)\t("+type+"r02)\t("+type+"r03)\t("+type+"r04)\t("+type+"r12)\t("+type+"r13)\t("+type+"r14)\t("+type+"r23)\t("+type+"r24)\t("+type+"34)\n")
    for i in range(len(xspec_im[0])):
        file_xspecb.write(str(xspec_im[0][i])+"\t"+str(xspec_im[1][i])+"\t"+str(xspec_im[2][i])+"\t"+str(xspec_im[3][i])+"\t"+str(xspec_im[4][i])+"\t"+str(xspec_im[5][i])+"\t"+str(xspec_im[6][i])+"\t"+str(xspec_im[7][i])+"\t"+str(xspec_im[8][i])+"\t"+str(xspec_im[9][i])+"\n")

    file_xspecb.close()