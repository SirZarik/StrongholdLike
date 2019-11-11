'''
money - 0, population - 1, food - 2, wood - 3, stone - 4

Формат записи BUILD_INFO -
 Имя кнопки строения: стоимость строительства(dict), текстура, имя строения, продукция(dict), расходы(dict)
'''

BUILD_INFO = {
    'Дом': [{'money': 5, 'wood': 10, 'stone': 5}, 'textures/house.png', 'Дом', {'population': 2, 'money': 3},
            {'food': -2}],
    'Жилой блок': [{'money': 50, 'wood': 10, 'stone': 20}, 'textures/house_block.png', 'Жилой блок',
                   {'population': 15, 'money': 12},
                   {'food': -10}],
    'Шахта': [{'money': 60, 'wood': 20, 'population': 50}, 'textures/cave.png', 'Шахта', {'stone': 7},
              {'money': -7}],
    'Рынок': [{'money': 10, 'wood': 5, 'population': 30}, 'textures/stall.png', 'Рынок', {'money': 20},
              {'food': -5, 'wood': -2, 'stone': -1}],
    'Ферма': [{'money': 15, 'wood': 10, 'population': 10}, 'textures/farm.png', 'Ферма', {'food': 11},
              {'money': -5, 'population': -1}],
    'Лесопилка': [{'money': 20, 'population': 35}, 'textures/woodcut.png', 'Лесопилка', {'wood': 15},
                  {'money': -5}],
    'Церковь': [{'money': 20, 'population': 35, 'stone': 50, 'wood': 40}, 'textures/church.png', 'Церковь', {},
                {'money': -10}]}

RESOURCES = {'money': 'Деньги', 'population': 'Население', 'food': 'Еда', 'wood': 'Дерево', 'stone': 'Камень'}


class Polygon:
    def __init__(self, x, y, image, name='Поле'):
        self.x = x
        self.y = y
        self.image = image
        self.name = name

    def __str__(self):
        return f'<p><b>{self.name}</b></p><p>Положение:{self.x},{self.y}</p>'


class Building(Polygon):
    def __init__(self, x, y, image, townhall, name='Здание'):
        super().__init__(x, y, image, name)
        self.townhall = townhall


class TownHall(Polygon):
    def __init__(self, x, y, image, contains, name='Ратуша'):
        super().__init__(x, y, image, name)
        self.contains = contains

    def __str__(self):
        for i in self.contains:
            if self.contains[i] < 0:
                self.contains[i] = 0
        str_contains = '\n'.join([f'<p>{RESOURCES[i]}: {self.contains[i]}</p>' for i in self.contains.keys()])
        return f'<p><b>{self.name}</b></p><p>Положение:{self.x},' \
            f'{self.y}</p><p><b>Всего в городе:</b>\n{str_contains}</p>'


class ProductBuilding(Building):
    def __init__(self, x, y, image, name, townhall, production, consums):
        super().__init__(x, y, image, townhall, name)
        if name == 'Церковь':
            self.anger_effect = 2
        else:
            self.anger_effect = 0
        self.production = production
        self.consums = consums

    def __str__(self):
        if self.consums:
            str_consums = '\n'.join([f'<p>{RESOURCES[i]}: {self.consums[i]}</p>' for i in self.consums.keys()])
        else:
            str_consums = '<p>Ничего не потребляет</p>'
        if self.production:
            str_production = '\n'.join([f'<p>{RESOURCES[i]}: {self.production[i]}</p>' for i in self.production.keys()])
        else:
            str_production = '<p>Ничего не производит</p>'
        return f'<p><b>{self.name}</b></p><p>Положение:{self.x},' \
            f'{self.y}</p><p><b>Необходимо ресурсов в год:</b>{str_consums}</p><p><b>Производит ресурсов:</b>{str_production}</p>'

    def make_step(self):
        f = True
        if self.consums:
            for i in self.consums.keys():
                if self.townhall.contains[i] + self.consums[i] < 0:
                    f = False
                self.townhall.contains[i] += self.consums[i]
        if f and self.production:
            for i in self.production.keys():
                self.townhall.contains[i] += self.production[i]
