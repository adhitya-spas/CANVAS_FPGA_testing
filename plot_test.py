import matplotlib.pyplot as plt

outpath='HW-output/parse/5-ch/'
file_spec = open(outpath+'parse-CCSDS_pkt_11272023_125321-SPECTRA_1.txt','r')
Lines = file_spec.readlines()

spec1 = []
spec2 = []
spec3 = []
spec4 = []
spec5 = []

for temp in Lines[86:152]:
    a = temp.split()
    spec1.append(int(a[0]))
    spec2.append(int(a[1]))
    spec3.append(int(a[2]))
    spec4.append(int(a[3]))
    spec5.append(int(a[4]))

file_model = open('Model_all/Spec_vals.txt','r')
Lines_Model = file_model.readlines()

M_spec1 = []
M_spec2 = []
M_spec3 = []
M_spec4 = []
M_spec5 = []

for temp in Lines[1351:1351+67]:
    b = temp.split()
    M_spec1.append(int(b[0]))
    M_spec2.append(int(b[1]))
    M_spec3.append(int(b[2]))
    M_spec4.append(int(b[3]))
    M_spec5.append(int(b[4]))

plt.figure()
plt.subplot(2, 3, 1)
plt.plot(spec1)
plt.subplot(2, 3, 1)
plt.plot(M_spec2)
plt.legend(["fpga", "py"])
plt.subplot(2, 3, 2)
plt.plot(spec2)
plt.plot(M_spec2)
plt.subplot(2, 3, 3)
plt.plot(spec3)
plt.plot(M_spec3)
plt.subplot(2, 3, 4)
plt.plot(spec4)
plt.plot(M_spec4)
plt.subplot(2, 3, 5)
plt.plot(spec5)
plt.plot(M_spec5)
plt.legend(["fpga", "py"])
plt.suptitle("Spectra 5 Ch")
plt.show()

plt.plot(np.log10(final_avg_pwr[0]))
plt.title('Average Power')
plt.show()
plt.close()


plt.figure()
plt.subplot(1, 2, 1)
plt.plot(fpga_data_r["Comp"][size_start[m]:size_end[m]], linewidth=1, color='cyan')

py_data_r = pd.read_table("D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/Data_compare/x-spec/Python_Results/high-high_" + l + "deg_" + j[m] + "khz_channel_r_cmprs_int.txt")

plt.plot(py_data_r.iloc[size_start[m]-1:size_end[m]], linewidth=1, linestyle="--", color='red')
plt.title(j[m] + "kHz " + l + "deg" + " (r)")
plt.legend(["fpga", "py"])

fpga_data_i = pd.read_table("D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/Data_compare/x-spec/FPGA_Results/FPGA-60220713_high-high_" + l + "deg_" + j[m] + "khz_xpec_im_avg_int.txt")

plt.subplot(1, 2, 2)
plt.plot(fpga_data_i["Comp"][size_start[m]:size_end[m]], linewidth=1, color='cyan')

py_data_i = pd.read_table("D:/CANVAS_work/Canvas-Algorithm/Canvas_FPGA/Data_compare/x-spec/Python_Results/high-high_" + l + "deg_" + j[m] + "khz_channel_i_cmprs_int.txt")

plt.plot(py_data_i.iloc[size_start[m]-1:size_end[m]], linestyle="--", color='red')
plt.title(j[m] + "kHz " + l + "deg" + " (im)")
plt.legend(["fpga", "py"])
plt.show()