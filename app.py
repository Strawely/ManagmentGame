import sqlite3
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
import db_connector
import game


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket = SocketIO(app)
db_connector.create_db()


@app.route('/')
def index():
    return 'Hello world'


@socket.on("connect")
def con(sid):

    print('Connected')
    emit('opened')


@socket.on("register_player")
def add_player(nick, avatar):
    try:
        db_connector.add_player(nick, avatar)
    except sqlite3.IntegrityError:
        return -1, "Невозможно зарегистрировать игрока"
    return db_connector.get_player(nick), "Ок"


@socket.on("get_player")
def get_player(nick, sid):
    res = db_connector.get_player(nick)
    emit("get_player_resp", res)


@socket.on("create_game")
def create_game(pid, sesid):
    join_room(pid, sid=sesid)
    game.create_game(pid)


@socket.on("join_game")
def join_game(game_id, sesid):
    join_room(game, sid=sesid)


@socket.on('disconnect')
def test_disconnect():

    print('Client disconnected')


if __name__ == '__main__':
    socket.run(app)
