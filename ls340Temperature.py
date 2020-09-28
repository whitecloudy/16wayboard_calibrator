import epics
import numpy as np
import time



class ls340Temperature():
	def __init__(self):
		self.threshold = 0.5
		self.thresholdTime = 30

		self.stopT = 0
		self.startT = 0

		self.setTemp = 0;


	def asynchronousMoveTo(self, temp):
		self.setTemp = temp
		epics.caput("ME01D-EA-TCTRL-01:RAMPST_S", 0)	# ramp off
		time.sleep(1)
		epics.caput("ME01D-EA-TCTRL-01:RAMPST_S", 0)	# ramp off
		time.sleep(1)
		epics.caput("ME01D-EA-TCTRL-01:RANGE_S", 5)	# 50 W heater range
		time.sleep(1)
		epics.caput("ME01D-EA-TCTRL-01:RANGE_S", 5)	# 50 W heater range
		time.sleep(1)
		epics.caput("ME01D-EA-TCTRL-01:SETP_S", self.setTemp)	# settle at startT K
		time.sleep(1)
		epics.caput("ME01D-EA-TCTRL-01:SETP_S", self.setTemp)	# settle at startT K
		time.sleep(1)



	def moveTo(self, temp):
		self.asynchronousMoveTo(temp)
		self.waitWhileBusy()

	def waitWhileBusy(self):
		okTime = time.time()
		print "waiting for temperature to reach %0.2f K" % self.setTemp
		while True:
			if abs(epics.caget("ME01D-EA-TCTRL-01:KRDG1") - self.setTemp) > self.threshold:
				okTime = time.time()
			
			if (time.time() - okTime) > self.thresholdTime:
				break
			time.sleep(1)
		time.sleep(1)
		print "temp stable at %0.2f K" % self.setTemp


	def getTemp(self):
		return [epics.caget("ME01D-EA-TCTRL-01:KRDG0"),epics.caget("ME01D-EA-TCTRL-01:KRDG1")]


	def startSweep(self, startT, stopT, rate):
		self.stopT = stopT
		self.startT = startT
	
		""" start increasing ramp """
		epics.caput("ME01D-EA-TCTRL-01:RAMP_S", rate)	# ramp rate
		time.sleep(1)
		epics.caput("ME01D-EA-TCTRL-01:RAMP_S", rate)	# ramp rate
		time.sleep(1)
		epics.caput("ME01D-EA-TCTRL-01:RAMPST_S", 1)	# ramp on
		time.sleep(1)
		cepicsa.caput("ME01D-EA-TCTRL-01:RAMPST_S", 1)	# ramp on
		time.sleep(1)
		if stopT > startT:
			epics.caput("ME01D-EA-TCTRL-01:SETP_S", stopT + 5)	# set to stop T
			time.sleep(1)
			epics.caput("ME01D-EA-TCTRL-01:SETP_S", stopT + 5)	# set to stop T
			time.sleep(1)
		else:
			epics.caput("ME01D-EA-TCTRL-01:SETP_S", stopT - 5)	# set to stop T
			time.sleep(1)
			epics.caput("ME01D-EA-TCTRL-01:SETP_S", stopT - 5)	# set to stop T
			time.sleep(1)

	def isSweepRunning(self):

		if (epics.caget("ME01D-EA-TCTRL-01:KRDG0") < self.stopT and self.stopT > self.startT):
			return True
		if (epics.caget("ME01D-EA-TCTRL-01:KRDG0") > self.stopT and self.stopT < self.startT):
			return True
		print "reached end of temp sweep"
		return False
		

