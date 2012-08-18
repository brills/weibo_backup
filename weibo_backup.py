import extractor
import sqlite
import config
import os
import time

weibo_list = extractor.run()

if os.path.exists(config.sqlite_db):
	os.rename(config.sqlite_db, config.sqlite_db + str(int(time.time())))

sqlite.insert_into_new_db(weibo_list)
sqlite.dump_db()
