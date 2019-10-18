Python 3.7.4 (tags/v3.7.4:e09359112e, Jul  8 2019, 20:34:20) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import sqlite3
>>> conn = sqlite3.connect("wordfreqapp.db")
>>> conn.execute('CREATE TABLE user(name TEXT PRIMARY KEY, password TEXT)')
<sqlite3.Cursor object at 0x0000004EFD68DDC0>
>>> conn.close()
>>> username = 'aaa'
>>> "SELECT * FROM user WHERE name='%s'" % (username)
"SELECT * FROM user WHERE name='aaa'"
>>> '\n\n'.join([])
''
>>> conn = sqlite3.connect("wordfreqapp.db")
>>> conn.execute('CREATE TABLE user(name TEXT PRIMARY KEY, password TEXT, status TEXT)')
Traceback (most recent call last):
  File "<pyshell#8>", line 1, in <module>
    conn.execute('CREATE TABLE user(name TEXT PRIMARY KEY, password TEXT, status TEXT)')
sqlite3.OperationalError: table user already exists
>>> conn.execute('drop table user')
<sqlite3.Cursor object at 0x0000004EFC67D2D0>
>>> conn.execute('CREATE TABLE user(name TEXT PRIMARY KEY, password TEXT, status TEXT)')
<sqlite3.Cursor object at 0x0000004EFC67D3B0>
>>> conn.close()
>>> 
>>> 
>>> 
>>> conn = sqlite3.connect("wordfreqapp.db")
>>> conn.execute('drop table user')
<sqlite3.Cursor object at 0x0000004EFC67D340>
>>> conn.execute('CREATE TABLE user(name TEXT PRIMARY KEY, password TEXT, start_date TEXT, expiry_date TEXT)')
<sqlite3.Cursor object at 0x0000004EFC67D2D0>
>>> conn.close()
>>> 
