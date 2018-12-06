import sqlite3
from flask import Flask
from flask_socketio import SocketIO, emit, join_room
import db_connector
import game
from game import Game
from order import Order

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket = SocketIO(app, async_mode="eventlet")
db_connector.create_db()

esm_orders: list = []


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
        on_start(game_id, db_connector.get_game(game_id))


def on_start(room: int, game: Game):
    emit("game_start", game.market_lvl, room=room)
    emit("wait_esm_order", room=room)


@socket.on('esm_order')
def esm_order(pid: int, price: int, qty: int):
    game: Game = db_connector.get_game(db_connector.get_game_id(pid))
    is_senior: bool = db_connector.get_player_state(pid).rang == game.turn_num % game.max_players
    esm_orders.append(Order(game.id, pid, price, qty, is_senior))
    if game.update_progress():
        send_esm_approved(game.start_auction(esm_orders), game.id)


def send_esm_approved(orders_approved: list, room: int):
    # todo Помимо оповещения, нужно внести необходимые изменения в БД
    for order in esm_orders:
        for order_app in orders_approved:
            if order.__eq__(order_app):
                esm_orders.remove(order)
    emit("esm_orders_approved", orders_approved, room=room)
    emit("wait_build_requests", room=room)


@socket.on('disconnect')
def test_disconnect():
    print('Client disconnected')


@socket.on('produce')
def produce(pid: int, quantity: int, fabrics_1: int, fabrics_2: int):
    # get player_state
    # if qty >= player_state.esm
    # give player esm
    # wait for all players
    # emit next stage
    player_state = db_connector.get_player_state(pid)
    if player_state.get_egp(quantity, fabrics_1, fabrics_2) == 0:
        emit("production_error")
        return
    game: Game = db_connector.get_game_id(pid)
    if game.update_progress():
        emit("wait_egp_request")



# проверить количество денег
# создать сущность стройки
# todo Торги по ЕГП
# todo Выплата ссудного процента
# todo Погашение ссуд
# todo Получение ссуд
# todo сделать запрос на стройку
#@socket.on('build_request')
#def build_request(pid: int, isAuto: bool):



if __name__ == '__main__':
    socket.run(app, host='0.0.0.0')
