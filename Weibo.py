class Weibo(object):
	IS_FWD = 1
	HAS_PIC = 2
	def __init__(self, fwd_from, contents, pic, fwd_reason, time, flag, from_client = None):
		self.fwd_from = fwd_from
		self.contents = contents
		self.pic = pic
		self.fwd_reason = fwd_reason
		self.time = time
		self.flag = flag
		self.from_client = from_client

	def __str__(self):
		r = 'time: %s\n' % self.time
		if self.flag & Weibo.IS_FWD != 0:
			r += "fwd from: %s\nfwd reason: %s\n" % (self.fwd_from, self.fwd_reason)
		if self.flag & Weibo.HAS_PIC != 0:
			r += "pic: %s\n" % self.pic
		r += 'contents: %s\n' % self.contents
		if self.from_client:
			r += 'from_client: %s\n' % self.from_client

		return r.encode('utf-8')


