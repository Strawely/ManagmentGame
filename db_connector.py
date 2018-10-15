import sqlite3


def sql(query, has_result=0, params=()):
    con = sqlite3.connect("test.db")
    curs = con.cursor()
    if has_result:
        return curs.execute(query, params).fetchall()
    curs.execute(query, params)
    con.commit()


def create_db():
    # sql("drop table if exists players")
    sql("drop table if exists games")
    sql("drop table if exists player_states")
    sql("drop table if exists credits")

    sql("create table players("
        "id  string  primary key, "
        "nickname string not null unique,"
        "avatar integer)")

    sql("CREATE TABLE games("
        "id INTEGER PRIMARY KEY,"
        "turn_num INTEGER,"
        "turn_stage INTEGER,"
        "market_lvl INTEGER,"
        "isOpened BOOLEAN,"
        "name VARCHAR,"
        "s_esm INTEGER,"
        "s_egp INTEGER,"
        "s_money INTEGER,"
        "s_fabrics_1 INTEGER,"
        "s_fabrics_2 INTEGER,"
        "max_players INTEGER)")

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


def get_player(nickname):
    return sql(f'SELECT * FROM players WHERE nickname = ?', 1, (nickname,))[0]


def add_player(nick, avatar):
    sql('INSERT INTO players (nickname, avatar) values (?, ?)', 0, (nick, avatar))


def add_game(pid, title, esm, egp, money, fabrics_1, fabrics_2):
    if title == '':
        title = pid
    sql(f'INSERT INTO games VALUES (NULL, 0, 0, 3, 1, ?, ?, ?, ?, ?, ?)',
        params=(title, esm, egp, money, fabrics_1, fabrics_2))

    game_id = sql('SELECT id FROM games WHERE isOpened == 1 AND name == ?', 1, title)
    sql('INSERT INTO player_states VALUES (?, ?, ?, ?, ?, ?, ?, 0)',
        params=(pid, esm, egp, fabrics_1, fabrics_2, game_id, money))


def join_player(pid, gid):
    start_res = sql(f'SELECT * FROM games WHERE id == ?', params=gid)
    rang = sql('SELECT count(player_id) FROM player_states WHERE game_id == ?', params=gid)
    sql('INSERT INTO player_states VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        params=(pid, start_res[6], start_res[7], start_res[9], start_res[10], start_res[0], start_res[8], rang))
    return rang == start_res[11]



