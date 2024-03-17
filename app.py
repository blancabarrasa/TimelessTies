from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length
from sqlalchemy.exc import IntegrityError
from datetime import datetime

path_to_database = '' #include the path to your database here

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = path_to_database + 'timelessties.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LOLUMS'
db = SQLAlchemy(app)


class User(db.Model):
    email = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    # interests = db.Column(db.String(80), nullable = False)

class LoginForm(FlaskForm):  # Corrected class name
    email = StringField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Email"})
    name = StringField(validators=[InputRequired(), Length(min=1, max=80)], render_kw={"placeholder": "Name"})
    # interests = StringField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Interests"})
    submit = SubmitField("Register")


class Activity(db.Model):
    activity_id = db.Column(db.Integer(), primary_key=True)
    time = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(80), db.ForeignKey('user.email'), nullable=False)
    user = db.relationship('User', backref=db.backref('activities', lazy=True))


@app.route('/', methods=['GET', 'POST'])

def home():
    form = LoginForm()  # Corrected form class instantiation
    if form.validate_on_submit():
        new_user = User(email=form.email.data, name=form.name.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('groups'))
    
    return render_template('login.html', form=form)
    

@app.route('/join-meetup', methods=['POST'])
def join_meetup():
    data = request.json
    email = data.get('email')
    activity_name = data.get('activity_name')
    date = datetime.strptime(data.get('date'), '%B %d, %Y').date()
    time = data.get('time')
    location = data.get('location')

    user = User.query.filter_by(email=email).first()
    if user:
        new_activity = Activity(activity_name=activity_name, date=date, time=time, location=location, user=user)
        db.session.add(new_activity)
        db.session.commit()
        return jsonify({'message': 'Meetup joined successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404
    
# Endpoint to leave a meetup
@app.route('/leave-meetup', methods=['POST'])
def leave_meetup():
    data = request.json
    email = data.get('email')
    activity_id = data.get('activity_id')

    user = User.query.filter_by(email=email).first()
    if user:
        activity = Activity.query.filter_by(activity_id=activity_id, user_email=email).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return jsonify({'message': 'Left meetup successfully'}), 200
        else:
            return jsonify({'error': 'Activity not found for this user'}), 404
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/groups')
def groups():
    return render_template('groups.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

