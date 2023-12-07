# 필수 라이브러리
'''
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
'''
from flask_sqlalchemy import SQLAlchemy
import os
from flask import Flask, render_template
app = Flask(__name__)

@app.route("/main/")
def main():
    return render_template('main.html')


@app.route("/travelallpage/")
def travelallpage():
    return render_template('travelallpage.html')


@app.route("/mytravelpage/")
def mytravelpage():
    return render_template('mytravelpage.html')


if __name__ == "__main__":
    app.run(debug=True)

    from flask import Flask

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)
