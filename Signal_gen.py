# Code for generating signal given Freq, Amp, Phase

import numpy as np
import random
from readFPGA import twos_complement_to_hex, proper_twos_complement
amp = 0.9*pow(2,15)   # V
freq = 23000  # Hz
phase = 0   # deg
pi = 3.14

t = range(0,65536)
x = []

# Generate signal
for time in t:
    x.append(amp * np.sin((2*pi*freq*time) + phase))

# Add bit noise to generated signal
x_random = []
bit_noise = [0,1]
for a in x:
    x_random.append(a + random.choice(bit_noise))

# Convert to hex
x_hex = []
for num in x_random:
    x_hex.append(proper_twos_complement(num))

# Print into text file
file_signal = open('Inputs/signal_'+str(freq)+'.txt','w')
for b in x_hex:
    file_signal.write(str(b) + "\n")
file_signal.close()

print(x)