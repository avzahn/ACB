import time
import serial
import datetime
from px import *
from serial import Serial
import numpy as np

utcnow = datetime.datetime.utcnow

def wait(ms):
	t0 = time.time()
	while True:
		dt = time.time() - t0
		if (1000*dt) >= ms:
			return dt

def el_cos(amplitude,frequency,offset,el0, sample_rate):
	"""
	amplitude: degrees
	frequency: Hz
	el0: starting elevation; degrees
	sample_rate: Hz
	"""

	T = 1.0 / frequency
	nsamples = int(T * sample_rate)

	phase0 = np.arccos((el0-offset)/float(amplitude))

	phase = np.linspace(phase0,phase0+2*np.pi,nsamples)
	el = (amplitude * np.cos(phase)) + offset
	elrate = -amplitude * np.sin(phase)

	scan = []

	for i in range(nsamples):
		scan.append((360,el[i],0,elrate[i]))

	return scan

class tracker(object):

	def __init__(self, tty, scan):
		"""
		scan is a list of az,el,azrate,elrate
		tuples
		"""

		self.tty = tty
		self.scan = scan

		self.mode = 0
		self.idx = 0

		self.wait = 100

		self.sent = []
		self.recieved = []

	def send(self):

		if self.idx > len(self.self.scan)-1:
			self.idx = 0

		target = self.scan[self.idx]

		cmd = command()
		cmd.azpos = target[0]
		cmd.elpos = target[1]
		cmd.azrate = target[2]
		cmd.elrate = target[3]
		cmd.mode = self.mode

		cmdval = cmd.compose()
		self.tty.write(cmdval)

		self.sent.append((cmd,time.time()))

		wait(self.wait)

	def recv(self):
		rsp = self.tty.read(48)
		self.recieved.append((rsp,time.time()))
		return rsp

	def stop(self):

		self.mode = 1
		self.send()
		self.mode = 0

	def track(seconds):

		self.tty.write('CTAKE')
		self.tty.read(3)
		self.tty.write('TRACK_BEAM')
		self.tty.read(3)

		t0 = time.time()
		while time.time() - t0 < seconds:
			self.send()
			self.recv()
		self.stop()
