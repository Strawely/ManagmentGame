import db_connector


def create_game(player_id, esm, egp, money, fabrics_1, fabrics_2, title=''):
    db_connector.add_game(player_id, title, esm, egp, money, fabrics_1, fabrics_2)


def player_join(player_id, game_id):
    db_connector.join_player(player_id, game_id)
