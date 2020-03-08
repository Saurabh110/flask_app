from flask import Flask ,render_template, redirect, url_for, request, flash, session, g
from functools import wraps
from flask_mysqldb import MySQL, MySQLdb

app = Flask(__name__)
app.secret_key = "saurabh"


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'
mysql = MySQL(app)

def authenticator(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash("You need to login first")
			return redirect(url_for('login'))
	return wrap


@app.route('/')
def index():
	return render_template('index.html',page_title="Welcome to Patagonia Health")


@app.route('/welcome')
def welcome():
    return render_template('welcome.html',page_title="Welcome Page")


@app.route('/login', methods=['GET','POST'])
def login():
	error = None

	if request.method == 'POST':
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM physicians WHERE email = '" +str(request.form['username'])+"'")
		data = cur.fetchone()
		# print("data: ", data[4])
		entered_password = request.form['password']
		cur.close()
		if data and data[4] == entered_password:
			session['logged_in'] = True
			session['p_id'] = data[0]
			session['name'] = data[1]
			return redirect(url_for('physician_page'))
		else:
			error = "Invalid Credentials"

	return render_template('login.html',page_title="Login", error=error)


@app.route('/logout')
@authenticator
def logout():
	session.pop('logged_in', None)
	session.pop('p_id', None)
	session.pop('name', None)
	flash('Logged out successfully')
	return redirect(url_for('index'))


@app.route('/physician_signup', methods=['GET','POST'])
def physician_signup():
	error = None

	if request.method == 'POST':
		cur = mysql.connection.cursor()
		query = "INSERT INTO physicians (f_name, l_name, email, password) VALUES ('"+request.form['f_name']+"', '"+request.form['l_name']+"', '"+request.form['email']+"', '"+request.form['password']+"');"
		try:
			cur.execute(query)
			mysql.connection.commit()
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			if e[0] == 1062:
				error = 'Account with email: ' + request.form['email'] + ' is already present.'
			else:
				error = e
			print(e[0])
		cur.close()
		if not error:
			flash('Account created successfully. Please Login!')
			return redirect(url_for('login'))
	return render_template('physician_signup.html', page_title="Physician Signup", error = error)

@app.route('/physician_page')
@authenticator
def physician_page():
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM patients WHERE physician_id = "+str(session['p_id']))
	data = cur.fetchall()
	return render_template('physician_page.html', page_title="List of Patients", patients = data)


@app.route('/add_patient', methods=['GET','POST'])
@authenticator
def add_patient():
	error = None
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		query = "INSERT INTO patients (f_name, l_name, email, physician_id) VALUES ('"+request.form['f_name']+"', '"+request.form['l_name']+"', '"+request.form['email']+"', "+str(session['p_id'])+");"
		try:
			cur.execute(query)
			mysql.connection.commit()
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			if e[0] == 1062:
				error = 'Patient with email: ' + request.form['email'] + ' is already present.'
			else:
				error = e
			# print(e[0])
		cur.close()
		if not error:
			flash('Patient created and added to your list successfully!')
			return redirect(url_for('physician_page'))
	return render_template('add_patient.html', page_title="Add a new Patient", error = error)


@app.route('/delete/<string:id_data>', methods = ['GET'])
@authenticator
def delete(id_data):
	cur = mysql.connection.cursor()
	flag = 0
	try:
		cur.execute("DELETE FROM patients WHERE id="+str(id_data))
		mysql.connection.commit()
	except (MySQLdb.Error, MySQLdb.Warning) as e:
		flash("Couldn't delete the patient")
		flag = 1
	cur.close()
	if not flag:
		flash("Record Has Been Deleted Successfully")
	return redirect(url_for('physician_page'))


@app.route('/edit_patient/<string:id_data>', methods = ['GET','POST']) 
@authenticator
def edit_patient(id_data):
	error = None
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		query = "UPDATE patients SET f_name = '"+request.form['f_name']+"', l_name = '"+request.form['l_name']+"', email = '"+request.form['email']+"' WHERE id = "+str(request.form['id'])+";"
		try:
			cur.execute(query)
			mysql.connection.commit()
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			error = e
			# print(e[0])
		cur.close()
		if not error:
			flash('Patient edited successfully!')
			return redirect(url_for('physician_page'))
	
	else:
		cur = mysql.connection.cursor()
		query = "SELECT * FROM patients WHERE id = "+str(id_data)+""
		try:
			cur.execute(query)
			mysql.connection.commit()
			data = cur.fetchone()
			print(data)
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			error = e
	return render_template('edit_patient.html', page_title="Edit a patient", data = data ,error = error)




if __name__ == '__main__':
    # app.run(debug=False)
    app.run(host="152.7.99.82",port=8080,debug=True)