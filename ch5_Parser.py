#####  CCSDS Packet Parser  #####
##### By Adhitya Sripennem  #####
# Disclaimer: to run this file, the CCSDS file should be having \n after every packet | Kindly make changes for a regular packet with no \n 
# Sample input file will be attached

#####   IMPORTED LIBRARIES  #####
import numpy as np
from datetime import datetime

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
    i=0
    # j=0
    # full_spectra_hex = []
    # spectra_hex = []
    spectra_vals = spectra_vals.strip()
    spectra_vals = spectra_vals.replace(" ","")

    ch1 = spectra_vals[0:201]
    ch2 = spectra_vals[202:403]
    ch3 = spectra_vals[404:605]
    ch4 = spectra_vals[606:807]
    ch5 = spectra_vals[808:1009]

    spectra_1 = [(ch1[i:i+3]) for i in range(0, len(ch1), 3)]
    spectra_2 = [(ch2[i:i+3]) for i in range(0, len(ch2), 3)]
    spectra_3 = [(ch3[i:i+3]) for i in range(0, len(ch3), 3)]
    spectra_4 = [(ch4[i:i+3]) for i in range(0, len(ch4), 3)]
    spectra_5 = [(ch5[i:i+3]) for i in range(0, len(ch5), 3)]

    # spectra_vals = spectra_vals.split("  ")
    # spectra_vals_split = []
    # for element in spectra_vals:
    #     spectra_vals_split.append(element[:2])
    #     spectra_vals_split.append(element[2:])

    # # spectra_vals_split_full = spectra_vals_split[:-3]
    # for k in range(5):
    #     spectra_vals_split = spectra_vals_split_full[101*k:101*(k+1)]

    #     # for j in range(0,len(spectra_vals_split)-3,3):
    #     #     top_val = spectra_vals_split[j]
    #     #     middle_val = spectra_vals_split[j+1]
    #     #     bottom_val = spectra_vals_split[j+2]

    #     #     first_val = "0" + middle_val[1:]+top_val
    #     #     second_val = "0" + bottom_val+middle_val[:1]

    #     #     spectra_hex.append(first_val)
    #     #     spectra_hex.append(second_val)

    #     j+=3
    #     top_val = spectra_vals_split[j]
    #     middle_val = spectra_vals_split[j+1]
    #     first_val = "0" + middle_val[1:]+top_val
    #     spectra_hex.append(first_val)
    #     # print(middle_val[:1])

    #     full_spectra_hex.append(spectra_hex)
    #     spectra_hex = []

    file.write("HEX\n(1)\t(2)\t(3)\t(4)\t(5)\n")
    for i in range(len(spectra_1)):
        file.write(str(spectra_1[i])+"\t"+str(spectra_2[i])+"\t"+str(spectra_3[i])+"\t"+str(spectra_4[i])+"\t"+str(spectra_5[i])+"\n")
    file.write("\n\nINT\n(1)\t(2)\t(3)\t(4)\t(5)\n")
    for i in range(len(spectra_1)):
        file.write(str(twos_complement(spectra_1[i],16))+"\t"+str(twos_complement(spectra_2[i],16))+"\t"+str(twos_complement(spectra_3[i],16))+"\t"+str(twos_complement(spectra_4[i],16))+"\t"+str(twos_complement(spectra_5[i],16))+"\n")
    return 0
# Saved as hex and int files
####################################################################################################
############################################## X - SPECTRA PARSER ######################################################
def read_xspectravals(file,xspec_vals,type='A'):
    i=0
    # full_xspec_hex = []
    # xspec_hex = []
    xspec_vals = xspec_vals.strip()
    xspec_vals = xspec_vals.replace(" ","")

    ch1  = xspec_vals[0:201]
    ch2  = xspec_vals[202:403]
    ch3  = xspec_vals[404:605]
    ch4  = xspec_vals[606:807]
    ch5  = xspec_vals[808:1009]
    ch6  = xspec_vals[1010:1211]
    ch7  = xspec_vals[1212:1413]
    ch8  = xspec_vals[1414:1615]
    ch9  = xspec_vals[1616:1817]
    ch10 = xspec_vals[1818:2019]

    xspectra_1  = [(ch1[i:i+3])  for i in range(0, len(ch1),  3)]
    xspectra_2  = [(ch2[i:i+3])  for i in range(0, len(ch2),  3)]
    xspectra_3  = [(ch3[i:i+3])  for i in range(0, len(ch3),  3)]
    xspectra_4  = [(ch4[i:i+3])  for i in range(0, len(ch4),  3)]
    xspectra_5  = [(ch5[i:i+3])  for i in range(0, len(ch5),  3)]
    xspectra_6  = [(ch6[i:i+3])  for i in range(0, len(ch6),  3)]
    xspectra_7  = [(ch7[i:i+3])  for i in range(0, len(ch7),  3)]
    xspectra_8  = [(ch8[i:i+3])  for i in range(0, len(ch8),  3)]
    xspectra_9  = [(ch9[i:i+3])  for i in range(0, len(ch9),  3)]
    xspectra_10 = [(ch10[i:i+3]) for i in range(0, len(ch10), 3)]

    # xspec_vals = xspec_vals.split("  ")
    # xspec_vals_split = []
    # for element in xspec_vals:
    #     xspec_vals_split.append(element[:2])
    #     xspec_vals_split.append(element[2:])

    # xspec_vals_split_full = xspec_vals_split[:-2]
    # for k in range(10):
    #     xspec_vals_split = xspec_vals_split_full[101*k:101*(k+1)]

    #     for j in range(0,len(xspec_vals_split)-3,3):
    #         top_val = xspec_vals_split[j]
    #         middle_val = xspec_vals_split[j+1]
    #         bottom_val = xspec_vals_split[j+2]

    #         first_val = "0" + middle_val[1:]+top_val
    #         second_val = "0" + bottom_val+middle_val[:1]

    #         xspec_hex.append(first_val)
    #         xspec_hex.append(second_val)

    #     j+=3
    #     top_val = xspec_vals_split[j]
    #     middle_val = xspec_vals_split[j+1]
    #     first_val = "0" + middle_val[1:]+top_val
    #     xspec_hex.append(first_val)
    #     # print(middle_val[:1])

    #     full_xspec_hex.append(xspec_hex)
    #     xspec_hex = []

    file.write("HEX\n("+type+"1)\t("+type+"2)\t("+type+"3)\t("+type+"4)\t("+type+"5)\t("+type+"6)\t("+type+"7)\t("+type+"8)\t("+type+"9)\t("+type+"10)\n")
    for i in range(len(xspectra_1)):
        file.write(str(xspectra_1[i])+"\t"+str(xspectra_2[i])+"\t"+str(xspectra_3[i])+"\t"+str(xspectra_4[i])+"\t"+str(xspectra_5[i])+"\t"+str(xspectra_6[i])+"\t"+str(xspectra_7[i])+"\t"+str(xspectra_8[i])+"\t"+str(xspectra_9[i])+"\t"+str(xspectra_10[i])+"\n")
    file.write("\n\nINT\n("+type+"1)\t("+type+"2)\t("+type+"3)\t("+type+"4)\t("+type+"5)\t("+type+"6)\t("+type+"7)\t("+type+"8)\t("+type+"9)\t("+type+"10)\n")
    for i in range(len(xspectra_1)):
        file.write(str(twos_complement(xspectra_1[i],16))+"\t"+str(twos_complement(xspectra_2[i],16))+"\t"+str(twos_complement(xspectra_3[i],16))+"\t"+str(twos_complement(xspectra_4[i],16))+"\t"+str(twos_complement(xspectra_5[i],16))+"\t"+str(twos_complement(xspectra_6[i],16))+"\t"+str(twos_complement(xspectra_7[i],16))+"\t"+str(twos_complement(xspectra_8[i],16))+"\t"+str(twos_complement(xspectra_9[i],16))+"\t"+str(twos_complement(xspectra_10[i],16))+"\n")
    return 0

    # file.close()
# Saved as hex and int files
####################################################################################################
############################################## MAIN CODE STARTS HERE ######################################################

# # Define Input and Output Location
# input_filename = "./HW-output/5-ch/5Ch_xspectra_read_allCCSDS_pkt_11202023_144910.txt"
# lines = open(input_filename).read().splitlines()
# cnt = 0
# now = datetime.now()
# date_time = now.strftime("_%m%d%Y_%H%M%S")
# outpath='HW-output/parse/5-ch/parse-'
# name = outpath+ 'CCSDS_pkt' + date_time

# # Looping till the end of the file - takes one line every iteration
# for pkt in lines:
#     # Checks for the Spectra header
#     if pkt[:4] == '0AB0':
#         print("Spectra")
#         cnt+=1
#         file_spec = open(name +'-SPECTRA_'+str(cnt)+'.txt','w')
#         spectra_header = pkt[:34]
#         spectra_vals = pkt[34:]
#         file_spec.write("SPECTRA "+str(cnt)+"\n")
#         read_headerCCSDS(file_spec, spectra_header)
#         try:
#             read_spectravals(file_spec, spectra_vals)
#         except Exception:
#             print("Incomplete")
#             pass
#         file_spec.close()
#     # Checks for the Cross-Spectra A header
#     elif pkt[:4] == '0AB4':
#         print("Cross Spectra A")
#         file_xspeca = open(name +'-XSPEC-A_'+str(cnt)+'.txt','w')
#         xspeca_header = pkt[:34]
#         xspeca_vals = pkt[34:]
#         file_xspeca.write("CROSS-SPECTRA A "+str(cnt)+"\n")
#         read_headerCCSDS(file_xspeca, xspeca_header)
#         try:
#             read_xspectravals(file_xspeca, xspeca_vals, 'A')
#         except Exception:
#             print("Incomplete")
#             pass
#         # try:
#         #     read_xspectravals(file_xspeca, xspeca_vals, 'A')
#         # except Exception:
#         #     print("Incomplete")
#         #     pass
#         file_xspeca.close()
#     # Checks for the Cross-Spectra B header
#     elif pkt[:4] == '0AB5':
#         print("Cross Spectra B")
#         file_xspecb = open(name +'-XSPEC-B_'+str(cnt)+'.txt','w')
#         xspecb_header = pkt[:34]
#         xspecb_vals = pkt[34:]
#         file_xspecb.write("CROSS-SPECTRA B "+str(cnt)+"\n")
#         read_headerCCSDS(file_xspecb, xspecb_header)
#         try:
#             read_xspectravals(file_xspecb, xspecb_vals, 'B')
#         except Exception:
#             print("Incomplete")
#             pass
#         file_xspecb.close()
#     # Checks for the Sync Pattern
#     elif pkt == '1ACF  FC1D':
#         print("Sync Pattern")
# # Prints done, cuz why not :)
# print("done")

