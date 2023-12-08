from flask import Flask, request, render_template, url_for, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os, secrets
from datetime import timedelta

app = Flask(__name__)

#Session
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)


#Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

app.config['SQLALCHEMY_BINDS'] = {
    'userdb': 'sqlite:///' + os.path.join(basedir, 'userdb.db')
}

db = SQLAlchemy(app)

class Travel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'{self.title} {self.image} {self.content} {self.user_email}'

class Users(db.Model):
    __bind_key__ = 'userdb'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(10000), nullable=False)

with app.app_context():
    db.create_all()

#메인페이지
@app.route("/")
def mainPage():
    travels = Travel.query.all()
    #유저 데이터 배열로 생성
    userData = {}
    userData["email"] = session.get("email",None)
    userData["username"] = session.get("username",None)
    userData["password"] = session.get("password",None)
    return render_template("mainPage.html", travels = travels, data = userData)

# 변수이름 카멜케이스, 스네이크 케이스 통일
# endpoint 하이픈으로 변경


#회원가입
@app.route("/join/", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        username_received = request.form.get("username", type=str)
        email_received = request.form.get("email", type=str)
        password1_received = request.form.get("password1", type=str)
        password2_received = request.form.get("password2", type=str)

        # case1-1
        if username_received == "" or email_received == "" or password1_received == "" or password2_received == "":
            flash("입력되지 않은 값이 있습니다.")
            return redirect(url_for("mainPage"))
        
        # case1-2
        if password1_received != password2_received:
            flash("비밀번호가 일치하지 않습니다.")
            return redirect(url_for("mainPage"))
        
        # case1-3
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

#로그인
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_received = request.form.get("email", type=str)
        password_received = request.form.get("password", type=str)

        # case2-1
        if email_received == "" or password_received == "":
            flash("입력되지 않은 값이 있습니다.")
            return render_template("mainPage.html")

        user = Users.query.filter_by(email = email_received).first()

        # case2-2
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
            # case2-3
            else:
                flash("비밀번호가 일치하지 않습니다.")
                return redirect(url_for("mainPage"))
    else:
        return render_template("mainPage.html")

#로그아웃
@app.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for("mainPage"))


#카드 생성, 수정, 삭제
@app.route('/newTravel', methods=['GET', 'POST']) 
def newTravel():
    # 로그인한 경우에만 접근 가능
    if session.get('email') is None:
        flash("먼저 로그인해 주세요.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_email = request.form['user_email']
        title = request.form['title']
        image = request.form['image']
        content = request.form['content']

        new_travel = Travel(user_email=user_email, title=title,
                            image=image, content=content)
        db.session.add(new_travel)
        db.session.commit()

        return redirect(url_for('mainPage'))
    user_email = session.get('email')
    return render_template('newTravel.html',user_email=user_email)


@app.route('/editTravel/<int:id>', methods=['GET', 'POST'])
def editTravel(id):
    travel = Travel.query.get(id)

    # 로그인한 경우에만 접근 가능
    if session.get('email') is None:
        flash("먼저 로그인해 주세요.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        travel.user_email = request.form['user_email']
        travel.title = request.form['title']
        travel.image = request.form['image']
        travel.content = request.form['content']

        db.session.commit()
        return redirect(url_for('mainPage'))

    return render_template('editTravel.html', travel=travel)

@app.route('/deleteTravel/<int:id>', methods=['GET', 'POST'])
def deleteTravel(id):
    travel = Travel.query.get(id)

    # 로그인한 경우에만 접근 가능
    if session.get('email') is None:
        flash("먼저 로그인해 주세요.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        db.session.delete(travel)
        db.session.commit()

    return redirect(url_for('mainPage'))


##여기는 문제가됩니다! 고치셔야돼요! -> endpoint가 같음
@app.route("/travelCardList/")
def travelallpage():
    travel_list = Travel.query.all()
    return render_template('travelallpage.html', data=travel_list)

@app.route("/travelCardList/")
def travelCardList():
    travel_list = Travel.query.all()
    return render_template('travelallpage.html', data = travel_list)


@app.route("/myTravelCardList/")
def mytravelpage():
    # 로그인한 경우에만 접근 가능
    if session.get('email') is None:
        flash("먼저 로그인해 주세요.")
        return redirect(url_for('login'))
    user_email = session.get('email')
    filter_list = Travel.query.filter_by(user_email=user_email).all()
    return render_template('mytravelpage.html', data = filter_list)
    
    
    #해당 카드와 페이지를 연결하는 함수  #강릉 카드면 강릉 전체 내용이 나오는 html
@app.route("/newtravelpage/<int:id>")
def newtravelpage(id):
    travellog=Travel.query.filter_by(id=id).first() 
    return render_template('newtravelpage.html', data = travellog)
    
if __name__ == '__main__':
    app.run(debug=True)