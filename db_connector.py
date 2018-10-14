import sqlite3


def sql(query, has_result=0, params=()):
    con = sqlite3.connect("test.db")
    curs = con.cursor()
    if has_result:
        return curs.execute(query, params).fetchall()
    curs.execute(query, params)
    con.commit()


def create_db():
    sql("drop table if exists players")
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
        "s_fabrics_2 INTEGER)")

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


def get_player(nickname):
    return sql(f'SELECT * FROM players WHERE nickname = ?', 1, (nickname,))[0]


def add_player(nick, avatar):
    sql('INSERT INTO players (nickname, avatar) values (?, ?)', 0, (nick, avatar))


def add_game(title, esm, egp, money, fabrics_1, fabrics_2):
    sql('INSERT INTO games VALUES (NULL, 0, 0, 3, 1, title, esm, egp, money, fabrics_1, fabrics_2 )')
