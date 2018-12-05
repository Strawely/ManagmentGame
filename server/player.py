class PlayerState:
    id: int
    rang: int

    def __init__(self, query: list):
        self.id = query[0]
        self.rang = query[7]
