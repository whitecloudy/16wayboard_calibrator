from audioop import avg
import re
from vna.anritsu import anritsu
from AD5371_comm import AD5371_comm, complex_packer
import struct
from time import sleep
import numpy
import cmath

def main():
    anal = anritsu("127.0.0.1", 0.910, 0.910, 1)

    anal.doCalibration()

    input("Ready the 16-wayboard and Press Enter to continue...")

    comm = AD5371_comm("192.168.1.160")
    avg_count = 2

    while(True):
        respond_bytes = comm.recv_data()
        respond = struct.unpack('B', respond_bytes)[0]
        print(respond)
        if respond == 1:
            print("We are DONE!")
            break
        elif respond != 0:
            assert False, str(respond)+": Respond from 16wayboard error"

        result = 0.0
        for i in range(avg_count):
            anal.doSweep()

            result += complex(anal.getTrace(2))
            
        result /= avg_count
        packed_data = complex_packer(result)

        comm.send_data(packed_data)
        

if __name__=="__main__":
    main()