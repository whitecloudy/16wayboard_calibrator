from beamline import device
import numpy as np
import time



class rasorTemperature():
	def __init__(self):
		self.ca = device()
		self.threshold = 0.5
		self.thresholdTime = 30

		self.stopT = 0
		self.startT = 0

	def setTemp(self,temp):
		self.ca.caput("ME01D-EA-TCTRL-01:RAMPST_S", 0)	# ramp off
		time.sleep(1)
		self.ca.caput("ME01D-EA-TCTRL-01:RAMPST_S", 0)	# ramp off
		time.sleep(1)
		self.ca.caput("ME01D-EA-TCTRL-01:RANGE_S", 5)	# 50 W heater range
		time.sleep(1)
		self.ca.caput("ME01D-EA-TCTRL-01:RANGE_S", 5)	# 50 W heater range
		time.sleep(1)
		self.ca.caput("ME01D-EA-TCTRL-01:SETP_S", temp)	# settle at startT K
		time.sleep(1)
		self.ca.caput("ME01D-EA-TCTRL-01:SETP_S", temp)	# settle at startT K
		time.sleep(1)


	def waitForStableTemp(self,temp):
		self.setTemp(temp)
		okTime = time.time()
		print "waiting for temperature to reach %0.2f K" % temp
		while True:
			if abs(self.ca.caget("ME01D-EA-TCTRL-01:KRDG0") - temp) > self.threshold:
				okTime = time.time()
			
			if (time.time() - okTime) > self.thresholdTime:
				break
			time.sleep(1)
		time.sleep(1)
		print "temp stable at %0.2f K" % temp


	def getTemp(self):
		return [self.ca.caget("ME01D-EA-TCTRL-01:KRDG0"),self.ca.caget("ME01D-EA-TCTRL-01:KRDG1")]


	def startSweep(self, startT, stopT, rate):
		self.stopT = stopT
		self.startT = startT
		ca = device()		
		""" start increasing ramp """
		ca.caput("ME01D-EA-TCTRL-01:RAMP_S", rate)	# ramp rate
		time.sleep(1)
		ca.caput("ME01D-EA-TCTRL-01:RAMP_S", rate)	# ramp rate
		time.sleep(1)
		ca.caput("ME01D-EA-TCTRL-01:RAMPST_S", 1)	# ramp on
		time.sleep(1)
		ca.caput("ME01D-EA-TCTRL-01:RAMPST_S", 1)	# ramp on
		time.sleep(1)
		if stopT > startT:
			ca.caput("ME01D-EA-TCTRL-01:SETP_S", stopT + 5)	# set to stop T
			time.sleep(1)
			ca.caput("ME01D-EA-TCTRL-01:SETP_S", stopT + 5)	# set to stop T
			time.sleep(1)
		else:
			ca.caput("ME01D-EA-TCTRL-01:SETP_S", stopT - 5)	# set to stop T
			time.sleep(1)
			ca.caput("ME01D-EA-TCTRL-01:SETP_S", stopT - 5)	# set to stop T
			time.sleep(1)

	def isSweepRunning(self):
		ca = device()
		if (ca.caget("ME01D-EA-TCTRL-01:KRDG0") < self.stopT and self.stopT > self.startT):
			return True
		if (ca.caget("ME01D-EA-TCTRL-01:KRDG0") > self.stopT and self.stopT < self.startT):
			return True
		print "reached end of temp sweep"
		return False
		

