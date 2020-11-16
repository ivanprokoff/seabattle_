from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from random import randint, choice
from PyQt5 import QtCore


class BattleField(QWidget):

    # возможные состояния клеток
    EMPTY_CELL = 0
    SHIP_CELL = 1
    HIT_CELL = 2
    MISS_CELL = 3

    V_ORIENTATION = 0
    H_ORIENTATION = 1

    FIELDS_NUM = 10

    def __init__(self, enemy_field=False):
        super(BattleField, self).__init__()
        self.enemy_field = enemy_field
        self.field = []
        self.setup_UI()

    def setup_UI(self):
        """
        Инициализация интерфейса поля морского боя
        """
        cell_size = 39
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setRowCount(10)
        self.table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        horizontal_header = QHeaderView(Qt.Horizontal)
        vertical_header = QHeaderView(Qt.Vertical)
        horizontal_header.setDefaultSectionSize(cell_size)
        vertical_header.setDefaultSectionSize(cell_size)
        self.table.setHorizontalHeader(horizontal_header)
        self.table.setHorizontalHeaderLabels([c for c in "АБВГДЕЖЗИК"])

        for r in range(10):
            for c in range(10):
                self.table.setItem(r, c, QTableWidgetItem())

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.init_ships()

    def update_field_UI(self, victory=False):
        my_ship_color = QColor(100, 100, 150)
        enemy_ship_color = QColor(100, 100, 150)
        miss_color = QColor(179, 179, 179)
        hit_color = QColor(255, 0, 0)

        for x in range(self.FIELDS_NUM):
            for y in range(self.FIELDS_NUM):
                if not victory:
                    if self.enemy_field:
                        if self.field[x][y] == self.HIT_CELL:
                            self.table.item(x, y).setBackground(hit_color)
                        elif self.field[x][y] == self.MISS_CELL:
                            self.table.item(x, y).setBackground(miss_color)
                        elif self.field[x][y] == self.SHIP_CELL:
                            pass
                    else:
                        if self.field[x][y] == self.HIT_CELL:
                            self.table.item(x, y).setBackground(hit_color)
                        elif self.field[x][y] == self.MISS_CELL:
                            self.table.item(x, y).setBackground(miss_color)
                        elif self.field[x][y] == self.SHIP_CELL:
                            self.table.item(x, y).setBackground(my_ship_color)
                else:
                    if self.field[x][y] == self.SHIP_CELL:
                        self.table.item(x, y).setBackground(enemy_ship_color)

    def init_ships(self):
        """
        Случайная расстановка кораблей и их отрисовка
        """
        # Создаем пустое поле битвы
        self.field = [[0] * self.FIELDS_NUM for i in range(self.FIELDS_NUM)]

        # Флот кораблей
        ship_fleet = [(1, 4), (2, 3), (3, 2), (4, 1)]
        # записываем корабли в матрицу расположения флота
        for ship in ship_fleet:
            for ship_count in range(ship[0]):
                valid = False
                random_x, random_y = -1, -1
                o = choice([self.H_ORIENTATION, self.V_ORIENTATION])
                while not valid:
                    random_x = randint(0, self.FIELDS_NUM - 1)
                    random_y = randint(0, self.FIELDS_NUM - 1)
                    valid = self.is_valid_position(random_x, random_y, o, ship[1])
                self.place_ship(random_x, random_y, o, ship[1])
        self.update_field_UI()

    def is_valid_position(self, start_x, start_y, orientation, length):
        """
        Проверка указанных координат и ориентации кораблся на пересечение с другими кораблями и
        на выход за границы игрового поля.
        :return: True, если корабль можно поставить в указанную позицию, иначе False.
        """
        end_x, end_y = -1, -1
        if orientation == self.H_ORIENTATION:
            if start_x + length > self.FIELDS_NUM:
                return False
            end_x = min(start_x + length, self.FIELDS_NUM - 1)
            end_y = min(start_y + 1, self.FIELDS_NUM - 1)
        elif orientation == self.V_ORIENTATION:
            if start_y + length > self.FIELDS_NUM:
                return False
            end_x = min(start_x + 1, self.FIELDS_NUM - 1)
            end_y = min(start_y + length, self.FIELDS_NUM - 1)

        start_x = start_x if start_x == 0 else start_x - 1
        start_y = start_y if start_y == 0 else start_y - 1

        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                if self.field[x][y] == self.SHIP_CELL:
                    return False
        return True

    def place_ship(self, start_x, start_y, orientation, length):
        """
        Ставит корабль в начальную точку и располагает его согласно значению ориентации.
        Считается, что задаваемое положение проверено с помощью функции is_valid_position.
        """
        end_x, end_y = -1, -1
        if orientation == self.H_ORIENTATION:
            end_x = start_x + length
            end_y = start_y + 1
        elif orientation == self.V_ORIENTATION:
            end_x = start_x + 1
            end_y = start_y + length

        # сохраняем информацию о корабле в матрицу расположения флота
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                self.field[x][y] = self.SHIP_CELL

    def count_if(self, value):
        """
        :return: Возвращает количество ячеек, значение в которых равно value.
        """
        count = 0
        for x in range(self.FIELDS_NUM):
            for y in range(self.FIELDS_NUM):
                if self.field[x][y] == value:
                    count += 1
        return count

    def is_valid_shot(self, x, y):
        """
        :return: Вернет True, если клетка не содержит корабля и ранее не была обстрелена
        """
        return self.field[x][y] == self.EMPTY_CELL or self.field[x][y] == self.SHIP_CELL
