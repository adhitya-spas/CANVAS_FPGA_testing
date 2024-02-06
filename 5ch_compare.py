# 5ch compare

# This code takes CCSDS parsed packets and compares with the model values
import pandas as pd
from readFPGA import twos_complement

# Mention folder locations
model_folder = "output-same/"
out_folder = "HW-output/parse/"
out_spectra = "parse-CCSDS_pkt_09072023_213642-SPECTRA_2"

# Saves all the values from spectra packet into nested list of 5 ch
df_spec = pd.read_csv(out_folder+out_spectra+'.txt')
hex_spec = list(df_spec.iloc[12:79,0])
out_ch1 = []
out_ch2 = []
out_ch3 = []
out_ch4 = []
out_ch5 = []
out_spec = []
for i in range(0,len(hex_spec)):
    temp = hex_spec[i].split('\t')
    out_ch1.append(temp[0])
    out_ch2.append(temp[1])
    out_ch3.append(temp[2])
    out_ch4.append(temp[3])
    out_ch5.append(temp[4])
out_spec.append(out_ch1)
out_spec.append(out_ch2)
out_spec.append(out_ch3)
out_spec.append(out_ch4)
out_spec.append(out_ch5)

# Saving model spec values as nested list
mod_spec=[]
for i in range(0,5):
    df = pd.read_csv(model_folder+'channel'+str(i)+'_cmprs_hex'+'.txt',header=None)
    temp2 = list(df.iloc[:,0])
    mod_spec.append(temp2)

# Finding difference between variables
diff_1 = []
diff_2 = []
diff_3 = []
diff_4 = []
diff_5 = []
diff_together = []
for i in range(0,len(out_spec[0])):   
    diff_1.append(abs(twos_complement(out_spec[0][i]) - twos_complement(mod_spec[0][i])))
    diff_2.append(abs(twos_complement(out_spec[1][i]) - twos_complement(mod_spec[1][i])))
    diff_3.append(abs(twos_complement(out_spec[2][i]) - twos_complement(mod_spec[2][i])))
    diff_4.append(abs(twos_complement(out_spec[3][i]) - twos_complement(mod_spec[3][i])))
    diff_5.append(abs(twos_complement(out_spec[4][i]) - twos_complement(mod_spec[4][i])))
diff_together.append(diff_1)
diff_together.append(diff_2)
diff_together.append(diff_3)
diff_together.append(diff_4)
diff_together.append(diff_5)

## Writing into text file 
file = open('HW-output/compare'+'/compare_'+out_spectra[17:31]+ '.txt','w')
file.write("mod_ch1"+"\t"+"mod_ch2"+"\t"+"mod_ch3"+"\t"+"mod_ch4"+"\t"+"mod_ch5"+"\t\t"+"out_ch1"+"\t"+"out_ch2"+"\t"+"out_ch3"+"\t"+"out_ch4"+"\t"+"out_ch5"+"\t\t"+"diff_ch1"+"\t"+"diff_ch2"+"\t"+"diff_ch3"+"\t"+"diff_ch4"+"\t"+"diff_ch5"+"\n")  
for i in range(0,len(out_spec[0])):
    file.write(str(mod_spec[0][i])+"\t"+str(mod_spec[1][i])+"\t"+str(mod_spec[2][i])+"\t"+str(mod_spec[3][i])+"\t"+str(mod_spec[4][i])+"\t\t"+str(out_spec[0][i])+"\t"+str(out_spec[1][i])+"\t"+str(out_spec[2][i])+"\t"+str(out_spec[3][i])+"\t"+str(out_spec[4][i])+"\t\t"+str(diff_together[0][i])+"\t\t"+str(diff_together[1][i])+"\t\t"+str(diff_together[2][i])+"\t\t"+str(diff_together[3][i])+"\t\t"+str(diff_together[4][i])+"\n")  
file.close()