import sqlite3
import datetime
import config
from Weibo import Weibo



def create_tables(cur):
	cur.execute('''create table weibo_main(
				id integer primary key autoincrement,
				time timestamp,
				contents text,
				from_client text
			)''')
	cur.execute('''create table weibo_fwd(
			id integer,
			fwd_from text,
			fwd_reason text,
			foreign key(id) references weibo_main(id)
			)''')

	cur.execute('''create table weibo_pic(
			id integer,
			pic_link, text,
			foreign key(id) references weibo_main(id)
			)''')



def insert_weibo(cur, weibo):
	cur.execute('insert into weibo_main(time, contents, from_client) values(?,?,?)',
			(weibo.time, weibo.contents, weibo.from_client))
	inserted_id = cur.lastrowid
	if weibo.flag & Weibo.IS_FWD != 0:
		cur.execute('insert into weibo_fwd(id, fwd_from, fwd_reason) values(?,?,?)',
				(inserted_id, weibo.fwd_from, weibo.fwd_reason))

	if weibo.flag & Weibo.HAS_PIC != 0:
		cur.execute('insert into weibo_pic(id, pic_link) values(?,?)',
				(inserted_id, weibo.pic))
		
def dump_db():
	conn = sqlite3.connect(config.sqlite_db, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
	cur = conn.cursor()
	cur.execute('''select time, contents, from_client, fwd_from, fwd_reason, pic_link 
		from weibo_main 
		left outer join weibo_fwd on weibo_main.id = weibo_fwd.id
		left outer join weibo_pic on weibo_main.id = weibo_pic.id''')
	r = cur.fetchall()
	for i in r:
		for j in i:
			if type(j) == datetime.datetime:
				print j
			elif j:
				print j.encode('utf-8')
			else:
				print ''
		print '----'

	
def insert_into_new_db(weibo_list):
	conn = sqlite3.connect(config.sqlite_db, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
	cur = conn.cursor()
	create_tables(cur)
	for weibo in weibo_list:
		insert_weibo(cur, weibo)
	conn.commit()
	cur.close()
	conn.close()


def test(weibo_list):
	conn = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
	cur = conn.cursor()
	create_tables(cur)
	for weibo in weibo_list:
		insert_weibo(cur, weibo)
	dump_db(cur)

def fetch_all_weibo_from_db(db = config.sqlite_db):
	conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
	cur = conn.cursor()
	cur.execute('''select time, contents, from_client, fwd_from, fwd_reason, pic_link 
		from weibo_main 
		left outer join weibo_fwd on weibo_main.id = weibo_fwd.id
		left outer join weibo_pic on weibo_main.id = weibo_pic.id''')
	r = cur.fetchall()
	return [Weibo(
		i[3], # fwd_from
		i[1], # contents
		i[5], #pic
		i[4], # fwd_reason
		i[0], # time
		0 | ((i[3] or 0) and Weibo.IS_FWD) | ((i[5] or 0) and Weibo.HAS_PIC) , #flag
		i[2]  # from_client
		) for i in r]


