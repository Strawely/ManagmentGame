import db_connector
from order import Order
import random
from player_state import PlayerState


def create_game(player_id, esm, egp, money, fabrics_1, fabrics_2, max_players, title=''):
    db_connector.add_game(player_id, title, esm, egp, money, fabrics_1, fabrics_2, max_players)


def player_join(player_id, game_id: int):
    db_connector.inc_game_progress(game_id)
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
    egp_orders = []
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
        self.market = ((1, 1 * self.max_players, 800, 5 * self.max_players, 6500),
                       (2, 2 * self.max_players, 650, 4 * self.max_players, 6000),
                       (3, 3 * self.max_players, 500, 3 * self.max_players, 5500),
                       (4, 4 * self.max_players, 400, 2 * self.max_players, 5000),
                       (5, 5 * self.max_players, 300, 1 * self.max_players, 4500))

    def sort_esm_orders(self) -> list:
        game_orders: list = self.esm_orders.copy()
        # game_orders.sort(key=lambda obj: obj[2])
        game_orders.sort(key=self.sort_esm, reverse=True)
        tmp_index: int = 0
        for order in game_orders:
            ps: PlayerState = db_connector.get_player_state_pid(order.player_id)
            if ps.money < order.quantity * order.price:
                order.quantity = 0
            if order.price < self.market[self.market_lvl-1][2]:
                order.quantity = 0
            if order.is_senior:
                tmp_index = game_orders.index(order)
                break
        if tmp_index != 0 and game_orders[tmp_index].price == game_orders[tmp_index - 1].price:
            a = game_orders[tmp_index]
            game_orders[tmp_index] = game_orders[tmp_index - 1]
            game_orders[tmp_index - 1] = a
        return game_orders

    def sort_esm(self, o: Order):
        return o.price

    # можно зарефакторить через передачу лямбды
    def sort_egp_orders(self) -> list:
        game_orders: list = self.egp_orders.copy()
        game_orders.sort(key=self.sort_esm, reverse=False)
        tmp_index: int = 0
        for order in game_orders:
            ps: PlayerState = db_connector.get_player_state_pid(order.player_id)
            if ps.egp < order.quantity:
                order.quantity = 0
            if order.price > self.market[self.market_lvl - 1][4]:
                order.quantity = 0
            if order.is_senior:
                tmp_index = game_orders.index(order)
                break
        if tmp_index != 0 and game_orders[tmp_index].price == game_orders[tmp_index - 1].price:
            a = game_orders[tmp_index]
            game_orders[tmp_index] = game_orders[tmp_index - 1]
            game_orders[tmp_index - 1] = a
        return game_orders

    def start_esm_auction(self, orders: list) -> list:
        self.esm_orders = orders
        orders1 = self.sort_esm_orders()
        count = self.esm_auction(orders1)
        result = []
        while count > 0:
            result.append(orders1.pop(0))
            count -= 1
        i: int = 0
        while i < len(result):
            order: Order = result[i]
            if order.quantity == 0:
                result.remove(order)
            else:
                i += 1
        db_connector.esm_result(result)
        return result

    def start_egp_auction(self, orders: list) -> list:
        self.egp_orders = orders
        orders1 = self.sort_egp_orders()
        count = self.egp_auction(orders1)
        result = []
        while count > 0:
            result.append(orders1.pop(0))
            count -= 1
        i: int = 0
        while i < len(result):
            order: Order = result[i]
            if order.quantity == 0:
                result.remove(order)
            else:
                i += 1
        db_connector.egp_result(result)
        return result

    # возвращает кол-во удовлетворенных заявок
    def esm_auction(self, orders: list) -> int:
        esm_left = self.market[self.market_lvl - 1][1]
        for index, order in enumerate(orders):
            if esm_left - order.quantity >= 0:
                esm_left -= order.quantity
            else:
                return index
        return len(orders)

    def egp_auction(self, orders: list) -> int:
        esm_left = self.market[self.market_lvl - 1][1]
        for index, order in enumerate(orders):
            if esm_left - order.quantity >= 0:
                esm_left -= order.quantity
            else:
                return index
        return len(orders)

    # инкрементируем количество игроков, сделавших ход и проверям, равно ли максимальному
    def update_progress(self) -> bool:
        db_connector.inc_game_progress(self.id)
        self.progress += 1
        if self.progress != self.max_players:
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
            sum: int = 0
            for credit in db_connector.get_credits(state.player_id):
                sum += credit[2]
            result.append((state.player_id, int(sum / 100)))
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
        if len(result) > 1:
            result = self.sorting_bankrupts(result)
        return result

    def sort_bankrupts(self, o: object):
        return o.money

    def sorting_bankrupts(self, bankrupts: list) -> list:
        b_sorted = bankrupts.copy()
        b_sorted.sort(key=self.sort_bankrupts, reverse=True)
        return b_sorted

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
        db_connector.new_market_lvl(self.id, new_lvl[0])
        return new_lvl[0]

    def get_score_list(self) -> list:
        result: list = []
        for ps in db_connector.get_player_state_gid(self.id):
            sum = ps.fabrics_1 * 5000 + ps.fabrics_2 * 10000 + ps.esm * self.market[self.market_lvl - 1][2] + \
                  ps.egp * self.market[self.market_lvl - 1][4]
            for credit in db_connector.get_credits(ps.player_id):
                sum -= credit[2]
            sum += ps.money
            result.append([ps.player_id, sum])
        return self.sort_results(result)

    def compare_scores(self, score):
        return score[1]

    def sort_results(self, score_list: list) -> list:
        score_list.sort(key=self.compare_scores, reverse=True)

    def player_leave(self, player_id: int):
        db_connector.del_player_state(player_id)
        self.progress -= 1
        db_connector.set_game(self)

    def close(self):
        db_connector.del_game(self.id)
