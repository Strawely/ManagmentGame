import db_connector
from order import Order
import random


def create_game(player_id, esm, egp, money, fabrics_1, fabrics_2, max_players, title=''):
    db_connector.add_game(player_id, title, esm, egp, money, fabrics_1, fabrics_2, max_players)


def player_join(player_id, game_id):
    return db_connector.join_player(player_id, game_id)


class Game:
    # свойства сущности в БД
    id: int = 0
    turn_num: int = 0
    turn_stage: int = 0
    market_lvl: int = 0
    isOpened: int = 0
    name: str = ''
    s_esm: int = 0
    s_egp: int = 0
    s_money: int = 0
    s_fabrics1: int = 0
    s_fabrics2: int = 0
    max_players: int = 0
    progress: int = 0

    esm_orders = []
    market = ((1, 1.0, 800, 3.0, 6500),
              (2, 1.5, 650, 2.5, 6000),
              (3, 2.0, 500, 2.0, 5500),
              (4, 2.5, 400, 1.5, 5000),
              (5, 3.0, 300, 1.0, 4500))

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
        self.market = ((1, 1.0 * self.max_players, 800, 3.0 * self.max_players, 6500),
                       (2, 1.5 * self.max_players, 650, 2.5 * self.max_players, 6000),
                       (3, 2.0 * self.max_players, 500, 2.0 * self.max_players, 5500),
                       (4, 2.5 * self.max_players, 400, 1.5 * self.max_players, 5000),
                       (5, 3.0 * self.max_players, 300, 1.0 * self.max_players, 4500))

    def sort_esm_orders(self) -> list:
        game_orders: list = self.esm_orders.copy()
        # game_orders.sort(key=lambda obj: obj[2])
        game_orders.sort(key=lambda obj1, obj2: obj1.price >= obj2.price)
        tmp_index: int
        for order in game_orders:
            if order.is_senior:
                tmp_index = game_orders.index(order)
                break
        if tmp_index != 0 and game_orders[tmp_index].price == game_orders[tmp_index - 1].price:
            a = game_orders[tmp_index]
            game_orders[tmp_index] = game_orders[tmp_index - 1]
            game_orders[tmp_index - 1] = a
        return game_orders

    # можно зарефакторить через передачу лямбды
    def sort_esm_orders(self) -> list:
        game_orders: list = self.esm_orders.copy()
        # game_orders.sort(key=lambda obj: obj[2])
        game_orders.sort(key=lambda obj1, obj2: obj1.price <= obj2.price)
        tmp_index: int
        for order in game_orders:
            if order.is_senior:
                tmp_index = game_orders.index(order)
                break
        if tmp_index != 0 and game_orders[tmp_index].price == game_orders[tmp_index - 1].price:
            a = game_orders[tmp_index]
            game_orders[tmp_index] = game_orders[tmp_index - 1]
            game_orders[tmp_index - 1] = a
        return game_orders

    def start_esm_auction(self, orders: list) -> list:
        for order in orders:
            if order.game_id == self.id:
                self.esm_orders.append(order)
        orders = self.sort_esm_orders()
        count = self.esm_auction(orders)
        result = []
        while count >= 0:
            result.append(orders.pop(0))
            count -= 1
        db_connector.esm_result(result)
        return result

    def start_egp_auction(self, orders: list) -> list:
        for order in orders:
            if order.game_id == self.id:
                self.esm_orders.append(order)
        orders = self.sort_egp_orders()
        count = self.egp_auction(orders)
        result = []
        while count >= 0:
            result.append(orders.pop(0))
            count -= 1
        return result

    # возвращает кол-во удовлетворенных заявок
    def esm_auction(self, orders: list) -> int:
        esm_left = self.market[self.market_lvl - 1][1] * self.max_players
        for index, order in enumerate(orders):
            if esm_left - order[3] >= 0:
                # emit('accepted', order[1], room=order[0])
                esm_left -= order[3]
            else:
                return index - 1
        return len(orders) - 1

    def egp_auction(self, orders: list) -> int:
        esm_left = self.market[self.market_lvl - 1][1] * self.max_players
        for index, order in enumerate(orders):
            if esm_left - order[3] >= 0:
                # emit('accepted', order[1], room=order[0])
                esm_left -= order[3]
            else:
                return index - 1
        return len(orders) - 1

    # инкрементируем количество игроков, сделавших ход и проверям, равно ли максимальному
    def update_progress(self) -> bool:
        db_connector.inc_game_progress(self.id)
        self.progress += 1
        if self.progress != self.max_players - 1:
            return False
        db_connector.zero_progress(self.id)
        self.progress = 0
        return True

    # возвращает список сумм (изъятая сумма у каждого игрока)
    def pay_bank_percent(self) -> list:
        # получить из бд по каждому игроку игры сумму ссуд и получить 1%
        ps: list = db_connector.get_player_state_gid(self.id)
        result: list = []
        for state in ps:
            sum = db_connector.get_credits(state.player_id)[2]
            result.append(int(sum / 100))
            db_connector.set_money(state.player_id, state.money - int(sum / 100))
        return result

    def inc_game_turn(self):
        db_connector.inc_game_turn(self.id)

    def get_json(self) -> list:
        return [self.id, self.turn_num, self.turn_stage, self.market_lvl, self.isOpened, self.name, self.s_esm,
                self.s_egp, self.s_money, self.s_fabrics1, self.s_fabrics2, self.max_players, self.progress]

    def get_bankrupts(self) -> list:
        result = []
        player_states = db_connector.get_player_state_gid(self.id)
        for ps in player_states:
            if ps.money <= 0:
                result.append(ps.player_id)
        return result

    def get_new_market_lvl(self) -> int:
        new_lvl = 3
        if self.market_lvl == 1:
            new_lvl = random.choices([1, 2, 3, 4, 5], weights=[1 / 3, 1 / 3, 1 / 6, 1 / 12, 1 / 12])
        elif self.market_lvl == 2:
            new_lvl = random.choices([1, 2, 3, 4, 5], weights=[1 / 4, 1 / 3, 1 / 4, 1 / 12, 1 / 12])
        elif self.market_lvl == 3:
            new_lvl = random.choices([1, 2, 3, 4, 5], weights=[1 / 12, 1 / 4, 1 / 3, 1 / 4, 1 / 12])
        elif self.market_lvl == 4:
            new_lvl = random.choices([1, 2, 3, 4, 5], weights=[1 / 12, 1 / 12, 1 / 4, 1 / 3, 1 / 4])
        elif self.market_lvl == 5:
            new_lvl = random.choices([1, 2, 3, 4, 5], weights=[1 / 12, 1 / 12, 1 / 6, 1 / 3, 1 / 3])
        db_connector.new_market_lvl(self.id, new_lvl)
        return new_lvl
