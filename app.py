import sqlite3
import uuid

from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


def sql(query):
    con = sqlite3.connect("test.db")
    curs = con.cursor()
    curs.execute(query)
    con.commit()


sql("drop table if exists players")
sql("create table players("
    "id  string  primary key, "
    "nickname string not null )")


@app.route('/')
def index():
    return 'Hello world'


@socketio.on("connect")
def con():
    print('Connected')
    emit('opened')


@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': message['data']})


@socketio.on("add player")
def add_player(message):
    con = sqlite3.connect("test.db")
    curs = con.cursor()
    curs.execute('INSERT INTO players (id, nickname) values (?,?)', (str(uuid.uuid4()).replace('-', ''), message))
    con.commit()


@socketio.on('my broadcast event')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
