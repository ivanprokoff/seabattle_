import sqlite3
import sys
from random import choice
from random import randrange

from pprint import pprint
from random import randint

from BattleField import BattleField

from PyQt5 import QtWidgets, QtMultimedia, QtCore
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QAbstractItemView, QTableWidget, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QColor, QFont


class NewGameWin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        super().__init__()
        # Создаем 2 поля боя
        self.myBattleField = BattleField(enemy_field=False)
        self.enemyBattleField = BattleField(enemy_field=True)
        # Инициализируем интерфейс
        self.setup_UI()

    def setup_UI(self):
        """
        Инициализация интерфейса
        """
        self.title = 'Battle Ship'
        self.left = 600
        self.top = 400
        self.width = 890
        self.height = 390
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.message_area = QLabel("Игра начинается!")
        self.message_area.setFont(QFont("Times", 14, QFont.Normal))
        self.start_button = QPushButton('Старт')

        battle_field_layout = QHBoxLayout()
        battle_field_layout.addWidget(self.myBattleField)
        battle_field_layout.addWidget(self.enemyBattleField)
        battle_field_layout.addWidget(self.start_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(battle_field_layout)
        main_layout.addWidget(self.message_area)

        self.setLayout(main_layout)
        self.show()

    def on_shot_status_changed(self, my_shot):
        """
        Функция вызывается после выстрела одного из игроков
        """
        if my_shot:
            self.message_area.setText("Ваш ход!")
        else:
            self.message_area.setText("Ход противника")

        self.is_game_over()

    def is_game_over(self):
        max_hits = 20
        # если 20 клеток помечены, как попадание, то все корабли потоплены
        if self.myBattleField.count_if(BattleField.HIT_CELL) == max_hits or \
                self.enemyBattleField.count_if(BattleField.HIT_CELL) == max_hits:
            self.game_over = True
            print("Game over")
            self.message_area.setText("Игра окончена!")



class SettingsWin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('settings.ui', self)


class RecordsWin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('records.ui', self)
        self.con = sqlite3.connect("records.db")
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM records").fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.newgameWindow = None
        self.settingsWindow = None
        self.recordsWindow = None
        uic.loadUi('main.ui', self)  # Загружаем дизайн
        self.start_btn.clicked.connect(self.newGame)
        self.settings_btn.clicked.connect(self.settings)
        self.records_btn.clicked.connect(self.records)

    def newGame(self):
        if not self.newgameWindow:
            self.newgameWindow = NewGameWin()
        self.newgameWindow.show()

    def settings(self):
        if not self.settingsWindow:
            self.settingsWindow = SettingsWin()
        self.settingsWindow.show()

    def records(self):
        if not self.recordsWindow:
            self.recordsWindow = RecordsWin()
        self.recordsWindow.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    filename = 'music.mp3'
    fullpath = QtCore.QDir.current().absoluteFilePath(filename)
    url = QtCore.QUrl.fromLocalFile(fullpath)
    content = QtMultimedia.QMediaContent(url)
    player = QtMultimedia.QMediaPlayer()
    player.setMedia(content)
    # player.play()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
