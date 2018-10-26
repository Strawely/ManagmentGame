import sqlite3


class PlayerState:
    id: int
    rang: int

    def __init__(self, query: list):
        id = query[0]
        rang = query[7]
