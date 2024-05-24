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
from fpga_main_function import run_fpga_output, parse_these_packets, compare_these_packets, model_generation

# Creating a log file
logfile = open('test_log_trs_rest.txt','w')
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
    file0 = inputs+'signal_512.txt'
    file1 = inputs+'signal_3000.txt'
    file2 = inputs+'signal_10000.txt'
    file3 = inputs+'signal_23000.txt'
    file4 = inputs+'signal_33000.txt'
    file5 = inputs+"signal_512"+'_1.txt'
    file6 = inputs+"signal_512"+'_2.txt'
    file7 = inputs+"signal_512"+'_3.txt'
    file8 = inputs+"signal_512"+'_4.txt'
    file9 = inputs+"signal_512"+'_5.txt'
    file10 = inputs+"signal_0"+'.txt'
    file11 = inputs+"signal_256"+'.txt'
    file12 = inputs+"signal_40384"+'.txt'
    
    fileHWU = inputs+"signal_18300"+'_HWUc.txt'
    fileNWC = inputs+"signal_19800"+'_NWCc.txt'
    fileNPM = inputs+"signal_21400"+'_NPMc.txt'
    fileJJI = inputs+"signal_22200"+'_JJIc.txt'
    fileDHO = inputs+"signal_23400"+'_DHOc.txt'
    fileNAA = inputs+"signal_24000"+'_NAAc.txt'
    fileNLK = inputs+"signal_24600"+'_NLK.txt'
    fileNML = inputs+"signal_25200"+'_NML.txt'
    fileNRK = inputs+"signal_37500"+'_NRK.txt'
    fileNAU = inputs+"signal_40800"+'_NAU.txt'
    
    logfile.write("From File mode: (1)"+freq0+" (2)"+freq1+" (3)"+freq2+" (4)"+freq3+" (5)"+freq4+" (6)"+"512_1Hz"+" (7)"+"512_2Hz"+" (8)"+"512_3Hz"+" (9)"+"512_4Hz"+" (10)"+"512_5Hz"+" (11)"+"0Hz"+" (12)"+"256Hz"+" (13)"+"40384Hz" )
else:
    # Generate random files here    
    print("TBD")
    
    
# Opening the pre determined combo file
file_combo = open('allch_combotrs_rest.txt').read().splitlines()

#initialize serial ports
pic_ser = serial.Serial("COM5",115200)
pic_ser1 = serial.Serial("COM3",115200)
pic_ser2 = serial.Serial("COM4",115200)
FPGA_ser = serial.Serial("COM7",115200) #Uncomment later


for iteration in range(0,len(file_combo)):
    time.sleep(5)
    logfile.write("\n=> Iteration "+str(iteration)+" ")
    line = file_combo[iteration].split("\t")
    file_input = []
    
    # Assigning files based on text file 
    for index in line:
        if index == '1':
            file_input.append(file0)
            logfile.write("("+str(index)+") "+freq0+" ")
        elif index == '2':
            file_input.append(file1)
            logfile.write("("+str(index)+") "+freq1+" ")
        elif index == '3':
            file_input.append(file2)
            logfile.write("("+str(index)+") "+freq2+" ")
        elif index == '4':
            file_input.append(file3)
            logfile.write("("+str(index)+") "+freq3+" ")
        elif index == '5':
            file_input.append(file4)
            logfile.write("("+str(index)+") "+freq4+" ")
        elif index == '6':
            file_input.append(file5)
            logfile.write("("+str(index)+") "+"512_1"+" ")
        elif index == '7':
            file_input.append(file6)
            logfile.write("("+str(index)+") "+"512_2"+" ")
        elif index == '8':
            file_input.append(file7)
            logfile.write("("+str(index)+") "+"512_3"+" ")
        elif index == '9':
            file_input.append(file8)
            logfile.write("("+str(index)+") "+"512_4"+" ")
        elif index == '10':
            file_input.append(file9)
            logfile.write("("+str(index)+") "+"512_5"+" ")
        elif index == '0':
            file_input.append(file10)
            logfile.write("("+str(index)+") "+"0"+" ")
        elif index == '11':
            file_input.append(file11)
            logfile.write("("+str(index)+") "+"256"+" ")
        elif index == '12':
            file_input.append(file12)
            logfile.write("("+str(index)+") "+"40384"+" ")
        elif index == '13':
            file_input.append(fileHWU)
            logfile.write("("+str(index)+") "+"HWU"+" ")
        elif index == '14':
            file_input.append(fileNWC)
            logfile.write("("+str(index)+") "+"NWC"+" ")
        elif index == '15':
            file_input.append(fileNPM)
            logfile.write("("+str(index)+") "+"NPM"+" ")
        elif index == '16':
            file_input.append(fileJJI)
            logfile.write("("+str(index)+") "+"JJI"+" ")
        elif index == '17':
            file_input.append(fileDHO)
            logfile.write("("+str(index)+") "+"DHO"+" ")
        elif index == '18':
            file_input.append(fileNAA)
            logfile.write("("+str(index)+") "+"NAA"+" ")
        elif index == '19':
            file_input.append(fileNLK)
            logfile.write("("+str(index)+") "+"NLK"+" ")
        elif index == '20':
            file_input.append(fileNML)
            logfile.write("("+str(index)+") "+"NML"+" ")
        elif index == '21':
            file_input.append(fileNRK)
            logfile.write("("+str(index)+") "+"NRK"+" ")
        elif index == '22':
            file_input.append(fileNRK)
            logfile.write("("+str(index)+") "+"NAU"+" ")
            
        
    # to get timestamp
    now = datetime.now()
    date_time = now.strftime("_%m%d%Y_%H%M%S")
    
    # RUnning FPGA files
    run_fpga_output(file_input, date_time, pic_ser,pic_ser1,pic_ser2,FPGA_ser)
    parse_these_packets(file_input, date_time)
    model_generation(file_input,date_time)
    try:
        compare_these_packets(date_time)
    except:
        logfile.write("\n Comparison error \n ")
    

