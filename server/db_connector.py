import sqlite3
from game import Game
from player_state import PlayerState
from player import Player


def sql(query, has_result: bool = False, params=()):
    con = sqlite3.connect("test.db")
    curs = con.cursor()
    if has_result:
        return curs.execute(query, params).fetchall()
    curs.execute(query, params)
    con.commit()


def create_db():
    # sql("drop table if exists players")
    # sql("drop table if exists games")
    sql("drop table if exists player_states")
    sql("drop table if exists credits")
    sql("DROP TABLE IF EXISTS construction")

    sql("create table if not exists players("
        "id  INTEGER primary key, "
        "nickname string not null unique,"
        "avatar integer)")

    sql("CREATE TABLE IF NOT EXISTS games("
        "id INTEGER PRIMARY KEY,"
        "turn_num INTEGER,"
        "turn_stage INTEGER,"
        "market_lvl INTEGER,"
        "isOpened INTEGER,"
        "name VARCHAR,"
        "s_esm INTEGER,"
        "s_egp INTEGER,"
        "s_money INTEGER,"
        "s_fabrics_1 INTEGER,"
        "s_fabrics_2 INTEGER,"
        "max_players INTEGER,"
        "progress INTEGER)")

    sql("CREATE TABLE player_states("
        "player_id INTEGER PRIMARY KEY,"
        "esm INTEGER,"
        "egp INTEGER,"
        "fabrics_1 INTEGER,"
        "fabrics_2 INTEGER,"
        "game_id INTEGER,"
        "money INTEGER,"
        "rang INTEGER,"
        "FOREIGN KEY (player_id) REFERENCES players(id),"
        "FOREIGN KEY (game_id) REFERENCES games(id))")

    sql("CREATE TABLE credits("
        "id INTEGER PRIMARY KEY,"
        "player_id INTEGER,"
        "amount INTEGER,"
        "month INTEGER,"
        "FOREIGN KEY (player_id) REFERENCES player_states(player_id) )")

    sql("CREATE TABLE construction("
        "id INTEGER PRIMARY KEY,"
        "player_id INTEGER,"
        "isAutomated BOOLEAN,"
        "start_month INTEGER,"
        "FOREIGN KEY (player_id) REFERENCES player_states(player_id))")


def get_player(nickname: str) -> Player:
    query = sql('SELECT * FROM players WHERE nickname = ?', True, (nickname,))[0]
    return Player(query[0], query[1], query[2])


def get_player_state_pid(pid: int) -> PlayerState:
    query_res = sql(f'SELECT * FROM player_states WHERE player_id = ?', True, pid)
    return PlayerState(query_res[0], query_res[1], query_res[2], query_res[3], query_res[4],
                       query_res[5], query_res[6], query_res[7])


# возвращает все сущности состояние_игрока привязанные к игре
def get_player_state_gid(gid: int) -> list:
    query_res = sql(f'SELECT * FROM player_states WHERE game_id = ?', True, gid)
    result: list = []
    for line in query_res:
        result.append(PlayerState(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7]))
    return result


def add_player(nick, avatar):
    sql('INSERT INTO players (nickname, avatar) values (?, ?)', params=(nick, avatar))


def add_game(pid, title, esm, egp, money, fabrics_1, fabrics_2, max_players):
    if title == '':
        title = pid
    sql(f'INSERT INTO games VALUES (NULL, 0, 0, 3, ?, ?, ?, ?, ?, ?, ?, ?, 0)',
        params=(1, title, esm, egp, money, fabrics_1, fabrics_2, max_players))

    game_id = sql('SELECT id FROM games WHERE isOpened == ? AND name == ?', True, (True, title))

    sql('INSERT INTO player_states VALUES (?, ?, ?, ?, ?, ?, ?, 0)',
        params=(pid, esm, egp, fabrics_1, fabrics_2, game_id[0][0], money))


def get_game_id(player_id: int):
    return sql(
        f"SELECT state.game_id FROM games "
        f"JOIN player_states state ON games.id = state.game_id "
        f"WHERE state.player_id = ? AND games.isOpened = ? "
        f"LIMIT 1", params=(player_id, True))[0]


def get_game(game_id: int):
    return Game(sql(f'SELECT * FROM games WHERE id = ?', True, game_id)[0])


def get_games_list() -> list:
    return sql('SELECT * FROM games WHERE isOpened = 1', True)


def inc_game_progress(game_id: int):
    sql(f'UPDATE games SET progress = progress + 1 WHERE id = ?', params=game_id)


def join_player(pid, game_id: int):
    game = Game(sql(f'SELECT * FROM games WHERE id == ? LIMIT 1', params=game_id))
    rang = sql('SELECT count(player_id) FROM player_states WHERE game_id == ?', params=game_id)
    sql('INSERT INTO player_states VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        params=(pid, game.s_esm, game.s_egp, game.s_fabrics1, game.s_fabrics2, game.id, game.s_money, rang))
    return rang == game.max_players


def esm_result(approved_orders: list):
    for order in approved_orders:
        ps: PlayerState = get_player_state_pid(order.player_id)
        ps.esm += order.quantity
        ps.money -= order.quantity * order.price
        sql('UPDATE player_states SET esm = ?, money = ? WHERE player_id = ?', params=(ps.esm, ps.money, ps.player_id))


def egp_result(approved_orders: list):
    for order in approved_orders:
        ps: PlayerState = get_player_state_pid(order.player_id)
        ps.egp -= order.quantity
        ps.money += order.quantity * order.price
        sql('UPDATE player_states SET egp = ?, money = ? WHERE player_id = ?', params=(ps.egp, ps.money, ps.player_id))


def egp_produce(ps: PlayerState):
    sql('UPDATE player_states SET egp = ?, esm = ?, money = ? WHERE player_id = ?',
        params=(ps.egp, ps.esm, ps.money, ps.player_id))


def get_credits(pid: int):
    return sql('SELECT credits.amount FROM credits WHERE player_id = ?', True, pid)


def set_money(pid: int, amount: int):
    sql('UPDATE player_states SET money = ? WHERE player_id = ?', params=(amount, pid))


def credit_payoff(credit_id: int):
    sql('DELETE FROM credits WHERE id = ?', params=credit_id)


def get_player_pid(pid: int) -> Player:
    query = sql('SELECT * FROM players WHERE id = ?', True, pid)
    return Player(query[0], query[1], query[2])


def take_credit(pid: int, amount: int, month: int):
    sql('INSERT INTO credits VALUES (NULL, ?, ?, ?)', params=(pid, amount, month))


def build_fabric(pid: int, is_auto: bool, month: int):
    sql('INSERT INTO construction VALUES (NULL, ?, ?, ?)', params=(pid, is_auto, month))


def inc_game_turn(game_id: int):
    sql('UPDATE games SET turn_num = turn_num + 1 WHERE id = ?', params=game_id)


def get_game_pid(pid: int) -> Game:
    return get_game(get_game_id(pid))
