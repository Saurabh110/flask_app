# import sqlite3

# with sqlite3.connect("test.db") as connection:
# 	c = connection.cursor()
# 	# c.execute("""CREATE TABLE test1(name TEXT, uname TEXT)""")
# 	c.execute('INSERT INTO test1 VALUES("user2","u2")')



from flask import Flask ,render_template, redirect, url_for, request, flash, session, g
from functools import wraps
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "saurabh"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'

mysql = MySQL(app)

@app.route('/')
def home():
	cur = mysql.connection.cursor()
	cur.execute("show tables")
	data = cur.fetchall()
	print(data)
	cur.close()
	return str(data)

if __name__ == '__main__':
    app.run(debug=True)