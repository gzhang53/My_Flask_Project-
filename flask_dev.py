from flask import Flask, render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from data import Articles
#config sql

app = Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='1234'
app.config['MYSQL_DB']='myflaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor' #default is tuple

#initilize MYSQL
mysql = MySQL(app)
Articles=Articles()

@app.route('/')
def index():
    return render_template('first_page.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html',articles = Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('articles.html',id=id)

class RegisterForm(Form):
    name = StringField('Name',[validators.Length(min=1,max=50)])
    username = StringField('Username', [validators.Length(min=4,max=25)])
    email = StringField('Email',[validators.Length(min=6,max=50)])
    password = PasswordField('Password',[validators.DataRequired(),
                                         validators.EqualTo('confirm',message='Password do not match')])
    confirm = PasswordField('Confirm Password')

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username , password)  VALUES(%s, %s, %s, %s)", (name, email, username, password))
        # commit to DB
        mysql.connection.commit()
        cur.close()
        flash("You are now registered and can log in", 'success')

        return  redirect(url_for('index'))
        '''return render_template('register.html')'''
    return render_template('register.html',form=form)
#user login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':

        # get form fields
        username = request.form('username')
        password_candidate = request.form['password']

        #create a cursor
        cur = mysql.connection.cursor()

        #get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # get stored hash
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate,password):

                app.logger.info('PASSWORD MATCHED')
        else:

            app.logger.info('NO USER')
    return render_template("login.html")

            # compare passwords
if __name__=='__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
