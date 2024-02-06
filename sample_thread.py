import logging
import threading
import time
import serial
import numpy as np
import queue
# from trial_code import counter

# global counter # 1 for running, 0 for end iteration
global buffer_pkt
global ser

def thread_function(name):
    logging.info("Thread %s: starting", name)
    while (counter==1):
        if(buffer_pkt.qsize()<3000): # Around 2600 is one packet
            buffer_pkt.put("hi")

    logging.info("Thread %s: finishing", name)

def thread_initialize():
    # global counter # 1 for running, 0 for end iteration
    global buffer_pkt
    global ser
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