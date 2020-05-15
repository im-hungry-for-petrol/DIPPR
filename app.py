from flask import Flask, render_template, request, session # other shit
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
# import Flask-Session
import requests
import re
import uuid

# basic flask app stuff
app = Flask(__name__)
app.secret_key = b'myFUKINGasshurtsBITCH'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dippr_db'

# database stuff
db = SQLAlchemy(app)
class sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(15), unique=True, nullable=False)
    # pickled list of joined members?
    joined = db.Column(db.String(1500), unique=True,nullable=False)

    def __init__(self, session_name, host):
        # creating session name, immediately adding host
        self.session_name = session_name
        self.joined = []
        self.joined.append(host)

        session.modified = True
    def __repr__(self):
        return repr('_sessions__: ' + str(self.id) + ' ' + str(self.session_name)
            + ' ' + str(self.joined))

# basic socket stuff
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        # creating a unique session id
        session['session_id'] = str(uuid.uuid1())
        user_session = session['session_id']

        if request.form.get('join_submit'):
            # query db to see if host code exists.
            sesh_name = request.form['join_code']
            query = sessions.query.filter_by(session_name=sesh_name).first()
            # if so, make a connection to session
            if query is not None:
                update_session = sessions.query.filter_by(session_name=sesh_name).first()
                appended_value = update_session.joined
                appended_value = appended_value.split()
                appended_value.append(user_session)
                update_session = sessions.query.filter_by(session_name=sesh_name).first()
                update_session.joined = str(appended_value)
                db.session.commit()
            else:
                print('''The session does not exist. Please try again after
                    your host has made a new session. ''')
                print(query)

        if request.form.get('host_submit'):
            # check to make sure session code doesn't already exist
            sesh_name = request.form['host_code']
            check = sessions.query.filter_by(session_name=sesh_name)
            # make new session in db, join as host
            if check is not None:
                try:
                    host = sessions(sesh_name, user_session)
                    db.session.add(host)
                    db.session.commit()
                except:
                    print("For the session: ")
                    print(session['session_id'])
                    print("Process could not be completed.")

        return render_template('lobby.html', session_id=session['session_id'])

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
