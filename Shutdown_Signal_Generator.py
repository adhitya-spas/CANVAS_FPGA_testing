# Run this code right after a longterm test to turn off the signal generators

import pyvisa
import time

rm = pyvisa.ResourceManager()

def shutdown_cmd():
    # Open SG-1
    SG2025_1 = rm.open_resource('USB0::0xF4ED::0xEE3A::SDG10GA2162677::INSTR')
    # Turn off output on Channel 1 (C1)
    SG2025_1.write("C1:OUTP OFF")
    time.sleep(5)
    # Turn off output on Channel 2 (C2)
    SG2025_1.write("C2:OUTP OFF")
    time.sleep(5)
    # Open SG-2
    SG2025_2 = rm.open_resource('USB0::0xF4ED::0xEE3A::SDG10GAQ1R1236::INSTR')
    # Turn off output on Channel 1 (C1)
    SG2025_2.write("C1:OUTP OFF")
    time.sleep(5)
    # Turn off output on Channel 2 (C2)
    SG2025_2.write("C2:OUTP OFF")
    time.sleep(5)
    # Open SG-3
    SG2025_3 = rm.open_resource('USB0::0xF4ED::0xEE3A::SDG10GAX1R0601::INSTR')
    # Turn off output on Channel 1 (C1)
    SG2025_3.write("C1:OUTP OFF")
    

    # # Write System OFF?
    # SG2025_1.write("SYSTem:POWer OFF")
    # SG2025_2.write("SYSTem:POWer OFF")
    # SG2025_3.write("SYSTem:POWer OFF")

    # Close connections
    SG2025_1.close()
    SG2025_2.close()
    SG2025_3.close()

shutdown_cmd()