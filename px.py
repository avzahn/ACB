from bitstring import BitStream, Bits

class command(object):

	def __init__(self, *args, **kwargs):

		self.bits = BitStream(int=0,length=128)
		self.val = ''

		if kwargs == None:
			self.header = 0
			self.azrate = 0
			self.elrate = 0
			self.mode = 0
			self.azpos = 0
			self.elpos = 0
			self.ck = 0
		else:
			for kw in kwargs:
				self.__dict__[kw] = kwargs[kw]

			if self.val != '':
				self.from_val(self.val)
		if len(args) == 1:
			self.from_val(args[0])

	def from_val(self,val):

		val = val.replace(' ','')

		self.header = int(val[4:8],16)
		self.azrate = decode_azelrate(val[8:12])
		self.elrate = decode_azelrate(val[12:16])
		self.mode = int(val[16:18],16)
		self.azpos = decode_azpos(val[18:24])
		self.elpos = decode_elpos(val[24:30])
		self.ck = int(val[30:32],16)

		self.val = val

	def compose(self):
		
		_header = Bits(uint=self.header,length=16)
		_azrate = encode_azelrate(self.azrate)
		_elrate = encode_azelrate(self.elrate)
		_mode = Bits(uint=self.mode,length=8)
		_azpos = encode_azpos(self.azpos)
		_elpos = encode_elpos(self.elpos)

		bits = self.bits

		bits[0:16] = Bits('0x5058')
		bits[16:32] = _header
		bits[32:48] = _azrate
		bits[48:64] = _elrate
		bits[64:72] = _mode
		bits[72:96] = _azpos
		bits[96:120] = _elpos
		bits[120:128] = self.checksum()

		self.val = bits.hex

		return self.val

	def checksum(self):
		bits = self.bits
		ck = bits[0:8]

		for i in range(8,120,8):

			ck ^= bits[i:i+8]

		self.ck = ck.uint
		return ck

	def banner(self):

		s="HEADER AZRATE ELRATE MODE AZPOS   ELPOS  CHECKSUM"
		return s

	def __str__(self):
		bits = self.bits
		l0 = "%s   %s   %s   %s   %s  %s %s\n" % (
			bits[16:32].hex,
			bits[32:48].hex,
			bits[48:64].hex,
			bits[64:72].hex,
			bits[72:96].hex,
			bits[96:120].hex,
			bits[120:128].hex)
		l1= "%i      %1.3f  %1.3f  %02i   %3.3f %2.3f %i" %(
			self.header,
			self.azrate,
			self.elrate,
			self.mode,
			self.azpos,
			self.elpos,
			self.ck)

		return l0+l1

def encode_azelrate(degs):
	RRV = degs
	SRV = int(round( (RRV/16.0) * 2.0**15 ))
	return Bits(int=SRV, length=16)

def decode_azelrate(SRV):
	SRV = SRV.int
	RRV = 16.0 * (SRV/2.0**15)
	return RRV

def encode_azpos(deg):
	RAPV = deg
	SAPV = int(round( (RAPV/180.0) * 2.0**23 ))
	return Bits(uint=SAPV, length=24)

def decode_azpos(SAPV):
	SAPV = SAPV.uint
	RAPV = 180.0 * (SAPV/(2.0**23))
	return RAPV

def encode_elpos(deg):
	REPV = deg
	if REPV < 0.0:
		SEPV =int(round( ((REPV-360.0)/180.0) * 2.0**23))
	else:
		SEPV = int(round((REPV/180.0) * 2.0**23))
	return Bits(int=SEPV, length=24)

def decode_elpos(SEPV):
	SEPV = SEPV.int
	if SEPV > 0:
		REPV = 360.0 + (180.0*(SEPV/2.0**23))
	else:
		REPV = (180.0*(SEPV/2.0**23))
	return REPV

def decode_time(t):
	return t.float

def extract_pxreport(stream):
	PX = Bits(hex='5058')
	idx = list(stream.findall(PX))

	if len(idx) % 2:
		idx = idx[:-1]

	arrays = []
	for i in range(len(idx)-2):
		arrays.append(stream[idx[i]:idx[i+1]])
	return arrays


