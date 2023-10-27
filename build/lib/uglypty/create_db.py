import sqlite3

conn = sqlite3.connect('settings.sqlite')
c = conn.cursor()

c.execute('''
          CREATE TABLE "creds" (
	"id" INTEGER NOT NULL  ,
	"username" TEXT NULL  ,
	"password" TEXT NULL
, "displayname"	TEXT)
          ''')

conn.commit()
print("settings.sqlite created")
