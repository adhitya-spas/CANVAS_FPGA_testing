from cmath import pi
from matplotlib.pyplot import show
import numpy as np
import os
import glob

# functions from this folder
from readFPGA import read_FPGA_input, read_INT_input, quick_compare, flatten, twos_complement, proper_twos_complement
from readFPGA import read_FPGA_fft_debug, read_FPGA_input_lines
from inputstimulus import test_signal, input_chirp, white_noise
from win import get_win
from fftcanvas import canvas_fft
from fftpwr import fft_spec_power, fft_xspec_power
from rebinacc import rebin_likefpga, acc_likefpga
from cfbinavg import rebin_canvas, fix_neg1
from log2compress import spec_compress, xspec_compress
from saveas import saveascsv

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
# get one or two test singals
#channels0_td = test_signal(fs, sample_len, signal_freq0, amp0, shift=shift0, channel_num=0, show_plots=False, save_output=None)
#channels1_td = test_signal(fs, sample_len, signal_freq1, amp1, shift=shift1, channel_num=1, show_plots=False, save_output='hex')
inputs = 'Inputs/'
amp = "hi"
phase0 = "512hz"
# file0 = inputs+amp+"_amp_"+phase0+'.txt'
file0 = inputs+'signal_512.txt'
phase1 = "03khz"
# file1 = inputs+amp+"_amp_"+phase1+'.txt'
file1 = inputs+'signal_3000.txt'
phase2 = "10khz"
# file2 = inputs+amp+"_amp_"+phase2+'.txt'
file2 = inputs+'signal_10000.txt'
phase3 = "24khz" # broken
#file3 = inputs+amp+"_amp_"+phase3+'.txt'
file3 = inputs+'signal_23000.txt'
phase4 = "33khz"
# file4 = inputs+amp+"_amp_"+phase4+'.txt'
file4 = inputs+'signal_33000.txt'


#file0 = "D:\CANVAS_work\CANVAS_git\CANVAS_FPGA_testing\Inputs\signal_1.txt"
#file1 = "D:\CANVAS_work\CANVAS_git\CANVAS_FPGA_testing\Inputs\signal_2.txt"
#file2 = "D:\CANVAS_work\CANVAS_git\CANVAS_FPGA_testing\Inputs\signal_3.txt"
#file3 = "D:\CANVAS_work\CANVAS_git\CANVAS_FPGA_testing\Inputs\signal_4.txt"
#file4 = "D:\CANVAS_work\CANVAS_git\CANVAS_FPGA_testing\Inputs\signal_5.txt"

channels0_td_pre = read_FPGA_input(file0,signed=True,show_plots=False)
channels1_td_pre = read_FPGA_input(file1,signed=True,show_plots=False)
channels2_td_pre = read_FPGA_input(file2,signed=True,show_plots=False)
channels3_td_pre = read_FPGA_input(file3,signed=True,show_plots=False)
channels4_td_pre = read_FPGA_input(file4,signed=True,show_plots=False)

num_samples = 20480 #len(channels0_td_pre) 
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

# STEP 8 ---- saving as meaningful data ----
file_spec = open('Spec_vals.txt','w')
file_spec.write("SPECTRA "+"\n")

file_spec.write("Channal Frequency "+"\n")
file_spec.write("0 -> "+phase0+"\n")
file_spec.write("1 -> "+phase1+"\n")
file_spec.write("2 -> "+phase2+"\n")
file_spec.write("3 -> "+phase3+"\n")
file_spec.write("4 -> "+phase4+"\n")

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

file_xspeca = open('Xspec_A_vals.txt','w')
file_xspeca.write("CROSS-SPECTRA A (Real) "+"\n")
type = 'A'

file_xspeca.write("Channal Frequency "+"\n")
file_xspeca.write("0 -> "+phase0+"\n")
file_xspeca.write("1 -> "+phase1+"\n")
file_xspeca.write("2 -> "+phase2+"\n")
file_xspeca.write("3 -> "+phase3+"\n")
file_xspeca.write("4 -> "+phase4+"\n")

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
file_xspecb = open('Xspec_B_vals.txt','w')
file_xspecb.write("CROSS-SPECTRA B (Imaginary) "+"\n")
type = 'B'

file_xspecb.write("Channal Frequency "+"\n")
file_xspecb.write("0 -> "+phase0+"\n")
file_xspecb.write("1 -> "+phase1+"\n")
file_xspecb.write("2 -> "+phase2+"\n")
file_xspecb.write("3 -> "+phase3+"\n")
file_xspecb.write("4 -> "+phase4+"\n")

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