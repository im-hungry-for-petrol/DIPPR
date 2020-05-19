"""
im-hungry-for-petrol
app.def
Main backend for DIPPR
"""
from flask import Flask, render_template, request, session, redirect, url_for # other shit
from flask_sqlalchemy import SQLAlchemy
import random
from flask_socketio import SocketIO, emit, send, join_room, leave_room
import func_assist # imported files to making it more organized
import requests
import re
import uuid
import ast

# amount of entries to be presented to user on scroll
NUM_ENTRIES = 10

# basic flask app stuff
app = Flask(__name__)
app.secret_key = b'myFUKINGasshurtsBITCH'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dippr_new2.db'

def generate_session_id():
    return str(uuid.uuid1())

# database stuff
db = SQLAlchemy(app)
class Joined(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(15), unique=True, nullable=False)
    joined = db.Column(db.Text, unique=True,nullable=False)
    food_list = db.Column(db.Text, nullable=False)

    def __init__(self, session_name, host):
        # creating session name, immediately adding host
        self.session_name = session_name
        host_list_format = []
        host_list_format.append(host)
        self.joined = str(host_list_format)

        # generating random list of foods, INEFFICIENT
        list_food = []
        for i in range(0, NUM_ENTRIES):
            rand = random.randrange(0, Admin.query.count())
            row = Admin.query[rand]
            list_food.append(row)
        list_food= str(list_food)
        self.food_list = list_food # the escape shall be plus

    def __repr__(self):
        return repr('_sessions__: ' + str(self.id) + ' ' + str(self.session_name)
            + ' ' + str(self.joined))

# basic socket stuff
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def homepage():
    # creating user session things
    user_session_current = generate_session_id()
    session['user_session'] = user_session_current

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
            return render_template('lobby.html', session_id=user_session_current, host=curr_host, join_code=join_code)
        elif request.form.get('host_submit'):
            # new session, unique host
            print("Trying to add new host.")
            host_code = request.form['host_code']
            new_group = Joined(session_name=host_code, host=user_session_current)
            db.session.add(new_group)
            db.session.commit()
            print("Done.")
            return render_template('lobby.html', session_id=user_session_current, host=user_session_current, join_code=host_code)
        else:
            return render_template('index.html', message='Invalid request.')


    return render_template('index.html')

@app.route('/lobby', methods=['GET', 'POST'])
def lobby():
    return render_template('lobby.html')

@socketio.on('my event')
def joining(data, methods=['GET', 'POST']):
    """
    Accepting connections from clients, sending food list
    to all clients. Each in separated rooms.
    """
    room = data['data']
    join_room(room)
    restaurant_list = Joined.query.filter_by(session_name=room).first()
    restaurant_list = restaurant_list.food_list
    print("Successfully connected to party.")
    emit('list_restaurant', {'restaurant_list':restaurant_list}, room=room)

class Counter_Guy(db.Model):
    """
    Responsible for tallying up votes at the end of everything
    """
    id = db.Column(db.Integer, primary_key=True)
    food_votes = db.Column(db.Text, nullable=False)   # stringified python dictionary
    current_session = db.Column(db.Text, unique=True, nullable=False)

    def __init__(self, curr_sesh, votes):
        self.food_votes = votes
        self.current_session = curr_sesh

    def __repr__():
        return "Votes: " + str(self.current_session)

@socketio.on('conclusion')
def conclusion(data, methods=['GET', 'POST']):
    """
    Accepting connections from clients, sending food list
    to all clients. Each in separated rooms.
    """
    room = data['data']
    rest_list = data['rest_list']
    votes = str(data['votes'])
    print(room)
    print(rest_list)
    print(votes)
    join_room(room)

    # updating votes
    try:
        # trying to add to an already defined thing will throw an exception
        print('%%%%%%%')
        new_tally = Counter_Guy(room, votes)
        db.session.add(new_tally)
        db.session.commit()
        print('Vote tried and submitted.')
    except:
        # get existing vote entries, append to string
        print('---------')
        curr_query = Counter_Guy.query.filter_by(current_session=room).first()
        curr_query.food_votes = curr_query.food_votes + votes
        db.session.commit()
        print('Vote successfully submitted, via exception.')

    # checking if the user is the host
    session_guy = session['user_session']

    query = Joined.query.filter_by(session_name=room).first()
    host_find = query.joined

    if (session_guy == host_find[0]):
        host_certainty = True
        print('He is the host!')

    print(session['user_session'])
    print("Successfully connected to party.")
    return render_template('waiting_conclusion', {'host_certainty':host_certainty})

@socketio.on('go_to_conclusion')
def go_to_conclusion(data):
    # tally up votes and send it to all connected clients
    room = data['data']
    curr_query = Counter_Guy.query.filter_by(current_session=room).first()
    vote_eval = curr_query.food_votes

    poop = dict()
    votes = vote_eval.split(',')
    for i in votes:
        poop[i] = poop.get(i, 0) + 1

    emit('end_of_story', winner=poop, redirect_gurl=url_for('conclusion'), room=room)

####################################################################################

@socketio.on('start_game')
def start_game(data, methods=['GET, POST']):
    """
    Simply redirecting to new page.
    """
    room = data['data']
    print("#### Redirecting all clients. ###")
    emit('cmd', {'url': url_for('swipepage'), 'waiting_conclusion': url_for('waiting_conclusion'), 'room': room}, room=room)
    return True

@app.route('/swipepage.html', methods=['GET', 'POST'])
def swipepage(methods=['GET, POST']):
    return render_template('swipepage.html')

@app.route('/waiting_conclusion')
def waiting_conclusion():
    return render_template('waiting_conclusion.html')

@app.route('/conclusion.html')
def conclusion():
    return render_template('conclusion.html')

class Admin(db.Model):
    """
    Model for administering the database
    """
    id = db.Column(db.Integer, primary_key=True)
    food_title = db.Column(db.String(20), unique=True, nullable=False)
    food_description = db.Column(db.Text, unique=True, nullable=False)
    food_img_link = db.Column(db.String(100), unique=True, default="Food Image")

    def __repr__(self):
        return "Food title: " + self.food_title + "Food Description: " + self.food_description

    def __init__(self, food_title, food_description, food_img_link):
        self.food_title = food_title
        self.food_description = food_description
        self.food_img_link = food_img_link

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """
    Adding instances to the database
    """
    current_entries = Admin.query.all()

    if request.method == 'POST':
        food_title = request.form['title']
        food_description = request.form['description']
        food_link = request.form['img']

        new_food_item = Admin(food_title, food_description, food_link)
        db.session.add(new_food_item)
        db.session.commit()

        return render_template('admin.html', message="Successfully added.", current_entries=current_entries)
    return render_template('admin.html', current_entries=current_entries)

if __name__ == "__main__":
    db.create_all()
    socketio.run(app, debug=True)
