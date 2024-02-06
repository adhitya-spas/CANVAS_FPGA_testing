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
from readFPGA import read_FPGA_input, twos_complement_to_hex
import matplotlib.pyplot as plt
import binascii
from datetime import datetime
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def arrow3d(ax, length=1, width=0.05, head=0.2, headwidth=2,
                theta_x=0, theta_y=0, theta_z=0, offset=(0,0,0), **kw):
    w = width
    h = head
    hw = headwidth
    theta_x = np.deg2rad(theta_x)
    theta_z = np.deg2rad(theta_z)

    a = [[0,0],[w,0],[w,(1-h)*length],[hw*w,(1-h)*length],[0,length]]
    a = np.array(a)

    r, theta = np.meshgrid(a[:,0], np.linspace(0,2*np.pi,30))
    z = np.tile(a[:,1],r.shape[0]).reshape(r.shape)
    x = r*np.sin(theta)
    y = r*np.cos(theta)

    rot_x = np.array([[1,0,0],[0,np.cos(theta_x),-np.sin(theta_x) ],
                      [0,np.sin(theta_x) ,np.cos(theta_x) ]])
    rot_y = np.array([[np.cos(theta_y),0,np.sin(theta_y) ],
                      [0,1,0],[-np.sin(theta_y),0 ,np.cos(theta_y) ]])
    rot_z = np.array([[np.cos(theta_z),-np.sin(theta_z),0 ],
                      [np.sin(theta_z) ,np.cos(theta_z),0 ],[0,0,1]])

    b1 = np.dot(rot_x, np.c_[x.flatten(),y.flatten(),z.flatten()].T)
    b2 = np.dot(rot_z, b1)
    b3 = np.dot(rot_z, b2)
    b3 = b3.T+np.array(offset)
    x = b3[:,0].reshape(r.shape); 
    y = b3[:,1].reshape(r.shape); 
    z = b3[:,2].reshape(r.shape); 
    ax.plot_surface(x,y,z, **kw)

# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')

# arrow3d(ax)

# arrow3d(ax, length=60, width=3, head=0.15, headwidth=1.8, offset=[-60,-60,0], 
#         theta_x=0, theta_y=0, theta_z=0,  color="limegreen")

# arrow3d(ax, length=1.4, width=0.03, head=0.15, headwidth=1.8, offset=[1,0.1,0], 
#         theta_x=-60, theta_z = 60,  color="limegreen")

# arrow3d(ax, length=2, width=0.02, head=0.1, headwidth=1.5, offset=[1,1,0], 
        # theta_x=40,  color="crimson")

# arrow3d(ax, length=1.4, width=0.03, head=0.15, headwidth=1.8, offset=[1,0.1,0], 
        # theta_x=-60, theta_z = 60,  color="limegreen")

# ax.set_xlim(0,1)
# ax.set_ylim(0,1)
# ax.set_zlim(0,1)
# plt.show()

# import matplotlib.pyplot as plt
# # Axes3D is needed for plotting 3D plots
# from mpl_toolkits.mplot3d import Axes3D
# # For interactive matplotlib sessions, turn on the matplotlib inline mode
# # %matplotlib inline
# # Dummy data
# x = [1, 2, 3, 4, 5] # X-coordinates
# y = [1, 2, 3, 4, 5] # Y-coordinates
# z = [4, 10, 20, 5, 3] # Z-ccordinates
# # Defining figure
# fig = plt.figure(figsize = (8, 6), dpi = 90)
# # Making 3D Plot using plot3D()
# ax = plt.axes(projection = '3d')
# ax.plot3D(x, y, z)
# # Setting Axis labels
# ax.set_xlabel('X-Axis')
# ax.set_ylabel('Y-Axis')
# ax.set_zlabel('Z-Axis')
# # Showing the plot
# plt.show()

# out_folder = 'HW-output'
# FPGA_rev = "60220713_"

# df1 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowFPGA-60220713_low5deg_03khz_iter1_06232023_125524ADCLoopback_int.txt', sep="\t")
    
# xmin = -80
# xmax = 80
# ymin = -90
# ymax = 80
# zmin = -80
# zmax = 80

# fig = plt.figure(figsize = (15, 12), dpi = 100)    
# ax = plt.axes(projection='3d')
# ax.scatter3D(df1.A1, df1.A2, df1.A3, c=df1.A3, cmap='Greens')
# arrow3d(ax, length=60, width=3, head=0.15, headwidth=1.8, offset=[-75,-75,0], 
#         theta_x=0, theta_y=0, theta_z=0,  color="red")
# ax.set_xlim([xmin, xmax])
# ax.set_ylim([ymin, ymax])
# ax.set_zlim([zmin, zmax])
# # plt.show()
# ax.set_xlabel('Channel 1')
# ax.set_ylabel('Channel 2')
# ax.set_zlabel('Channel 3')
# plt.show()

# fig = plt.figure(figsize = (15, 12), dpi = 100)      
# ax1 = plt.axes(projection='3d')
# ax1.scatter3D(df1.R1, df1.R2, df1.R3, c=df1.R3, cmap='Blues')
# arrow3d(ax1, length=60, width=3, head=0.15, headwidth=1.8, offset=[-75,-75,0], 
#         theta_x=-90, theta_y=0, theta_z=0,  color="red")
# ax1.set_xlim([xmin, xmax])
# ax1.set_ylim([ymin, ymax])
# ax1.set_zlim([zmin, zmax])
# ax1.set_xlabel('Channel 1')
# ax1.set_ylabel('Channel 2')
# ax1.set_zlabel('Channel 3')
# plt.show()

# # fig, (ax11, ax21) = plt.subplots(1, 2)
# # fig.suptitle('Horizontally stacked subplots')
# # ax11.scatter3D(df1.A1, df1.A2, df1.A3, c=df1.A3, cmap='Greens')
# # ax21.scatter3D(df1.R1, df1.R2, df1.R3, c=df1.R3, cmap='Blues')
# # plt.show()

# df2 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowFPGA-60220713_low5deg_03khz_iter2_06232023_125529ADCLoopback_int.txt', sep="\t")

# fig = plt.figure(figsize = (15, 12), dpi = 100)    
# ax2 = plt.axes(projection='3d')
# ax2.scatter3D(df2.R1, df2.R2, df2.R3, c=df2.R3, cmap='Blues')
# arrow3d(ax2, length=60, width=3, head=0.15, headwidth=1.8, offset=[-75,-75,0], 
#         theta_x=-20, theta_y=0, theta_z=0,  color="red")
# ax2.set_xlim([xmin, xmax])
# ax2.set_ylim([ymin, ymax])
# ax2.set_zlim([zmin, zmax])
# ax2.set_xlabel('Channel 1')
# ax2.set_ylabel('Channel 2')
# ax2.set_zlabel('Channel 3')
# plt.show()

# df2 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowFPGA-60220713_low5deg_03khz_iter3_06232023_125534ADCLoopback_int.txt', sep="\t")

# fig = plt.figure(figsize = (15, 12), dpi = 100)      
# ax3 = plt.axes(projection='3d')
# ax3.scatter3D(df2.R1, df2.R2, df2.R3, c=df2.R3, cmap='Blues')
# arrow3d(ax3, length=60, width=3, head=0.15, headwidth=1.8, offset=[-75,-75,0], 
#         theta_x=-45, theta_y=0, theta_z=0,  color="red")
# ax3.set_xlim([xmin, xmax])
# ax3.set_ylim([ymin, ymax])
# ax3.set_zlim([zmin, zmax])
# ax3.set_xlabel('Channel 1')
# ax3.set_ylabel('Channel 2')
# ax3.set_zlabel('Channel 3')
# plt.show()

# df2 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowFPGA-60220713_low5deg_03khz_iter4_06232023_125538ADCLoopback_int.txt', sep="\t")

# fig = plt.figure(figsize = (15, 12), dpi = 100)      
# ax4 = plt.axes(projection='3d')
# ax4.scatter3D(df2.R1, df2.R2, df2.R3, c=df2.R3, cmap='Blues')
# arrow3d(ax4, length=60, width=3, head=0.15, headwidth=1.8, offset=[-75,-75,0], 
#         theta_x=45, theta_y=0, theta_z=0,  color="red")
# ax4.set_xlim([xmin, xmax])
# ax4.set_ylim([ymin, ymax])
# ax4.set_zlim([zmin, zmax])
# ax4.set_xlabel('Channel 1')
# ax4.set_ylabel('Channel 2')
# ax4.set_zlabel('Channel 3')
# plt.show()

# df2 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowFPGA-60220713_low5deg_03khz_iter5_06232023_125543ADCLoopback_int.txt', sep="\t")

# fig = plt.figure(figsize = (15, 12), dpi = 100)    
# ax5 = plt.axes(projection='3d')
# ax5.scatter3D(df2.R1, df2.R2, df2.R3, c=df2.R3, cmap='Blues')
# arrow3d(ax5, length=60, width=3, head=0.15, headwidth=1.8, offset=[-75,-75,0], 
#         theta_x=55, theta_y=0, theta_z=0,  color="red")
# ax5.set_xlim([xmin, xmax])
# ax5.set_ylim([ymin, ymax])
# ax5.set_zlim([zmin, zmax])
# ax5.set_xlabel('Channel 1')
# ax5.set_ylabel('Channel 2')
# ax5.set_zlabel('Channel 3')
# plt.show()

# df2 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowFPGA-60220713_low5deg_03khz_iter6_06232023_125547ADCLoopback_int.txt', sep="\t")

# fig = plt.figure(figsize = (15, 12), dpi = 100)   
# ax6 = plt.axes(projection='3d')
# ax6.scatter3D(df2.R1, df2.R2, df2.R3, c=df2.R3, cmap='Blues')
# arrow3d(ax6, length=60, width=3, head=0.15, headwidth=1.8, offset=[-75,-75,0], 
#         theta_x=90, theta_y=0, theta_z=0,  color="red")
# ax6.set_xlim([xmin, xmax])
# ax6.set_ylim([ymin, ymax])
# ax6.set_zlim([zmin, zmax])
# ax6.set_xlabel('Channel 1')
# ax6.set_ylabel('Channel 2')
# ax6.set_zlabel('Channel 3')
# plt.show()


# # ax3 = plt.axes(projection='3d')
# # ax3.scatter3D(df1.R1[:100], df1.R2[:100], df1.R3[:100], c=df1.R3[:100], cmap='Blues')
# # plt.show()

# print(df1.A1)

out_folder = 'HW-output'
FPGA_rev = "60220713_"

    
# xmin = -80
# xmax = 80
# ymin = -90
# ymax = 80
# zmin = -80
# zmax = 80

#fig = plt.figure(figsize = (15, 12), dpi = 100)    
# ax = plt.axes(projection='3d')
# ax.scatter3D(df1.A1, df1.A2, df1.A3, c=df1.A3, cmap='Greens')
# arrow3d(ax, length=60, width=3, head=0.15, headwidth=1.8, offset=[-75,-75,0], 
#         theta_x=0, theta_y=0, theta_z=0,  color="red")
# ax.set_xlim([xmin, xmax])
# ax.set_ylim([ymin, ymax])
# ax.set_zlim([zmin, zmax])

# plt.show()
# ax.set_xlabel('Channel 1')
# ax.set_ylabel('Channel 2')
# ax.set_zlabel('Channel 3')

df1 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowFPGA-60220713_low5deg_03khz_iter0_06232023_125520ADCLoopback_int.txt', sep="\t")
df3 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowModel-0_07202023_143140.txt', sep="\t")
# plt.figure(figsize=(10,6))
plt.subplot(3, 2, 1)
plt.title("No Rotation")
plt.plot(df1.A3[0:50],label = "FPGA-I/P")
plt.plot(df1.R3[0:50],label = "FPGA-O/P")
plt.plot(df3.A3[0:50],label = "Model-I/P")
plt.plot(df3.R3[0:50],label = "Model-O/P")
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
                       ncol=2,borderaxespad=0.)
plt.ylabel("Channel 3")
plt.xlabel("Time")

plt.subplot(3, 2, 3)
plt.plot(df1.A2[0:50])
plt.plot(df1.R2[0:50])
plt.plot(df3.A2[0:50])
plt.plot(df3.R2[0:50])
plt.ylabel("Channel 2")
plt.xlabel("Time")

plt.subplot(3, 2, 5)
plt.plot(df1.A1[0:50])
plt.plot(df1.R1[0:50])
plt.plot(df3.A1[0:50])
plt.plot(df3.R1[0:50])
plt.ylabel("Channel 1")
plt.xlabel("Time")

df2 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowVerification-0_07202023_142536.txt', sep="\t")
plt.subplot(3, 2, 2)
plt.title("Difference between data points (FPGA - Model)")
plt.plot(df2.R3_df[0:50],label = "Difference")
#plt.plot(df2.R3[0:50],label = "O/P")
# plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
#                        ncol=2,borderaxespad=0.)
plt.ylabel("Channel 3")
plt.xlabel("Time")
plt.ylim([-60,60])
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
                       ncol=2,borderaxespad=0.)

plt.subplot(3, 2, 4)
plt.plot(df2.R2_df[0:50])
#plt.plot(df2.R2[0:50])
plt.ylabel("Channel 2")
plt.xlabel("Time")
plt.ylim([-60,60])

plt.subplot(3, 2, 6)
plt.plot(df2.R1_df[0:50])
#plt.plot(df2.R1[0:50])
plt.ylabel("Channel 1")
plt.xlabel("Time")
plt.ylim([-60,60])
plt.show()

####
df1 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/hiFPGA-60220713_hi5deg_03khz_iter2_06232023_130941ADCLoopback_int.txt', sep="\t")
df3 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/hiModel-2_06232023_130941.txt', sep="\t")
# plt.figure(figsize=(10,6))
plt.subplot(3, 2, 1)
plt.title("Rotation of 20"+chr(176)+ " about X (Channel 1) (Hi)",loc='left')
plt.plot(df1.A3[0:50],label = "FPGA-I/P")
plt.plot(df1.R3[0:50],label = "FPGA-O/P")
plt.plot(df3.A3[0:50],label = "Model-I/P")
plt.plot(df3.R3[0:50],label = "Model-O/P")
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
                       ncol=2,borderaxespad=0.)
plt.ylabel("Channel 3")
plt.xlabel("Time")

plt.subplot(3, 2, 3)
plt.plot(df1.A2[0:50])
plt.plot(df1.R2[0:50])
plt.plot(df3.A2[0:50])
plt.plot(df3.R2[0:50])
plt.ylabel("Channel 2")
plt.xlabel("Time")

plt.subplot(3, 2, 5)
plt.plot(df1.A1[0:50])
plt.plot(df1.R1[0:50])
plt.plot(df3.A1[0:50])
plt.plot(df3.R1[0:50])
plt.ylabel("Channel 1")
plt.xlabel("Time")

df2 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/hiVerification-2_06232023_130941.txt', sep="\t")
plt.subplot(3, 2, 2)
plt.title("Difference b/w data points (FPGA - Model)")
plt.plot(df2.R3_df[0:50],label = "Difference")
#plt.plot(df2.R3[0:50],label = "O/P")
# plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
#                        ncol=2,borderaxespad=0.)
plt.ylabel("Channel 3")
plt.xlabel("Time")
plt.ylim([-max(df2.R3_df[0:50]),max(df2.R3_df[0:50])])
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
                       ncol=2,borderaxespad=0.)

plt.subplot(3, 2, 4)
plt.plot(df2.R2_df[0:50])
#plt.plot(df2.R2[0:50])
plt.ylabel("Channel 2")
plt.xlabel("Time")
plt.ylim([-max(df2.R3_df[0:50]),max(df2.R3_df[0:50])])

plt.subplot(3, 2, 6)
plt.plot(df2.R1_df[0:50])
#plt.plot(df2.R1[0:50])
plt.ylabel("Channel 1")
plt.xlabel("Time")
plt.ylim([-max(df2.R3_df[0:50]),max(df2.R3_df[0:50])])
plt.show()

####
df2 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowFPGA-60220713_low5deg_03khz_iter7_06232023_125552ADCLoopback_int.txt', sep="\t")
plt.figure(figsize=(10,6))
plt.subplot(3, 1, 1)
plt.title("Rotation of 90"+chr(176)+ " about Y (Channel 2)", loc='left')
plt.plot(df2.A3[0:50], label="I/P")
plt.plot(df2.R3[0:50], label="O/P")
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
                       ncol=2,borderaxespad=0.)
plt.ylabel("Channel 3")
plt.xlabel("Time")

plt.subplot(3, 1, 2)
plt.plot(df2.A2[0:50])
plt.plot(df2.R2[0:50])
plt.ylabel("Channel 2")
plt.xlabel("Time")

plt.subplot(3, 1, 3)
plt.plot(df2.A1[0:50])
plt.plot(df2.R1[0:50])
plt.ylabel("Channel 1")
plt.xlabel("Time")

plt.show()

df2 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowFPGA-60220713_low5deg_03khz_iter13_06232023_125620ADCLoopback_int.txt', sep="\t")
plt.figure(figsize=(10,6))
plt.subplot(3, 1, 1)
plt.title("Rotation of 90"+chr(176)+ " about Z (Channel 3)")
plt.plot(df2.A3[0:50], label="I/P")
plt.plot(df2.R3[0:50], label="O/P")
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
                       ncol=2,borderaxespad=0.)
plt.ylabel("Channel 3")
plt.xlabel("Time")

plt.subplot(3, 1, 2)
plt.plot(df2.A2[0:50])
plt.plot(df2.R2[0:50])
plt.ylabel("Channel 2")
plt.xlabel("Time")

plt.subplot(3, 1, 3)
plt.plot(df2.A1[0:50])
plt.plot(df2.R1[0:50])
plt.ylabel("Channel 1")
plt.xlabel("Time")
plt.show()

df2 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowFPGA-60220713_low5deg_03khz_iter19_06232023_125648ADCLoopback_int.txt', sep="\t")
plt.figure(figsize=(10,6))
plt.subplot(3, 1, 1)
plt.title("Rotation of 25"+chr(176)+ " about X and 43"+chr(176)+ " about Y")
plt.plot(df2.A3[0:50], label="I/P")
plt.plot(df2.R3[0:50], label="O/P")
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
                       ncol=2,borderaxespad=0.)
plt.ylabel("Channel 3")
plt.xlabel("Time")

plt.subplot(3, 1, 2)
plt.plot(df2.A2[0:50])
plt.plot(df2.R2[0:50])
plt.ylabel("Channel 2")
plt.xlabel("Time")

plt.subplot(3, 1, 3)
plt.plot(df2.A1[0:50])
plt.plot(df2.R1[0:50])
plt.ylabel("Channel 1")
plt.xlabel("Time")
plt.show()

df2 = pd.read_csv('D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/HW-output/3-ch/Looped_twice_all/lowFPGA-60220713_low5deg_03khz_iter25_06232023_130049ADCLoopback_int.txt', sep="\t")
plt.figure(figsize=(10,6))
plt.subplot(3, 1, 1)
plt.title("Rotation of 35"+chr(176)+ " about X, 15"+chr(176)+ " about Y and 47"+chr(176)+ " about Z")
plt.plot(df2.A3[0:50], label="I/P")
plt.plot(df2.R3[0:50], label="O/P")
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
                       ncol=2,borderaxespad=0.)
plt.ylabel("Channel 3")
plt.xlabel("Time")

plt.subplot(3, 1, 2)
plt.plot(df2.A2[0:50])
plt.plot(df2.R2[0:50])
plt.ylabel("Channel 2")
plt.xlabel("Time")

plt.subplot(3, 1, 3)
plt.plot(df2.A1[0:50])
plt.plot(df2.R1[0:50])
plt.ylabel("Channel 1")
plt.xlabel("Time")
plt.show()

print("done")