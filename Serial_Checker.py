"""This module is responsible for checking the serial connection with the GPS
    This module only works with the @@HA GPS message
"""

# Imported Modules
import sys
import os.path
import argparse
from datetime import datetime
from threading import Thread
from serial import Serial, SerialException, SerialTimeoutException
import numpy as np

RESTARTS_TO_TEST = 20
exceptions = 0

def int_from_bytes(b):
    '''Convert big-endian signed integer bytearray to int

    int_from_bytes(b) == int.from_bytes(b, 'big', signed=True)'''
    
    if not b: # special-case 0 to avoid b[0] raising
        return 0
    n = b[0] & 0x7f # skip sign bit
    for by in b[1:]:
        n = n * 256 + by
    if b[0] & 0x80: # if sign bit is set, 2's complement
        bits = 8*len(b)
        offset = 2**(bits-1)
        return n - offset
    else:
        return n

class SerialChecker():
    def __init__(self, comPortNumber):
        # Variables
        self.thread = None
        self.is_running = False
        self.ser = None
        self.comPortNumber = comPortNumber


        # Add motorola GPS commands
        self.cmd={}
        self.cmd["start"] = b'@@Ha\x01\x28\x0d\x0a'
        self.cmd["stop"] = b'@@Ha\x00\x29\x0d\x0a'

        # Initalize the serial port
        print ("Opening serial COM Port: %d" % self.comPortNumber)
        try:
            self.ser = Serial(port='COM%d' % self.comPortNumber,
                                     baudrate=9600, 
                                     bytesize=8, 
                                     parity='N', 
                                     stopbits=1,
                                     timeout=1)
        except:
            print('Could not open serial COM Port: %d' % self.comPortNumber)
            raise

    def Start(self):
        global exceptions
        # Make sure serial Port is open
        if not self.ser.is_open:
            print("Reopening Serial Port...")
            self.ser.open()
        
        print ("Writing START msg...")
        try:
            bytes_written = self.ser.write(self.cmd["start"])
        except SerialTimeoutException:
            print ("Serial timeout. Could not write START msg to serial GPS.")
            exceptions += 1
        except:
            print ("Some other exception happened.")
            exceptions += 1
        else:
            if bytes_written < 8:
                print ("Serial port did not transmit full message to GPS.")
                exceptions += 1
                
            
        # Start the Mainloop thread - use this to start and stop , save in a file and read
        self.thread = Thread(target=self.MainLoop, name='SerialChecker MainLoop')
        self.thread.daemon = True
        self.thread.start()
        print('MainLoop thread started')
        return
    
    def Stop(self):
        global exceptions
        # Stop MainLoop
        self.is_running = False  
        # Have to give MainLoop time to stop
        sleep(1)

        # Write stop command to GPS
        print ("Writing STOP msg...")
        try:
            bytes_written = self.ser.write(self.cmd['stop'])
        except SerialTimeoutException:
            print ("Serial timeout. Could not write STOP msg to serial GPS.")
            exceptions += 1
        except:
            print ("Some other exception happened.")
            exceptions += 1
        else:
            if bytes_written < 8:
                print ("Serial port did not transmit full message to GPS.")
                exceptions += 1 
        
        # Close serial Port
        self.ser.close()
        
        # Kill MainLoop thread
        if self.thread is not None:
            self.thread.join(timeout=10)
            self.thread = None

        print("Waiting 1s before Restart...")
        sleep(1)
        return
    
    def MainLoop(self):
        global exceptions
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        self.is_running = True

        while self.is_running:
            try:
                bytes_read = self.ser.read(2) #154
                # self.JustPrintData(bytes_read)
            except SerialTimeoutException:
                print ("Serial timeout Exception.")
                exceptions += 1
                self.is_running = False
                continue
            except:
                print ("Some other exception happened.")
                exceptions += 1
                self.is_running = False
                continue
            if len(bytes_read) < 2: #154
                print ("Could not read full message (%d/154) from serial GPS." 
                       % len(bytes_read))
                exceptions += 1
                continue
                
            self.JustPrintData(bytes_read)

            sleep(0.1)

    def JustPrintData(self, bytes):
        # val = int.from_bytes(bytes, 'big')
        # hex_val = format(np.int16(val) & 0xffff, '04X')
        # # first=""
        # for i in bytes[2:]:
        #     first.append(str(i))
        #     if "\\x" in first:
        #         val = int.from_bytes(first[:-2], 'big')
        #         hex_val = format(np.int16(val) & 0xffff, '04X')
        #         print(hex_val)
        # bytes_str = str(bytes)
        # bytes_str = bytes_str[2:].replace("\\x","")
        # for i in bytes:
        #     val = int.from_bytes(i, 'big')
        #     hex_val = format(np.int16(val) & 0xffff, '04X')
        print(bytes)
        return
    
    def DecodeTimestamp(self, bytes):
        dt = datetime(year=int_from_bytes(bytearray([bytes[6],bytes[7]])), 
                      month=(bytes[4]),
                      day=(bytes[5]), 
                      hour=(bytes[8]),
                      minute=(bytes[9]), 
                      second=(bytes[10]), 
                      tzinfo=None)
        print(dt)
        return

def FindCOMPort():
    ComPorts = range(30)
    for comPort in ComPorts:
        try:
            # Try to Open Serial Port
            ser = Serial('COM%d'%(comPort), baudrate=115200, bytesize=8, parity='N', stopbits=1)
            comPort = 6
            print("Serial Port found on COM: %d" % comPort)
            return comPort
        except:
            pass
    sys.exit("Could not find COM port in range 1-30")

if __name__ == '__main__':
    from time import sleep
    
    # ========================
    # Setup options parser
    # ========================
    parser = argparse.ArgumentParser(description='Check for Serial GPS')
    parser.add_argument("--search", default=True, action="store_true", 
                        help="Automatically search for Serial GPS.")
    parser.add_argument('--port',  help="Test port #", default=5)
    args = parser.parse_args()
    
    if not args.search and args.port is None:
        sys.exit("No argmuents provided. Please run with -h flag for help.")
    
    if args.search:
        comPortNumber = FindCOMPort()
    else:
        comPortNumber = int(args.port)

    for i in range(RESTARTS_TO_TEST):
        print("*****  Cyle %d/%d  *****" % (i+1, RESTARTS_TO_TEST))
        s = SerialChecker(comPortNumber)
        s.Start()
        sleep(5)
        s.Stop()
        s.Start()
        sleep(2)
        s.Stop()


    print("Program Finsihed")
    print("Total Exceptions: %d" % exceptions)
   