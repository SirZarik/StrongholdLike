import random
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QDialog, QLineEdit, QTableWidget, \
    QTableWidgetItem
import sqlite3

from classes import *
from design import Ui_MainWindow

RANDOM_EVENTS = ['' for i in range(21)]
RANDOM_EVENTS[13] = 'fire'
RANDOM_EVENTS[20] = 'ill'
RANDOM_EVENTS[10] = 'ill'

PEOPLE_REACTION = {'money': 'Народ бедствует!Нечем платить зарплаты,срочно увеличьте объем казны',
                   'food': 'Люди голодают,нам необходимо больше пищи!',
                   'population': 'Город пустует!Нам нужно больше домов',
                   'fire': 'Пожар в городе!Казне придется возместить расходы',
                   'ill': 'Город заражен эпидемией.Неизбежно сокращение населения'}


class Game(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowIcon(QIcon("textures/icon_app.png"))

        self.turn_btn = QPushButton(self.centralwidget)
        self.turn_btn.setGeometry(95, 791, 120, 60)
        self.turn_btn.setText('Сделать ход!')
        self.turn_btn.clicked.connect(self.make_turn)

        self.new_game_btn = QPushButton(self.centralwidget)
        self.new_game_btn.setGeometry(1050, 856, 80, 24)
        self.new_game_btn.setText('Новая игра')
        self.new_game_btn.clicked.connect(self.create_new_game)

        for i in range(9):
            for j in range(9):
                btn = QPushButton()
                btn.id = (i, j)
                btn.setFixedSize(90, 90)
                btn.clicked.connect(self.push)
                self.gridLayout.addWidget(btn, i, j)

        self.res_labels = [self.resources, self.resources_2, self.resources_3, self.resources_4, self.resources_5]
        self.create_new_game()

    def create_new_game(self):
        self.turn_btn.setEnabled(True)
        self.playground = [[Polygon(i, j, 'textures/grass.png') for j in range(9)] for i in range(9)]
        self.playground[4][4] = TownHall(4, 4, 'textures/townhall.jpg',
                                         {'money': 50, 'population': 20, 'food': 50, 'wood': 40,
                                          'stone': 45})
        self.game_over = True
        self.safe_years = 20
        self.fire_time = 0

        self.anger = 0  # max == 100
        self.anger_level.setValue(self.anger)

        self.bad_years = {}
        self.list_notif = []

        self.years = ['Год', 1550]
        self.year_lbl.setText(f'{self.years[0]}: {int(self.years[1] // 1)}')

        self.update_playground()
        self.update_res()

    def push(self):
        coord = self.sender()
        x, y = self.gridLayout.indexOf(coord) % 9, self.gridLayout.indexOf(coord) // 9
        self.info_display.setText(str(self.playground[x][y]))

        if type(self.playground[x][y]) == Polygon and self.game_over:
            dialog = BuildDialog(self, x, y)
            dialog.exec()

    def update_res(self):
        for i in self.playground[4][4].contains.keys():
            if self.playground[4][4].contains[i] < 0:
                self.playground[4][4].contains[i] = 0
        for i, lbl in zip(self.playground[4][4].contains.keys(), self.res_labels):
            lbl.setText(f'{RESOURCES[i]}: {self.playground[4][4].contains[i]}')
            if self.playground[4][4].contains[i] >= 20:
                lbl.setStyleSheet("color: rgb(0, 0, 0)")
            elif self.playground[4][4].contains[i] < 20:
                lbl.setStyleSheet("color: rgb(255, 0, 0)")

    def update_playground(self):
        for i in range(9):
            for j in range(9):
                cell = self.gridLayout.itemAtPosition(i, j).widget()
                cell.setIcon(QIcon(self.playground[j][i].image))
                cell.setIconSize(QSize(90, 90))

    def make_turn(self):
        if self.game_over:
            for i in self.playground:
                for j in i:
                    if type(j) == ProductBuilding:
                        j.make_step()
                        self.anger -= j.anger_effect
            self.years[1] += 0.1
            self.year_lbl.setText(f'{self.years[0]}: {int(self.years[1] // 1)}')
            self.check_life_level()
            self.chance()
            self.update_res()
            if self.fire_time == 0:
                self.update_playground()
            else:
                self.fire_time -= 1

    def chance(self):
        if self.safe_years == 0:
            r = random.choice(RANDOM_EVENTS)
            if r == 'fire':
                self.playground[4][4].contains['money'] -= int(0.75 * self.playground[4][4].contains['money'])
                self.playground[4][4].contains['population'] -= int(0.5 * self.playground[4][4].contains['population'])
                self.playground[4][4].contains['wood'] -= int(0.75 * self.playground[4][4].contains['wood'])
                self.anger += 10
            elif r == 'ill':
                self.playground[4][4].contains['population'] -= int(0.8 * self.playground[4][4].contains['population'])
                self.playground[4][4].contains['money'] -= int(0.5 * self.playground[4][4].contains['money'])
                self.anger += 10
            if r != '':
                self.safe_years = 10
                notif = Notification(self, r)
                notif.exec()
        if self.safe_years > 0:
            self.safe_years -= 1

    def check_life_level(self):
        self.anger_level.setValue(self.anger)
        if self.anger > 100:
            self.anger_level.setValue(100)
        elif self.anger < 0:
            self.anger_level.setValue(0)
        for i in self.playground[4][4].contains:
            if self.playground[4][4].contains[i] <= 0 and (i == 'money' or i == 'food' or i == 'population'):
                self.anger += 10
                self.anger_level.setValue(self.anger)
                self.bad_years[i] = self.bad_years.get(i, 0) + 1
        for i in self.bad_years:
            if self.bad_years[i] > 5:
                if i not in self.list_notif:
                    self.list_notif.append(i)
                    notif = Notification(self, i)
                    notif.exec()
        if self.anger >= 100:
            notif = End(self)
            notif.exec()


class Notification(QDialog):
    def __init__(self, main, kind_of, *args):
        QDialog.__init__(self, *args)
        self.setWindowIcon(QIcon("textures/icon_app.png"))
        self.main = main
        self.kind_of = kind_of
        self.setFixedSize(500, 150)
        self.setWindowTitle('Народ недоволен!')
        self.alert = QLabel(self)
        self.alert.move(100, 60)
        if kind_of == 'fire':
            self.main.fire_time = 2
            for i in range(9):
                for j in range(9):
                    cell = self.main.gridLayout.itemAtPosition(j, i).widget()
                    if self.main.playground[i][j].name == 'Дом':
                        cell.setIcon(QIcon('textures/burning_house'))
                        cell.setIconSize(QSize(90, 90))
                    elif self.main.playground[i][j].name == 'Рынок':
                        cell.setIcon(QIcon('textures/burning_stall'))
                        cell.setIconSize(QSize(90, 90))
        self.alert.setText(PEOPLE_REACTION[self.kind_of])


class End(QDialog):
    def __init__(self, main, *args):
        QDialog.__init__(self, *args)
        self.setWindowIcon(QIcon("textures/icon_app.png"))
        self.main = main
        self.main.game_over = False
        self.setFixedSize(700, 500)
        self.setWindowTitle('Вам осталось править пеплом!')

        self.name_of_player = QLineEdit(self)
        self.name_of_player.setGeometry(200, 77, 90, 20)

        self.score = 0
        for i in self.main.playground:
            for j in i:
                if type(j) == ProductBuilding:
                    self.score += 1

        self.restart = QPushButton(self)
        self.restart.setText('Сохранить результат')
        self.restart.setGeometry(QRect(60, 130, 220, 60))
        self.restart.clicked.connect(self.add_result)

        self.table = QTableWidget(self)
        self.table.setGeometry(QRect(350, 30, 320, 400))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Имя", "Годы правления", 'Число зданий'])

        self.alert = QLabel(self)
        self.alert.move(60, 30)
        self.alert.setText(
            f'<p>Город разрушен!Народ поднял против вас восстание!</p><p>Ваше правление длилось до'
            f' {int(self.main.years[1] // 1)} года</p><p>История запомнит вас как:</p>')
        for i in range(9):
            for j in range(9):
                cell = self.main.gridLayout.itemAtPosition(j, i).widget()
                if type(self.main.playground[i][j]) == ProductBuilding:
                    self.main.playground[i][j].image = 'textures/broken_building'
                    cell.setIcon(QIcon('textures/broken_building'))
                    cell.setIconSize(QSize(90, 90))
                elif type(self.main.playground[i][j]) == Polygon:
                    self.main.playground[i][j].image = 'textures/grass_dark'
                    cell.setIcon(QIcon('textures/grass_dark'))
                    cell.setIconSize(QSize(90, 90))
                elif type(self.main.playground[i][j]) == TownHall:
                    self.main.playground[i][j].image = 'textures/broken_hall'
                    cell.setIcon(QIcon('textures/broken_hall'))
                    cell.setIconSize(QSize(90, 90))
        self.main.turn_btn.setEnabled(False)

    def add_result(self):
        self.name_of_player.setEnabled(False)
        self.restart.setEnabled(False)
        self.con = sqlite3.connect("records.db")
        self.con.execute(
            f"INSERT INTO stats(player, years, builds) VALUES('{self.name_of_player.text()}',"
            f" {int(self.main.years[1])},{self.score})")
        self.con.commit()
        self.con.close()
        self.update_result()

    def update_result(self):
        con = sqlite3.connect("records.db")
        cur = con.cursor()
        res = cur.execute("SELECT player, years, builds FROM stats ORDER BY -builds").fetchall()
        self.table.setRowCount(len(res))
        for j, result in enumerate(res):
            for i, val in enumerate(result):
                self.table.setItem(j, i, QTableWidgetItem(str(val)))


class BuildDialog(QDialog):
    def __init__(self, main, x, y, *args):
        QDialog.__init__(self, *args)
        self.setWindowIcon(QIcon("textures/icon_app.png"))
        self.main = main
        self.x = x
        self.y = y
        self.init_UI()

    def init_UI(self):
        self.setFixedSize(700, 100)
        self.setWindowTitle('Выберите здание для строительства')
        for i, name in enumerate(BUILD_INFO.keys()):
            pb = QPushButton(self)
            pb.setGeometry(QRect(0 + i * 100, 0, 100, 100))
            pb.setText(
                '\n'.join([name] + [f'{RESOURCES[i]}:{BUILD_INFO[name][0][i]}' for i in BUILD_INFO[name][0].keys()]))
            pb.clicked.connect(self.check_n_build)

    def check_n_build(self):
        build = self.sender().text().split('\n')[0]
        f = True
        for i in BUILD_INFO[build][0]:
            if self.main.playground[4][4].contains[i] - BUILD_INFO[build][0][i] < 0:
                error = Error()
                error.exec()
                f = False
                self.close()
                break
        if f:
            for i in BUILD_INFO[build][0].keys():
                self.main.playground[4][4].contains[i] -= BUILD_INFO[build][0][i]
            self.main.playground[self.x][self.y] = ProductBuilding(self.x, self.y, BUILD_INFO[build][1], build,
                                                                   self.main.playground[4][4],
                                                                   BUILD_INFO[build][3], BUILD_INFO[build][4])
            self.main.make_turn()
            self.close()


class Error(QDialog):
    def __init__(self, *args):
        QDialog.__init__(self, *args)
        self.setWindowIcon(QIcon("textures/icon_app.png"))
        self.init_UI()

    def init_UI(self):
        self.setFixedSize(300, 100)
        self.setWindowTitle('Слишком дорого для казны!')
        err_lbl = QLabel(self)
        err_lbl.setGeometry(QRect(10, 20, 300, 50))
        err_lbl.setText('Не хватает ресурсов для постройки данного здания!')


app = QApplication(sys.argv)
ex = Game()
ex.show()
sys.exit(app.exec_())
