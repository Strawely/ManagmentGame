import db_connector


class Player:
    id: int
    nickname: str
    avatar: int

    def __init__(self, id: int, nickname: str, avatar: int):
        self.id = id
        self.nickname = nickname
        self.avatar = avatar

    # возвращает выплаченную сумму
    def check_credit_payoff(self) -> int:
        current_month = db_connector.get_game_pid(self.id).turn_num
        result = 0
        for credit in db_connector.get_credits(self.id):
            if credit[3] == current_month - 12:
                self.pay_credit(credit[0], credit[3])
                result += credit[3]

    def pay_credit(self, credit_id: int, amount: int):
        current_money = db_connector.get_player_state_pid(self.id).money
        db_connector.set_money(self.id, current_money - amount)
        db_connector.credit_payoff(credit_id)
