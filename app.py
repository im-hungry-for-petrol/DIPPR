"""
im-hungry-for-petrol
app.def
Main backend for DIPPR
"""
from flask import Flask, render_template, request, session # other shit
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import func_assist # imported files to making it more organized
import requests
import re
import uuid
import ast

# basic flask app stuff
app = Flask(__name__)
app.secret_key = b'myFUKINGasshurtsBITCH'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dippr.db'

def generate_session_id():
    return str(uuid.uuid1())

# database stuff
db = SQLAlchemy(app)
class Joined(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(15), unique=True# never mind this dumb ass file
, nullable=False)
    joined = db.Column(db.Text, unique=True,nullable=False)

    def __init__(self, session_name, host):
        # creating session name, immediately adding host
        self.session_name = session_name
        host_list_format = []
        host_list_format.append(host)
        self.joined = str(host_list_format)

    def __repr__(self):
        return repr('_sessions__: ' + str(self.id) + ' ' + str(self.session_name)
            + ' ' + str(self.joined))

# basic socket stuff
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def homepage():
    user_session_current = generate_session_id()

    # checking for POST request
    if request.method == 'POST':
        if request.form.get('join_submit'):
            print("Trying to join.")
            join_code = request.form['join_code']
            query = Joined.query.filter_by(session_name=join_code).all()
            query_list = query[0].joined    # STRING
            query_list = ast.literal_eval(query_list)
            query_list.append(user_session_current)
            curr_host = query_list[0]

            # update
            update_query = Joined.query.filter_by(session_name=join_code).first()
            update_query.joined = str(query_list)
            db.session.commit()

            print("Successfully joined.")
            return render_template('lobby.html', session_id=user_session_current, host=curr_host)
        elif request.form.get('host_submit'):
            # new session, unique host
            print("Trying to add new host.")
            host_code = request.form['host_code']
            new_group = Joined(session_name=host_code, host=user_session_current)
            db.session.add(new_group)
            db.session.commit()
            print("Done.")
            return render_template('lobby.html', session_id=user_session_current, host=user_session_current)
        else:
            return render_template('index.html', message='Invalid request.')


    return render_template('index.html')

@app.route('/lobby')
def lobby():
    return render_template('lobby.html')

@app.route('/swipe')
def swipepage():
    return render_template('swipepage.html')

@app.route('/waiting_conclusion')
def waiting_conclusion():
    return render_template('waiting_conclusion.html')

@app.route('/conclusion.html')
def conclusion():
    return render_template('conclusion.html')

if __name__ == "__main__":
    db.create_all()
    socketio.run(app, debug=True)
