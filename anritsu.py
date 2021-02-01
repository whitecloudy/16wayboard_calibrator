"""
class file for ANRITSU MS46122A VNA

David Burn

Edit : Whitecloudy
"""


import socket
import struct
import numpy as np


class anritsu():
	def __init__(self, host):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((host, 5001))
		print("socket setup")
		self.sock.send(str.encode("*IDN?\n"))
		print(self.sock.recv(2056))


		self.bandwidth = None
		self.setup()


	def query(self, message):
		self.sock.send(str.encode(message+"\n"))
		return self.sock.recv(2056)

	def write(self, message):
		self.sock.send(str.encode(message+"\n"))


	def setup(self):
		""" display layout settings """
		self.write("CALCulate1:PARameter1:DEFine S11")
		self.write("CALCulate1:PARameter1:FORMat MLOGarithmic")
		

		self.write("CALCulate1:PARameter2:DEFine S21")
		self.write("CALCulate1:PARameter2:FORMat MLOGarithmic")

		self.write("CALCulate1:PARameter3:DEFine S22")
		self.write("CALCulate1:PARameter3:FORMat MLOGarithmic")

		self.write("CALCulate1:PARameter4:DEFine S12")
		self.write("CALCulate1:PARameter4:FORMat MLOGarithmic")

		self.write("SENSe:HOLD:FUNCtion HOLD")		# single sweep and hold

		""" data transfer settings """
		self.write(":FORMat:DATA REAL")				# ASC, REAL or REAL32
		self.write(":FORMat:BORDer SWAP")			# MSB/LSB: Normal or Swapped
		
		self.setFrequency(0.900,0.910)
		self.setNumPoints(10)
		self.setBandwidth(40000) 
		print(self.query("SYST:ERR?"))				#returns "No Error"




	def getData(self):
		s11 = self.getTrace(1)	#S11
		s21 = self.getTrace(2)	#S21
		s22 = self.getTrace(3)	#S22
		s12 = self.getTrace(4)	#S12
		return [s11,s21,s22,s12]

 



	def getTrace(self, par):
		# floating point with 8 bytes / 64 bits per number
		self.write("SYST:ERR:CLE")
		self.query("*OPC?")

		print(self.query("SYST:ERR?"))				#returns "No Error"

		self.sock.send(str.encode("CALC1:PAR%1d:SEL\n" % par))
		print(self.query("CALC1:PAR:SEL?").decode("utf-8"))
		self.query("*OPC?")

		self.write(":CALC1:DATA:SDAT?")	#works

		head =  self.sock.recv(2)				# header part 1
		head = head.decode("utf-8")
		head =  self.sock.recv(int(head[1]))	# header part 2
		MSGLEN = int(head)			# extrace message len from header
		chunks = []
		bytes_recd = 0
		while bytes_recd < MSGLEN:
			chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
			chunks.append(chunk)
			bytes_recd = bytes_recd + len(chunk)
		data = b''.join(chunks)

		extra = self.sock.recv(2048)
		#print(len(extra))
		#print(chr(extra))

		#print len(data), " bytes, ", len(data)/8, " numbers"

		num = len(data) / 8
		[data,] = struct.unpack('%dd' % num, data),
		
		return  complex(np.array(data[::2])   + np.array(data[1::2])*1j)



	def getFrequency(self):
		self.write("SYST:ERR:CLE")

		self.write(":SENSe:FREQuency:DATA?")
		head =  self.sock.recv(2)				# header part 1
		head =  self.sock.recv(int(head[1]))			# header part 2
		MSGLEN = int(head)			# extrace message len from header

		chunks = []
		bytes_recd = 0
		while bytes_recd < MSGLEN:
			chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
			chunks.append(chunk)
			bytes_recd = bytes_recd + len(chunk)
		data = b''.join(chunks)

		#print len(data), " bytes, ", len(data)/8, " numbers"

		extra = self.sock.recv(2048)

		num = len(data) / 8
		[data,] = struct.unpack('%dd' % num, data),
		return np.array(data)/1e9


	def doSweep(self):
		self.write("SYST:ERR:CLE")
		opc = self.query("*OPC?")
		print("opc ", opc)

		self.write("TRIG:SING")
		# there is a wait here until anritsu has finished collecting
		err = self.query("SYST:ERR?")
		print("err ", err)



	def setFrequency(self, start, stop):
		""" frequency settings """
		start = start*1.0e9
		stop = stop*1.0e9
		self.write("SENS:FREQ:STAR %d" % start)
		self.write("SENS:FREQ:STOP %d" % stop)



	def setBandwidth(self,bandwidth):
		self.bandwidth = bandwidth
		self.write("SENS:BAND %6d" % bandwidth)				# IFBW Frequency (Hz)

	def setNumPoints(self,num):
		self.write("SENS:SWEEP:POINT %4d" % num)		




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
