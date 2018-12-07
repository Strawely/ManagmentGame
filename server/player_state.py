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
        if quantity > self.esm or fabrics_1 > self.fabrics_1 + self.fabrics_2 or fabrics_2 > self.fabrics_2 \
                or quantity > fabrics_1 + fabrics_2 * 2:
            return 0
        produced_egp: int = fabrics_2 * 2
        cost: int = fabrics_2 * 3000
        if produced_egp > quantity:
            return 0, 0
        if quantity > produced_egp:
            produced_egp += fabrics_1
            cost += fabrics_1 * 2000
            if produced_egp > quantity:
                return 0, 0

        if quantity == produced_egp:
            self.egp += produced_egp
            self.money -= cost
        self.egp += produced_egp
        self.esm -= produced_egp
        self.money -= cost
        return produced_egp, cost
