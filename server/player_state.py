import db_connector


class PlayerState:
    player_id: int
    esm: int
    egp: int
    fabrics_1: int
    fabrics_2: int
    game_id: int
    money: int
    rang: int

    def __init__(self, player_id: int, esm: int, egp: int, fabrics_1: int, fabrics_2: int, game_id: int,
                 money: int, rang: int):
        self.player_id = player_id
        self.esm = esm
        self.egp = egp
        self.fabrics_1 = fabrics_1
        self.fabrics_2 = fabrics_2
        self.game_id = game_id
        self.money = money
        self.rang = rang

    # возвращает количество созданных ЕГП и затраченных денег
    def get_egp(self, quantity: int, fabrics_1: int, fabrics_2: int) -> (int, int):
        # todo Проверить количество денег
        if fabrics_1 > self.fabrics_1 + self.fabrics_2 or fabrics_2 > self.fabrics_2:
            return 0
        produced_egp: int = fabrics_2 * 2
        cost: int = fabrics_2 * 3000
        #if produced_egp > quantity:
         #   return 0
        #if quantity > produced_egp:
        produced_egp += fabrics_1
        cost += fabrics_1 * 2000
          #  if produced_egp > quantity:
           #     produced_egp = quantity
        if cost > self.money:
            return 0
        #if quantity == produced_egp:
        self.esm -= produced_egp
        self.egp += produced_egp
        self.money -= cost
        # self.egp += produced_egp
        # self.esm -= produced_egp
        # self.money -= cost
        db_connector.update_player_state(self)
        return produced_egp, cost

    def take_credit(self, amount: int) -> int:
        db_connector.set_money(self.player_id, self.money + amount)
        max_amount: int = self.fabrics_1 * 2500 + self.fabrics_2 * 5000
        already_taken: int = 0
        for credit in db_connector.get_credits(self.player_id):
            already_taken += credit[2]
        if already_taken < max_amount:
            max_amount -= already_taken
            if amount > max_amount:
                amount = max_amount
            db_connector.get_credits(self.player_id)
            db_connector.take_credit(self.player_id, amount,
                                     db_connector.get_game_pid(self.player_id).turn_num)
            return amount
        return 0

    def build_fabric(self, is_auto: bool):
        if db_connector.check_month(self.player_id, db_connector.get_game_pid(self.player_id).turn_num+1)[0]:
            db_connector.set_money(self.player_id, self.money - 5000 if db_connector.check_month(self.player_id, db_connector.get_game_pid(self.player_id).turn_num+1)[1] else 2500)
        if self.money > 5000 if is_auto else 2500:
            db_connector.set_money(self.player_id, self.money - (5000 if is_auto else 2500))
        month = db_connector.get_game_pid(self.player_id).turn_num + 7 if is_auto else 5
        db_connector.build_fabric(self.player_id, is_auto, month)

    def upgrade_fabric(self, doIt:bool):
        if db_connector.check_upgrade(self.player_id, db_connector.get_game_pid(self.player_id).turn_num):
                db_connector.set_fabrics1(self.player_id,self.fabrics_1-1)
                db_connector.set_money(self.player_id, self.money - 3500)
        if(doIt):
            if self.money > 3500:
                db_connector.set_money(self.player_id, self.money - 3500)
            month = db_connector.get_game_pid(self.player_id).turn_num + 9
            db_connector.upgrade_fabric(self.player_id, month)

    def pay_taxes(self):
        taxes_value = self.esm * 150 + self.egp * 250 + self.fabrics_1 * 500 + self.fabrics_2 * 750
        db_connector.set_money(self.player_id, self.money - taxes_value)

    def get_json(self):
        return [self.player_id, self.esm, self.egp, self.fabrics_1, self.fabrics_2, self.game_id, self.money, self.rang]
