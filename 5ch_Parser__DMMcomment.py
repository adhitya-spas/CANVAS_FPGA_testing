#####  CCSDS Packet Parser  #####
##### By Adhitya Sripennem  #####
# Disclaimer: to run this file, the CCSDS file should be having \n after every packet | Kindly make changes for a regular packet with no \n 
# Sample input file will be attached

#####   IMPORTED LIBRARIES  #####
import numpy as np
from datetime import datetime

## Add something to plot with 
import matplotlib.pyplot as plt

##### REQUIRED FUNCTIONS #####
# twos_complement(hexstr,b) -> takes hexadecimal as input and returns corresponding integer value
# read_headerCCSDS(file, header) -> Takes first 34 characters and converts into binary to split them into headers
# read_spectravals(file, spectra_vals) -> Takes the file and spectra values to parse them
# read_xspectravals(file, xspec_vals) -> Takes the file and x-spectra values to parse them

############################################## 2s comp ######################################################
def twos_complement(hexstr,b):
    value = int(hexstr,16) # hex is base 16
    if value & (1 << (b-1)):
        value -= 1 << b
    return value
####################################################################################################
############################################## HEADER READER ######################################################
def read_headerCCSDS(file, header):
    hex = header.replace(" ","")
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
####################################################################################################
############################################## SPECTRA PARSER ######################################################
def read_spectravals(file,spectra_vals):

    ## Create indices 
    i=0
    j=0
    
    ## Create empty arrays 
    full_spectra_hex    = []
    spectra_hex         = []
    
    ## Remove white space, leading / trailing
    spectra_vals = spectra_vals.strip()

    ## Split into 4 nibble pieces 
    spectra_vals = spectra_vals.split("  ")
    
    for j in range(len(spectra_vals[:])-1):

        ## Top and bottom values (?)
        top_val    = spectra_vals[j]
        bottom_val = spectra_vals[j+1]

        ## What the hell? 
        
        astop

        if j%2==0:
            first_val = "0" + top_val[3]+top_val[0:2]
            second_val = "0" + bottom_val[0:2]+top_val[2]
        else:
            first_val = "0" + bottom_val[3]+top_val[2:4]
            second_val = "0" + bottom_val[2:4]+bottom_val[0]
        spectra_hex.append(first_val)
        spectra_hex.append(second_val)

    spectra_hex = "".join([str(item) for item in spectra_hex])
    spectra_split = [spectra_hex[i:i+4] for i in range(0, len(spectra_hex), 4)]
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

    file.write("HEX\n(1)\t(2)\t(3)\t(4)\t(5)\n")
    for i in range(len(full_spectra_hex[0])):
        file.write(str(full_spectra_hex[0][i])+"\t"+str(full_spectra_hex[1][i])+"\t"+str(full_spectra_hex[2][i])+"\t"+str(full_spectra_hex[3][i])+"\t"+str(full_spectra_hex[4][i])+"\n")
    file.write("\n\nINT\n(1)\t(2)\t(3)\t(4)\t(5)\n")
    for i in range(len(full_spectra_hex[0])):
        file.write(str(twos_complement(full_spectra_hex[0][i],16))+"\t"+str(twos_complement(full_spectra_hex[1][i],16))+"\t"+str(twos_complement(full_spectra_hex[2][i],16))+"\t"+str(twos_complement(full_spectra_hex[3][i],16))+"\t"+str(twos_complement(full_spectra_hex[4][i],16))+"\n")
    return 0
# Saved as hex and int files
####################################################################################################
############################################## X - SPECTRA PARSER ######################################################
def read_xspectravals(file,xspec_vals):
    i=0
    full_xspec_hex = []
    xspec_hex = []
    xspec_vals = xspec_vals.strip()
    xspec_vals = xspec_vals.split("  ")
    for j in range(len(xspec_vals[:])   -1):
        top_val = xspec_vals[j]
        bottom_val = xspec_vals[j+1]
        if j%2==0:
            first_val = "0" + top_val[3]+top_val[0:2]
            second_val = "0" + bottom_val[0:2]+top_val[2]
        else:
            first_val = "0" + bottom_val[3]+top_val[2:4]
            second_val = "0" + bottom_val[2:4]+bottom_val[0]
        xspec_hex.append(first_val)
        xspec_hex.append(second_val)
    # full_spectra_hex.append(spectra_hex)

    xspec_hex = "".join([str(item) for item in xspec_hex])
    xspec_split = [xspec_hex[i:i+4] for i in range(0, len(xspec_hex), 4)]
    cnt = 0
    ch_xspec_hex=[]
    for ch in range(10):
        ch_xspec_hex = xspec_split[0+(101*ch):101+(101*ch)]
        full_xspec_hex.append(ch_xspec_hex)
    # for ch in xspec_split:
    #     ch = ch.zfill(4)
    #     if cnt==101:
    #         full_xspec_hex.append(ch_xspec_hex)
    #         ch_xspec_hex = []
    #         cnt=0
    #     ch_xspec_hex.append(ch)
    #     cnt+=1


    # now = datetime.now()
    # date_time = now.strftime("_%m%d%Y_%H%M%S")
    # outpath='HW-output/5-ch/read_all'        
    # name = outpath+ 'CCSDS_pkt' + date_time
    # file1 = open(name + '_xspec_hex_' + str(count) + '.txt','w')
    file.write("HEX\n(A1)\t(A2)\t(A3)\t(A4)\t(A5)\t(A6)\t(A7)\t(A8)\t(A9)\t(A10)\n")
    for i in range(len(full_xspec_hex[0])):
        file.write(str(full_xspec_hex[0][i])+"\t"+str(full_xspec_hex[1][i])+"\t"+str(full_xspec_hex[2][i])+"\t"+str(full_xspec_hex[3][i])+"\t"+str(full_xspec_hex[4][i])+"\t"+str(full_xspec_hex[5][i])+"\t"+str(full_xspec_hex[6][i])+"\t"+str(full_xspec_hex[7][i])+"\t"+str(full_xspec_hex[8][i])+"\t"+str(full_xspec_hex[9][i])+"\n")
    file.write("\n\nINT\n(A1)\t(A2)\t(A3)\t(A4)\t(A5)\t(A6)\t(A7)\t(A8)\t(A9)\t(A10)\n")
    for i in range(len(full_xspec_hex[0])):
        file.write(str(twos_complement(full_xspec_hex[0][i],16))+"\t"+str(twos_complement(full_xspec_hex[1][i],16))+"\t"+str(twos_complement(full_xspec_hex[2][i],16))+"\t"+str(twos_complement(full_xspec_hex[3][i],16))+"\t"+str(twos_complement(full_xspec_hex[4][i],16))+"\t"+str(twos_complement(full_xspec_hex[5][i],16))+"\t"+str(twos_complement(full_xspec_hex[6][i],16))+"\t"+str(twos_complement(full_xspec_hex[7][i],16))+"\t"+str(twos_complement(full_xspec_hex[8][i],16))+"\t"+str(twos_complement(full_xspec_hex[9][i],16))+"\n")

    # file.close()
# Saved as hex and int files
####################################################################################################
############################################## MAIN CODE STARTS HERE ######################################################

# Define Input and Output Location

#input_filename = "./HW-output/5-ch/parse_check_1.txt"

## Define data path on DMM computer 
input_filename = './HW-output/5-ch/parse_check_same.txt'


lines       = open(input_filename).read().splitlines()
cnt         = 0
now         = datetime.now()
date_time   = now.strftime("_%m%d%Y_%H%M%S")
outpath     ='HW-output/parse/parse-'
name        = outpath+ 'CCSDS_pkt' + date_time

# Looping till the end of the file - takes one line every iteration
for pkt in lines:
    # Checks for the Spectra header
    if pkt[:4] == '0AB0':
        
                
        print("Spectra")
        cnt            +=1
        file_spec       = open(name +'-SPECTRA_'+str(cnt)+'.txt','w')
        spectra_header  = pkt[:34]
        spectra_vals    = pkt[34:]

        file_spec.write("SPECTRA "+str(cnt)+"\n")
        read_headerCCSDS(file_spec, spectra_header)

        try:
            read_spectravals(file_spec, spectra_vals)
        except Exception:
            print("Incomplete")
            pass

        file_spec.close()

        ##############################
        ## DMM write your own parser for debug 
        ##############################
        
        ## Remove white space, leading / trailing
        spectra_vals = spectra_vals.strip()
    
        ## Split into 4 nibble pieces 
        spectra_vals = spectra_vals.split("  ")
                        
        ## Create a list of bytes
        byte_list = []
        for j in range(len(spectra_vals[:])-1):
            atemp = spectra_vals[j][:2]
            btemp = spectra_vals[j][2:]
            byte_list.append(atemp)
            byte_list.append(btemp)
            
        ##############################
        ## Extract Spectra 1 (first 101 bytes)
        ##############################

        spec_1_bytes = byte_list[0:101]
        
        ## Pattern is three bytes chunks
        odd_bins_7_0    = spec_1_bytes[0::3] ## 34 elements
        split_bins      = spec_1_bytes[1::3] ## 34 elements 
        even_bins_11_4  = spec_1_bytes[2::3] ## 33 elements
        
        
        ## Check that there is padding (0's) where you expect it to be 
        ## That is, in the last split bins packet, first four bits
        atemp = split_bins[-1]
        print( atemp[0] )
        ## It is infact 8.  Not 0's at all.  
        ## That's not good 
        


        
        ## Break apart the split bins
        odd_bins_11_8   = []
        even_bins_7_0   = []
        for indx in range(len(split_bins)):
            local                = split_bins[indx]
            odd_bins_11_8.append(  local[1]  )
            even_bins_7_0.append(  local[0]  )

        ## create the 33 even bins, and 33 of the 34 odd bins
        odd_bins  = []
        even_bins = []
        for indx in range(len(even_bins_11_4)):
            odd_bins.append(odd_bins_11_8[indx] + odd_bins_7_0[indx])
            even_bins.append(even_bins_11_4[indx] + even_bins_7_0[indx])

        ## Create the 34th odd bin 
        odd_bins.append(odd_bins_11_8[-1] + odd_bins_7_0[-1])
        
        ## Interleave bins 
        all_bins = []
        ## First 66 bins
        for indx in range(len(even_bins_11_4)):
            all_bins.append(odd_bins[indx]) 
            all_bins.append(even_bins[indx]) 
        ## Add the 67th bin 
        all_bins.append(odd_bins[-1]) 
        
        ## Convert to decimals 
        all_bins_dec = []
        ## First 66 bins
        for indx in range(len(all_bins)):
            all_bins_dec.append( int('0' + all_bins[indx], 16) ) 
        
        ## Decompress (assume no compression)
        all_bins_dec = np.array(all_bins_dec)
        all_bins_dec = 2**(all_bins_dec / 12)
        
        ## Values_non_tx 
        values_non_tx = all_bins_dec[0:57]
        values_tx     = all_bins_dec[57:]
        
        ## Spectra 1 output 
        spectra_1_values_non_tx = values_non_tx*1
        spectra_1_values_yes_tx = values_tx*1
        

        ##############################
        ## Extract Spectra 2 (next 101 bytes)
        ##############################

        spec_2_bytes = byte_list[101:202]
                
        ## Pattern is three bytes chunks
        odd_bins_7_0    = spec_2_bytes[0::3] ## 34 elements
        split_bins      = spec_2_bytes[1::3] ## 34 elements 
        even_bins_11_4  = spec_2_bytes[2::3] ## 33 elements
        
        ## Break apart the split bins
        odd_bins_11_8   = []
        even_bins_7_0   = []
        for indx in range(len(split_bins)):
            local                = split_bins[indx]
            odd_bins_11_8.append(  local[1]  )
            even_bins_7_0.append(  local[0]  )

        ## create the 33 even bins, and 33 of the 34 odd bins
        odd_bins  = []
        even_bins = []
        for indx in range(len(even_bins_11_4)):
            odd_bins.append(odd_bins_11_8[indx] + odd_bins_7_0[indx])
            even_bins.append(even_bins_11_4[indx] + even_bins_7_0[indx])

        ## Create the 34th odd bin 
        odd_bins.append(odd_bins_11_8[-1] + odd_bins_7_0[-1])
        
        ## Interleave bins 
        all_bins = []
        ## First 66 bins
        for indx in range(len(even_bins_11_4)):
            all_bins.append(odd_bins[indx]) 
            all_bins.append(even_bins[indx]) 
        ## Add the 67th bin 
        all_bins.append(odd_bins[-1]) 
        
        ## Convert to decimals 
        all_bins_dec = []
        ## First 66 bins
        for indx in range(len(all_bins)):
            all_bins_dec.append( int('0' + all_bins[indx], 16) ) 
        
        ## Decompress (assume no compression)
        all_bins_dec = np.array(all_bins_dec)
        all_bins_dec = 2**(all_bins_dec / 12)
        
        ## Values_non_tx 
        values_non_tx = all_bins_dec[0:57]
        values_tx     = all_bins_dec[57:]
        
        ## Spectra 1 output 
        spectra_2_values_non_tx = values_non_tx*1
        spectra_2_values_yes_tx = values_tx*1
        
        ######### 
        ## Diagnostic plots 
        ######### 

        ## 57 non-transmitter bins 
        non_transmitter_freq = [256.0, 384.0, 512.0, 640.0, 768.0, 896.0, 1024.0, 1152.0, 1280.0,
                               1408.0, 1536.0, 1664.0, 1792.0, 1920.0, 2048.0, 2176.0, 2304.0, 2432.0,
                               2624.0, 2880.0, 3136.0, 3392.0, 3648.0, 3904.0, 4160.0, 4416.0, 4672.0,
                               4928.0, 5312.0, 5824.0, 6336.0, 6848.0, 7360.0, 7872.0, 8384.0, 8896.0,
                               9408.0, 10176.0, 11200.0, 12224.0, 13248.0, 14272.0, 15296.0, 16320.0,
                               17344.0, 18368.0, 19392.0, 20928.0, 22976.0, 25024.0, 27072.0, 29120.0,
                               31168.0, 33216.0, 35264.0, 37312.0, 40384.0]
        
        non_transmitter_freq = np.array(non_transmitter_freq)


        ## 10 x transmitters (lower bin edge)
        transmitter_freq = [18240.0, 19648.0, 21312.0, 22080.0, 23232.0, 23872.0, 24640.0, 25152.0, 37440.0, 40640.0]
        transmitter_freq = np.array(transmitter_freq)


        ## Plot to get an idea 
        plt.scatter(non_transmitter_freq, spectra_1_values_non_tx, color = 'blue', label = 'Pow Pkt 2 Spec 1')
        plt.scatter(non_transmitter_freq, spectra_2_values_non_tx, color = 'orange', label = 'Pow Pkt 2 Spec 2')
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Freq (no Tx bins)')
        plt.ylabel('Uncompressed amplitudes')
        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)






        
        
        astop        
        
        
        for j in range(len(spectra_vals[:])-1):
    
            ## Top and bottom values (?)
            top_val    = spectra_vals[j]
            bottom_val = spectra_vals[j+1]
    
            ## What the hell? 
            
            astop
    
            if j%2==0:
                first_val = "0" + top_val[3]+top_val[0:2]
                second_val = "0" + bottom_val[0:2]+top_val[2]
            else:
                first_val = "0" + bottom_val[3]+top_val[2:4]
                second_val = "0" + bottom_val[2:4]+bottom_val[0]
            spectra_hex.append(first_val)
            spectra_hex.append(second_val)
    
        spectra_hex = "".join([str(item) for item in spectra_hex])
        spectra_split = [spectra_hex[i:i+4] for i in range(0, len(spectra_hex), 4)]
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
        
        
        astop





    # Checks for the Cross-Spectra A header
    elif pkt[:4] == '0AB4':
        print("Cross Spectra A")
        file_xspeca = open(name +'-XSPEC-A_'+str(cnt)+'.txt','w')
        xspeca_header = pkt[:34]
        xspeca_vals = pkt[34:]
        file_xspeca.write("CROSS-SPECTRA A "+str(cnt)+"\n")
        read_headerCCSDS(file_xspeca, xspeca_header)
        try:
            read_xspectravals(file_xspeca, xspeca_vals)
        except Exception:
            print("Incomplete")
            pass
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
            read_xspectravals(file_xspecb, xspecb_vals)
        except Exception:
            print("Incomplete")
            pass
        file_xspecb.close()
    # Checks for the Sync Pattern
    elif pkt == '1ACF  FC1D':
        print("Sync Pattern")
# Prints done, cuz why not :)
print("done")

