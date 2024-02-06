# # from readFPGA import read_FPGA_input, twos_complement_to_hex, twos_complement, proper_twos_complement
# import binascii 
# import numpy as np
# from datetime import datetime
# import pandas as pd

import logging
from threading import Thread
import time
# from sample_thread import thread_initialize, thread_function

global counter # 1 for running, 0 for end iteration

import logging
import threading
import time
import serial
import numpy as np
import queue

# # create a class containing buffer details and stack details... ughhh
class CCSDS_Pkt():
    def __init__(self):
        # Variables
        self.thread = None
        self.ser = None
        self.is_running = False
        self.buffer_pkt = queue.Queue()

    def Start(self):            
        # Start the Mainloop thread - use this to start and stop , save in a file and read
        self.thread = Thread(target=self.MainLoop, name='SerialChecker MainLoop')
        self.thread.daemon = True
        self.thread.start()
        time.sleep(10)
        print('MainLoop thread started')
        return
    
    def Stop(self):
        # Stop MainLoop
        self.is_running = False  
        # Have to give MainLoop time to stop
        time.sleep(1)

        # Kill MainLoop thread
        if self.thread is not None:
            self.thread.join(timeout=10)
            self.thread = None

        print("Waiting 1s before Restart...")
        time.sleep(1)
        return
    
    def MainLoop(self):

        self.is_running = True

        while self.is_running:
            if(self.buffer_pkt.qsize()<3000): # Around 2600 is one packet
                self.buffer_pkt.put("hi")
                
            self.JustPrintData()

            time.sleep(0.1)

    def JustPrintData(self):
        for i in range(200):
            print(self.buffer_pkt.get())

c = CCSDS_Pkt()
c.Start()
time.sleep(20)
c.MainLoop()
c.Stop()


# # End of class
# def thread_function(name):
#     global buffer_pkt
#     global counter
#     buffer_pkt = queue.Queue()
#     logging.info("Thread %s: starting", name)
#     while (counter==1):
#         if(buffer_pkt.qsize()<3000): # Around 2600 is one packet
#             buffer_pkt.put("hi")

#     logging.info("Thread %s: finishing", name)

# def thread_initialize():
#     global counter
#     counter =1
#     global buffer_pkt
#     global x
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")
#     logging.info("Main    : before creating thread")
#     x = threading.Thread(target=thread_function, args=(1,))
#     logging.info("Main    : before running thread")
#     x.start()

# def thread_stop():
#     global counter
#     global buffer_pkt
#     global x
#     logging.info("Main    : wait for the thread to finish")
#     x.join()
#     logging.info("Main    : all done")

# thread_initialize()

# for i in range(200):
#     global buffer_pkt
#     print(buffer_pkt.get())
# counter =0

# thread_stop()




















# first =""
# bytes = b'&\x02 B\x00BBBBB\x00BBBBBB\xc2\xef\xcb\xefK\n\x80g!cVBB\x1a\x02BBBBB\x02\x00B\x00\x02 BB\x00BB\x00BB\x00\x02 \x02 BB\x02BBBBBB\x02BB\x02\x00B\x00B\x00\x02\x00BBBB\x02\x00B\x00BBBB\x00B\x00\xdev\x02N\xfeF/BN'
# j=-1
# for i in bytes[2:]:
#     val = int.from_bytes(i, 'big')
#     hex_val = format(np.int16(val) & 0xffff, '04X')
#     print(hex_val)
#     print("")

# print("done")
# # theta = 270 * np.pi / 180
# # SCM_x00 = twos_complement_to_hex(-np.sin(theta))

# # #SCM_x00 = SCM_x00.encode('unicode_escape')
# # #SCM_x00 = r'{}'.format(SCM_x00)
# # #output = "7FFF".encode('unicode_escape')
# # text = binascii.unhexlify(SCM_x00)

# # to get timestamp
# # now = datetime.now()
# # date_time = now.strftime("%m%d%Y_%H%M%S")

# # theta = 45 * np.pi / 180 # First no rotation

# # print(twos_complement_to_hex(-1))
# # print(twos_complement_to_hex(1))
# # print(twos_complement_to_hex(-0.5))
# # print(twos_complement_to_hex(0.5))

# # df1 = pd.read_csv("D:\CANVAS_work\Canvas-Algorithm\Canvas_FPGA\HW-output\FPGA-60220713_high-high_5deg_03khz_0ADCLoopback_int.txt", sep="\t")
# # print(df1)

# # df2 = pd.read_csv("test_1.txt", sep="\t")
# # print(df2)

# # diff_3 = abs(df1.R3 - df2.R3)
# # diff_2 = abs(df1.R2 - df2.R2)
# # diff_1 = abs(df1.R1 - df2.R1)


# # df = pd.read_csv("D:\CANVAS_work\Canvas-Algorithm\Canvas_FPGA\Inputs\mid_amp_03khz.txt", names=['lines'])
# # for i in range(0,1000):
# #     print(twos_complement(str(df.lines[i]),16))

# import numpy as np
# import matplotlib.pyplot as plt
# import os
# import glob
# import math

# # from readFPGA import read_FPGA_input, read_INT_input, quick_compare, flatten, twos_complement
# # from readFPGA import read_FPGA_fft_debug, read_FPGA_input_lines

# # a = twos_complement_to_hex(-1)
# # # b = bytes(a,'utf-8')
# # print(b)

# # def twos_complement_dum(value):
# #     if value < 0:
# #         c_value = round(value)
# #         hex_value = hex(c_value)
# #         hex_value = hex_value.zfill(4)
# #         # Convert the absolute value to binary and remove the prefix '0b'
# #         binary_value = bin(abs(c_value))[2:]
# #         # Pad the binary value with zeros to make it 16 bits long
# #         binary_value = binary_value.zfill(16)
# #         # Invert all the bits in the binary value
# #         inverted_binary_value = ''.join(['1' if b == '0' else '0' for b in binary_value])
# #         # Convert the inverted binary value to an integer and add 1
# #         inverted_decimal_value = int(inverted_binary_value, 2) + 1
# #         # Convert the decimal value to hexadecimal format
# #         hex_value = hex(inverted_decimal_value)[2:]
# #         # Pad the hexadecimal value with zeros to make it 4 digits long
# #         hex_value = hex_value.zfill(4)
# #         # Add a minus sign to the hexadecimal value
# #         hex_value = hex_value

# #         # c_value = round(value * 32768)
# #         # # If the value is non-negative, just convert it to hexadecimal format
# #         # hex_value = hex(c_value)[2:]
# #         # # Pad the hexadecimal value with zeros to make it 4 digits long
# #         # hex_value = hex_value.zfill(4)
# #     else:
# #         c_value = round(value)
# #         # If the value is non-negative, just convert it to hexadecimal format
# #         hex_value = hex(c_value)[2:]
# #         # Pad the hexadecimal value with zeros to make it 4 digits long
# #         hex_value = hex_value.zfill(4)
# #     return hex_value

# # out_folder = 'HW-output'
# # date_time = '134902'
# # iterate=24        
# # df_v = pd.read_csv('Verification-24_06202023_134902.txt', sep="\t")
# # if not all(num<3 for num in df_v.R1_df):
# #     print("OVER THE LIMIT!!" * 10)
# # elif not all(num<3 for num in df_v.R2_df):
# #     print("OVER THE LIMIT!!" * 10)
# # elif not all(num<3 for num in df_v.R3_df):
# #     print("OVER THE LIMIT!!" * 10)
# # else:
# #     print("You're safe for now")


# # twos_complement_dum(5)

# # # def rotateSCM(fname):
# # #     x,y = read_FPGA_input_lines(fname, 16, 6, 0, 1)
# # #     z,u = read_FPGA_input_lines(fname, 16, 6, 2, 3)
# # #     v,w = read_FPGA_input_lines(fname, 16, 6, 4, 5)

# # #     Rm = np.array([[1,0,0],[0,1,0],[0,0,1]])

# # #     for i in range(len(x)-1):
# # #         xyz = np.array([x[i],y[i],z[i]])
# # #         uvw = np.matmul(xyz,Rm)
# # #         print(xyz, uvw, u[i],v[i],w[i])
    
# # # rotateSCM('FPGA/adc_in_rotate_out.txt')

# # # print("done")


# # twos_complement_to_hex(0.1)

# # matrix_first = np.array( [9, 30, 58] )
                        
# # # Checking with theta
# # theta1 = -50 * np.pi / 180
# # theta2 = 24 * np.pi / 180
# # theta3 = -153 * np.pi / 180

# # x_rot = np.array( [ [1,             0,              0], 
# #                                     [0, np.cos(theta1), -np.sin(theta1)], 
# #                                     [0, np.sin(theta1),  np.cos(theta1)] ] )

# # y_rot = np.array( [ [ np.cos(theta2),  0, np.sin(theta2)], 
# #                                     [             0,  1,             0], 
# #                                     [-np.sin(theta2),  0, np.cos(theta2)] ] )

# # z_rot       = np.array( [ [np.cos(theta3), -np.sin(theta3), 0], 
# #                                     [np.sin(theta3),  np.cos(theta3), 0], 
# #                                     [            0,              0, 1] ] )

# # z_rot_FPGA       = np.array( [ [np.cos(theta1), np.sin(theta1), 0], 
# #                                     [-np.sin(theta1),  np.cos(theta1), 0], 
# #                                     [            0,              0, 1] ] )

# # z_rot_360       = np.array( [ [np.cos(theta2), -np.sin(theta2), 0], 
# #                                     [np.sin(theta2),  np.cos(theta2), 0], 
# #                                     [            0,              0, 1] ] )

# # product1 = np.matmul(x_rot,y_rot)
# # product2 = np.matmul(product1,z_rot)
# # product3 = np.matmul(matrix_first,product2)

# # final_matrix1 = np.matmul(product1,y_rot)

# # multi_matrix = np.matmul(x_rot,y_rot)
# # final_matrix2 = np.matmul(matrix_first,multi_matrix)

# # # Checking with 360 - theta
# # theta3 = 180 - 25
# # theta4 = 180 - 43

# # x_rot2 = np.array( [ [1,             0,              0], 
# #                                     [0, np.cos(theta3), -np.sin(theta3)], 
# #                                     [0, np.sin(theta3),  np.cos(theta3)] ] )

# # y_rot2 = np.array( [ [ np.cos(theta4),  0, np.sin(theta4)], 
# #                                     [             0,  1,             0], 
# #                                     [-np.sin(theta4),  0, np.cos(theta4)] ] )

# # product3 = np.matmul(matrix_first,x_rot2)
# # final_matrix3 = np.matmul(product3,y_rot2)

# # multi_matrix2 = np.matmul(x_rot2,y_rot2)
# # final_matrix4 = np.matmul(matrix_first,multi_matrix2)

# # # Checking how multiplying data individually with matrix behaves
# # # It should only give a -ve answer, instead it gives different value

# # # it's not the opposite

# # # It might be 180 - theta

# # # print(product1)

# # print("done")

# # # a = twos_complement_to_hex(0)
# # # b = bytes(a,'utf-8')
# # # print(b)
# # # b = np.array([[int(a[0]),int(a[1])],[int(a[2]),int(a[3])]])
# # # print(b)
# # # print(b.tobytes)
# # # c = b.tobytes
# # SCM_x00 = binascii.unhexlify(twos_complement_to_hex(np.cos(theta)))
# # SCM_x01 = binascii.unhexlify(twos_complement_to_hex(-np.sin(theta)))
# # SCM_x02 = binascii.unhexlify(twos_complement_to_hex(0)) 
# # SCM_y10 = binascii.unhexlify(twos_complement_to_hex(np.sin(theta)))
# # SCM_y11 = binascii.unhexlify(twos_complement_to_hex(np.cos(theta)))
# # SCM_y12 = binascii.unhexlify(twos_complement_to_hex(0)) 
# # SCM_z20 = binascii.unhexlify(twos_complement_to_hex(0)) 
# # SCM_z21 = binascii.unhexlify(twos_complement_to_hex(0)) 
# # SCM_z22 = binascii.unhexlify(twos_complement_to_hex(1)) 
# # SCM_xoff = binascii.unhexlify(twos_complement_to_hex(0))
# # SCM_yoff = binascii.unhexlify(twos_complement_to_hex(0))
# # SCM_zoff = binascii.unhexlify(twos_complement_to_hex(0))

# # print("FPGA_matrix_sent")
# # print(SCM_x00)
# # print(SCM_x01)
# # print(SCM_x02)
# # print(SCM_y10)
# # print(SCM_y11)
# # print(SCM_y12)
# # print(SCM_z20)
# # print(SCM_z21)
# # print(SCM_z22)
# # print("\n")

# # print("done")
# # print(twos_complement_to_hex(-1))
# # print(twos_complement("8000",16))

# # print(twos_complement_to_hex(1))
# # print(twos_complement("7FFF",16))
# # print("done")



# # theta = 270 * np.pi / 180  # TEST 1: # Rotation matrix from x to y (90 deg about z, counter-clockwise)
# # SCM_x00 = binascii.unhexlify(twos_complement_to_hex(np.cos(theta)))
# # SCM_x01 = binascii.unhexlify(twos_complement_to_hex(-np.sin(theta)))
# # SCM_x02 = binascii.unhexlify(twos_complement_to_hex(0)) 
# # SCM_y10 = binascii.unhexlify(twos_complement_to_hex(np.sin(theta)))
# # SCM_y11 = binascii.unhexlify(twos_complement_to_hex(np.cos(theta)))
# # SCM_y12 = binascii.unhexlify(twos_complement_to_hex(0)) 
# # SCM_z20 = binascii.unhexlify(twos_complement_to_hex(0)) 
# # SCM_z21 = binascii.unhexlify(twos_complement_to_hex(0)) 
# # SCM_z22 = binascii.unhexlify(twos_complement_to_hex(1)) 
# # SCM_xoff = binascii.unhexlify(twos_complement_to_hex(0))
# # SCM_yoff = binascii.unhexlify(twos_complement_to_hex(0))
# # SCM_zoff = binascii.unhexlify(twos_complement_to_hex(0))

# # print("FPGA_matrix_sent")
# # print(SCM_x00)
# # print(SCM_x01)
# # print(SCM_x02)
# # print(SCM_y10)
# # print(SCM_y11)
# # print(SCM_y12)
# # print(SCM_z20)
# # print(SCM_z21)
# # print(SCM_z22)
# # print("\n")

# # theta         = 270 * np.pi / 180
# # x_to_y_matrix = np.array( [ [np.cos(theta), -np.sin(theta), 0], 
# #                             [np.sin(theta),  np.cos(theta), 0], 
# #                             [            0,              0, 1] ] )

# # SCM_x00 = binascii.unhexlify(twos_complement_to_hex(x_to_y_matrix[0][0]))
# # SCM_x01 = binascii.unhexlify(twos_complement_to_hex(x_to_y_matrix[0][1]))
# # SCM_x02 = binascii.unhexlify(twos_complement_to_hex(x_to_y_matrix[0][2]))
# # SCM_y10 = binascii.unhexlify(twos_complement_to_hex(x_to_y_matrix[1][0]))
# # SCM_y11 = binascii.unhexlify(twos_complement_to_hex(x_to_y_matrix[1][1]))
# # SCM_y12 = binascii.unhexlify(twos_complement_to_hex(x_to_y_matrix[1][2]))
# # SCM_z20 = binascii.unhexlify(twos_complement_to_hex(x_to_y_matrix[2][0]))
# # SCM_z21 = binascii.unhexlify(twos_complement_to_hex(x_to_y_matrix[2][1]))
# # SCM_z22 = binascii.unhexlify(twos_complement_to_hex(x_to_y_matrix[2][2]))

# # print("Model_result_matrix_sent")
# # print(SCM_x00)
# # print(SCM_x01)
# # print(SCM_x02)
# # print(SCM_y10)
# # print(SCM_y11)
# # print(SCM_y12)
# # print(SCM_z20)
# # print(SCM_z21)
# # print(SCM_z22)

# # print("done")



# # df = pd.read_csv('HW-output/5-ch/read_allCCSDS_pkt_07132023_114622' + '.txt')

# # print("Printing entire thing")
# #             now = datetime.now()
# #             date_time = now.strftime("_%m%d%Y_%H%M%S")
# #             outpath='HW-output/5-ch/read_all'
# #             name = outpath+ 'CCSDS_pkt' + date_time
# #             file = open(name +'.txt','w')

# #             file1 = open(name + '_spectra' + '.txt','w')
# #             spectra_cnt = -1
# #             spectra_vals = np.zeros((words,5))
# #             j=0
# #             for i in range(13000):
# #                 val = int.from_bytes(ser.read(2), 'big')
# #                 hex_val = format(np.int16(val) & 0xffff, '04X')
# #                 match str(hex_val):
# #                     case "BA5E":
# #                         file.write("\n")
# #                         file.write(str(hex_val))
# #                         val = int.from_bytes(ser.read(2), 'big')
# #                         hex_val = format(np.int16(val) & 0xffff, '04X')
# #                         file.write("  ")
# #                         file.write(str(hex_val))
# #                         file.write("\n")
# #                     case "1ACF":
# #                         file.write("\n")
# #                         file.write(str(hex_val))
# #                         val = int.from_bytes(ser.read(2), 'big')
# #                         hex_val = format(np.int16(val) & 0xffff, '04X')
# #                         file.write("  ")
# #                         file.write(str(hex_val))
# #                         file.write("\n")
# #                         for i in range(6):
# #                             val = int.from_bytes(ser.read(2), 'big')
# #                             hex_val = format(np.int16(val) & 0xffff, '04X')
# #                             file.write(str(hex_val))
# #                             file.write("  ")
# #                         file.write("\n")
# #                         j=0
# #                         spectra_cnt+=1
# #                     case _:
# #                         file.write(str(hex_val))
# #                         file.write("  ")
# #                         if spectra_cnt%3==0:
# #                             spectra_vals[j][spectra_cnt%3]= val
# #                             j+=1
# #                 #file.write(ser.read(2))
# #             file.close()
# #             # Printing spectra into seperate file
# #             file1.close()

# # header_spectra = ["0AB0",  "C000",  "0201",  "C0FF",  "EE02",  "9AA6"]
# # hex = header_spectra[0] + header_spectra[1] + header_spectra[2] + header_spectra[3] + header_spectra[4] + header_spectra[5]
# # # converts into binary
# # res = "{0:08b}".format(int(hex, 16))
# # # fills in 0s in the beginning to get 96 length
# # res = res.zfill(96)
# # # Splitting header
# # Pkt_Ver_num = res[0:3].zfill(4)         # Packet Version Number
# # Pkt_Ver_num_int = int(Pkt_Ver_num,2)
# # Pkt_Ver_num_hex = format(np.int16(Pkt_Ver_num_int) & 0xffff, '04X')

# # Pkt_Type = res[3].zfill(4)              # Packet Type
# # Pkt_Type_int = int(Pkt_Type,2)
# # Pkt_Type_hex = format(np.int16(Pkt_Type_int) & 0xffff, '04X')

# # Sec_Hdr_Flag = res[4].zfill(4)          # Secondary Header Flag
# # Sec_Hdr_Flag_int = int(Sec_Hdr_Flag,2)
# # Sec_Hdr_Flag_hex = format(np.int16(Sec_Hdr_Flag_int) & 0xffff, '04X')

# # App_id = res[5:16].zfill(12)            # App ID
# # App_id_int = int(App_id,2)
# # App_id_hex = format(np.int16(App_id_int) & 0xffff, '04X')

# # Seq_Flag = res[16:18].zfill(4)          # Sequence Flags
# # Seq_Flag_int = int(Seq_Flag,2)
# # Seq_Flag_hex = format(np.int16(Seq_Flag_int) & 0xffff, '04X')

# # Seq_Cnt = res[18:32].zfill(16)          # Sequence Count
# # Seq_Cnt_int = int(Seq_Cnt,2)
# # Seq_Cnt_hex = format(np.int16(Seq_Cnt_int) & 0xffff, '04X')

# # Pkt_Data_len = res[32:48].zfill(16)     # Packet Data Length
# # Pkt_Data_len_int = int(Pkt_Data_len,2)
# # Pkt_Data_len_hex = format(np.int16(Pkt_Data_len_int) & 0xffff, '04X')

# # Coarse_Time = res[48:80].zfill(32)      # Coarse Time
# # Coarse_Time_int = int(Coarse_Time,2)
# # Coarse_Time_hex = format(np.int16(Coarse_Time_int) & 0xffff, '04X')

# # Fine_Time = res[80:96].zfill(16)        # Fine Time
# # Fine_Time_int = int(Fine_Time,2)
# # Fine_Time_hex = format(np.int16(Fine_Time_int) & 0xffff, '04X')

# # file.write("Header:\n")
# # file.write("\nPacket Version Number: "+Pkt_Ver_num+" = "str(Pkt_Ver_num_int)+" = "+str(Pkt_Ver_num_hex))
# # file.write("\nPacket Type: "+Pkt_Type+" = "str(Pkt_Type_int)+" = "+str(Pkt_Type_hex))
# # file.write("\nSecondary Header Flag: "+Sec_Hdr_Flag+" = "str(Sec_Hdr_Flag_int)+" = "+str(Sec_Hdr_Flag_hex))
# # file.write("\nApp ID: "+App_id+" = "str(App_id_int)+" = "+str(App_id_hex))
# # file.write("\nSequence Flags: "+Seq_Flag+" = "str(Seq_Flag_int)+" = "+str(Seq_Flag_hex))
# # file.write("\nSequence Count: "+Seq_Cnt+" = "str(Seq_Cnt_int)+" = "+str(Seq_Cnt_hex))
# # file.write("\nPacket Data Length: "+Pkt_Data_len+" = "str(Pkt_Data_len_int)+" = "+str(Pkt_Data_len_hex))
# # file.write("\nCoarse Time: "+Coarse_Time+" = "str(Coarse_Time_int)+" = "+str(Coarse_Time_hex))
# # file.write("\nFine_Time: "+Fine_Time+" = "str(Fine_Time_int)+" = "+str(Fine_Time_hex))

# #print(hex)

# # print(res)




# print("done")