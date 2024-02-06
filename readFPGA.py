import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
#from readFPGA import proper_twos_complement,twos_complement
# python functions to read FPGA input files (in hex)

# ---------------------------- 2's comp (hex to int) ---------------------------------------------
def twos_complement(hexstr,b=16):
    value = int(hexstr,16) # hex is base 16
    if value & (1 << (b-1)):
        value -= 1 << b
    return value
# ------------------------------------------------------------------------------------

# ---------------------------- 2's comp (int to hex) ---------------------------------------------
def twos_complement_to_hex(value):
    # Converting value to be in terms of 32767 because -32768 to +32767 corresponds to -1 to +1 
    # value = value * 32767
    # c_value = round(value)

    # Check if the value is negative
    if value < 0:
        c_value = round(value * -32768)
        hex_value = hex(c_value)
        hex_value = hex_value.zfill(4)
        # Convert the absolute value to binary and remove the prefix '0b'
        binary_value = bin(abs(c_value))[2:]
        # Pad the binary value with zeros to make it 16 bits long
        binary_value = binary_value.zfill(16)
        # Invert all the bits in the binary value
        inverted_binary_value = ''.join(['1' if b == '0' else '0' for b in binary_value])
        # Convert the inverted binary value to an integer and add 1
        inverted_decimal_value = int(inverted_binary_value, 2) + 1
        # Convert the decimal value to hexadecimal format
        hex_value = hex(inverted_decimal_value)[2:]
        # Pad the hexadecimal value with zeros to make it 4 digits long
        hex_value = hex_value.zfill(4)
        # Add a minus sign to the hexadecimal value
        hex_value = hex_value

        # c_value = round(value * 32768)
        # # If the value is non-negative, just convert it to hexadecimal format
        # hex_value = hex(c_value)[2:]
        # # Pad the hexadecimal value with zeros to make it 4 digits long
        # hex_value = hex_value.zfill(4)
    else:
        c_value = round(value * 32767)
        # If the value is non-negative, just convert it to hexadecimal format
        hex_value = hex(c_value)[2:]
        # Pad the hexadecimal value with zeros to make it 4 digits long
        hex_value = hex_value.zfill(4)
    
    return hex_value

# ------------------------------------------------------------------------------------
def proper_twos_complement(value):
    if value < 0:
        c_value = round(value)
        hex_value = hex(c_value)
        hex_value = hex_value.zfill(4)
        # Convert the absolute value to binary and remove the prefix '0b'
        binary_value = bin(abs(c_value))[2:]
        # Pad the binary value with zeros to make it 16 bits long
        binary_value = binary_value.zfill(16)
        # Invert all the bits in the binary value
        inverted_binary_value = ''.join(['1' if b == '0' else '0' for b in binary_value])
        # Convert the inverted binary value to an integer and add 1
        inverted_decimal_value = int(inverted_binary_value, 2) + 1
        # Convert the decimal value to hexadecimal format
        hex_value = hex(inverted_decimal_value)[2:]
        # Pad the hexadecimal value with zeros to make it 4 digits long
        hex_value = hex_value.zfill(4)
        # Add a minus sign to the hexadecimal value
        hex_value = hex_value

        # c_value = round(value * 32768)
        # # If the value is non-negative, just convert it to hexadecimal format
        # hex_value = hex(c_value)[2:]
        # # Pad the hexadecimal value with zeros to make it 4 digits long
        # hex_value = hex_value.zfill(4)
    else:
        c_value = round(value)
        # If the value is non-negative, just convert it to hexadecimal format
        hex_value = hex(c_value)[2:]
        # Pad the hexadecimal value with zeros to make it 4 digits long
        hex_value = hex_value.zfill(4)
    return hex_value
#---------------------------- read spectra vals --------------------------------------
def read_spec_vals(spectra_vals,date_time,count):
    i=0
    j=0
    full_spectra_hex = []
    spectra_hex = []
    for j in range(len(spectra_vals[:])-1):
        top_val = spectra_vals[j]
        bottom_val = spectra_vals[j+1]
        if j%2==0:
            first_val = "0" + top_val[3]+top_val[0:2]
            second_val = "0" + bottom_val[0:2]+top_val[2]
        else:
            first_val = "0" + bottom_val[3]+top_val[2:4]
            second_val = "0" + bottom_val[2:4]+bottom_val[0]
        spectra_hex.append(first_val)
        spectra_hex.append(second_val)
    # full_spectra_hex.append(spectra_hex)

    spectra_hex = "".join([str(item) for item in spectra_hex])
    spectra_split = [spectra_hex[i:i+2] for i in range(0, len(spectra_hex), 2)]
    cnt = 0
    ch_spectra_hex=[]
    for ch in spectra_split:
        ch = ch.zfill(4)
        if cnt==101:
            full_spectra_hex.append(ch_spectra_hex)
            ch_spectra_hex = []
            cnt=0
        ch_spectra_hex.append(ch)
        cnt+=1

    # for i in range(len(spectra_vals[0])):
    #     spectra_hex = []
    #     for j in range(len(spectra_vals[:][:])-1):
    #         top_val = proper_twos_complement(spectra_vals[j][i])
    #         bottom_val = proper_twos_complement(spectra_vals[j+1][i])
    #         if j%2==0:
    #             first_val = "0" + top_val[3]+top_val[0:2]
    #             second_val = "0" + bottom_val[0:2]+top_val[2]
    #         else:
    #             first_val = "0" + bottom_val[3]+top_val[2:4]
    #             second_val = "0" + bottom_val[2:4]+bottom_val[0]
    #         spectra_hex.append(first_val)
    #         spectra_hex.append(second_val)
    #     full_spectra_hex.append(spectra_hex)

    # now = datetime.now()
    # date_time = now.strftime("_%m%d%Y_%H%M%S")
    outpath='HW-output/5-ch/read_all'        
    name = outpath+ 'CCSDS_pkt' + date_time
    file1 = open(name + '_spectra_hex_' + str(count) + '.txt','w')
    file1.write("(1)\t(2)\t(3)\t(4)\t(5)\n")
    for i in range(len(full_spectra_hex[0])):
        file1.write(str(full_spectra_hex[0][i])+"\t"+str(full_spectra_hex[1][i])+"\t"+str(full_spectra_hex[2][i])+"\t"+str(full_spectra_hex[3][i])+"\t"+str(full_spectra_hex[4][i])+"\n")
    file1.close()
    file2 = open(name + '_spectra_int_' + str(count) + '.txt','w')
    file2.write("(1)\t(2)\t(3)\t(4)\t(5)\n")
    for i in range(len(full_spectra_hex[0])):
        file2.write(str(twos_complement(full_spectra_hex[0][i],16))+"\t"+str(twos_complement(full_spectra_hex[1][i],16))+"\t"+str(twos_complement(full_spectra_hex[2][i],16))+"\t"+str(twos_complement(full_spectra_hex[3][i],16))+"\t"+str(twos_complement(full_spectra_hex[4][i],16))+"\n")
    file2.close()
    return 0
# Saved as hex and int files
#----------------------------- read x-spec values-------------------------------------
def read_xspec_vals(xspec_vals_a,xspec_vals_b,date_time,count):
    i=0
    j=0
    full_xspec_a_hex = []
    xspec_a_hex = []
    for j in range(len(xspec_vals_a[:])-1):
        top_val = xspec_vals_a[j]
        bottom_val = xspec_vals_a[j+1]
        if j%2==0:
            first_val = "0" + top_val[3]+top_val[0:2]
            second_val = "0" + bottom_val[0:2]+top_val[2]
        else:
            first_val = "0" + bottom_val[3]+top_val[2:4]
            second_val = "0" + bottom_val[2:4]+bottom_val[0]
        xspec_a_hex.append(first_val)
        xspec_a_hex.append(second_val)
    # full_spectra_hex.append(spectra_hex)

    xspec_a_hex = "".join([str(item) for item in xspec_a_hex])
    xspec_a_split = [xspec_a_hex[i:i+2] for i in range(0, len(xspec_a_hex), 2)]
    cnt = 0
    ch_xspec_hex=[]
    for ch in xspec_a_split:
        ch = ch.zfill(4)
        if cnt==101:
            full_xspec_a_hex.append(ch_xspec_hex)
            ch_xspec_hex = []
            cnt=0
        ch_xspec_hex.append(ch)
        cnt+=1

    #For B vals
    full_xspec_b_hex = []
    xspec_b_hex = []
    for j in range(len(xspec_vals_b[:])-1):
        top_val = xspec_vals_b[j]
        bottom_val = xspec_vals_b[j+1]
        if j%2==0:
            first_val = "0" + top_val[3]+top_val[0:2]
            second_val = "0" + bottom_val[0:2]+top_val[2]
        else:
            first_val = "0" + bottom_val[3]+top_val[2:4]
            second_val = "0" + bottom_val[2:4]+bottom_val[0]
        xspec_b_hex.append(first_val)
        xspec_b_hex.append(second_val)
    # full_spectra_hex.append(spectra_hex)

    xspec_b_hex = "".join([str(item) for item in xspec_b_hex])
    xspec_b_split = [xspec_b_hex[i:i+2] for i in range(0, len(xspec_b_hex), 2)]
    cnt = 0
    ch_xspec_hex=[]
    for ch in xspec_b_split:
        ch.zfill(4)
        if cnt==101:
            full_xspec_b_hex.append(ch_xspec_hex)
            ch_xspec_hex = []
            cnt=0
        ch_xspec_hex.append(ch)
        cnt+=1

    # now = datetime.now()
    # date_time = now.strftime("_%m%d%Y_%H%M%S")
    outpath='HW-output/5-ch/read_all'        
    name = outpath+ 'CCSDS_pkt' + date_time
    file1 = open(name + '_xspec_hex_' + str(count) + '.txt','w')
    file1.write("(A1)\t(A2)\t(A3)\t(A4)\t(A5)\t(A6)\t(A7)\t(A8)\t(A9)\t(A10)\t\t(B1)\t(B2)\t(B3)\t(B4)\t(B5)\t(B6)\t(B7)\t(B8)\t(B9)\t(B10)\n")
    for i in range(len(full_xspec_a_hex[0])):
        file1.write(str(full_xspec_a_hex[0][i])+"\t"+str(full_xspec_a_hex[1][i])+"\t"+str(full_xspec_a_hex[2][i])+"\t"+str(full_xspec_a_hex[3][i])+"\t"+str(full_xspec_a_hex[4][i])+"\t"+str(full_xspec_a_hex[5][i])+"\t"+str(full_xspec_a_hex[6][i])+"\t"+str(full_xspec_a_hex[7][i])+"\t"+str(full_xspec_a_hex[8][i])+"\t"+str(full_xspec_a_hex[9][i])+"\t\t"+str(full_xspec_b_hex[0][i])+"\t"+str(full_xspec_b_hex[1][i])+"\t"+str(full_xspec_b_hex[2][i])+"\t"+str(full_xspec_b_hex[3][i])+"\t"+str(full_xspec_b_hex[4][i])+"\t"+str(full_xspec_b_hex[5][i])+"\t"+str(full_xspec_b_hex[6][i])+"\t"+str(full_xspec_b_hex[7][i])+"\t"+str(full_xspec_b_hex[8][i])+"\t"+str(full_xspec_b_hex[9][i])+"\n")
    file1.close()
    file2 = open(name + '_xspec_int_' + str(count) + '.txt','w')
    file2.write("(A1)\t(A2)\t(A3)\t(A4)\t(A5)\t(A6)\t(A7)\t(A8)\t(A9)\t(A10)\t\t(B1)\t(B2)\t(B3)\t(B4)\t(B5)\t(B6)\t(B7)\t(B8)\t(B9)\t(B10)\n")
    for i in range(len(full_xspec_a_hex[0])):
        file2.write(str(twos_complement(full_xspec_a_hex[0][i],16))+"\t"+str(twos_complement(full_xspec_a_hex[1][i],16))+"\t"+str(twos_complement(full_xspec_a_hex[2][i],16))+"\t"+str(twos_complement(full_xspec_a_hex[3][i],16))+"\t"+str(twos_complement(full_xspec_a_hex[4][i],16))+"\t"+str(twos_complement(full_xspec_a_hex[5][i],16))+"\t"+str(twos_complement(full_xspec_a_hex[6][i],16))+"\t"+str(twos_complement(full_xspec_a_hex[7][i],16))+"\t"+str(twos_complement(full_xspec_a_hex[8][i],16))+"\t"+str(twos_complement(full_xspec_a_hex[9][i],16))+"\t\t"+str(twos_complement(full_xspec_b_hex[0][i],16))+"\t"+str(twos_complement(full_xspec_b_hex[1][i],16))+"\t"+str(twos_complement(full_xspec_b_hex[2][i],16))+"\t"+str(twos_complement(full_xspec_b_hex[3][i],16))+"\t"+str(twos_complement(full_xspec_b_hex[4][i],16))+"\t"+str(twos_complement(full_xspec_b_hex[5][i],16))+"\t"+str(twos_complement(full_xspec_b_hex[6][i],16))+"\t"+str(twos_complement(full_xspec_b_hex[7][i],16))+"\t"+str(twos_complement(full_xspec_b_hex[8][i],16))+"\t"+str(twos_complement(full_xspec_b_hex[9][i],16))+"\n")
    file2.close()
    return 0
# Saved as hex and int files
# ---------------------------- read header file --------------------------------------
def read_header_CCSDS(file, header_spectra):
    hex = "".join([str(item) for item in header_spectra])
    # converts into binary
    res = "{0:08b}".format(int(hex, 16))
    # fills in 0s in the beginning to get 96 length
    res = res.zfill(96)
    # Splitting header
    Pkt_Ver_num = res[0:3].zfill(4)         # Packet Version Number
    Pkt_Ver_num_int = int(Pkt_Ver_num,2)
    Pkt_Ver_num_hex = format(np.int16(Pkt_Ver_num_int) & 0xffff, '04X')

    Pkt_Type = res[3].zfill(4)              # Packet Type
    Pkt_Type_int = int(Pkt_Type,2)
    Pkt_Type_hex = format(np.int16(Pkt_Type_int) & 0xffff, '04X')

    Sec_Hdr_Flag = res[4].zfill(4)          # Secondary Header Flag
    Sec_Hdr_Flag_int = int(Sec_Hdr_Flag,2)
    Sec_Hdr_Flag_hex = format(np.int16(Sec_Hdr_Flag_int) & 0xffff, '04X')

    App_id = res[5:16].zfill(12)            # App ID
    App_id_int = int(App_id,2)
    App_id_hex = format(np.int16(App_id_int) & 0xffff, '04X')

    Seq_Flag = res[16:18].zfill(4)          # Sequence Flags
    Seq_Flag_int = int(Seq_Flag,2)
    Seq_Flag_hex = format(np.int16(Seq_Flag_int) & 0xffff, '04X')

    Seq_Cnt = res[18:32].zfill(16)          # Sequence Count
    Seq_Cnt_int = int(Seq_Cnt,2)
    Seq_Cnt_hex = format(np.int16(Seq_Cnt_int) & 0xffff, '04X')

    Pkt_Data_len = res[32:48].zfill(16)     # Packet Data Length
    Pkt_Data_len_int = int(Pkt_Data_len,2)
    Pkt_Data_len_hex = format(np.int16(Pkt_Data_len_int) & 0xffff, '04X')

    Coarse_Time = res[48:80].zfill(32)      # Coarse Time
    Coarse_Time_int = int(Coarse_Time,2)
    #Coarse_Time_hex = format(np.int64(Coarse_Time_int) & 0xffff, '04X')

    Fine_Time = res[80:96].zfill(16)        # Fine Time
    Fine_Time_int = int(Fine_Time,2)
    Fine_Time_hex = format(np.int16(Fine_Time_int) & 0xffff, '04X')

    file.write("\nHeader:")
    file.write("\nPacket Version Number: "+Pkt_Ver_num + " = " + str(Pkt_Ver_num_int) + " = " + str(Pkt_Ver_num_hex))
    file.write("\nPacket Type: "+Pkt_Type+" = "+str(Pkt_Type_int)+" = "+str(Pkt_Type_hex))
    file.write("\nSecondary Header Flag: "+Sec_Hdr_Flag+" = "+str(Sec_Hdr_Flag_int)+" = "+str(Sec_Hdr_Flag_hex))
    file.write("\nApp ID: "+App_id+" = "+str(App_id_int)+" = "+str(App_id_hex))
    file.write("\nSequence Flags: "+Seq_Flag+" = "+str(Seq_Flag_int)+" = "+str(Seq_Flag_hex))
    file.write("\nSequence Count: "+Seq_Cnt+" = "+str(Seq_Cnt_int)+" = "+str(Seq_Cnt_hex))
    file.write("\nPacket Data Length: "+Pkt_Data_len+" = "+str(Pkt_Data_len_int)+" = "+str(Pkt_Data_len_hex))
    file.write("\nCoarse Time: "+Coarse_Time+" = "+str(Coarse_Time_int))#+str(Coarse_Time_hex))
    file.write("\nFine_Time: "+Fine_Time+" = "+str(Fine_Time_int)+" = "+str(Fine_Time_hex)+"\n\n")

    return 0


# ---------------------------- read FPGA input ---------------------------------------
def read_FPGA_input(file, b=16, signed=True, show_plots=False):
    f = open(file, 'r')
    datalines = [line for line in f]
    if signed:
        fpga_in_data = [twos_complement(p,b) for p in datalines]
    else:
        fpga_in_data = [int(p,16) for p in datalines]

    f.close()

    if show_plots:
        plt.plot(fpga_in_data[:1024],'-')
        plt.show()
        plt.title(file)
        plt.close()

    print('reading FPGA input \n file length is: ', len(fpga_in_data))

    return fpga_in_data


# ------------------------------------------------------------------------------------

def read_FPGA_cmprs(file, line_n):
    f = open(file, 'r')
    datalines = [line for line in f]
    comp = datalines[line_n:]
    f.close()

    sign_mask = b'\x08\x00'
    mag_mask = b'\x07\xFF'

    comp_val=[]
    for i in range(len(comp)):
        hex_comp = bytes.fromhex(comp[i])
        sign = andbytes(hex_comp,sign_mask)
        comp_mag = int.from_bytes(andbytes(hex_comp,mag_mask),'big')
        if int.from_bytes(sign,'big')>0:
            comp_val.append(-comp_mag)
        else:
            comp_val.append(comp_mag)
            
    d1 = comp_val

    return d1

# ---------------------------- read INT input ---------------------------------------
def read_INT_input(file, show_plots=False):
    f = open(file, 'r')
    data = [int(line.strip('\n')) for line in f]
    f.close()

    if show_plots:
        plt.plot(data[:1024],'-')
        plt.show()
        plt.title(file)
        plt.close()

    print('reading FPGA input \n file length is: ', len(data))

    return data
# ------------------------------------------------------------------------------------

# ---------------------------- quick compare ---------------------------------------
def quick_compare(py_array, fp_array, vals, show_plots=False):
    py_array = np.array(py_array)
    fp_array = np.array(fp_array)

    diff = (py_array[:vals] - fp_array[:vals]) / py_array[:vals]
    
    if show_plots:
        plt.plot(diff)
        plt.show()
        plt.close()

    return diff
# ------------------------------------------------------------------------------------

def flatten(mylist):
    flat_list = [item for sublist in mylist for item in sublist]
    return flat_list

# ------------------------------------------------------------------------------------

def read_FPGA_fft_debug(file, b, signed):
    f = open(file, 'r')
    datalines = [line for line in f]
    
    fpga_data = {}
    save_di = 0
    count = 0
    for di,dl in enumerate(datalines):
        if dl[0] == 'F':
            if dl == 'FFT Stage 9 Input Samples\n' and di!=0:
                data_len = 256
            else:
                data_len = 258
            dl = dl.strip('\n')
            fpga_data[dl+str(count//10)] = {}
            headers = datalines[di+1].split()
            cd = datalines[di+2:di+data_len]
            cd_split = [c.split() for c in cd]
            cd_flat = flatten(cd_split)
            for hi, h in enumerate(headers):
                if h == 'WR':
                    h = 'WR(COS)'
                    headers.pop(8)
                that_data = [cd_flat[k] for k in range(hi,len(cd_flat),len(headers))]
                fpga_data[dl+str(count//10)][h] = that_data
            count += 1 

    print(fpga_data['FFT Stage 8 Input Samples23']['TF_INDEX'])
    
    if signed:
        fpga_in_data = [twos_complement(p,b) for p in datalines]
    else:
        fpga_in_data = [int(p,16) for p in datalines]

    f.close()

    if show_plots:
        plt.plot(fpga_in_data[:1024],'-')
        plt.show()
        plt.title(file)
        plt.close()

    print('reading FPGA input \n file length is: ', len(fpga_in_data))

    return fpga_in_data
    
# ------------------------------------------------------------------------------------ 

# ------------------------------------------------------------------------------------ 

def read_FPGA_input_lines(file, b, line_n, x, y, signed=True, show_plots=False):
    f = open(file, 'r')
    datalines = [line.split() for line in f]
    datalines = flatten(datalines)
    datalines = datalines[line_n:]
    if signed:
        fpga_in_data = [twos_complement(p,b) for p in datalines]
    else:
        fpga_in_data = [int(p,16) for p in datalines]

    f.close()

    if show_plots:
        plt.plot(fpga_in_data[:1024],'-')
        plt.show()
        plt.title(file)
        plt.close()

    print('reading FPGA input \n file length is: ', len(fpga_in_data))

    d1 = [fpga_in_data[n] for n in range(x,len(fpga_in_data),line_n)]
    d2 = [fpga_in_data[n] for n in range(y,len(fpga_in_data),line_n)]

    return d1, d2

def read_FPGA_xspectra(file, line_n):
    f = open(file, 'r')
    datalines = [line.split() for line in f]
    sbin=[];comp=[];uncomp=[]
    for r in datalines:
        sbin.append(r[0])
        comp.append(r[1])
        uncomp.append(r[2])
    sbin = sbin[line_n:]
    comp = comp[line_n:]
    uncomp = uncomp[line_n:]
    f.close()

    sign_mask = b'\x08\x00'
    mag_mask = b'\x07\xFF'

    comp_val=[]
    uncomp_val=[]
    for i in range(len(comp)):
        hex_comp = bytes.fromhex(comp[i])
        sign = andbytes(hex_comp,sign_mask)
        comp_mag = int.from_bytes(andbytes(hex_comp,mag_mask),'big')
        if int.from_bytes(sign,'big')>0:
            comp_val.append(-comp_mag)
            uncomp_val.append(-int(uncomp[i],16))
        else:
            comp_val.append(comp_mag)
            uncomp_val.append(int(uncomp[i],16))


    d1 = comp_val
    d2 = uncomp_val

    return d1, d2

# ------------------------------------------------------------------------------------ 

def read_FPGA_fft(file,b=32,header=True,signed=True):
    f = open(file,'r')
    re = []
    im = []
    datalines = [line.split() for line in f]
    if header:
        datalines = datalines[1:]
    for i in datalines:
        re.append(i[1])
        im.append(i[2])
    real = [twos_complement(p,b) for p in re]
    imaginary = [twos_complement(p,b) for p in im]
    return real,imaginary

def andbytes(abytes, bbytes):
    val = bytes([a & b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])
    return val
