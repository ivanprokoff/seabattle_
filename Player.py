import random


class ActivePlayer:
    """
    Класс игрока с набором необходимых атрибутов
    """

    def __init__(self, player_field, enemy_field):
        self.last_shot = None, None
        self.enemy_filed = enemy_field
        self.player_field = player_field
        self.row = None
        self.col = None
        self.sucess_shot = False
        self.enemy_field = enemy_field
        self.player_field = player_field

    def shot(self):
        pass


class BotPlayer:
    """
    Класс игрока - бота с набором атрибутов
    """
    success_shot = False

    def __init__(self, player_field, enemy_field):
        self.last_shot = None, None
        self.enemy_filed = enemy_field
        self.player_field = player_field
        self.row = None
        self.col = None
        self.sucess_shot = False
        self.name = 'Бот'
        self.enemy_field = enemy_field
        self.player_field = player_field
        self.row = None
        self.col = None

    def shot(self):
        """
        Выстрел бота
        :return: координаты выстрела
        """
        self.row, self.col = self._get_random_coordinats()
        while not self.enemy_filed.is_valid_shot(self.row, self.col):
            self.row, self.col = self._get_random_coordinats()
        if self.enemy_field.field[self.row][self.col] == 1:
            self.enemy_field.field[self.row][self.col] = 2
            self.success_shot = True
        else:
            self.enemy_field.field[self.row][self.col] = 3
            self.success_shot = False
        self.enemy_field.update_field_UI()

    def _get_random_coordinats(self):
        return random.randint(0, 9), random.randint(0, 9)
