import unittest
# import coverage

# cov = coverage.coverage(branch=True)
# cov.start()


import sqlite3
from flask import Flask
from flask_socketio import SocketIO, emit, join_room
import db_connector
import game
from game import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket = SocketIO(app)
db_connector.create_db()
market = ((1, 1.0, 800, 3.0, 6500),
          (2, 1.5, 650, 2.5, 6000),
          (3, 2.0, 500, 2.0, 5500),
          (4, 2.5, 400, 1.5, 5000),
          (5, 3.0, 300, 1.0, 4500))
esm_orders = []


@app.route('/')
def index():
    return 'Hello world'


@socket.on("connect")
def con():
    print('Connected')
    emit('opened')


@socket.on("register_player")
def add_player(nick, avatar):
    try:
        db_connector.add_player(nick, avatar)
    except sqlite3.IntegrityError:
        return -1, "Невозможно зарегистрировать игрока"
    return db_connector.get_player(nick), "Ok"


@socket.on("get_player")
def get_player(nick):
    res = db_connector.get_player(nick)
    emit("get_player_resp", res)


@socket.on("create_game")
def create_game(pid, sesid, esm, egp, money, fabrics_1, fabrics_2, max_players):
    game.create_game(pid, esm, egp, money, fabrics_1, fabrics_2, max_players)
    join_room(db_connector.get_game_id(pid), sid=sesid)


@socket.on("join_game")
def join_game(game_id, sesid, pid):
    join_room(game_id, sesid)
    if game.player_join(pid, game_id):
        on_start(pid, db_connector.get_game(game_id))


def on_start(room: int, game: Game):
    emit("game_start", game.market_lvl, room=room)


@socket.on('esm_order')
def esm_order(pid: int, price: int, qty: int):
    game: Game = db_connector.get_game(db_connector.get_game_id(pid))
    is_senior: bool = db_connector.get_player_state(pid).rang == game.turn_num % game.max_players
    esm_orders.append((game.id, pid, price, qty, is_senior))
    db_connector.inc_game_progress(game.id)
    game.progress += 1
    if game.progress == game.max_players:
        orders = sort_esm_orders(game)
        esm_auction(orders, game.market_lvl, game.max_players)


def sort_esm_orders(game: Game) -> list:
    game_orders = []
    for order in esm_orders:
        if order[0] == game.id:
            game_orders.append(order)
    game_orders.sort(key=lambda obj: obj[2])
    tmp_index: int
    for order in game_orders:
        if order[4]:
            tmp_index = game_orders.index(order)
            break
    if tmp_index != 0 and game_orders[tmp_index][2] == game_orders[tmp_index - 1][2]:
        a = game_orders[tmp_index]
        game_orders[tmp_index] = game_orders[tmp_index - 1]
        game_orders[tmp_index - 1] = a
    return game_orders


def esm_auction(orders: list, market_lvl: int, players: int):
    esm_left = market[market_lvl - 1][1] * players
    for order in orders:
        if esm_left - order[3] >= 0:
            emit('accepted', order[1], room=order[0])
            esm_left -= order[3]
        else:
            break


@socket.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socket.run(app, host='0.0.0.0')


class TestSocketIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # def test_connect(self):
    #     client = socket.test_client(app)
    #     received = client.get_received()
    #     self.assertEqual(received[0]['name'], 'opened')
    #     client.disconnect()
    #
    # def test_register(self):
    #     client = socket.test_client(app)
    #     client.emit('register_player', 'a', 0)
    #     received = client.get_received()
    #     print(received)
    #     self.assertEqual(received[0]['args'], 'Ok')

    def test_create_game(self):
        client = socket.test_client(app)
        client.emit('create_game', 1, '2e23ea', 2, 2, 10000, 1, 1, 4)
        client.disconnect()
