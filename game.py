import db_connector


def create_game(player_id, esm, egp, money, fabrics_1, fabrics_2, max_players, title=''):
    db_connector.add_game(player_id, title, esm, egp, money, fabrics_1, fabrics_2, max_players)


def player_join(player_id, game_id):
    return db_connector.join_player(player_id, game_id)


class Game:

    id: int = 0
    turn_num: int = 0
    turn_stage: int = 0
    market_lvl: int = 0
    isOpened: bool = False
    name: str = ''
    s_esm: int = 0
    s_egp: int = 0
    s_money: int = 0
    s_fabrics1: int = 0
    s_fabrics2: int = 0
    max_players: int = 0
    progress: int = 0

    def __init__(self, query):
        self.id = query[0]
        self.turn_num = query[1]
        self.turn_stage = query[2]
        self.market_lvl = query[3]
        self.isOpened = query[4]
        self.name = query[5]
        self.s_esm = query[6]
        self.s_egp = query[7]
        self.s_money = query[8]
        self.s_fabrics1 = query[9]
        self.s_fabrics2 = query[10]
        self.max_players = query[11]
        self.progress = query[12]
