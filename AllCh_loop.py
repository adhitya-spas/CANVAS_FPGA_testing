# First randomize different frequencies
# Get inputs first
# Make model as a function
# MAke fpga function

# Importing libraries
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
from datetime import datetime

# Importing custom libraries]
from fpga_main_function import run_fpga_output, parse_these_packets, compare_these_packets

# Creating a log file
logfile = open('test_log.txt','w')
logfile.write("Logging combinations\n")

#Generate input signal from file or aribitrarily
fromFile = True

if fromFile:
    inputs = 'Inputs/'
    
    amp = "hi"
    f = "_03khz"
    phase = "5deg"

    freq0 = "512hz"
    freq1 = "03khz"
    freq2 = "10khz"
    freq3 = "23khz" #"24khz" # broken
    freq4 = "33khz"

    #file0 = inputs+amp+"_amp_"+freq0+'.txt'
    file0 = inputs+'signal_0.txt'
    file1 = inputs+amp+"_amp_"+freq1+'.txt'
    file2 = inputs+amp+"_amp_"+freq2+'.txt'
    file3 = inputs+'signal_23000.txt'   
    file4 = inputs+amp+"_amp_"+freq4+'.txt'
    logfile.write("From File mode: (1)"+freq0+" (2)"+freq1+" (3)"+freq2+" (4)"+freq3+" (5)"+freq4)
else:
    # Generate random files here    
    print("TBD")
    
    
# Opening the pre determined combo file
file_combo = open('allch_combo.txt').read().splitlines()

#initialize serial ports
pic_ser = serial.Serial("COM4",115200)
pic_ser1 = serial.Serial("COM10",115200)
pic_ser2 = serial.Serial("COM9",115200)
FPGA_ser = serial.Serial("COM7",115200) #Uncomment later


for iteration in range(0,len(file_combo)):
    time.sleep(5)
    logfile.write(" => Iteration "+str(iteration))
    line = file_combo[iteration].split("\t")
    file_input = []
    
    # Assigning files based on text file 
    for index in line:
        if index == '1':
            file_input.append(file0)
        elif index == '2':
            file_input.append(file1)
        elif index == '3':
            file_input.append(file2)
        elif index == '4':
            file_input.append(file3)
        elif index == '5':
            file_input.append(file4)
        
    # to get timestamp
    now = datetime.now()
    date_time = now.strftime("_%m%d%Y_%H%M%S")
    
    # RUnning FPGA files
    run_fpga_output(file_input, date_time, pic_ser,pic_ser1,pic_ser2,FPGA_ser)
    parse_these_packets(file_input, date_time)
    # compare_these_packets(date_time)
    

