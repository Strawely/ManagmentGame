import sqlite3
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room
import db_connector
import game
from game import Game
from order import Order
from player import Player
from player_state import PlayerState
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket = SocketIO(app, async_mode="gevent")
db_connector.create_db()

esm_orders: list = []
egp_orders: list = []


@app.route('/')
def index():
    return 'Hello world'


@socket.on("connect")
def con():
    print('Connected')
    emit('success')


def encode_player(player: Player):
    return player.id, player.nickname, player.avatar


# 0 - удалось добавить, 1 - уже существует, -1 - ошибка
@socket.on("register_player")
def add_player(nick: str, avatar: int):
    try:
        if db_connector.get_player(nick) is None:
            db_connector.add_player(nick, avatar)
            return 0, db_connector.get_player(nick).get_json()
        else:
            return 1, db_connector.get_player(nick).get_json()
    except sqlite3.IntegrityError:
        return -1, "Невозможно зарегистрировать игрока"


# @socket.on("get_player")
# def get_player(nick):
#     res = db_connector.get_player(nick)
#     emit("get_player_resp", res)


@socket.on('get_games_list')
def get_games_list():
    return db_connector.get_games_list()


@socket.on("create_game")
def create_game(pid, sesid, name, esm, egp, money, fabrics_1, fabrics_2, max_players):
    game.create_game(pid, esm, egp, money, fabrics_1, fabrics_2, max_players, name)
    join_room(db_connector.get_game_id(pid), sid=sesid)
    db_connector.inc_game_progress(db_connector.get_game_id(pid))
    return db_connector.get_game_pid(pid).get_json()
    # game.player_join(pid, db_connector.get_game_id(pid))


@socket.on("join_game")
def join_game(game_id, sesid, pid):
    join_room(game_id, sesid)
    if game.player_join(pid, game_id):
        db_connector.zero_progress(game_id)
        on_start(game_id, db_connector.get_game(game_id))


@socket.on('leave_game')
def leave_game(pid: int, sid: int):
    game_instance: Game = db_connector.get_game_pid(pid)
    is_senior: bool = db_connector.get_player_state_pid(pid).rang == game_instance.turn_num % game_instance.max_players
    if is_senior:
        senior_leave(game_instance.id)
    leave_room(game_instance.id, sid)
    game_instance.player_leave(pid)


@socket.on('senior_leave')
def senior_leave(game_id):
    db_connector.get_game(game_id).close()
    emit('game_canceled', room=game_id)
    close_room(game_id)


def on_start(room: int, game: Game):
    db_connector.close_game(game.id)
    emit("game_start", game.market_lvl, room=room)


def wait_esm(room: int):
    emit("wait_esm_order", room=room)


@socket.on('esm_order')
def esm_order(pid: int, price: int, qty: int):
    game: Game = db_connector.get_game_pid(pid)
    is_senior: bool = db_connector.get_player_state_pid(pid).rang == game.turn_num % game.max_players
    esm_orders.append(Order(game.id, pid, price, qty, is_senior))
    if game.update_progress():
        game_orders: list = []
        for order in esm_orders:
            if order.game_id == game.id:
                game_orders.append(order)
                esm_orders.remove(order)
        send_esm_approved(game.start_esm_auction(game_orders), game.id)


def send_esm_approved(orders_approved: list, room: int):
    orders_json: list = []
    for order in orders_approved:
        orders_json.append(order.get_json())
    emit("esm_orders_approved", orders_json, room=room)
    emit("wait_build_requests", room=room)


@socket.on('disconnect')
def test_disconnect():
    print('Client disconnected')


@socket.on('produce')
def produce(pid: int, quantity: int, fabrics_1: int, fabrics_2: int):
    player_state = db_connector.get_player_state_pid(pid)
    result = player_state.get_egp(quantity, fabrics_1, fabrics_2)
    if result[0] == 0:
        emit('production_error')
        return
    emit('produced', (result[0], result[1]))
    game: Game = db_connector.get_game_pid(pid)
    if game.update_progress():
        emit('wait_egp_request')


# метод обработки заявки на ЕГП, тут же произвдится выплата банковского процента
@socket.on('egp_request')
def egp_request(pid: int, price: int, qty: int):
    game: Game = db_connector.get_game_pid(pid)
    is_senior: bool = db_connector.get_player_state_pid(pid).rang == game.turn_num % game.max_players
    egp_orders.append(Order(game.id, pid, price, qty, is_senior))
    if game.update_progress():
        send_egp_approved(game.start_egp_auction(egp_orders), game.id)
        pay_bank_percent(game, db_connector.get_game_id(pid))


def send_egp_approved(orders_approved: list, room: int):
    for order in esm_orders:
        for order_app in orders_approved:
            if order.__eq__(order_app):
                esm_orders.remove(order)
    emit("egp_orders_approved", orders_approved, room=room)


def pay_bank_percent(game: Game, room: int):
    emit('paid_percents', game.pay_bank_percent(), room=room)  # в зависимости от значения rang можно для каждого
    #  игрока получить выплаченные проценты
    emit('wait_credit_payoff', room=room)


@socket.on('credit_payoff')
def credit_payoff(pid: int):
    player: Player = db_connector.get_player_pid(pid)
    emit('paid_credit_sum', player.check_credit_payoff())
    game: Game = db_connector.get_game_pid(pid)
    if game.update_progress():
        emit('wait_take_credit')


@socket.on('take_credit')
def take_credit(pid: int, amount: int):
    ps: PlayerState = db_connector.get_player_state_pid(pid)
    ps.take_credit(amount)
    if db_connector.get_game_pid(pid).update_progress():
        emit('wait_build_request')


@socket.on('build_request')
def build_request(pid: int, is_auto: bool):
    ps: PlayerState = db_connector.get_player_state_pid(pid)
    ps.build_fabric(is_auto)
    if db_connector.get_game_pid(pid).update_progress():
        define_bankrupts(pid)
        emit('wait_next_turn', room=db_connector.get_game_id(pid))


@socket.on('next_turn')
def next_turn(pid: int):
    ps: PlayerState = db_connector.get_player_state_pid(pid)
    ps.pay_taxes()
    game: Game = db_connector.get_game_pid(pid)
    if game.update_progress():
        socket.emit('new_market_lvl', game.get_new_market_lvl(), room=game.id)
        socket.emit('wait_esm_order', room=game.id)


def define_bankrupts(pid: int):
    bankrupts = db_connector.get_game_pid(pid).get_bankrupts()
    emit('bankrupts', bankrupts, room=db_connector.get_game_id(pid))


@socket.on('get_player_state')
def get_player_state(pid: int):
    ps: PlayerState = db_connector.get_player_state_pid(pid)
    return [ps.player_id, ps.esm, ps.egp, ps.fabrics_1, ps.fabrics_2, ps.game_id, ps.money, ps.rang]


@socket.on('bankrupt_leave')
def bankrupt_leave(pid: int, sid):
    leave_room(db_connector.get_game_id(pid), sid)
    db_connector.del_player_state(pid)
    db_connector.dec_max_players(db_connector.get_game_id(pid))
    if db_connector.get_game_pid(pid).max_players == 1:
        emit('game_over')
        define_winner(db_connector.get_game_id(pid))


def define_winner(game_id: int):
    scores = db_connector.get_game(game_id).get_score_list()
    emit('scores_list', scores)


# todo располовинить стоимость фабрик
if __name__ == '__main__':
    socket.run(app, host='0.0.0.0')
