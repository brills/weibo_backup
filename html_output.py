# -*- coding: utf-8 -*-
from jinja2 import Environment, FileSystemLoader
import config
import sqlite

env = Environment(loader=FileSystemLoader('templates'))
print 'Reading SQLite file %s...' % config.sqlite_db
weibo_list = sqlite.fetch_all_weibo_from_db()
template = env.get_template('template.html')

html = template.render(weibo_list = weibo_list).encode('utf-8')
f = open(config.html_output, 'w+')
f.write(html)
f.close()

print 'Done. Use your browser to open %s' % config.html_output

#for w in weibo_list:
#	print w
