from tkinter import E
import serial #import serial library
import time
import numpy as np
from datetime import datetime
from readFPGA import twos_complement, read_spec_vals, read_header_CCSDS, read_xspec_vals
from saveas import save_FFT, save_power, save_spectra, save_xspectra, saveall, save_rotate, save_IF, save_ram
# from thread_funcs import thread_function, thread_initialize
import logging
import threading
import queue

# Global variable for Threading

global counter # 1 for running, 0 for end iteration
global buffer_pkt
global ser

def thread_function(name):
    logging.info("Thread %s: starting", name)
    while (counter==1):
        if(buffer_pkt.qsize()<3000): # Around 2600 is one packet
            val = int.from_bytes(ser.read(2), 'big') # Create func that reads from port - create buffer to store and throws serial bytes in - 
            hex_val = format(np.int16(val) & 0xffff, '04X')
            buffer_pkt.put(hex_val)

    logging.info("Thread %s: finishing", name)

def thread_initialize():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    buffer_pkt = queue.Queue()
    logging.info("Main    : before creating thread")
    x = threading.Thread(target=thread_function, args=(1,))
    logging.info("Main    : before running thread")
    x.start()

    logging.info("Main    : wait for the thread to finish")
    x.join()
    logging.info("Main    : all done")

def response_check(ser,ack,dump_line = True):
    msg_len = len(ack)
    ack_read = False
    val = ''
    while ack_read == False:
        if (ser.in_waiting > 0):
            if dump_line:
                if ser.in_waiting>msg_len: #clear to end of serial line
                    dump = ser.read(ser.in_waiting-msg_len) 
            
            val = ser.read(msg_len)
            if val == ack:
                ack_read = True
    return 

def read_header(ser):
    #define sycn bytes
    #sync = b'\x35\x2E\xF8\x53'
    sync = b'\x1A\xCF\xFC\x1D'

    #Synchronize with expected packet
    response_check(ser,sync,dump_line=False)

    #extract header info
    alg_id = ser.read(1)
    test_mode = ser.read(1)
    payload_len = ser.read(2)
    length = int.from_bytes(payload_len,'big') +1 #'big' => most significant byte is at the beginning of the byte array
    mask = b'\x0f' 
    test_mode = bytes([test_mode[0] & mask[0]])

    return length,test_mode

def readFPGA(ser, num_read = 1, readcon = 'none', outpath = 'HW-output/default-file', time_CCSDS = False, byte_type = 2):

    default_words = 10        
    length,test_mode = read_header(ser)
    word_length = 12 #bytes

    words = int(length/word_length)
    for i in range(num_read): # For repeating read
        #read in payload 
        print("Printing entire thing")
        date_time = outpath[-16:]
        outpath='HW-output/5-ch/read_all'
        name = outpath+ 'CCSDS_pkt' + date_time
        file = open(name +'.txt','w')
        # initializing thread
        thread_initialize()
        if time_CCSDS == True:
            print("Timing the Packets")
            # Starting Thread
            format = "%(asctime)s: %(message)s"
            logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
            buffer_pkt = queue.Queue()
            logging.info("Main    : before creating thread")
            x = threading.Thread(target=thread_function, args=(1,))
            logging.info("Main    : before running thread")
            x.start()
            for i in range(13000): # originally, 130000
            
                val = int.from_bytes(ser.read(2), 'big') # Create func that reads from port - create buffer to store and throws serial bytes in - 
                hex_val = format(np.int16(val) & 0xffff, '04X')
                file.write(str(hex_val))
            file.close()
        else:
            if byte_type == 2:
                #file1 = open(name + '_spectra' + '.txt','w')
                spectra_cnt = -1
                # spectra_vals=[]
                spectra_vals = []
                xspec_vals_a = []
                xspec_vals_b = []
                # spectra_vals = np.zeros((words,5))
                # xspec_vals_a = np.zeros((10000,10))
                # xspec_vals_b = np.zeros((10000,10))
                j=0
                ph = "c"
                for i in range(7500):
                    val = int.from_bytes(ser.read(2), 'big')
                    hex_val = format(np.int16(val) & 0xffff, '04X')
                    match str(hex_val):
                        case "BA5E":
                            file.write("\n")
                            file.write(str(hex_val))
                            val = int.from_bytes(ser.read(2), 'big')
                            hex_val = format(np.int16(val) & 0xffff, '04X')
                            file.write("  ")
                            file.write(str(hex_val))
                            file.write("\n")
                            # if spectra_cnt%3==0 and spectra_vals!=[]:
                            #     read_spec_vals(spectra_vals)
                            #     read_xspec_vals(xspec_vals_a,xspec_vals_b) 

                        case "1ACF":
                            file.write("\n")
                            file.write(str(hex_val))
                            val = int.from_bytes(ser.read(2), 'big')
                            hex_val = format(np.int16(val) & 0xffff, '04X')
                            file.write("  ")
                            file.write(str(hex_val))
                            file.write("\n")
                            header_spectra = []
                            for i in range(6):
                                val = int.from_bytes(ser.read(2), 'big')
                                hex_val = format(np.int16(val) & 0xffff, '04X')
                                file.write(str(hex_val))
                                file.write("  ")
                                #header_spectra.append(str(twos_complement(hex_val,16)))
                                header_spectra.append(str(hex_val))
                                #header_spectra+=str(twos_complement(hex_val))
                            file.write("\n")
                            # file.write("Header:\n"+"Packet Version: \t"+header_spectra[1])
                            # file.write("\nSec Header Flag: \t"+header_spectra[2])
                            read_header_CCSDS(file,header_spectra)
                            j=0
                            spectra_cnt+=1
                            if (spectra_cnt-1)%3==0:
                                ph='a'
                            elif (spectra_cnt+1)%3==0:
                                ph='b'
                            if spectra_cnt%3==0 and spectra_vals!=[]:
                                read_spec_vals(spectra_vals,date_time,spectra_cnt/3)
                            if xspec_vals_a!=[] and xspec_vals_b!=[]:
                                read_xspec_vals(xspec_vals_a,xspec_vals_b,date_time,spectra_cnt/3) 
                                spectra_vals = []
                                xspec_vals_a = []
                                xspec_vals_b = []
                            
                        case _:
                            file.write(str(hex_val))
                            file.write("  ")
                            if spectra_cnt%3==0:
                                spectra_vals.append(str(hex_val))
                                j+=1
                            else:
                                if ph=='a' and spectra_cnt/3<5:
                                    # xspec_vals_a[j][int(spectra_cnt/3)]= val
                                    xspec_vals_a.append(str(hex_val))
                                    j+=1
                                elif ph=='b'and spectra_cnt/3<5:
                                    # xspec_vals_b[j][int(spectra_cnt/3)]= val
                                    xspec_vals_b.append(str(hex_val))
                                    j+=1
                    #file.write(ser.read(2))
                file.close()
                # Printing spectra into seperate file
                #file1.write("(1)\t(2)\t(3)\t(4)\t(5)\n")
                # for i in range(254):
                #     file1.write(str(int(spectra_vals[i][0]))+"\t"+str(int(spectra_vals[i][1]))+"\t"+str(int(spectra_vals[i][2]))+"\t"+str(int(spectra_vals[i][3]))+"\t"+str(int(spectra_vals[i][4]))+"\n")
                # file1.close()

                # read_spec_vals(spectra_vals)
                # read_xspec_vals(xspec_vals_a,xspec_vals_b)
            elif byte_type==1:
                #file1 = open(name + '_spectra' + '.txt','w')
                spectra_cnt = -1
                # spectra_vals=[]
                spectra_vals = []
                xspec_vals_a = []
                xspec_vals_b = []
                # spectra_vals = np.zeros((words,5))
                # xspec_vals_a = np.zeros((10000,10))
                # xspec_vals_b = np.zeros((10000,10))
                j=0
                ph = "c"
                val1 = int.from_bytes(ser.read(1), 'big')
                hex_val1 = format(np.int16(val1) & 0xffff, '04X')
                cntr=1
                for i in range(7500):
                    val2 = int.from_bytes(ser.read(1), 'big')
                    hex_val2 = format(np.int16(val1) & 0xffff, '04X')
                    hex_val = hex_val1+hex_val2
                    #if cntr == 1:

                    match str(hex_val):
                        case "BA5E":
                            file.write("\n")
                            file.write(str(hex_val))
                            val = int.from_bytes(ser.read(2), 'big')
                            hex_val = format(np.int16(val) & 0xffff, '04X')
                            file.write("  ")
                            file.write(str(hex_val))
                            file.write("\n")
                            # if spectra_cnt%3==0 and spectra_vals!=[]:
                            #     read_spec_vals(spectra_vals)
                            #     read_xspec_vals(xspec_vals_a,xspec_vals_b) 

                        case "1ACF":
                            file.write("\n")
                            file.write(str(hex_val))
                            val = int.from_bytes(ser.read(2), 'big')
                            hex_val = format(np.int16(val) & 0xffff, '04X')
                            file.write("  ")
                            file.write(str(hex_val))
                            file.write("\n")
                            header_spectra = []
                            for i in range(6):
                                val = int.from_bytes(ser.read(2), 'big')
                                hex_val = format(np.int16(val) & 0xffff, '04X')
                                file.write(str(hex_val))
                                file.write("  ")
                                #header_spectra.append(str(twos_complement(hex_val,16)))
                                header_spectra.append(str(hex_val))
                                #header_spectra+=str(twos_complement(hex_val))
                            file.write("\n")
                            # file.write("Header:\n"+"Packet Version: \t"+header_spectra[1])
                            # file.write("\nSec Header Flag: \t"+header_spectra[2])
                            read_header_CCSDS(file,header_spectra)
                            j=0
                            spectra_cnt+=1
                            if (spectra_cnt-1)%3==0:
                                ph='a'
                            elif (spectra_cnt+1)%3==0:
                                ph='b'
                            if spectra_cnt%3==0 and spectra_vals!=[]:
                                read_spec_vals(spectra_vals)
                            if xspec_vals_a!=[] and xspec_vals_b!=[]:
                                read_xspec_vals(xspec_vals_a,xspec_vals_b) 
                                spectra_vals = []
                                xspec_vals_a = []
                                xspec_vals_b = []
                            
                        case _:
                            file.write(str(hex_val))
                            file.write("  ")
                            if spectra_cnt%3==0:
                                spectra_vals.append(str(hex_val))
                                j+=1
                            else:
                                if ph=='a' and spectra_cnt/3<5:
                                    # xspec_vals_a[j][int(spectra_cnt/3)]= val
                                    xspec_vals_a.append(str(hex_val))
                                    j+=1
                                elif ph=='b'and spectra_cnt/3<5:
                                    # xspec_vals_b[j][int(spectra_cnt/3)]= val
                                    xspec_vals_b.append(str(hex_val))
                                    j+=1
                    #file.write(ser.read(2))
                file.close()
                # Printing spectra into seperate file
                #file1.write("(1)\t(2)\t(3)\t(4)\t(5)\n")
                # for i in range(254):
                #     file1.write(str(int(spectra_vals[i][0]))+"\t"+str(int(spectra_vals[i][1]))+"\t"+str(int(spectra_vals[i][2]))+"\t"+str(int(spectra_vals[i][3]))+"\t"+str(int(spectra_vals[i][4]))+"\n")
                # file1.close()

                # read_spec_vals(spectra_vals)
                # read_xspec_vals(xspec_vals_a,xspec_vals_b)

    return vals
