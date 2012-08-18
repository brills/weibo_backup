#!/bin/env python2
# -*- coding: utf-8 -*-
import urllib2
import re
from config import *
from bs4 import BeautifulSoup
from datetime import datetime
from Weibo import Weibo

def get_max_page(soup):
	return int(soup.find_all('input', attrs = {'name':'mp'})[0].get('value'))

def purge(soup):
	re_comment = '/comment/.*'
	re_repost = '/repost/.*'
	re_fav = '/fav/.*'
	re_topblog = '/mblog/topmblog\?.*'
	re_delblog = '/mblog/del\?.*'
	cr_del = re.compile(re_comment + '|' + re_repost + '|' + re_fav + '|' + re_topblog + '|' + re_delblog)
	l = soup.find_all('div',attrs = {'class':'c'})
	
	for c in l:
	#	print c.prettify()
		#purge function links
		garbage = c.find_all('a', attrs = {'href':cr_del})
		for g in garbage: 
			g.decompose()

		#purge non-weibo c-class
		if len(c.find_all('div')) == 0:
			c.decompose()
			
#	print soup.find_all('div', attrs = {'class':'c'})
		
def extract(soup):
	cr_pic = re.compile('/mblog/oripic\?.*')
	weibo_on_page = []
	l = soup.find_all('div',attrs = {'class':'c'})
	print 'Extracting %d Weibo(s)...' % len(l)
	
	for c in l:
#		print c.prettify()
		flag = 0
		div_list = c.find_all('div', recursive = False)
		cmt = div_list[0].find_all('span', attrs = {'class':'cmt'}, recursive = False)
		if len(cmt) > 0:
			cmt = cmt[0]
		ctt = div_list[0].find_all('span', attrs = {'class':'ctt'}, recursive = False)[0]
		# no comment no pic
		if len(div_list) == 1:
			ct = div_list[0].find_all('span', attrs = {'class':'ct'}, recursive = False)[0]
			weibo_on_page.append(Weibo(None, ''.join([i for i in ctt.strings]), None, None, ''.join(ct.stripped_strings), flag))

		# either comment or pic but not both
		elif len(div_list) == 2:
			# comment only
			if cmt:
				flag |= Weibo.IS_FWD
				fwd_from = ''.join([i for i in cmt.strings])
				ct = div_list[1].find_all('span', attrs = {'class':'ct'}, recursive = True)[0]
				ct_str = ''.join(ct.stripped_strings)
				ct.decompose()
				#print div_list[1].strings
				reason = ''.join([i for i in div_list[1].strings])
				weibo_on_page.append(Weibo(fwd_from, ''.join([i for i in ctt.strings]), None, reason , ct_str, flag))
				continue
			else:
				flag |= Weibo.HAS_PIC
				pic = div_list[1].find_all('a', attrs = {'href':cr_pic})[0]
				pic = pic.get('href')
				ct = div_list[1].find_all('span', attrs = {'class':'ct'}, recursive = True)[0]
				ct_str = ''.join(ct.stripped_strings)
				ct.decompose()
				weibo_on_page.append(Weibo(None, ''.join([i for i in ctt.strings]), pic, None , ct_str, flag))
				continue
		elif len(div_list) == 3:
			flag |= Weibo.IS_FWD | Weibo.HAS_PIC
			fwd_from = ''.join([i for i in cmt.strings])
			pic = div_list[1].find_all('a', attrs = {'href':cr_pic})[0]
			pic = pic.get('href')
			ct = div_list[2].find_all('span', attrs = {'class':'ct'}, recursive = False)[0]
			ct_str = ''.join(ct.stripped_strings)
			ct.decompose()
			reason = ''.join([i for i in div_list[2].strings])
			weibo_on_page.append(Weibo(fwd_from, ''.join([i for i in ctt.strings]), pic, reason , ct_str, flag))
			

	return weibo_on_page
				
			
#time format / forward format
def adjust_format(weibo_list):

	time_fmt_list = ['%m月%d日 %H:%M', '%Y-%m-%d %H:%M:%S']
	for weibo in weibo_list:
		# process the 'time' string
		# example: 2011-05-02 23:23:22 来自Android客户端
		# example 2: 01月09日 21:23 来自iPad客户端
		time_str_end = weibo.time.find(u'来自');

		if time_str_end == -1:
			time_str_end = len(weibo.time)

		success = False

		for fmt in time_fmt_list:
			try:
				time = datetime.strptime(weibo.time[0:time_str_end - 1].encode('utf-8'),fmt)
				success = True
				continue
			except ValueError:
				# XXX: ugly patch for ugly weibo output
				if weibo.time.find(u'今天') != -1:
					success = True
					time = datetime.strptime(weibo.time[3:time_str_end - 1].encode('utf-8'), '%H:%M')
					today = datetime.today()
					time = time.replace(year = today.year, month = today.month, day = today.day)
					continue

				if weibo.time.find(u'29日') != -1:
					success = True
					today = datetime.today()
					time = datetime.strptime((u'2012年'+weibo.time[0:time_str_end - 1]).encode('utf-8'),'%Y年%m月%d日 %H:%M')
					continue

				if weibo.time.find(u'分钟') != -1 or weibo.time.find(u'小时') != -1:
					success = True
					time = datetime.today()

				pass
				#print 'time string: %s parsed error on fmt string %s' % (weibo.time[0:time_str_end - 1].encode('utf-8'), fmt)

		weibo.from_client = weibo.time[time_str_end + 2 :]
		if success:
			if time.year == 1900:
				time = time.replace(year = datetime.today().year)
			weibo.time = time 
		else:
			print "Warning: unknown time format in weibo: " + str(weibo)

		# process the 'forward from' and 'forward reason' string
		# example of 'forward from': 转发了 程序员的那些事 的微博:
		# example of 'forward reason': 转发理由://@IT程序猿:#开源风暴# 对于开源许可证，你都了解了吗？
		if weibo.flag & Weibo.IS_FWD != 0:
			weibo.fwd_from = weibo.fwd_from[4:-4]
			weibo.fwd_reason = weibo.fwd_reason[5:]
		

def run():
	req = urllib2.Request(baseurl)
	req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.2')
	f = urllib2.urlopen(req)
	soup = BeautifulSoup(f.read())
	f.close()
	mp = get_max_page(soup)
#	mp = 1
	print 'Max page number: %d\n' % mp
	r = []
	for i in range(1, mp + 1):
		print "Processing page %d" % i
		url = baseurl + '&page=%d' % i
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.2')
		f = urllib2.urlopen(req)
		soup = BeautifulSoup(f.read())
		purge(soup)
		r += extract(soup)

	adjust_format(r)
	return r
	
