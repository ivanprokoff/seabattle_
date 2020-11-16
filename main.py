import sqlite3
import sys
from random import choice

from pprint import pprint

from BattleField import BattleField
from Player import BotPlayer, ActivePlayer

from PyQt5 import QtWidgets, QtMultimedia, QtCore
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QInputDialog, \
    QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import pyqtSignal, QTimer


class NewGameWin(QtWidgets.QWidget):
    timeout = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Создаем 2 поля боя
        self.myBattleField = BattleField(enemy_field=False)
        self.enemyBattleField = BattleField(enemy_field=True)
        self.con = sqlite3.connect("records.db")
        self.name = None
        self.shot = None, None
        self.winner = None
        self.count = 0
        self.make_record = False
        self.time = 0
        self.timeInterval = 1000
        self.timerUp = QTimer()
        self.timerUp.setInterval(self.timeInterval)
        self.timerUp.timeout.connect(self.updateUptime)
        player.pause()

        # Инициализируем интерфейс
        self.name_quest()
        self.setup_UI()

    def name_quest(self):
        """
        узнаем имя игрока
        :return:
        """
        name, ok_pressed = QInputDialog.getText(self, "Введите имя",
                                                "Как тебя зовут?")
        if not ok_pressed:
            self.name = "Player"
        elif name == '':
            self.name = 'Player'
        else:
            self.name = name

    def setup_UI(self):
        """
        Инициализация интерфейса
        """
        self.title = 'Battle Ship'
        self.left = 600
        self.top = 410
        self.width = 890
        self.height = 480
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.setFixedSize(890, 480)

        self.message_area = QLabel(f"Добро пожаловать в 'Морской бой', {self.name}! "
                                   f"Перед началом просим ознакомиться с правилами")
        self.message_area.setFont(QFont("Times", 14, QFont.Normal))

        self.exit_button = QPushButton('Выход')
        self.exit_button.clicked.connect(self.exit_)

        self.start_button = QPushButton('Старт')
        self.start_button.clicked.connect(self.battle_loop)

        self.pause_btn = QPushButton('Пауза')
        self.pause_btn.clicked.connect(self.pause)

        battle_field_layout = QHBoxLayout()
        battle_field_layout.addWidget(self.myBattleField)
        battle_field_layout.addWidget(self.enemyBattleField)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.pause_btn)
        buttons_layout.addWidget(self.exit_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(battle_field_layout)
        main_layout.addWidget(self.message_area)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)
        self.show()

    def battle_loop(self):
        """
        основной игровой цикл
        """
        self.start_button.setEnabled(False)
        self.timerUp.start()
        self.player = ActivePlayer(self.myBattleField, self.enemyBattleField)
        self.bot = BotPlayer(self.enemyBattleField, self.myBattleField)
        self.game_over = False
        players = [self.bot.name, self.name]
        pprint(self.bot.player_field.field)
        first = choice(players)
        self.message_area.setText(f'Игра началась! Первым ходит {first}.')
        if first == self.bot.name:
            self.winner = self.bot.name
            self.message_area.setText(f'Ход {self.bot.name}.')
            self.bot.shot()
            self.message_area.setText(f'Ваш ход, {self.name}.')
            self.player.enemy_field.table.cellClicked.connect(self.make_shot)
        else:
            self.winner = self.name
            self.player.enemy_field.table.cellClicked.connect(self.make_shot)

    def make_shot(self, row, col):
        """
        функция выстрела игрока
        :param row: строка таблицы - поля
        :param col: колонка таблицы - поля
        """
        if not self.game_over:
            a = row
            b = col
            if self.player.enemy_field.is_valid_shot(a, b):
                if self.player.enemy_field.field[a][b] == 1:
                    self.winner = self.name
                    self.message_area.setText(f'Попадание! {self.name} ходит повторно!')
                    self.player.enemy_field.field[a][b] = 2
                else:
                    """
                    Если игрок промахнулся, то ходит бот
                    """
                    self.player.enemy_field.field[a][b] = 3
                    self.bot.shot()
                    while self.bot.success_shot:
                        self.count += 1
                        self.message_area.setText(f'Попадание! {self.bot.name} ходит повторно!')
                        self.bot.shot()
                        self.bot.enemy_field.update_field_UI()
                        self.winner = self.bot.name
                    self.message_area.setText(f'Попал {self.count} раз (-а)! Ход {self.name}.')
                    self.count = 0
            self.player.enemy_field.update_field_UI()
        self.is_game_over()

    def updateUptime(self):
        """
        счет времени
        """
        self.time += 1

    def is_game_over(self):
        max_hits = 20
        if not self.game_over:
            # если 20 клеток помечены, как попадание, то все корабли потоплены
            if self.myBattleField.count_if(BattleField.HIT_CELL) == max_hits or \
                    self.enemyBattleField.count_if(BattleField.HIT_CELL) == max_hits:
                self.message_area.setText(f"Игра окончена! Победил {self.winner}")
                self.game_over = True
                self.make_record = True
                self.player.enemy_field.update_field_UI(victory=True)
        if self.winner != self.bot.name and self.make_record:
            # Если победил игроК, создаем запись с его времени в бд
            self.timerUp.stop()
            cur = self.con.cursor()
            cur.execute("INSERT INTO records VALUES (?, ?)", (self.name, self.time))
            self.con.commit()

    def pause(self):
        """
        Функция паузы
        """

        def continue_():
            self.timerUp.start()
            self.pause_btn.setText('Пауза')
            self.message_area.setText(f"Продолжаем!!")

        self.timerUp.stop()
        self.pause_btn.setText('Продолжим')
        self.message_area.setText(f"Пауза...")
        self.pause_btn.clicked.connect(continue_)

    def exit_(self):
        """
        Выход
        """
        msgBox = QMessageBox()
        msgBox.setText(f"{self.name}, Вы действительно хотите выйти? Ваш результат не сохранится.")
        msgBox.setWindowTitle("Выход")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            self.close()
        player.play()


class SettingsWin(QtWidgets.QWidget):
    """
    Класс "настройки"
    """

    def __init__(self):
        super().__init__()
        uic.loadUi('settings.ui', self)
        self.setWindowTitle('Settings')
        self.setFixedSize(525, 538)
        self.exit_btn.clicked.connect(self.exit_)
        self.volume_btn.clicked.connect(self.change_volume)

    def change_volume(self):
        global player
        VOLUME = int(self.volume_edit.text())
        player.setVolume(VOLUME)

    def exit_(self):
        self.close()


class RecordsWin(QtWidgets.QWidget):
    """
    Класс "окно рекордов"
    """

    def __init__(self):
        super().__init__()
        uic.loadUi('records.ui', self)
        self.setWindowTitle('Records')

        self.setFixedSize(322, 484)
        self.exit_btn.clicked.connect(self.exit_)

        # Выводим в таблицу все записи из бд ,если они там есть
        try:
            self.con = sqlite3.connect("records.db")
            cur = self.con.cursor()
            result = cur.execute("SELECT * FROM records ORDER BY time").fetchall()
            if result:
                self.tableWidget.setRowCount(len(result))
                self.tableWidget.setColumnCount(len(result[0]))
                self.titles = [description[0] for description in cur.description]
                for i, elem in enumerate(result):
                    for j, val in enumerate(elem):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            else:
                pass
        except Exception:
            msgBox = QMessageBox()
            msgBox.setText('База данных не найдена!')
            msgBox.setWindowTitle("Выход")
            msgBox.setStandardButtons(QMessageBox.Ok)
            returnValue = msgBox.exec()
            if returnValue == QMessageBox.Ok:
                self.close()

    def exit_(self):
        self.close()


class MainWindow(QMainWindow):
    """
    Главное окно игры
    """

    def __init__(self):
        super().__init__()
        self.settingsWindow = None
        self.recordsWindow = None
        self.theme = None
        uic.loadUi('main.ui', self)  # Загружаем дизайн
        self.setWindowTitle('Seabattle')
        self.setFixedSize(392, 394)
        self.start_btn.clicked.connect(self.newGame)
        self.settings_btn.clicked.connect(self.settings)
        self.records_btn.clicked.connect(self.records)
        self.exit_button.clicked.connect(self.exit)
        self.choose_theme()

    def choose_theme(self):
        """
        перед тем, как перейти к главному окну, происходит выбор цветовой темы
        :return:
        """
        self.theme, ok_pressed = QInputDialog.getItem(
            self, "Выберите цветовую тему", "Тема",
            ("Light-blue", "Gradient", "Classic"), 1, False)
        if ok_pressed:
            if self.theme == 'Gradient':
                self.setStyleSheet('background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, '
                                   'stop:0 rgba(0, 104, 178, 255), stop:1 rgba(255, 255, 255, 255));')
            elif self.theme == 'Classic':
                pass
            elif self.theme == 'Light-blue':
                self.setStyleSheet('background-color: rgb(156, 177, 240);')

    def newGame(self):
        """
        Создание новой игры
        """
        self.newgameWindow = NewGameWin()
        self.newgameWindow.show()

    def settings(self):
        """
        Вызов окна настроек
        """
        if not self.settingsWindow:
            self.settingsWindow = SettingsWin()
        self.settingsWindow.show()

    def records(self):
        """
        Вызов окна рекордов
        """
        if not self.recordsWindow:
            self.recordsWindow = RecordsWin()
        self.recordsWindow.show()

    def exit(self):
        msgBox = QMessageBox()
        msgBox.setText(f"Вы действительно хотите выйти?")
        msgBox.setWindowTitle("Выйти из игры")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.ico'))
    filename = 'music.wav'
    fullpath = QtCore.QDir.current().absoluteFilePath(filename)
    url = QtCore.QUrl.fromLocalFile(fullpath)
    content = QtMultimedia.QMediaContent(url)
    player = QtMultimedia.QMediaPlayer()
    player.setMedia(content)
    player.play()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
