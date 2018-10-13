import sqlite3
from flask import Flask
from flask_socketio import SocketIO, emit
import db_connector


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
db_connector.create_db()

#
@app.route('/')
def index():
    return 'Hello world'


@socketio.on("connect")
def con():
    print('Connected')
    emit('opened')


@socketio.on("add player")
def add_player(nick, avatar):
    try:
        db_connector.add_player(nick, avatar)
    except sqlite3.IntegrityError:
        return -1, "Невозможно зарегистрировать игрока"
    return 1, "Ок"


@socketio.on("get_player")
def get_player(nick):
    res = db_connector.get_player(nick)
    emit("get_player_resp", res)


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
