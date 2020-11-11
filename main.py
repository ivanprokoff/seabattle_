import sqlite3
import sys
from random import choice
from random import randrange
from datetime import time, datetime

from pprint import pprint
from random import randint

from BattleField import BattleField
from Player import BotPlayer, ActivePlayer

from PyQt5 import QtWidgets, QtMultimedia, QtCore
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QAbstractItemView, QTableWidget, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import pyqtSlot


class NewGameWin(QtWidgets.QWidget):
    def __init__(self):
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
        self.top = 410
        self.width = 890
        self.height = 390
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.setFixedSize(890, 390)

        self.time = QtWidgets.QLabel(self)
        self.time.setGeometry(QtCore.QRect(222, 195, 299, 46))

        self.message_area = QLabel("Игра начинается!")
        self.message_area.setFont(QFont("Times", 14, QFont.Normal))
        self.start_button = QPushButton('Старт')
        self.start_button.clicked.connect(self.battle_loop)

        self.exit_btn = QPushButton('Назад')
        self.exit_btn.resize(75, 23)
        self.exit_btn.move(20, 300)
        self.exit_btn.clicked.connect(self.exit_)

        self.pause_btn = QPushButton('Назад')
        self.pause_btn.resize(75, 23)
        self.pause_btn.move(20, 300)
        self.pause_btn.clicked.connect(self.pause)

        battle_field_layout = QHBoxLayout()
        battle_field_layout.addWidget(self.myBattleField)
        battle_field_layout.addWidget(self.enemyBattleField)
        battle_field_layout.addWidget(self.start_button)
        battle_field_layout.addWidget(self.time)

        main_layout = QVBoxLayout()
        main_layout.addLayout(battle_field_layout)

        self.setLayout(main_layout)
        self.show()

    def battle_loop(self):
        """
        основной игровой цикл
        """
        # self.timer = QtCore.QTimer(self)
        # self.timer.setInterval(1000)
        # self.timer.timeout.connect(self.displayTime)
        # self.timer.start()

        print('Начали!')

        self.game_over = False

        self.first_player = ActivePlayer(self.myBattleField, self.enemyBattleField)
        self.second_player = BotPlayer(self.myBattleField, self.enemyBattleField)
        self.first_player.shot_status_changed.connect(self.on_shot_status_changed)

    @pyqtSlot(bool)
    def on_shot_status_changed(self, my_shot):
        """
        Функция вызывается после выстрела одного из игроков
        """
        if my_shot:
            self.message_area.setText("Ваш ход!")
        else:
            self.message_area.setText("Ход противника")
            self.first_player, self.second_player = self.second_player, self.first_player

        self.is_game_over()

    def is_game_over(self):
        max_hits = 20
        # если 20 клеток помечены, как попадание, то все корабли потоплены
        if self.myBattleField.count_if(BattleField.HIT_CELL) == max_hits or \
                self.enemyBattleField.count_if(BattleField.HIT_CELL) == max_hits:
            self.game_over = True
            print("Game over")
            self.message_area.setText("Игра окончена!")

    def pause(self):
        pass

    def exit_(self):
        self.close()


class SettingsWin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('settings.ui', self)
        self.setFixedSize(525, 399)
        self.exit_btn.clicked.connect(self.exit_)

    def exit_(self):
        self.close()


class RecordsWin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('records.ui', self)

        self.setFixedSize(593, 484)
        self.exit_btn.clicked.connect(self.exit_)

        self.con = sqlite3.connect("records.db")
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM records").fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

    def exit_(self):
        self.close()


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
    player.play()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
