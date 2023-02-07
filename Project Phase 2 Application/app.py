from flask import Flask, flash, redirect, request, render_template, session, url_for

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

import sqlite3
import pickle
import numpy as np

# creating database to store the data of both user(login and registration) and prediction( real time inputs)

con=sqlite3.connect("database.db")
print("Opened database successfully")

con.execute("create table if not exists user(pid integer primary key, name text, email text, password text,status BOOLEAN)")
print("User table created successfully")

con.execute("create table if not exists details(pid integer primary key, HighBP REAL, HighChol REAL, CholCheck REAL, BMI REAL, Smoker REAL, Stroke REAL, HeartDiseaseorAttack REAL, PhysActivity REAL, Fruits REAL, Veggies REAL, HvyAlcoholConsump REAL, AnyHealthcare REAL, NoDocbcCost REAL, GenHlth REAL, MentHlth REAL, PhysHlth REAL, DiffWalk REAL, Sex REAL, Age REAL, Education REAL, Income REAL)")
print("Details table created successfully")

con.close()

app = Flask(__name__)

# Secret key is created to make sure the database connectioon establishment stays secure 

app.secret_key="#@diabeticpredictionflaskapp@#"

# email verification

app.config.from_pyfile('config.cfg')

mail=Mail(app)

s = URLSafeTimedSerializer(app.config['SECRET_KEY']) 

# routeing the application basic pages

@app.route("/",methods=['POST','GET'])
def index():
    return render_template("index.html")

@app.route("/loginpage",methods=['POST','GET'])
def loginpage():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/wrong")
def wrong():
    return render_template('wrong.html')

# result pages render methods

# Result 0 page for 'No diabetis' and other two are for 'Type 1' and 'Type 2'

@app.route("/result")
def result0():
    return render_template('result0.html')

@app.route("/result1")
def result1():
    return render_template('result1.html')

@app.route("/result2")
def result2():
    return render_template('result2.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("logged out successfully","warning")
    return render_template('index.html')

# login and register page render methods

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        try:
            name=request.form['name']
            email=request.form['email']
            password=request.form['password']

            # Connecting the database

            con=sqlite3.connect("database.db")

            # 'con' is used to execute the MySql queary

            cur=con.cursor()
            cur.execute("INSERT INTO user(name,email,password) VALUES (?,?,?)",(name,email,password))

            # After the insearting the data , changes are commited
            flash("Registered successfully","success")
            con.commit()
        except:

            # This message is flashed if any error is found

            con.rollback()  
            flash("Problem in Registration, Please try again","danger")
        finally:

            # This page is rendered if everything is good
            
            print("Registered")
            return redirect(url_for('login'))

            # After the process the database connection is closed

            con.close()
    else:
        flash("Registered failed","danger")
        return render_template("wrong.html")

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method =='POST':

        # getting the data from database to validate the user

        email = request.form['email']
        password = request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("SELECT * FROM user where email=? and password=?",(email,password))

        # the data that are featched are stored in the variable called 'data'

        data=cur.fetchone() 

        if data:

            # The data of user that are featched are store for application use "Only the email not the password"

            session["email"]=data["email"]
            session["name"]=data["name"]
            print("sent to home")
            flash("login successful","success")
            return redirect(url_for("home"))
                      
        else:
            flash("Username or Password is incorrect","danger")
            print("not sent to home")
    return redirect(url_for('loginpage'))

model = pickle.load(open("second_model_2.pkl","rb"))

# email verification

@app.route("/form",methods=['GET','POST'])
def form():
    email = session["email"]
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("SELECT status FROM user where email=?",[email])
    data=cur.fetchone()
    con.commit()
    print(data)
    if data[0]==1:
        return render_template("form.html")
    else:
        return render_template("verify.html")

@app.route('/verify')
def verify():
    email = session["email"]

    token = s.dumps(email, salt='email-confirm')

    msg=Message('Confirm Email', sender='ibmproject2023@gmail.com', recipients=[email])

    link=url_for('confirm_email', token=token, _external=True)

    msg.body= 'Please click the link to verify your account to continue  : {} '.format(link)

    mail.send(msg)
    flash("Verification mail has been sent to your email","info")
    return redirect(url_for("home"))

@app.route('/confirm_email/<token>')
def confirm_email(token):
  try:
    email=s.loads(token, salt='email-confirm' , max_age=3600*5)
  except SignatureExpired:
    return render_template("verify.html")
  con=sqlite3.connect("database.db")
  con.row_factory=sqlite3.Row
  cur=con.cursor()
  cur.execute("UPDATE user SET status = 1 WHERE email = ?",(email,))
  con.commit()
  con.close()
  return redirect(url_for("form"))

@app.route("/predict",methods = ['POST','GET'])
def predict():

    # Getting the data form the user through the form

    name = request.form.get("name")
    print(name)

    age = request.form.get("age")
    gender = request.form.get("gender")
    bmi = request.form.get("bmi")
    mhealth = request.form.get("mhealth")
    phealth = request.form.get("phealth")
    bp = request.form.get("bp")
    hc = request.form.get("hc")
    cc = request.form.get("cc")
    smoker = request.form.get("smoker")
    stroke = request.form.get("stroke")
    hearta = request.form.get("hearta")
    phact = request.form.get("phact")
    fruit = request.form.get("fruit")
    veggies = request.form.get("veggies")
    drinker = request.form.get("drinker")
    hcare = request.form.get("hcare")
    cost = request.form.get("cost")
    walking = request.form.get("walking")
    education = request.form.get("education")
    income = request.form.get("income")
    ghealth = request.form.get("ghealth")


    # data insertion in database of user reak time input

    con=sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("INSERT INTO details(HighBP,HighChol,CholCheck,BMI,Smoker,Stroke,HeartDiseaseorAttack,PhysActivity,Fruits,Veggies,HvyAlcoholConsump,AnyHealthcare,NoDocbcCost,GenHlth,MentHlth,PhysHlth,DiffWalk,Sex,Age,Education,Income) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bp,hc,cc,bmi,smoker,stroke,hearta,phact,fruit,veggies,drinker,hcare,cost,ghealth,mhealth,phealth,walking,gender,age,education,income))
    con.commit()
    cur.execute("INSERT INTO data(HighBP,HighChol,CholCheck,BMI,Smoker,Stroke,HeartDiseaseorAttack,PhysActivity,Fruits,Veggies,HvyAlcoholConsump,AnyHealthcare,NoDocbcCost,GenHlth,MentHlth,PhysHlth,DiffWalk,Sex,Age,Education,Income) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bp,hc,cc,bmi,smoker,stroke,hearta,phact,fruit,veggies,drinker,hcare,cost,ghealth,mhealth,phealth,walking,gender,age,education,income))
    con.commit()
    flash("Registered successfully","success")
    print("Registered")

    # Passing the data to model to predict the output

    feature = np.array([[bp,hc,cc,bmi,smoker,stroke,hearta,phact,fruit,veggies,drinker,hcare,cost,ghealth,mhealth,phealth,walking,gender,age,education,income]],dtype=float)
    print(name)
    print(feature)
    prediction = model.predict(feature)
    print(prediction)

    # Based on the prediction result the pages are routed

    if prediction[0] == 1:
        return render_template("result0.html")
    elif prediction[0] == 2:
        return render_template("result1.html",type="Type 1")
    else:
        return render_template("result2.html",type="Type 2")

# dashboard process
@app.route("/dashboard")
def dashboard():

    # Connecting to database
    con=sqlite3.connect("database.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()

    # To get recent predictions
    cur.execute("SELECT * FROM (SELECT * FROM data ORDER BY pid DESC LIMIT 15 ) ORDER BY pid ASC")
    data=cur.fetchall()

    # To get no of users detsils either verified or not
    cur.execute("SELECT * FROM (SELECT * FROM user ORDER BY pid DESC LIMIT 8 ) ORDER BY pid ASC")
    user=cur.fetchall()

    # To get size(no of users)
    cur.execute("SELECT * from user")
    sizeClient=cur.fetchall()
    sizeClient=len(sizeClient)
    print(sizeClient)

    # To get Size of dataset
    cur.execute("SELECT * from data")
    sizeOfDataset=cur.fetchall()
    sizeOfDataset=len(sizeOfDataset)
    print(sizeOfDataset)

    return render_template('dashboard.html',Name=session["name"],Email=session["email"],data=data,user=user,ToatalNoOfClients=sizeClient,TotalData=sizeOfDataset)

@app.route("/dashboard2")
def dashboard2():
    return render_template('dashboard2.html',Name=session["name"],Email=session["email"])


if __name__ == '__main__':
    app.run(Debug = True)