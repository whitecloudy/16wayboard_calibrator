"""
class file for ANRITSU MS46122A VNA

David Burn

Edit : Whitecloudy
"""


import socket
import struct
import numpy as np
from time import sleep


class anritsu():
	def __init__(self, host, freq_start=0.1, freq_stop=8, point=2048):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((host, 5001))
		print("socket setup")
		self.sock.send(str.encode("*IDN?\n"))
		print(self.sock.recv(2056))


		self.bandwidth = None
		self.setup(freq_start, freq_stop, point)


	def query(self, message):
		self.sock.send(str.encode(message+"\n"))
		return self.recvAnswer()

	def write(self, message):
		self.sock.send(str.encode(message+"\n"))


	def setup(self, freq_start, freq_stop, point):
		""" display layout settings """
		self.write(":CALCulate1:PARameter1:DEFine S11")
		self.write(":CALCulate1:PARameter1:FORMat MLOGarithmic")

		self.write(":CALCulate1:PARameter2:DEFine S21")
		self.write(":CALCulate1:PARameter2:FORMat MLOGarithmic")

		self.write(":CALCulate1:PARameter3:DEFine S22")
		self.write(":CALCulate1:PARameter3:FORMat MLOGarithmic")

		self.write(":CALCulate1:PARameter4:DEFine S12")
		self.write(":CALCulate1:PARameter4:FORMat MLOGarithmic")

		self.write(":SENSe:HOLD:FUNCtion HOLD")		# single sweep and hold

		""" data transfer settings """
		self.write(":FORMat:DATA REAL")				# ASC, REAL or REAL32
		self.write(":FORMat:BORDer SWAP")			# MSB/LSB: Normal or Swapped
		
		self.setFrequency(freq_start, freq_stop)
		self.setNumPoints(point)
		self.setBandwidth(40000) 
		print(self.query(":SYST:ERR?"))				#returns "No Error"




	def getData(self):
		s11 = self.getTrace(1)	#S11
		s21 = self.getTrace(2)	#S21
		s22 = self.getTrace(3)	#S22
		s12 = self.getTrace(4)	#S12
		return [s11,s21,s22,s12]

 



	def getTrace(self, par):
		# floating point with 8 bytes / 64 bits per number
		self.write(":SYST:ERR:CLE")
		opc = self.query("*OPC?")
		print(opc)

		print(self.query(":SYST:ERR?"))				#returns "No Error"

		self.sock.send(str.encode(":CALC1:PAR%1d:SEL\n" % par))
		print(self.query(":CALC1:PAR:SEL?").decode("utf-8"))
		self.query("*OPC?")

		self.write(":CALC1:DATA:SDAT?")	#works

		data = self.recvData()

		num = len(data) / 8
		[data,] = struct.unpack('%dd' % num, data),
		
		return  np.array(data[::2])   + np.array(data[1::2])*1j




	def getFrequency(self):
		self.write("SYST:ERR:CLE")

		self.write(":SENSe:FREQuency:DATA?")
		
		data = self.recvData()

		num = len(data) / 8
		[data,] = struct.unpack('%dd' % num, data),
		return np.array(data)/1e9




	def recvAnswer(self):
		chunk = b''
		while True:
			chunk += self.sock.recv(2056)
			if chunk[-1:].decode("utf-8") == '\n' :
				break

		return chunk



	def recvData(self):
		MSGLEN = 0

		head = ''
		# header part 1
		while len(head) < 2:
			head += self.sock.recv(2 - len(head)).decode("utf-8")				

		if head[0] != '#':
			raise ValueError('First byte must be # : Actual Value = '+head[0])
		else:
			MSGLEN = int(head[1])

		head = b''
		# header part 2
		while len(head) < MSGLEN:				
			head += self.sock.recv(MSGLEN - len(head))			
		
		MSGLEN = int(head) 		# extrace message len from header

		# get actual data
		datas = b''
		while len(datas) < MSGLEN:
			datas += self.sock.recv(min(MSGLEN - len(datas), 2048))

		extra = self.recvAnswer()

		return datas




	def doSweep(self):
		self.write(":SYST:ERR:CLE")
		opc = self.query("*OPC?")
		print("opc ", opc)

		self.write(":TRIG:SING")
		# there is a wait here until anritsu has finished collecting
		sleep(10e-3)
		opc = self.query("*OPC?")
		print("opc ", opc)
		err = self.query(":SYST:ERR?")
		print("err ", err)



	def setFrequency(self, start, stop):
		""" frequency settings """
		start = start*1.0e9
		stop = stop*1.0e9
		self.write(":SENS:FREQ:STAR %d" % start)
		self.write(":SENS:FREQ:STOP %d" % stop)



	def setBandwidth(self,bandwidth):
		self.bandwidth = bandwidth
		self.write(":SENS:BAND %6d" % bandwidth)				# IFBW Frequency (Hz)



	def setNumPoints(self,num):
		self.write(":SENS:SWEEP:POINT %4d" % max(2, num))	# Minimum number of point is 2



	def doCalibration(self):
		self.write(":SENS:CORR:COLL:PORT1:CONN CFKT")
		print(self.query(":SYST:ERR?"))				#returns "No Error"
		self.write(":SENS:CORR:COLL:PORT2:CONN CFKT")
		print(self.query(":SYST:ERR?"))				#returns "No Error"

		print(self.query(":SENS:CORR:COLL:PORT1:CONN?"))
		print("[PORT1]")
		print("\tSHORT")
		input("\tConnect SHORT and Press Enter")
		input("\tAre you sure to proceed?")
		self.write(":SENS:CORR:COLL:PORT1:SHORt")
		print(self.query(":SYST:ERR?"))				#returns "No Error"
		print("\tOPEN")
		input("\tConnect OPEN and Press Enter")
		input("\tAre you sure to proceed?")
		self.write(":SENS:CORR:COLL:PORT1:OPEN")
		print(self.query(":SYST:ERR?"))				#returns "No Error"
		print("\tLOAD")
		input("\tConnect LOAD and Press Enter")
		input("\tAre you sure to proceed?")
		self.write(":SENS:CORR:COLL:PORT1:LOAD")
		print(self.query(":SYST:ERR?"))				#returns "No Error"

		print("[PORT2]")
		print("\tSHORT")
		input("\tConnect SHORT and Press Enter")
		input("\tAre you sure to proceed?")
		self.write(":SENS:CORR:COLL:PORT2:SHORt")
		print(self.query(":SYST:ERR?"))				#returns "No Error"
		print("\tOPEN")
		input("\tConnect OPEN and Press Enter")
		input("\tAre you sure to proceed?")
		self.write(":SENS:CORR:COLL:PORT2:OPEN")
		print(self.query(":SYST:ERR?"))				#returns "No Error"
		print("\tLOAD")
		input("\tConnect LOAD and Press Enter")
		input("\tAre you sure to proceed?")
		self.write(":SENS:CORR:COLL:PORT2:LOAD")
		print(self.query(":SYST:ERR?"))				#returns "No Error"
		
		print("[PORT12]")
		print("\tTHRU")
		input("\tConnect THRU and Press Enter")
		input("\tAre you sure to proceed?")
		self.write(":SENS:CORR:COLL:PORT12:THRU")
		print(self.query(":SYST:ERR?"))				#returns "No Error"
		
		print("<Calibration Complete>")
		self.write(":SENSe:CORRection:COLLect:SAVE")
		print(self.query(":SYST:ERR?"))				#returns "No Error"
		self.write(":SENSe:CORRection:ISOLation:STATe ON")
		print(self.query(":SYST:ERR?"))				#returns "No Error"
		self.write(":SENSe:CORRection:STATe ON")
		print(self.query(":SYST:ERR?"))				#returns "No Error"







#vna.send(str.encode("RTL\n"))	# return to local mode




"""
terminal readout when the anritsu freezes


after do sweep
after get data
Field: 16.00 mT
set the field: 16.000 mT (7.609 mm)
opc  1

err  No Error

after do sweep
after get data
Field: 16.10 mT
set the field: 16.100 mT (7.536 mm)
opc  1

^CTraceback (most recent call last):
  File "run-vnafmr.py", line 74, in <module>
    vnafmr.fieldScan(8, 28, 0.1) 
  File "/scratch/


"""
