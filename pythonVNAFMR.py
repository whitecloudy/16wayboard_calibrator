import numpy as np
import matplotlib.pyplot as plt
import time
import h5py
import os




from rohdeSchwarz_zvb20 import zvb20
#from pythonVNAFMR.anritsu import anritsu

from pomsMagnets import vmag as vmagClass
#from pythonVNAFMR.rasorMagnets import rasorMagnets
#from pythonVNAFMR.rasorTemperature import rasorTemperature



""" temperature configuration """
#rasorTemp = rasorTemperature()

""" field configuration """
#vmag = vmagClass("172.23.240.102", 4042) 				# POMS raspberry in the lab
vmag = vmagClass("172.23.110.103", 4042) 				# POMS raspberry in i10
#mag = rasorMagnets(a=28.58, t=9.06, y0=3.66)		# RASOR medium magnets
#mag = rasorMagnets(a=177.0, t=8.16, y0=18.1)		# RASOR big magnets


""" vna configuation """
vna = zvb20("TCPIP::192.168.0.3::INSTR")


directory = ""


def setDirectory(newDirectory):
    global directory
    directory = newDirectory
    if not os.path.exists(directory):
        print "Directory doesn't exist -> creating %s" % directory
        os.makedirs(directory)


def dummyScan():
    global directory
    print directory
    
    
    
def scan(axis, start, stop, step, vna, reference=None):
	global directory
    
	if (stop > start) :
		positions = np.arange(start, (stop+0.1), step)			# 0.1 extra so stop is included
	else:
		positions = np.arange(start, (stop-0.1), step)			# 0.1 extra so stop is included		
			
	count = np.loadtxt("C:\\Users/poms/Documents/scanCounter.dat", dtype="d")
	count = count + 1
	np.savetxt("C:\\Users/poms/Documents/scanCounter.dat", [count], fmt="%06d")
	
	#path = open('./filePath.dat', 'r').read()
	print "Starting scan %s #%06d" % (directory, count)
	f = h5py.File(directory + "/poms-vnafmr-%06d.hdf5" % count, "w", libver='latest')
		
		
	vna.doSweep()
	freq = vna.getFrequency()
	freqPts = len(freq)
	#freqPts = self.freqPts

	grp = f
	grp.create_dataset('freq', data=freq)
	grp.create_dataset('s12', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)
	grp.create_dataset('s21', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)
	grp.create_dataset('s11', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)
	grp.create_dataset('s22', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)

	grp.create_dataset('s12r', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)
	grp.create_dataset('s21r', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)
	grp.create_dataset('s11r', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)
	grp.create_dataset('s22r', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)

	grp.swmr_mode = True
		
		

	# metadata
	f.attrs['power'] = vna.power 
	f.attrs['bandwidth'] = vna.bandwidth
	f.attrs['averages'] = vna.averages 
	f.attrs['theta'] = axis.theta 
	f.attrs['phi'] = axis.phi 
	
	
	f.create_dataset(axis.name, (0,), chunks=(1,), maxshape=(None,))

	
	for position in positions:
		i = np.shape(f[axis.name])[0]
		
		if reference != None:
			axis.moveTo(position)
			time.sleep(2)
			vna.doSweep()
			s12, s21, s11, s22 = vna.getData()
			f['s12r'].resize((i+1, freqPts))
			f['s12r'][i,:] = s12
			
			
		axis.moveTo(position)			
		time.sleep(2)
		vna.doSweep()
		s12, s21, s11, s22 = vna.getData()

		#freqPts = freqPts
		f['s12'].resize((i+1, freqPts))
		#f['s21'].resize((i+1, freqPts))
		#f['s11'].resize((i+1, freqPts))
		#f['s22'].resize((i+1, freqPts))

		f['s12'][i,:] = s12
		#f['s21'][i,:] = s21
		#f['s11'][i,:] = s11
		#['s22'][i,:] = s22
		
		
	
		f[axis.name].resize((i+1,))
		f[axis.name][i] = position
		f.flush()
		
	f.close()
		

		
		
		
		
		
		
		
		
		
		
		
		
		

class vnafmrClass():
	def __init__(self, vna, mag, path):
		self.vna = vna
		self.mag = mag
		self.path = path
		
		self.f = None
		self.freqPts = 0
		
	def startNewScan(self):
		pass

	def measureRef(self):
		#self.mag.setField(500)
		self.vna.doSweep()
		#freq = self.vna.getFrequency()
		#self.freqPts = len(freq)
		
		self.vna.inst.write("CALCULATE1:PARAMETER:SELECT 'Trc1'")
		#self.vna.inst.write("CORR:LOSS:AUTO ONCE")					# auto length and loss correction
		self.vna.inst.write("CORR:EDEL:AUTO ONCE")
		
		self.f.attrs['electrical_length'] = self.vna.inst.query("CORRection:EDELay1:ELENgth?")
		print "the electrical length is " + self.f.attrs['electrical_length']

		#self.vna.inst.write("DISP:WIND1:TRAC1:Y:BOTT 0; TOP 20")	# set the screen scale 
		#self.vna.inst.write("DISP:WIND1:TRAC1:Y:RLEV 0")			# reference value
		#self.vna.inst.write("DISP:WIND1:TRAC1:Y:RPOS 0")			# reference position
		self.vna.inst.write("DISPlay:WINDow1:TRACe1:Y:SCALe:AUTO ONCE") 			# autoscale
		
		#self.vna.inst.write("CALCULATE1:PARAMETER:SELECT 'Trc2'")
		#self.vna.inst.write("CORR:LOSS:AUTO ONCE")
		
		#self.vna.inst.write("DISP:WIND2:TRAC1:Y:BOTT 0; TOP 20")	# set the screen scale 
		#self.vna.inst.write("DISP:WIND2:TRAC1:Y:RLEV 0")			# reference value
		#self.vna.inst.write("DISP:WIND2:TRAC1:Y:RPOS 0")			# reference position
		self.vna.inst.write("DISPlay:WINDow2:TRACe1:Y:SCALe:AUTO ONCE")
		
		#s12r, s21r, s11r, s22r = self.vna.getData()
			

		#i = np.shape(self.f['s12r'])[0]
		#self.f['s12r'].resize((i+1, self.freqPts))
		#self.f['s21r'].resize((i+1, self.freqPts))
		#self.f['s11r'].resize((i+1, self.freqPts))
		#self.f['s22r'].resize((i+1, self.freqPts))
			
		#self.f['s12r'][i,:] = s12r
		#self.f['s21r'][i,:] = s21r
		#self.f['s11r'][i,:] = s11r
		#self.f['s22r'][i,:] = s22r
		
	def fieldScan(self, start, stop, step):
		self.scanStart()
		self.measureRef()
		if (stop > start) :
			fields = np.arange(start, (stop+0.1), step)			# 0.1 extra so stop is included
		else:
			fields = np.arange(start, (stop-0.1), step)			# 0.1 extra so stop is included		
		self.f.create_dataset('field', (0,), chunks=(1,), maxshape=(None,))
		
		self.f.attrs['power'] = self.vna.power 
		self.f.attrs['bandwidth'] = self.vna.bandwidth
		self.f.attrs['averages'] = self.vna.averages 
		
		self.f.attrs['theta'] = self.mag.theta 
		self.f.attrs['phi'] = self.mag.phi 
		
		for field in fields:
			self.mag.setField(field)			
			time.sleep(2)
			
			i = np.shape(self.f['field'])[0]
			self.scanStep(i)
			self.f['field'].resize((i+1,))
			self.f['field'][i] = field
			self.f.flush()
			
		self.f.close()
		
		
	def fieldScanWithReference(self, start, stop, step, refField):
		self.scanStart()
		#self.measureRef()
		if (stop > start) :
			fields = np.arange(start, (stop+0.1), step)			# 0.1 extra so stop is included
		else:
			fields = np.arange(start, (stop-0.1), step)			# 0.1 extra so stop is included		
		self.f.create_dataset('field', (0,), chunks=(1,), maxshape=(None,))
		
		self.f.attrs['power'] = self.vna.power 
		self.f.attrs['bandwidth'] = self.vna.bandwidth
		self.f.attrs['averages'] = self.vna.averages 
		
		self.f.attrs['theta'] = self.mag.theta 
		self.f.attrs['phi'] = self.mag.phi 
		
		for field in fields:
			i = np.shape(self.f['field'])[0]
			
			self.mag.setField(refField)			
			time.sleep(2)
			self.refStep(i)			
			
			self.mag.setField(field)			
			time.sleep(2)
			self.scanStep(i)
			
			self.f['field'].resize((i+1,))
			self.f['field'][i] = field
			self.f.flush()
			
		self.f.close()
		
	def dummyScan(self,steps):
		self.scanStart()
		dummy = np.arange(1, steps, 1)
		self.f.create_dataset('dummy', (0,), chunks=(1,), maxshape=(None,))
		
		for d in dummy:
			print "dummy: %4d " % d
			i = np.shape(self.f['dummy'])[0]
			self.f['dummy'].resize((i+1,))
			self.scanStep(i)
			self.f.flush()
	

	def tempScan(self, start, stop, rate):
		from rasorTemperature import rasorTemperature
		rasorTemp = rasorTemperature()

		rasorTemp.waitForStableTemp(start)	

		self.scanStart()
		self.f.create_dataset('waveguide_temp', (0,), chunks=(1,), maxshape=(None,))
		self.f.create_dataset('cryo_temp', (0,), chunks=(1,), maxshape=(None,))


		
		rasorTemp.startSweep(start, stop, rate)
			
		while rasorTemp.isSweepRunning():

			i = np.shape(self.f['waveguide_temp'])[0]
			self.scanStep(i)
			waveguide, cryo = rasorTemp.getTemp()
			self.f['waveguide_temp'].resize((i+1,))
			self.f['cryo_temp'].resize((i+1,))
			self.f['waveguide_temp'][i] = waveguide
			self.f['cryo_temp'][i] = cryo
			self.f.flush()

			print "temp: %0.2f mT" % waveguide
		rasorTemp.setTemp(stop)
		self.f.close()
			
	
	
	def scanStart(self):
		pass

		

		

		
		
	def scanStep(self, i):
		pass
		
	def refStep(self, i):
		self.vna.doSweep()
		s12, s21 = self.vna.getData()
		grp = self.f
		freqPts = self.freqPts
		grp['s12r'].resize((i+1, freqPts))
		grp['s21r'].resize((i+1, freqPts))

		grp['s12r'][i,:] = s12
		grp['s21r'][i,:] = s21
		



		
	


		
		
		



