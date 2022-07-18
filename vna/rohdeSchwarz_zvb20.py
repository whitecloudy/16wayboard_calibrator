"""
Manual:
https://www.rohde-schwarz.com/webhelp/webhelp_zvb/start.htm
"""


import visa
import numpy as np
import matplotlib.pyplot as plt
import time

class zvb20():
	def __init__(self, host):
		rm = visa.ResourceManager()
		self.inst = rm.open_resource(host)
		print(self.inst.query("*IDN?"))
		
		self.numPts = 0
		self.power = 0 #dBm
		self.averages = 0
		self.bandwidth = 0

		self.setup()
		
	def setup(self):
		self.inst.write("*RST")
		self.inst.write(":SYSTEM:DISPLAY:UPDATE ON")
		
		self.inst.write("FORM REAL, 32") # change to 32 bit binary transfer format
		self.inst.write("SYST:COMM:GPIB:RTER EOI")

		self.setPower(10)
		self.setAverages(4)
		self.setBandwidth(5000)
		self.setNumPoints(601)

		self.inst.write(":INITIATE:CONTINUOUS OFF")
	
		
		
		""" configure s parameters to traces """
		self.inst.write("CALCulate1:PARameter:SDEFine 'Trc1', 'S12'")
		self.inst.write("CALCulate1:FORMat MLOG") 
		self.inst.write("CALCulate1:PARameter:SDEFine 'Trc2', 'S21'")
		self.inst.write("CALCulate1:FORMat MLOG") 
		self.inst.write("CALCulate1:PARameter:SDEFine 'Trc3', 'S11'")
		self.inst.write("CALCulate1:FORMat MLOG") 
		self.inst.write("CALCulate1:PARameter:SDEFine 'Trc4', 'S22'")
		self.inst.write("CALCulate1:FORMat MLOG") 

		self.inst.write("DISPlay:WINDow1:STATe ON")
		self.inst.write("DISPlay:WINDow2:STATe ON")
		#self.inst.write("DISPlay:WINDow3:STATe ON")
		#self.inst.write("DISPlay:WINDow4:STATe ON")

		""" what to show on the screen """
		self.inst.write("DISPlay:WINDow1:TRACe1:FEED 'Trc1'")
		self.inst.write("DISPlay:WINDow1:TRACe2:FEED 'Trc2'")  
		self.inst.write("DISPlay:WINDow2:TRACe1:FEED 'Trc3'")
		self.inst.write("DISPlay:WINDow2:TRACe2:FEED 'Trc4'") 
		
		
		self.inst.write("DISPlay:WINDow1:TRACe1:Y:OFFS 0")
		self.inst.write("DISPlay:WINDow1:TRACe2:Y:OFFS 0")
		
		""" wait until all functions complete before proceeding """
		self.inst.write("*OPC") 
		while int(self.inst.query("*ESR?")) != 1:
			print "waiting after setup"
			time.sleep(0.1)

	
	
			
	def getFrequency(self):
		freq = self.inst.query_binary_values("CALC1:DATA:STIM?", datatype='f', is_big_endian=False, container = np.array)
		return freq / 1.0e9
		
	def getData(self):
		sdata = self.inst.query_binary_values("CALC1:DATA:ALL? SDAT", datatype='f', is_big_endian=False, container = np.array)
		#print np.shape(s)

		s12, s21, s11, s22 = sdata.reshape((4, self.numPts*2), order="C")
		#s12, s21 = sdata.reshape((2, self.numPts*2), order="C")
		s12 = s12[0:self.numPts*2:2] + s12[1:self.numPts*2:2]*1j # separate real and imaginary parts
		s21 = s21[0:self.numPts*2:2] + s21[1:self.numPts*2:2]*1j # separate real and imaginary parts
		s11 = s11[0:self.numPts*2:2] + s11[1:self.numPts*2:2]*1j # separate real and imaginary parts
		s22 = s22[0:self.numPts*2:2] + s22[1:self.numPts*2:2]*1j # separate real and imaginary parts
		return [s12, s21, s11, s22]
	
	
	def doSweep(self):
		self.inst.write("INITiate1:IMMediate; *OPC")
		while int(self.inst.query("*ESR?")) != 1:
			time.sleep(0.2)

	
	
	
	def setAverages(self, avg):
		self.averages = avg
		if avg == 0:
			self.inst.write("INIT1:SCOP SING")
			self.inst.write("SENS1:AVER OFF")
		else:
			self.inst.write("SENS1:SWE:COUN %2d" % avg)
			self.inst.write("SENS1:AVER:COUN %2d" % avg)
			self.inst.write("SENS1:AVER ON")
			
			
	def setFrequency(self, start, stop):
		self.inst.write("SENS:FREQ:STAR %11d" % (start*1e9))
		self.inst.write("SENS:FREQ:STOP %11d" % (stop*1e9))
	
	
	def setNumPoints(self, num):
		self.numPts = num
		self.inst.write("SWE:POIN %4d" % num)
	
	def setPower(self, power):
		self.power = power
		self.inst.write("SOUR:POW %2d" % power)
		
	def setBandwidth(self, bandwidth):
		self.bandwidth = bandwidth
		self.inst.write("BAND %8d" % bandwidth) # measurement bandwidth
		

		
	
#print a.inst.query("CALCulate1:PARameter:CAT?")

