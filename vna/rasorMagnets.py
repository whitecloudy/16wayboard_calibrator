import numpy as np
import time
import epics as CAClient


class motor():
	def __init__(self, rootPV, axis):
		self.rootPV = rootPV + ":" + axis
		#self.ca = EpicsDevice()

		self.ca = CAClient

	def moveTo(self, position):
		#print "move to ", position
		self.ca.caput(self.rootPV + ".VAL", position)

		self.waitWhileBusy()

	def asynchronousMoveTo(self, position):
		#print "move to ", position
		self.ca.caput(self.rootPV + ".VAL", position)

	def waitWhileBusy(self):
		while self.ca.caget(self.rootPV +".DMOV") != 1:
			time.sleep(0.1)



class rasorMagnets():
	def __init__(self, a,t,y0):
		self.emecy1 = motor("ME01D-EA-EMEC-01","Y1")
		self.emecy2 = motor("ME01D-EA-EMEC-01","Y2")
		self.emecpitch = motor("ME01D-EA-EMEC-01","PITCH")

		self.a = a
		self.t = t
		self.y0 = y0


	def setField(self, field):
		if (field == 0):
			fieldmm = 19.8
		else:
			fieldmm = -self.t * np.log((field - self.y0) / self.a)

		if (fieldmm >= 20.0) or (fieldmm <= 1.0): 
			print "out of range"
			raise ValueError('Magnet field is out of range')

		print "set the field: %0.3f mT (%0.3f mm)" % (field, fieldmm)
		self.emecy1.asynchronousMoveTo(-fieldmm)
		self.emecy2.asynchronousMoveTo(fieldmm)
		self.emecy1.waitWhileBusy()
		self.emecy2.waitWhileBusy()

	def setAngle(self, angle):
		self.emecpitch.asynchronousMoveTo(angle)
		self.emecpitch.waitWhileBusy()



"""
medium magnets
a = 28.58
t = 9.06
y0 = 3.66

big magnets
a = 177
t = 8.16
y0 = 18.1
"""
