from flask import Flask, render_template, request, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)


class Travel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    travelTitle = db.Column(db.String(255), nullable=False)
    travelPic_url = db.Column(db.String(255), nullable=False)
    travelInfo = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'{self.travelTitle} {self.travelPic_url} {self.travelInfo}'


@app.route('/')
def home():
    travels = Travel.query.all()
    return render_template('index.html', travels=travels)


with app.app_context():
    db.create_all()


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

if __name__ == '__main__':
    app.run(debug=True)
