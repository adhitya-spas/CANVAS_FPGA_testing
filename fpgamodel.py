from cmath import pi
from matplotlib.pyplot import show
import numpy as np
import os
import glob

# functions from this folder
from readFPGA import read_FPGA_input, read_INT_input, quick_compare, flatten, twos_complement
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

signal_freq0 = 24e3         # signal freq. 1 in Hz
signal_freq1 = 24e3         # signal freq. 2 in Hz
amp0 = hi_amp               # amplitudes (in ADC units)
amp1 = hi_amp               # amplitudes (in ADC units)
shift0 = 0                  # phase shift in radians
shift1 = 83 * np.pi/180     # phase shift in radians
sample_len = 0.5            # seconds
nFFT = 1024                 # length of FFT
n_acc = 8                   # number of FFTs to accummulate

# STEP 1 -------------------- GENERATE INPUT ----------------------------- 
# get one or two test singals
#channels0_td = test_signal(fs, sample_len, signal_freq0, amp0, shift=shift0, channel_num=0, show_plots=False, save_output=None)
#channels1_td = test_signal(fs, sample_len, signal_freq1, amp1, shift=shift1, channel_num=1, show_plots=False, save_output='hex')
inputs = 'Inputs/'
freq = '_03khz'
phase = "5deg"
file0 = inputs + 'high-high_'+'0deg'+freq+'.txt'
file1 = inputs +  'high-high_' + phase + freq + '.txt' 
channels0_td = read_FPGA_input(file0,signed=True,show_plots=False)
channels1_td = read_FPGA_input(file1,signed=True,show_plots=False)

#print(max(channels0_td))
# STEP 2 ----------------- GET HANNING WINDOW ----------------------------
# get a window based on IDL code
win = get_win(nFFT, show_plots=False, save_output=None)

# STEP 3 ----------------------- TAKE FFT --------------------------------
# take fft on each channel

channel0_fd_real, channel0_fd_imag = canvas_fft(nFFT, fs, win, channels0_td, overlap=True,  channel_num=0, show_plots=False, save_output=None)
channel1_fd_real, channel1_fd_imag = canvas_fft(nFFT, fs, win, channels1_td, overlap=True,  channel_num=1, show_plots=False, save_output=None)

# STEP 4 ----------------------- CALC PWR --------------------------------
# calculate power, diff for spectra and x-spec
#fpga_rev = "Rev14p1"
#fpga_file_path_0 = "Data_compare/xspec_im_test/"+"0712_03khz_spec0_FFT_hex.txt"
#fpga_file_path_1 = "Data_compare/xspec_im_test/"+"0712_03khz_spec1_FFT_hex.txt"

#f_ar_0, f_ai_0 = read_FPGA_input_lines(fpga_file_path_0, 32, line_n=3, x=1, y=2)
#f_ar_1, f_ai_1 = read_FPGA_input_lines(fpga_file_path_1, 32, line_n=3, x=1, y=2)

spec_pwr0 = fft_spec_power(channel0_fd_real, channel0_fd_imag, channel_num=0, show_plots=False, save_output=None)
spec_pwr1 = fft_spec_power(channel1_fd_real, channel1_fd_imag, channel_num=1, show_plots=False, save_output=None)
xspec_pwr_r, xspec_pwr_i = fft_xspec_power(channel0_fd_real, channel0_fd_imag, channel1_fd_real, channel1_fd_imag, channel_nums=[0,1], show_plots=False, save_output=None)

#spec_pwr0 = fft_spec_power(f_ar_0, f_ai_0, channel_num=0, show_plots=False, save_output='both')
#spec_pwr1 = fft_spec_power(f_ar_1, f_ai_1, channel_num=1, show_plots=False, save_output='both')
#xspec_pwr_r, xspec_pwr_i = fft_xspec_power(f_ar_0, f_ai_0, f_ar_1, f_ai_1, channel_nums=[0, 1], show_plots=False,save_output='both')
#xspec_pwr_r, xspec_pwr_i = fft_spec_power([channel0_fd_real], [channel0_fd_imag], [channel1_fd_real], [channel1_fd_imag], channel_nums=[0,1], show_plots=False, save_output='both')
# STEP 5 -------------------- rebin and acc -------------------------------
# functions written to rebin (avg in freq) and acc (avg in time)
rebin_pwr0= rebin_likefpga(spec_pwr0, channel_num=0, show_plots=False, save_output=None)
rebin_pwr1= rebin_likefpga(spec_pwr1, channel_num=1, show_plots=False, save_output=None)

rebin_pwr_01_r= rebin_likefpga(xspec_pwr_r, channel_num=2, show_plots=False, save_output='both')
rebin_pwr_01_i= rebin_likefpga(xspec_pwr_i, channel_num=3, show_plots=False, save_output='both')

acc_pwr0 = acc_likefpga(rebin_pwr0, n_acc, channel_num=0, show_plots=False, save_output=None)
acc_pwr1 = acc_likefpga(rebin_pwr1, n_acc, channel_num=1, show_plots=False, save_output=None)

acc_pwr01_r = acc_likefpga(rebin_pwr_01_r, n_acc, channel_num=2, show_plots=False, save_output='both')
acc_pwr01_i = acc_likefpga(rebin_pwr_01_i, n_acc, channel_num=3, show_plots=False, save_output='both')

# STEP 6 ---------------- average in time and freq -------------------------
# import canvas bins correctly -- make sure you have this file
fname = 'CANVAS_fbins/fbins.txt'                                 
fbins_str = np.genfromtxt(fname, dtype='str') 
fbins_dbl = [(float(f[0].replace(',','')),float(f[1].replace(',',''))) for f in fbins_str]
c_fbins = [item for sublist in fbins_dbl for item in sublist]
center_freqs = [fs/nFFT * ff for ff in np.arange(0, 512)]

avg_pwr0 = rebin_canvas(acc_pwr0, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=0, show_plots=False, save_output=None)
avg_pwr1 = rebin_canvas(acc_pwr1, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=1, show_plots=False, save_output=None)

avg_pwr01_r = rebin_canvas(acc_pwr01_r, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=2, show_plots=False, save_output='both')
avg_pwr01_i = rebin_canvas(acc_pwr01_i, n_acc, c_fbins, center_freqs, tx_bins=True, channel_num=3, show_plots=False, save_output='both')

# STEP 7 ---------------- compress -------------------------
# use spec compress or xspec compress for log2 compression
cpmrs_val0 = spec_compress(avg_pwr0, channel_num=0, show_plots=False, save_output=None)
cpmrs_val1 = spec_compress(avg_pwr1, channel_num=1, show_plots=False, save_output=None)

cmprs_val_r = xspec_compress(avg_pwr01_r, coefficient='r', show_plots=False, save_output='both')
cmprs_val_i = xspec_compress(avg_pwr01_i, coefficient='i', show_plots=False, save_output='both')
print("Done! Freq: ",signal_freq0)