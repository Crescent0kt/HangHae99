from flask import Flask, request, render_template, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
import os, secrets

from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

app.config['SQLALCHEMY_BINDS'] = {
    'userdb': 'sqlite:///' + os.path.join(basedir, 'userdb.db')
}

db = SQLAlchemy(app)

class Travel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    travelTitle = db.Column(db.String(255), nullable=False)
    travelPic_url = db.Column(db.String(255), nullable=False)
    travelInfo = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'{self.travelTitle} {self.travelPic_url} {self.travelInfo}'

@app.route('/home')
def home():
    travels = Travel.query.all()
    return render_template('index.html', travels=travels)

@app.route('/newTravel', methods=['GET', 'POST'])
def newTravel():
    if request.method == 'POST':
        travelTitle = request.form['travelTitle']
        travelPic_url = request.form['travelPic_url']
        travelInfo = request.form['travelInfo']

        new_travel = Travel(travelTitle=travelTitle,
                            travelPic_url=travelPic_url, travelInfo=travelInfo)
        db.session.add(new_travel)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('newTravel.html')

with app.app_context():
    db.create_all()


class Users(db.Model):
    __bind_key__ = 'userdb'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(10000), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def mainPage():
    #유저 데이터 배열로 생성
    userData = {}
    userData["email"] = session.get("email",None)
    userData["username"] = session.get("username",None)
    userData["password"] = session.get("password",None)
    return render_template("mainPage.html",data = userData)


@app.route("/join/", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        username_received = request.form.get("username", type=str)
        email_received = request.form.get("email", type=str)
        password1_received = request.form.get("password1", type=str)
        password2_received = request.form.get("password2", type=str)

        # 값을 다 입력하지 않은 경우
        if username_received == "" or email_received == "" or password1_received == "" or password2_received == "":
            flash("입력되지 않은 값이 있습니다.")
            return redirect(url_for("mainPage"))
        
        # 비밀번호가 일치하지 않는 경우
        if password1_received != password2_received:
            flash("비밀번호가 일치하지 않습니다.")
            return redirect(url_for("mainPage"))
        
        # 가입된 정보가 있는 경우
        cnt = Users.query.filter_by(email = email_received).count()
        if cnt > 0:
            flash("중복된 이메일 주소입니다.")
            return redirect(url_for("mainPage"))
        
        user = Users(username = username_received, email = email_received, password = password1_received)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for("mainPage"))

    else: # if request.method == "GET":
        return redirect(url_for("mainPage"))
    

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_received = request.form.get("email", type=str)
        password_received = request.form.get("password", type=str)

        # 값을 다 입력하지 않은 경우
        if email_received == "" or password_received == "":
            flash("입력되지 않은 값이 있습니다.")
            return render_template("mainPage.html")

        user = Users.query.filter_by(email = email_received).first()

        # 가입된 정보가 없는 경우
        if user is None:
            flash("일치하는 회원 정보가 없습니다.")
            return redirect(url_for("mainPage"))
        else:
            if user.password == password_received:
                session['email'] = user.email
                session['username'] = user.username
                session['password'] = user.password
                session.permanent = True
                return redirect(url_for("mainPage"))
            # 비밀번호가 일치하지 않는 경우
            else:
                flash("비밀번호가 일치하지 않습니다.")
                return redirect(url_for("mainPage"))
    else:
        return render_template("mainPage.html")
    
@app.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for("mainPage"))


    
if __name__ == '__main__':
    app.run()