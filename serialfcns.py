from tkinter import E
import serial #import serial library
import time
import numpy as np
from datetime import datetime
from readFPGA import twos_complement, read_spec_vals, read_header_CCSDS, read_xspec_vals
from saveas import save_FFT, save_power, save_spectra, save_xspectra, saveall, save_rotate, save_IF, save_ram

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

def adi_junk_remove(ser,ack,dump_line = True):
    msg_len = len(ack)
    ack_read = False
    val = ''
    if (ser.in_waiting > 0):
        if dump_line:
            if ser.in_waiting>msg_len: #clear to end of serial line
                dump = ser.read(ser.in_waiting-msg_len) 
            
        val = ser.read(msg_len)
    return

def ser_write(ser, command, len_header = True):
    if len_header:
        msg_len = len(command)
        header = msg_len.to_bytes(1,'big')
        ser.write(header)
    ser.write(command)
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

def readFPGA(ser, freq0, freq1, freq2, freq3, freq4, num_read = 1, readcon = 'none', outpath = 'HW-output/default-file', time_CCSDS = False, byte_type = 2):
    #define data modes
    tx_packet_gen = b'\x02'
    rotation = b'\x03'
    fft_result = b'\x04'
    power_calc = b'\x05'
    spec_to_x_spec = b'\x06' 
    spec_result = b'\x07'
    X_Spec_Real_Results = b'\x0C'
    X_Spec_Imaginary_Results = b'\x0F'
    Real_RAM_port_A = b'\x0A'
    Real_RAM_port_B = b'\x0B'
    Imaginary_RAM_port_A = b'\x0D'
    Imaginary_RAM_port_B = b'\x0E'
    CCSDS_packets = b'\x08'# Changed again: b'\x00' # Previously '\x08'

    default_words = 10

    if readcon == 'all': #skip everything if Read All is chosen
        print('Read All')
        words = default_words #change number of 12byte words read
        vals = readAll(words,ser,outpath='HW-output/5-ch/read_all')
        return vals
        
    length,test_mode = read_header(ser)
    word_length = 12 #bytes

    if test_mode==tx_packet_gen:
        print("tx_packet_gen")
        word_length = 4 #bytes

    words = int(length/word_length)
    for i in range(num_read):
    #read in payload 
        if test_mode==tx_packet_gen:
            raise Exception("Packet Gen not yet supported")
        elif test_mode == rotation:
            print("rotation")
            vals = readRotate(words,ser,outpath)
        elif test_mode == fft_result:
            print("FFT Result")
            vals = readFFT(words,ser,outpath)
        elif test_mode == power_calc:
            print("Power Calculation")
            name = outpath + '_spectra' 
            vals = readPwr(words,ser,name)
        elif test_mode == spec_result:
            print("Spectral Result")
            vals = readSpec(words,ser,outpath)
        elif test_mode == X_Spec_Real_Results:
            print("Real Cross-Spectral Result")
            name = outpath + '_xpec_re'
            vals = readXSpec(words,ser,name)
        elif test_mode == X_Spec_Imaginary_Results:
            print("Imaginary Cross-Spectral Result")
            name = outpath + '_xpec_im'
            vals = readXSpec(words,ser,name)
        elif test_mode == Real_RAM_port_A:
            print("Real Ram Port A")
            name = outpath + '_re_RAM_A'
            vals = readRAM(words,ser,name)
        elif test_mode == Real_RAM_port_B:
            print("Real Ram Port B")
            name = outpath + '_re_RAM_B'
            vals = readRAM(words,ser,name)
        elif test_mode == Imaginary_RAM_port_A:
            print("Imaginary Ram Port A")
            name = outpath + '_im_RAM_A'
            vals = readRAM(words,ser,name)
        elif test_mode == Imaginary_RAM_port_B:
            print("Imaginary Ram Port B")
            name = outpath + '_im_RAM_B'
            vals = readRAM(words,ser,name)
        elif test_mode == spec_to_x_spec:
            print("SPEC to X-SPEC I/F")
            name = outpath+ 'spec_to_xspec_IF'
            vals = readIF(words,ser,name)
        elif test_mode == CCSDS_packets:
            print("Printing entire thing")
            # now = datetime.now()
            # date_time = now.strftime("_%m%d%Y_%H%M%S")
            date_time = outpath[-16:]
            outpath='HW-output/5-ch/dtest_10/read_all'
            name = outpath+ 'CCSDS_pkt' + date_time + '_' + freq0[0:3] + freq1[0:3] + freq2[0:3] + freq3[0:3] + freq4[0:3]
            file = open(name +'.txt','w')
            if time_CCSDS == True:
                print("Timing the Packets")
                #file1 = open(name + '_spectra' + '.txt','w')
                #spectra_cnt = -1
                spectra_vals = np.zeros((words,5))
                #j=0
                for i in range(13000): # originally, 130000
                    val = int.from_bytes(ser.read(2), 'big') # Create func that reads from port - create buffer to store and throws serial bytes in - 
                    hex_val = format(np.int16(val) & 0xffff, '04X')
                    match str(hex_val):
                        case "BA11" | "FC1D" | "9BDC" | "CCCC":
                            file.write(str(hex_val))
                            file.write("\n")
                        case _:
                            file.write(str(hex_val))
                            file.write("  ")
                    # file.write(str(hex_val))
                    #file.write(ser.read(2))
                file.close()
                # Printing spectra into seperate file
                # file1.close()
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
                else:
                    print("Mention Byte Type?")
            vals = 0
        else:
            print("Unexpected Test Mode - Forcing ReadAll")
            words=default_words
            vals = readAll(words,ser,outpath='HW-output/5-ch/read_all')
    return vals


def readIF(words, ser, outpath):
    vals = np.zeros((words,6))
    Last_mask = b'\x40'
    End_mask = b'\x20'
    Start_mask = b'\x10'
    for i in range(words):
        Last = 0 
        End = 0 
        Start = 0

        BinID = int.from_bytes(ser.read(2),'big',signed=False)
        boolopts = ser.read(1)
        dump = ser.read(1)
        rFFT = int.from_bytes(ser.read(4),'big',signed=True)
        iFFT = int.from_bytes(ser.read(4),'big',signed=True)

        if bytes([boolopts[0] & Last_mask[0]]) == Last_mask:
            Last = 1
        if bytes([boolopts[0] & End_mask[0]])== End_mask:
            End = 1
        if bytes([boolopts[0] & Start_mask[0]]) == Start_mask:
            Start = 1
        
        vals[i][0] = BinID
        vals[i][1] = Last
        vals[i][2] = End
        vals[i][3] = Start
        vals[i][4] = rFFT
        vals[i][5] = iFFT
    save_IF(vals,outpath,'both')
    return vals



def readRAM(words, ser, outpath):
    vals = np.zeros((words,3))
    
    address_mask = b'\x03\xFF'
    
    for i in range(words):
        OpCode = int.from_bytes(ser.read(1), 'big', signed=False)
        options = ser.read(2)
        dump = ser.read(1)
        dataread = ser.read(8)
        Data = int.from_bytes(dataread,'big',signed=True)

        Address = andbytes(options,address_mask)
        
        vals[i][0] = OpCode
        vals[i][1] = int.from_bytes(Address,'big',signed=False)
        vals[i][2] = Data
    save_ram(vals,outpath,'hex')
    return vals

def readRotate(words,ser,outpath):
    vals = np.zeros((words,6))
    for i in range(words):
        adc3_r = int.from_bytes(ser.read(2), 'big')
        adc2_r = int.from_bytes(ser.read(2), 'big')
        adc1_r = int.from_bytes(ser.read(2),'big')
        adc3 = int.from_bytes(ser.read(2), 'big')
        adc2 = int.from_bytes(ser.read(2), 'big')
        adc1 = int.from_bytes(ser.read(2), 'big')
        if i==1000:
            print("Test Point")
        vals[i][0] = adc3_r
        vals[i][1] = adc2_r
        vals[i][2] = adc1_r
        vals[i][3] = adc3
        vals[i][4] = adc2
        vals[i][5] = adc1
    save_rotate(vals,outpath+'ADCLoopback','both')
    return vals


def readFFT(words,ser,outpath):
    vals = np.zeros((words,3))
    for i in range(words):
        cur_bin = int.from_bytes(ser.read(2),'big')
        unused = ser.read(2)
        rFFT = int.from_bytes(ser.read(4),'big',signed=True)
        iFFT = int.from_bytes(ser.read(4),'big',signed=True)

        vals[i][0] = cur_bin
        vals[i][1] = rFFT
        vals[i][2] = iFFT
    save_FFT(vals,outpath+'_FFT',out_type='both')
    return vals

def readPwr(words,ser,outpath): #both with power and accumulated power
    vals = np.zeros((words,2),dtype=np.uint64)
    for i in range(words):
        cur_bin = int.from_bytes(ser.read(2),'big')
        unused = ser.read(2)
        pwr = int.from_bytes(ser.read(8),'big')

        vals[i][0] = cur_bin
        vals[i][1] = pwr
    save_power(vals,outpath,out_type='both')
    return vals

def readSpec(words,ser,outpath):
    vals = np.zeros((words,3),dtype=np.uint64)
    for i in range(words):
        cur_bin = int.from_bytes(ser.read(2),'big')
        v=ser.read(2)
        mask = b'\x0f\xff'#4 bits unused 
        comp_rst = andbytes(v,mask)
        comp_rst = int.from_bytes(comp_rst,'big')
        uncomp_rst = int.from_bytes(ser.read(8),'big')

        vals[i][0] = cur_bin
        vals[i][1] = comp_rst
        vals[i][2] = uncomp_rst
    save_spectra(vals,outpath + '_avg',out_type='both')
    return vals

def readXSpec(words,ser,outpath):
    vals = np.zeros((words,3),dtype=np.uint64)
    for i in range(words):
        neg = False
        cur_bin = int.from_bytes(ser.read(2),'big')
        v=ser.read(2)
        mask = b'\x0f\xff'#4 bits unused 
        comp_rst = andbytes(v,mask)
        comp_rst = int.from_bytes(comp_rst,'big') #uses sign-magnitude not two's compliment
        #if (comp_rst>2048): #2^11 is 2048 so we use this as our comparison 
            #comp_rst = 2048 - comp_rst 
            #neg = True
        uncomp_rst = int.from_bytes(ser.read(8),'big',signed=False) #uses sign-magnitude, not two's compliment
        #if (neg):
            #uncomp_rst = -uncomp_rst

        vals[i][0] = cur_bin
        vals[i][1] = comp_rst
        vals[i][2] = uncomp_rst
    save_xspectra(vals,outpath + '_avg',out_type='both')
    return vals

def readAll(words,ser,outpath): #basic read function, reads in two-byte intervals
    s1 = b'\x35'
    s2= b'\x2E'
    s3 = b'\xF8'
    s4 = b'\x53'
    vals = np.zeros((words,6),dtype=np.uint16)
    #vals = bytearray()
    for i in range(words):
            if i%1000==0:
                print("reading vals ", i)
            v0 = ser.read(2)
            vals[i][0] = int.from_bytes(v0,'big')
            if v0 == (s1+s2):
                v1 = ser.read(2)
                vals[i][1] = int.from_bytes(v1,'big')
                if v1 == (s3+s4):
                    low = 2
                    high = 4
                else:
                    low = 2
                    high = 6
            else:
                low = 1
                high = 6
            for j in range(low,high):
                v = ser.read(2)
                vals[i][j] = int.from_bytes(v,'big')
                
    saveall(vals,outpath + '_avg',out_type='both')
    return vals



def andbytes(abytes, bbytes):
    val = bytes([a & b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])
    return val