import gc #garbage collector
import string
import random


from flask import Flask, render_template, flash, request, url_for, redirect, session, g #flask
from dbconnect import connection #database file
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from passlib.hash import sha256_crypt #hash
from MySQLdb import escape_string as thwart

app = Flask(__name__)


@app.route("/")
def mornin():
	flash('tesoantuoaseu')
	return render_template("dash.html")


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
			#email = c.fetchone()[3]
			#checka hvort pass matcha
			dotheymatch = sha256_crypt.verify(password, data)
			if dotheymatch:
				session['logged_in'] = True
				session['username'] = name
				#session['email'] = email

				c.close()
				conn.close()
				gc.collect()
				return redirect(url_for('dashboard'))
		return render_template('login.html')
	except Exception as e:
		message = "login did not work correctly"
		return render_template('login.html', message=message)


@app.route('/login/', methods=["GET","POST"])
def login():
	return render_template('login.html')

@app.route('/logout/')
def logout():
	session.clear()
	gc.collect()
	return redirect(url_for('login'))


@app.route('/mypage/', methods=['POST','GET'])
def mypage():
	return render_template('mypage.html')

@app.route('/mypastes/', methods = ['POST', 'GET'])
def userpastas():
	if session['logged_in'] == True:
		#grab all his pastas from db.
		user = session['username']
		c, conn = connection()
		c.execute("SELECT * FROM pastes WHERE user = (%s)", (thwart(user)))
		results = c.fetchall()
		#for x in results:
		#todo in jinai

@app.route('/deleteuser/', methods=['POST'])
def deleteuser():
	try:
		username = session['username']
		c, conn = connection()
		c.execute("DELETE FROM users WHERE name = (%s)", username)
		conn.commit()
		conn.close()
		c.close()
		gc.collect()
		return render_template('dash.html')
	except Exception as e:
		return(str(e))



@app.route('/ChangePassword/', methods = ['POST'])
def changepassword():
	try:
		pass1 = request.form['password1']
		pass2 = request.form['password2']
		pass3 = request.form['password3']
		message = None
		if len(pass1) > 0 and len(pass2) > 0 and len(pass3) > 0 and pass2 == pass3:
			c, conn = connection()
			data = c.execute("SELECT * FROM users WHERE name = (%s)", thwart(session['username']))
			data = c.fetchone()[2]
			#checka hvort pass matcha
			dotheymatch = sha256_crypt.verify(pass1, data)
			if dotheymatch:
				c.execute("UPDATE users SET password = (%s) WHERE name = (%s)", (sha256_crypt.hash(pass3), thwart(session['username'])));
				conn.commit()
				c.close()
				conn.close()
				gc.collect()
				message = 'password has been changed'
				return render_template('mypage.html', message=message)
		message = 'something went wrong'
		return render_template('mypage.html',message = message)
	except Exception as e:
		return(str(e))


@app.route('/changeusername/')
def changeemail():
	try:
		newuser = request.form('username')
		if len(newuser) > 0 and session['logged_in'] == True: #continue
			name = session['username']
			c, conn  = connection()
			c.execute("UPDATE users SET name = (%s) WHERE name = (%s)", (thwart(newuser), thwart(name)))
			conn.commit()
			c.close()
			conn.close()
			gc.collect()
			message = "username has been changed to {}".format(newname)
			return render_template('mypage.html', message = message)

		message = "something went wrong"
		return render_template('mypage.html', message = message)
	except Exception as e:
		return render_template('mypage.html')

@app.route("/createnewpaste/", methods=["POST"])
def createnewpaste():
	try:
		text = request.form['textarea']
		if len(text) > 0: #continue
			url = id_generator() # 10 digits long
			if session['logged_in'] == True: #user is logged in
				author = session['username']
				c, conn = connection()
				#todo create url
				c.execute("INSERT INTO pastes (url, text, author ) VALUES (%s, %s, %s)", (thwart(url), thwart(text), thwart(author)))
			else:
				c.execute("INSERT INTO pastes (url, text ) VALUES (%s, %s)", (thwart(url), thwart(text)))
			conn.commit()
			c.close()
			conn.close()
			gc.collect()

			#return redirect(url_for('newpaste')',url)
		return render_template('dash.html',text=url)
	except Exception as e:
		return render_template('dash.html')


@app.route('/findpaste/', methods=["POST"])
def findPastes():
	try:
		variable = request.form['name']
		c, conn = connection()
		x = c.execute("SELECT * FROM pastes WHERE url = (%s)", (thwart(variable)))
		x = c.fetchone()[2]
		text = x
		c.close()
		conn.close()
		gc.collect()
		return render_template('dash.html',text=text)
	except Exception as e:
		return render_template('dash.html')

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))



#####error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(405)
def method_not_allowed(e):
	return render_template('405.html'), 405

@app.errorhandler(500)
def exception_handler(e):
    return render_template('500.html'), 500

###starting the program

if __name__ == "__main__":
	app.run()
