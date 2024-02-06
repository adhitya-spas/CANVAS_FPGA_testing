#####   IMPORTED LIBRARIES  #####
import numpy as np
from datetime import datetime
import pandas as pd

# Define Input and Output Location
input_filename = "33khz-hi.csv"
data = pd.read_csv(input_filename)

var = data.data
var1= []
new_var = []

for i in range(0,len(var)):
    end = len(var[i])
    var1.append(var[i][end-2:end])

for j in range(0,len(var1)-3,3):
            top_val = var1[j]
            middle_val = var1[j+1]
            bottom_val = var1[j+2]

            first_val = "0" + middle_val[1:]+top_val
            second_val = "0" + bottom_val+middle_val[:1]

            new_var.append(first_val)
            new_var.append(second_val)




print("meh")
# lines = open(input_filename).read().splitlines()
# cnt = 0
# now = datetime.now()
# date_time = now.strftime("_%m%d%Y_%H%M%S")
# outpath='HW-output/parse/parse-'
# name = outpath+ 'CCSDS_pkt' + date_time
