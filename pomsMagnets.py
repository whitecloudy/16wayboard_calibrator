import socket
import time

class vmag():
	def __init__(self, host="127.0.0.1", port=4042):
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.host, self.port))
		#self.sock.send(str.encode("*IDN?\n"))
		#print self.sock.recv(2056)
		self.theta = 0
		self.phi = 0
		self.positiveField = True
		
		self.name = "field"
		
		time.sleep(1)
		self.setAngle(0,0)
		self.setField(0)
		
		
	def setAngle(self, theta, phi):
		self.theta = theta
		self.phi = phi
		self.positiveField = True
		self.setFieldAngleRaw(theta, phi)
		
	def setFieldAngleRaw(self, theta, phi):
		cmd='setFieldDirection %(v1)10.2f %(v2)10.2f\n\r' % {'v1': theta, 'v2': phi}
		self.send(cmd)
		
	def setField(self,field):
		self.moveTo(field)
	
	def moveTo(self, field):
		if (field < 0.0) and self.positiveField:
			print "change field direction"
			self.positiveField = False
			self.setFieldAngleRaw(-self.theta, (self.phi+180)%360)
		if (field > 0.0) and not self.positiveField:
			print "change field direction back"
			self.positiveField = True
			self.setFieldAngleRaw(self.theta, self.phi)
			
		print "Field: %3.1f mT" % field
					
		field = field / 1000.0				#assume specified in mT rather than Tesla 
		cmd='setField %(v1)10.4f 600000000\n\r' %{'v1': abs(field)};
		self.send(cmd)
		time.sleep(2)						# wait for field to adjust
		
	def send(self, cmd):
		attempts = 0
		while (attempts < 3):
			try:
				self.sock.send(cmd) 
				reply = self.sock.recv(1024)
				if reply == "OK": break
				print "Magnet field set error:" + reply
			except:
				self.sock.close()
				self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.sock.connect((self.host, self.port))
			attempts = attempts + 1
		
		if (attempts == 3):
			raise RuntimeError("socket connection broken")

	
		
"""
theta=0, phi=0 : field along waveguide axis
theta=0, phi=90 : field along x-ray beam direction

theta=90, phi=0 : field towards ceiling

0.6 T is possible along principle x y z axes

temperature shutdown abouve 56 degrees

rest time should be added when current exceeds 55 A


# This works for all phi angles without overheating:
vna.setBandwidth(5000)
vna.setNumPoints(1024)
vna.setAverages(10)
vna.setFrequency(0.1, 20) 
vnafmr.fieldScan(0, 500, 10)  

# This works for all phi angles without overheating:
vna.setBandwidth(5000)
vna.setNumPoints(1024)
vna.setAverages(10)
vna.setFrequency(0.1, 20) 
vnafmr.fieldScan(-500, 500, 10)  with 1 min rest at 0



"""	

