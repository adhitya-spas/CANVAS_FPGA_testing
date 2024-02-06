import logging
import threading
import time
import serial
import numpy as np
import queue

global counter # 1 for running, 0 for end iteration
global buffer_pkt
global ser

def thread_function(name):
    logging.info("Thread %s: starting", name)
    while (counter==1):
        if(buffer_pkt.qsize()<3000): # Around 2600 is one packet
            val = int.from_bytes(ser.read(2), 'big') # Create func that reads from port - create buffer to store and throws serial bytes in - 
            hex_val = format(np.int16(val) & 0xffff, '04X')
            buffer_pkt.put(hex_val)

    logging.info("Thread %s: finishing", name)

def thread_initialize():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    buffer_pkt = queue.Queue()
    logging.info("Main    : before creating thread")
    x = threading.Thread(target=thread_function, args=(1,))
    logging.info("Main    : before running thread")
    x.start()

    logging.info("Main    : wait for the thread to finish")
    x.join()
    logging.info("Main    : all done")
