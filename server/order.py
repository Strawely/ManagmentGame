class Order:
    game_id: int
    player_id: int
    price: int
    quantity: int
    is_senior: bool

    def __init__(self, game: int, player: int, price: int, quantity: int, is_senior: bool):
        self.game_id = game
        self.player_id = player
        self.price = price
        self.quantity = quantity
        self.is_senior = is_senior

    def __eq__(self, o: object) -> bool:
        other: Order = o
        return self.game_id == other.game_id and self.player_id == other.player_id \
            and self.is_senior == other.is_senior and self.price == other.price and self.quantity == other.quantity

    def get_json(self):
        return [self.game_id, self.player_id, self.price, self.quantity, self.is_senior]
