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

    def get_egp(self, quantity: int, fabrics_1: int, fabrics_2: int) -> int:
        if quantity > self.esm or fabrics_1 > self.fabrics_1 or fabrics_2 > self.fabrics_2 \
                or quantity > fabrics_1 + fabrics_2 * 2:
            return 0
        quantity -= fabrics_2 * 2
        if quantity > 0:
            quantity -= fabrics_1
        if quantity == 0:
            return quantity
        return 0
