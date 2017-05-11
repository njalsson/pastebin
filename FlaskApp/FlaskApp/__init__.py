import gc #garbage collector
from flask import Flask, render_template, flash, request, url_for, redirect, session, g #flask
from dbconnect import connection #database file
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from passlib.hash import sha256_crypt #hash
from MySQLdb import escape_string as thwart

app = Flask(__name__)

@app.route("/")
def mornin():
	flash('tesoantuoaseu')
	return render_template("header.html")


@app.route('/dashboard/')
def dashboard():
	return render_template("dash.html")

class RegistrationForm(Form):
	username = StringField('Username', [validators.Length(min=4, max=255)])
	email = StringField('Email Address', [validators.Length(min=6, max=255)])
	password = PasswordField('New Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Repeat Password')
	accept_tos = BooleanField('I accept the Terms of Service )', [validators.DataRequired()])

@app.route('/register/', methods=["GET","POST"])
def register():
		return render_template("register.html")


@app.route('/createuser/', methods=['POST'])
def createuser():
	try:
		username = request.form['username']
		email = request.form['email']
		pass1 = request.form['pass1']
		pass2 = request.form['pass2']
		#got all 4 things we need
		if len(username) > 0 and len(email) > 0 and len(pass1) > 0 and len(pass2) > 0 and pass1 == pass2:
			#create user
			password = sha256_crypt.hash(pass1)
			c, conn = connection()
			x = c.execute("SELECT * FROM users WHERE name = (%s)", (thwart(username)))

			if int(x) > 0:
				return render_template('register.html')

			else:
				c.execute("INSERT INTO users (name, password, email ) VALUES (%s, %s, %s)", (thwart(username), thwart(password), thwart(email)))

				conn.commit()
				c.close()
				conn.close()
				gc.collect()

				session['logged_in'] = True
				session['username'] = username

				return redirect(url_for('dashboard'))

		return render_template("register.html")

	except Exception as e:
		return(str(e))



@app.route('/hello/', methods=["POST"])
def hello():
	try:
		name=request.form['username']
		password=request.form['password']
		if len(name) > 0 and len(password) > 0:
			c, conn = connection()
			data = c.execute("SELECT * FROM users WHERE name = (%s)", thwart(name))
			data = c.fetchone()[2]
			#checka hvort pass matcha
			dotheymatch = sha256_crypt.verify(password, data)
			if dotheymatch:
				session['logged_in'] = True
				session['username'] = name
				c.close()
				conn.close()
				gc.collect()
				return redirect(url_for('dashboard'))
		return render_template('login.html')
	except Exception as e:
		return(str(e))


@app.route('/login/', methods=["GET","POST"])
def login():
	return render_template('login.html')

@app.route('/logout/')
def logout():
	session.clear()
	gc.collect()
	return redirect(url_for('login'))


@app.route('/mypage/')
def mypage():
	return render_template('mypage.html')


if __name__ == "__main__":
	app.run()
