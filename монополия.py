import sys
import json
import random
import math # Добавлен для отрисовки
import os # Добавлен для путей сохранения
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFormLayout, QComboBox,
    QRadioButton, QButtonGroup, QMessageBox, QTableWidget, QSlider,
    QGroupBox, QLineEdit, QHeaderView, QTableWidgetItem, QGraphicsOpacityEffect,
    QDialog, QDialogButtonBox, QSpinBox, QListWidget, QListWidgetItem, QTextEdit,
    QFileDialog, QSizePolicy # Добавлены QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QRectF, QPointF, QSize, QTimer # Добавлены QRectF, QPointF, QSize
from PyQt6.QtGui import (
    QFont, QIcon, QPalette, QColor, QPixmap, QPainter, QPen, QBrush, QTransform, # Добавлены QPainter, QPen, QBrush, QTransform
    QFontMetrics
)

# --- Стилизация (без изменений, предполагается наличие APPLE_STYLE) ---
SYSTEM_FONT = "System"
APPLE_STYLE = f"""
QWidget {{
    font-family: {SYSTEM_FONT}; font-size: 14px; background-color: #F2F2F7; color: #1D1D1F;
}}
QMainWindow {{ background-color: #F2F2F7; }}
QGroupBox {{
    border: 1px solid #E5E5EA; border-radius: 8px; margin-top: 15px;
    padding: 20px 15px 15px 15px; font-weight: 600; background-color: #FFFFFF;
}}
QGroupBox::title {{
    subcontrol-origin: margin; subcontrol-position: top left; padding: 0 8px 5px 8px;
    left: 10px; color: #6C6C70; font-size: 13px; font-weight: 500;
}}
QLabel {{ background-color: transparent; padding: 2px; }}
QLabel#TitleLabel {{ font-size: 28px; font-weight: 600; margin-bottom: 15px; padding: 0; }}
QLabel#InfoLabel {{ font-size: 15px; color: #3C3C43; margin-bottom: 8px; padding: 0; }}
QLabel#GameStatusLabel {{
    font-size: 14px; color: #3C3C43; padding: 12px; background-color: #FFFFFF;
    border-radius: 8px; border: 1px solid #E5E5EA; margin-bottom: 15px; text-align: center;
}}
QPushButton {{
    background-color: #007AFF; color: white; border: none; border-radius: 8px;
    padding: 10px 20px; font-size: 14px; font-weight: 500; min-width: 80px; min-height: 30px;
}}
QPushButton:hover {{ background-color: #005ECB; }}
QPushButton:pressed {{ background-color: #004CA8; }}
QPushButton:disabled {{ background-color: #D1D1D6; color: #8E8E93; }}
QLineEdit, QComboBox, QTextEdit, QSpinBox {{
    padding: 9px 12px; border: 1px solid #C6C6C8; border-radius: 6px;
    background-color: #FFFFFF; min-height: 30px; font-size: 14px;
}}
QTextEdit {{ background-color: #F9F9F9; }}
QTableWidget {{
    border: 1px solid #E5E5EA; border-radius: 8px; background-color: #FFFFFF;
    gridline-color: #E5E5EA; font-size: 13px;
}}
QHeaderView::section {{
    background-color: #F9F9F9; color: #3C3C43; padding: 8px; border: none;
    border-bottom: 1px solid #E5E5EA; font-weight: 500; text-align: left;
}}
QTableWidget::item {{ padding: 8px; border-bottom: 1px solid #F2F2F7; }}
QListWidget {{
    border: 1px solid #E5E5EA; border-radius: 8px; background-color: #FFFFFF; padding: 5px;
}}
QListWidget::item {{ padding: 8px 10px; border-radius: 5px; }}
QListWidget::item:hover {{ background-color: #F2F2F7; }}
QListWidget::item:selected {{ background-color: #007AFF; color: white; }}
QDialog {{ background-color: #F2F2F7; }}
QMessageBox {{ font-family: {SYSTEM_FONT}; }}
QMessageBox QLabel {{ font-size: 14px; color: #1D1D1F; }}
QMessageBox QPushButton {{ min-width: 70px; padding: 8px 15px; }}
"""

# --- Константы (без изменений) ---
STARTING_MONEY = 1500
PASS_GO_MONEY = 200
JAIL_POSITION = 10
GO_TO_JAIL_POSITION = 30
INCOME_TAX_AMOUNT = 200
LUXURY_TAX_AMOUNT = 100
JAIL_FINE = 50
MAX_HOUSES = 4
HOTEL_LEVEL = 5
MORTGAGE_INTEREST_RATE = 0.10
MAX_DOUBLES_BEFORE_JAIL = 3
BOARD_SIZE = 40
SAVE_DIR = "monopoly_saves" # Папка для сохранений

# --- Данные игрового поля (без изменений) ---
BOARD_DATA = [
    {"name": "Вперед", "type": "go"},
    {"name": "Старая улица", "type": "street", "price": 60, "rent": [2, 10, 30, 90, 160, 250], "house_cost": 50, "color": "brown"},
    {"name": "Общественная казна", "type": "community_chest"},
    {"name": "Новая улица", "type": "street", "price": 60, "rent": [4, 20, 60, 180, 320, 450], "house_cost": 50, "color": "brown"},
    {"name": "Подоходный налог", "type": "income_tax"},
    {"name": "Вокзал Рижский", "type": "railroad", "price": 200},
    {"name": "Улица Вавилова", "type": "street", "price": 100, "rent": [6, 30, 90, 270, 400, 550], "house_cost": 50, "color": "lightblue"},
    {"name": "Шанс", "type": "chance"},
    {"name": "Улица Варшавская", "type": "street", "price": 100, "rent": [6, 30, 90, 270, 400, 550], "house_cost": 50, "color": "lightblue"},
    {"name": "Улица Рязанская", "type": "street", "price": 120, "rent": [8, 40, 100, 300, 450, 600], "house_cost": 50, "color": "lightblue"},
    {"name": "Тюрьма / Просто посетили", "type": "jail"},
    {"name": "Улица Полянка", "type": "street", "price": 140, "rent": [10, 50, 150, 450, 625, 750], "house_cost": 100, "color": "pink"},
    {"name": "Электростанция", "type": "utility", "price": 150},
    {"name": "Улица Сретенка", "type": "street", "price": 140, "rent": [10, 50, 150, 450, 625, 750], "house_cost": 100, "color": "pink"},
    {"name": "Улица Ростовская", "type": "street", "price": 160, "rent": [12, 60, 180, 500, 700, 900], "house_cost": 100, "color": "pink"},
    {"name": "Вокзал Курский", "type": "railroad", "price": 200},
    {"name": "Проспект Мира", "type": "street", "price": 180, "rent": [14, 70, 200, 550, 750, 950], "house_cost": 100, "color": "orange"},
    {"name": "Общественная казна", "type": "community_chest"},
    {"name": "Проспект Маяковского", "type": "street", "price": 180, "rent": [14, 70, 200, 550, 750, 950], "house_cost": 100, "color": "orange"},
    {"name": "Улица Смоленская", "type": "street", "price": 200, "rent": [16, 80, 220, 600, 800, 1000], "house_cost": 100, "color": "orange"},
    {"name": "Бесплатная стоянка", "type": "free_parking"},
    {"name": "Улица Пушкинская", "type": "street", "price": 220, "rent": [18, 90, 250, 700, 875, 1050], "house_cost": 150, "color": "red"},
    {"name": "Шанс", "type": "chance"},
    {"name": "Улица Тверская", "type": "street", "price": 220, "rent": [18, 90, 250, 700, 875, 1050], "house_cost": 150, "color": "red"},
    {"name": "Улица Малая Бронная", "type": "street", "price": 240, "rent": [20, 100, 300, 750, 925, 1100], "house_cost": 150, "color": "red"},
    {"name": "Вокзал Казанский", "type": "railroad", "price": 200},
    {"name": "Улица Грузинский Вал", "type": "street", "price": 260, "rent": [22, 110, 330, 800, 975, 1150], "house_cost": 150, "color": "yellow"},
    {"name": "Улица Чайковского", "type": "street", "price": 260, "rent": [22, 110, 330, 800, 975, 1150], "house_cost": 150, "color": "yellow"},
    {"name": "Водопровод", "type": "utility", "price": 150},
    {"name": "Улица Кутузовский проспект", "type": "street", "price": 280, "rent": [24, 120, 360, 850, 1025, 1200], "house_cost": 150, "color": "yellow"},
    {"name": "Отправляйтесь в тюрьму", "type": "go_to_jail"},
    {"name": "Арбат", "type": "street", "price": 300, "rent": [26, 130, 390, 900, 1100, 1275], "house_cost": 200, "color": "green"},
    {"name": "Улица Гоголевский бульвар", "type": "street", "price": 300, "rent": [26, 130, 390, 900, 1100, 1275], "house_cost": 200, "color": "green"},
    {"name": "Общественная казна", "type": "community_chest"},
    {"name": "Улица Малая Дмитровка", "type": "street", "price": 320, "rent": [28, 150, 450, 1000, 1200, 1400], "house_cost": 200, "color": "green"},
    {"name": "Вокзал Ленинградский", "type": "railroad", "price": 200},
    {"name": "Шанс", "type": "chance"},
    {"name": "Улица Первая Парковая", "type": "street", "price": 350, "rent": [35, 175, 500, 1100, 1300, 1500], "house_cost": 200, "color": "darkblue"},
    {"name": "Налог на роскошь", "type": "luxury_tax"},
    {"name": "Улица Малая Лубянка", "type": "street", "price": 400, "rent": [50, 200, 600, 1400, 1700, 2000], "house_cost": 200, "color": "darkblue"},
]

# --- Карточки Шанс/Казна (без изменений) ---
COMMUNITY_CHEST_CARDS = [
    {"text": "Банковская ошибка в вашу пользу. Получите $200", "action": "get_money", "amount": 200},
    {"text": "Оплата услуг врача. Заплатите $50", "action": "pay_money", "amount": 50},
    {"text": "Возврат подоходного налога. Получите $20", "action": "get_money", "amount": 20},
    {"text": "Отправляйтесь в тюрьму.", "action": "go_to_jail"},
    {"text": "Получите $100 от продажи акций.", "action": "get_money", "amount": 100},
    {"text": "Бесплатная карта выхода из тюрьмы.", "action": "get_out_of_jail_free", "deck": "community_chest"},
    {"text": "Перейдите на поле Вперед.", "action": "go_to", "position": 0},
    {"text": "Оплата страховки. Заплатите $50", "action": "pay_money", "amount": 50},
    {"text": "Получите наследство $100", "action": "get_money", "amount": 100},
    # Добавим карты из предыдущей версии, если они были
    {"text": "Оплата школьных налогов. Заплатите $150", "action": "pay_money", "amount": 150},
    {"text": "Получите $25 за консультационные услуги", "action": "get_money", "amount": 25},
    {"text": "Ремонт вашей собственности: $40 за дом, $115 за отель.", "action": "pay_repairs", "house_rate": 40, "hotel_rate": 115},
    {"text": "Вы выиграли в конкурсе красоты. Получите $10", "action": "get_money", "amount": 10},
    {"text": "Сбор со всех игроков. Получите $50 от каждого.", "action": "collect_from_players", "amount": 50},
]

CHANCE_CARDS = [
    {"text": "Перейдите на поле Вперед.", "action": "go_to", "position": 0},
    {"text": "Перейдите на Арбат.", "action": "go_to", "position": 31},
    {"text": "Перейдите на ближайшую коммунальную службу.", "action": "go_to_nearest", "type": "utility"},
    {"text": "Перейдите на ближайший вокзал.", "action": "go_to_nearest", "type": "railroad"},
    {"text": "Банк платит вам дивиденды $50.", "action": "get_money", "amount": 50},
    {"text": "Бесплатная карта выхода из тюрьмы.", "action": "get_out_of_jail_free", "deck": "chance"},
    {"text": "Вернитесь на 3 клетки назад.", "action": "move_relative", "amount": -3},
    {"text": "Отправляйтесь в тюрьму.", "action": "go_to_jail"},
    {"text": "Штраф за превышение скорости. Заплатите $15.", "action": "pay_money", "amount": 15},
    {"text": "Перейдите на Старую улицу.", "action": "go_to", "position": 1},
    # Добавим карты из предыдущей версии, если они были
    {"text": "Вас избрали председателем правления. Заплатите каждому игроку $50.", "action": "pay_players", "amount": 50},
    {"text": "Ваше здание и кредит погашены. Получите $150.", "action": "get_money", "amount": 150},
    {"text": "Перейдите на бесплатную стоянку.", "action": "go_to", "position": 20},
]


# --- Классы Property, Street, Railroad, Utility, Card, Player, GameBoard (без изменений, предполагаются здесь) ---
# --- Добавлены/Изменены классы и методы для отрисовки и UI ---

class Property:
    """ Базовый класс для клетки на поле """
    def __init__(self, data, index):
        self.index = index
        self.name = data['name']
        self.type = data['type']
        self.price = data.get('price', 0)
        self.owner = None
        self.is_mortgaged = False
        self.mortgage_value = self.price // 2 if self.price else 0
        # Добавим атрибут color для всех, чтобы упростить отрисовку
        self.color_key = data.get('color', None) # Ключ цвета ('brown', 'lightblue', etc.)

    def get_rent(self, dice_roll=0, board=None):
        return 0 # Базовая рента 0

    def to_dict(self):
        return {
            'index': self.index, 'owner_index': self.owner.index if self.owner else None,
            'is_mortgaged': self.is_mortgaged, '_class': self.__class__.__name__
        }

    @classmethod
    def from_dict(cls, data, players):
        prop_data = BOARD_DATA[data['index']]
        class_name = data.get('_class', 'Property')
        target_class = globals().get(class_name, Property)
        prop = target_class(prop_data, data['index'])
        if data['owner_index'] is not None and players:
            prop.owner = next((p for p in players if p.index == data['owner_index']), None)
        prop.is_mortgaged = data['is_mortgaged']
        return prop

class Street(Property):
    """ Класс для улицы """
    def __init__(self, data, index):
        super().__init__(data, index)
        self.rent_levels = data['rent']
        self.house_cost = data['house_cost']
        # self.color_key уже есть в базовом классе
        self.num_houses = 0 # 0..4 дома, 5 отель

    def get_rent(self, dice_roll=0, board=None):
        if self.is_mortgaged or self.owner is None: return 0
        # Двойная рента на монополии без домов
        if self.num_houses == 0 and board and board.player_has_monopoly(self.owner, self.color_key):
            return self.rent_levels[0] * 2
        # Проверка выхода за границы массива rent_levels
        rent_index = min(self.num_houses, len(self.rent_levels) - 1)
        return self.rent_levels[rent_index]

    def to_dict(self):
        data = super().to_dict()
        data['num_houses'] = self.num_houses
        return data

    @classmethod
    def from_dict(cls, data, players):
        street = super(Street, cls).from_dict(data, players)
        street.num_houses = data.get('num_houses', 0)
        return street

class Railroad(Property):
    """ Класс для вокзала """
    def __init__(self, data, index):
        super().__init__(data, index)
        self.base_rent = 25

    def get_rent(self, dice_roll=0, board=None):
        if self.is_mortgaged or self.owner is None or board is None: return 0
        num_owned = board.count_player_properties(self.owner, 'railroad')
        return self.base_rent * (2 ** (num_owned - 1)) # 25, 50, 100, 200

class Utility(Property):
    """ Класс для коммунальной службы """
    def get_rent(self, dice_roll, board=None):
        if self.is_mortgaged or self.owner is None or board is None: return 0
        num_owned = board.count_player_properties(self.owner, 'utility')
        if num_owned == 1: return 4 * dice_roll
        if num_owned == 2: return 10 * dice_roll
        return 0

class Card:
    """ Класс для карт Шанс и Казна """
    def __init__(self, data):
        self.text = data['text']
        self.action = data['action']
        self.amount = data.get('amount')
        self.position = data.get('position')
        self.type = data.get('type')
        self.deck = data.get('deck') # Для карт "Выйти из тюрьмы"
        # Добавим поля для ремонта из COMMUNITY_CHEST_CARDS
        self.house_rate = data.get('house_rate')
        self.hotel_rate = data.get('hotel_rate')

    def to_dict(self):
        # Включаем все возможные атрибуты
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        return cls(data)

class Player:
    """ Класс игрока """
    def __init__(self, index, name):
        self.index = index
        self.name = name
        self.money = STARTING_MONEY
        self.position = 0
        self.properties = [] # Список объектов Property
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail_cards = [] # Список объектов Card
        self.is_bankrupt = False
        self.color = QColor(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)) # Цвет фишки

    def change_money(self, amount):
        self.money += amount

    def move(self, steps, board_size):
        old_position = self.position
        self.position = (self.position + steps) % board_size
        passed_go = False
        if not self.in_jail and steps > 0 and self.position < old_position:
            passed_go = True
        return passed_go

    def move_to(self, position, collect_go=True, board_size=BOARD_SIZE):
        passed_go = False
        if not self.in_jail and position < self.position:
            passed_go = True
        old_position = self.position
        self.position = position % board_size
        return passed_go and collect_go

    def add_property(self, prop):
        if prop not in self.properties:
            self.properties.append(prop)
            prop.owner = self
            self.properties.sort(key=lambda x: x.index)

    def remove_property(self, prop):
        if prop in self.properties:
            self.properties.remove(prop)
            prop.owner = None

    def total_assets(self, board):
        """ Полная стоимость активов (деньги + залог + полцены домов) """
        assets = self.money
        for prop in self.properties:
            assets += prop.mortgage_value # Упрощенно считаем по залоговой стоимости
            if isinstance(prop, Street):
                assets += prop.num_houses * (prop.house_cost // 2)
        return assets

    def liquid_assets(self, board):
        """ Активы для срочного погашения (деньги + продажа домов) """
        assets = self.money
        for prop in self.properties:
             if isinstance(prop, Street) and prop.num_houses > 0 and not prop.is_mortgaged:
                 assets += prop.num_houses * (prop.house_cost // 2)
        return assets

    def can_afford(self, amount):
        return self.money >= amount

    def needs_to_raise_money(self, amount_needed, board):
         return self.money < amount_needed and self.total_assets(board) >= amount_needed

    def add_jail_card(self, card):
        self.get_out_of_jail_cards.append(card)

    def use_jail_card(self):
        if self.get_out_of_jail_cards:
            return self.get_out_of_jail_cards.pop(0)
        return None

    def to_dict(self):
        return {
            'index': self.index, 'name': self.name, 'money': self.money, 'position': self.position,
            'property_indices': [prop.index for prop in self.properties],
            'in_jail': self.in_jail, 'jail_turns': self.jail_turns,
            'get_out_of_jail_cards': [card.to_dict() for card in self.get_out_of_jail_cards],
            'is_bankrupt': self.is_bankrupt, 'color': self.color.name(),
        }

    @classmethod
    def from_dict(cls, data):
        player = cls(data['index'], data['name'])
        player.money = data['money']
        player.position = data['position']
        player.in_jail = data['in_jail']
        player.jail_turns = data['jail_turns']
        player.get_out_of_jail_cards = [Card.from_dict(c) for c in data['get_out_of_jail_cards']]
        player.is_bankrupt = data['is_bankrupt']
        player.color = QColor(data.get('color', '#000000'))
        player.property_indices = data.get('property_indices', []) # Для связывания позже
        return player

class GameBoard:
    """ Класс игрового поля """
    def __init__(self):
        self.tiles = self._create_board()
        self.community_chest_deck = self._create_deck(COMMUNITY_CHEST_CARDS)
        self.chance_deck = self._create_deck(CHANCE_CARDS)
        self._discard_community_chest = []
        self._discard_chance = []
        self.colors = self._get_colors()
        # Добавим словарь цветов для отрисовки
        self.color_map = {
            "brown": QColor("#955436"), "lightblue": QColor("#AAE0FA"),
            "pink": QColor("#D93A96"), "orange": QColor("#F7941D"),
            "red": QColor("#ED1B24"), "yellow": QColor("#FEF200"),
            "green": QColor("#1FB25A"), "darkblue": QColor("#0072BB"),
            None: QColor("#FFFFFF") # Цвет по умолчанию
        }

    def _create_board(self):
        tiles = []
        for i, data in enumerate(BOARD_DATA):
            tile_type = data['type']
            if tile_type == 'street': tiles.append(Street(data, i))
            elif tile_type == 'railroad': tiles.append(Railroad(data, i))
            elif tile_type == 'utility': tiles.append(Utility(data, i))
            else: tiles.append(Property(data, i))
        return tiles

    def _get_colors(self):
        colors = {}
        for tile in self.tiles:
            if isinstance(tile, Street):
                colors.setdefault(tile.color_key, []).append(tile)
        return colors

    def _create_deck(self, card_data_list):
        deck = [Card(data) for data in card_data_list]
        random.shuffle(deck)
        return deck

    def draw_card(self, deck_type):
        deck = self.community_chest_deck if deck_type == 'community_chest' else self.chance_deck
        discard_pile = self._discard_community_chest if deck_type == 'community_chest' else self._discard_chance

        if not deck:
            deck.extend(discard_pile)
            random.shuffle(deck)
            discard_pile.clear()
            if not deck: return None # Совсем пусто

        card = deck.pop(0)
        # Карты "Выйти из тюрьмы" не кладутся в сброс сразу
        if card.action != "get_out_of_jail_free":
            discard_pile.append(card)
        return card

    def return_jail_card(self, card):
        """ Возвращает карту выхода из тюрьмы в сброс """
        if card and card.action == "get_out_of_jail_free":
            discard_pile = self._discard_community_chest if card.deck == 'community_chest' else self._discard_chance
            discard_pile.append(card)

    def get_tile(self, position):
        return self.tiles[position % BOARD_SIZE]

    def count_player_properties(self, player, prop_type):
        return sum(1 for prop in player.properties if prop.type == prop_type)

    def get_properties_by_color(self, color_key):
        return self.colors.get(color_key, [])

    def player_has_monopoly(self, player, color_key):
        color_group = self.get_properties_by_color(color_key)
        if not color_group: return False
        # Учитываем, что на заложенной монополии нельзя строить, но она все еще монополия
        return all(prop.owner == player for prop in color_group)

    def can_build_house(self, player, street):
        if not isinstance(street, Street) or street.owner != player or street.is_mortgaged: return False
        if not self.player_has_monopoly(player, street.color_key): return False
        if street.num_houses >= HOTEL_LEVEL: return False

        # Равномерная застройка
        color_group = self.get_properties_by_color(street.color_key)
        if any(prop.is_mortgaged for prop in color_group): return False # Нельзя строить на заложенной группе
        min_houses = min(prop.num_houses for prop in color_group)
        return street.num_houses == min_houses

    def can_sell_house(self, player, street):
        if not isinstance(street, Street) or street.owner != player or street.num_houses <= 0: return False
        # Равномерная продажа
        color_group = self.get_properties_by_color(street.color_key)
        max_houses = max(prop.num_houses for prop in color_group)
        return street.num_houses == max_houses

    def get_nearest_property_index(self, current_position, prop_type):
        for i in range(1, BOARD_SIZE):
            check_pos = (current_position + i) % BOARD_SIZE
            if self.tiles[check_pos].type == prop_type:
                return check_pos
        return current_position # Не найдено

    def to_dict(self):
        # Сохраняем только изменяемые части: карты и состояние тайлов
        return {
            'tiles': [tile.to_dict() for tile in self.tiles],
            'community_chest_deck': [card.to_dict() for card in self.community_chest_deck],
            'chance_deck': [card.to_dict() for card in self.chance_deck],
            '_discard_community_chest': [card.to_dict() for card in self._discard_community_chest],
            '_discard_chance': [card.to_dict() for card in self._discard_chance],
        }

    @classmethod
    def from_dict(cls, data, players):
        board = cls()
        # Восстанавливаем состояние тайлов
        board.tiles = [Property.from_dict(t_data, players) for t_data in data['tiles']]
        # Восстанавливаем состояние карт
        board.community_chest_deck = [Card.from_dict(c) for c in data['community_chest_deck']]
        board.chance_deck = [Card.from_dict(c) for c in data['chance_deck']]
        board._discard_community_chest = [Card.from_dict(c) for c in data['_discard_community_chest']]
        board._discard_chance = [Card.from_dict(c) for c in data['_discard_chance']]
        board.colors = board._get_colors() # Обновляем группы цветов
        return board

class PauseSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Сохраняем ссылку на родительский виджет

        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel("Пауза/Настройки")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Кнопки
        self.btn_resume = QPushButton("Возобновить игру")
        self.btn_main_menu = QPushButton("В главное меню")
        self.btn_save_game = QPushButton("Сохранить игру")
        self.btn_load_game = QPushButton("Загрузить игру")

        layout.addWidget(self.btn_resume)
        layout.addWidget(self.btn_main_menu)
        layout.addWidget(self.btn_save_game)
        layout.addWidget(self.btn_load_game)

        # Подключение сигналов
        self.btn_resume.clicked.connect(self.resume_game)
        self.btn_main_menu.clicked.connect(self.go_to_main_menu)
        self.btn_save_game.clicked.connect(self.save_game)
        self.btn_load_game.clicked.connect(self.load_game)

    def resume_game(self):
        """ Возобновляет игру """
        if self.parent_window:
            self.parent_window.show_game_board()  # Переход на экран игры

    def go_to_main_menu(self):
        """ Переход в главное меню """
        if self.parent_window:
            self.parent_window.show_main_menu()  # Переход в главное меню

    def save_game(self):
        """ Сохранение игры """
        if self.parent_window:
            self.parent_window.save_game()  # Вызов метода сохранения из родителя

    def load_game(self):
        """ Загрузка игры """
        if self.parent_window:
            self.parent_window.load_game()  # Вызов метода загрузки из родителя

# --- Менеджер игры (GameManager - без изменений, предполагается здесь) ---
class GameManager(QObject):
    # Сигналы для UI
    player_turn_changed = pyqtSignal(Player)
    player_moved = pyqtSignal(Player, int, int, bool) # player, old_pos, new_pos, passed_go
    dice_rolled = pyqtSignal(Player, int, int, bool) # player, d1, d2, is_double
    money_changed = pyqtSignal(Player)
    property_changed = pyqtSignal(Property) # Общий сигнал об изменении собственности (покупка, залог, дома)
    player_jailed = pyqtSignal(Player)
    player_released = pyqtSignal(Player)
    card_drawn = pyqtSignal(Player, str, str) # player, deck_type, card_text
    auction_started = pyqtSignal(Property, list) # prop, bidders
    auction_update = pyqtSignal(str) # Сообщение о ходе аукциона
    auction_ended = pyqtSignal(Property, Player, int) # prop, winner, price
    player_bankrupt = pyqtSignal(Player, object) # player, creditor ('bank' or Player)
    game_over = pyqtSignal(Player) # winner
    action_needed = pyqtSignal(Player, list) # player, available_actions
    log_message = pyqtSignal(str)
    request_human_action = pyqtSignal(str, dict) # Запрос действия у UI (action_type, params)
    force_ui_update = pyqtSignal() # Сигнал для принудительного обновления UI

    def __init__(self, player_configs, parent=None):
        super().__init__(parent)
        self.board = GameBoard()
        self.players = [Player(i, cfg["name"]) for i, cfg in enumerate(player_configs)]
        self.current_player_index = 0
        self.current_player = self.players[self.current_player_index]
        self.current_dice_roll = (0, 0)
        self.doubles_count = 0
        self.game_phase = "START_TURN" # Фазы: START_TURN, ROLLED, ACTION, AUCTION, JAIL_TURN, MANAGE_PROPERTIES, GAME_OVER, BANKRUPTCY_RESOLUTION
        self.auction_state = None
        self.pending_rent = None # {'payer': Player, 'receiver': Player, 'amount': int, 'property': Property}
        self.pending_card_action = None # Для многошаговых карт (напр. ближайшая утилита)

        self._link_properties_to_players() # Связываем свойства (для загрузки)
        self.log_message.emit(f"Игра началась! Игроки: {', '.join([p.name for p in self.players])}")
        # _start_player_turn() вызывается из MonopolyGameWindow.setup_game() или при загрузке

    def _link_properties_to_players(self):
        """ Связывает объекты Property с игроками после загрузки """
        # Сначала сбросим всех владельцев на доске
        for tile in self.board.tiles:
            tile.owner = None
        # Затем пройдемся по игрокам и их сохраненным индексам
        for player in self.players:
            indices_to_link = getattr(player, 'property_indices', [])
            player.properties = [] # Очищаем список перед заполнением
            for prop_index in indices_to_link:
                if 0 <= prop_index < len(self.board.tiles):
                    prop = self.board.tiles[prop_index]
                    player.add_property(prop) # Метод add_property устанавливает и владельца
            # Удаляем временный атрибут
            if hasattr(player, 'property_indices'):
                delattr(player, 'property_indices')

    def _start_player_turn(self):
        """ Начинает ход текущего игрока """
        self.current_dice_roll = (0, 0)
        # self.doubles_count не сбрасывается здесь, а только после не-дубля или в next_turn
        self.log_message.emit(f"--- Ход игрока {self.current_player.name} (${self.current_player.money}) ---")
        self.player_turn_changed.emit(self.current_player)

        if self.current_player.in_jail:
            self.game_phase = "JAIL_TURN"
            self.log_message.emit(f"{self.current_player.name} в тюрьме ({self.current_player.jail_turns+1}-й ход).")
        else:
            self.game_phase = "START_TURN"
            self.log_message.emit("Бросайте кубики.")
        self._emit_action_needed()

    def next_turn(self):
        """ Передает ход следующему игроку """
        if self.game_phase == "GAME_OVER": return

        self.log_message.emit(f"{self.current_player.name} завершил ход.")
        self.doubles_count = 0 # Сбрасываем счетчик дублей
        self.pending_rent = None
        self.pending_card_action = None

        active_players = [p for p in self.players if not p.is_bankrupt]
        if len(active_players) <= 1:
            self.game_phase = "GAME_OVER"
            winner = active_players[0] if active_players else None
            if winner:
                self.log_message.emit(f"Игра окончена! Победитель: {winner.name}")
                self.game_over.emit(winner)
            else:
                 self.log_message.emit("Игра окончена! Нет победителя.")
            self._emit_action_needed()
            return

        # Находим индекс текущего игрока среди активных
        try:
            current_active_index = active_players.index(self.current_player)
            next_active_index = (current_active_index + 1) % len(active_players)
            self.current_player = active_players[next_active_index]
            self.current_player_index = self.players.index(self.current_player)
        except ValueError: # Текущий игрок выбыл, ищем следующего активного
             self.current_player_index = (self.current_player_index + 1) % len(self.players)
             while self.players[self.current_player_index].is_bankrupt:
                 self.current_player_index = (self.current_player_index + 1) % len(self.players)
             self.current_player = self.players[self.current_player_index]

        self._start_player_turn()

    def roll_dice(self):
        """ Бросок кубиков """
        # Проверка фазы игры
        can_roll = (self.game_phase == "START_TURN" or
                    (self.game_phase == "JAIL_TURN" and self.current_player.jail_turns < 3) or
                    self.game_phase == "ROLLED_DOUBLE") # Можно бросать после дубля

        if not can_roll:
            self.log_message.emit("Нельзя бросить кубики сейчас.")
            return

        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        # die1, die2 = 1, 2 # Для тестов
        self.current_dice_roll = (die1, die2)
        is_double = die1 == die2
        roll_total = die1 + die2

        self.log_message.emit(f"{self.current_player.name} выбросил {die1} и {die2} (Всего: {roll_total}){' - Дубль!' if is_double else ''}")
        self.dice_rolled.emit(self.current_player, die1, die2, is_double)

        if self.current_player.in_jail:
            self._handle_jail_roll(is_double, roll_total)
        else:
            self._handle_normal_roll(roll_total, is_double)

    def _handle_jail_roll(self, is_double, roll_total):
        """ Обработка броска в тюрьме """
        if is_double:
            self.log_message.emit(f"{self.current_player.name} выбросил дубль и выходит из тюрьмы!")
            self._release_from_jail(move_after=True, roll_total=roll_total)
            # Ход продолжается с движением
        else:
            self.current_player.jail_turns += 1
            if self.current_player.jail_turns >= 3:
                self.log_message.emit("Третья попытка выйти по дублю неудачна.")
                # Пытаемся заставить заплатить штраф
                if self._request_payment(self.current_player, JAIL_FINE, "bank", "штраф за выход из тюрьмы"):
                    # Если оплатил, выходим и двигаемся
                     self._release_from_jail(move_after=True, roll_total=roll_total)
                else:
                    # Не смог оплатить - банкротство или нужно собрать деньги
                    if not self.current_player.is_bankrupt: # Если еще не банкрот
                         self.log_message.emit(f"{self.current_player.name} не может заплатить штраф ${JAIL_FINE}. Нужно собрать средства или объявить банкротство.")
                         self.game_phase = "BANKRUPTCY_RESOLUTION" # Переходим в фазу сбора средств
                         self.pending_rent = {'payer': self.current_player, 'receiver': 'bank', 'amount': JAIL_FINE, 'reason': 'jail_fine'}
                         self._emit_action_needed()
                    # Если уже банкрот, то ход просто заканчивается
                    else:
                         self.next_turn()

            else:
                self.log_message.emit(f"Не дубль. Остается в тюрьме ({self.current_player.jail_turns}/3). Ход окончен.")
                self.next_turn() # Ход заканчивается, если не дубль и не 3-й ход

    def _handle_normal_roll(self, roll_total, is_double):
        """ Обработка обычного броска """
        if is_double:
            self.doubles_count += 1
            if self.doubles_count >= MAX_DOUBLES_BEFORE_JAIL:
                self.log_message.emit(f"Третий дубль подряд! {self.current_player.name} отправляется в тюрьму.")
                self._send_to_jail(self.current_player)
                # Ход заканчивается немедленно
                # self.next_turn() # Вызывается из _send_to_jail
                return
            else:
                # Дубль, но не третий. Ход продолжается после движения.
                self.game_phase = "ROLLED_DOUBLE" # Позволяет бросить еще раз
        else:
            # Не дубль. Ход закончится после действий на клетке.
            self.doubles_count = 0 # Сбрасываем счетчик дублей
            self.game_phase = "ACTION" # Переходим к действиям на клетке

        # Двигаем игрока
        self._move_player(roll_total)

        # Если после движения фаза не изменилась на что-то требующее ожидания (аукцион, банкротство),
        # то обновляем доступные действия.
        if self.game_phase not in ["AUCTION", "BANKRUPTCY_RESOLUTION", "GAME_OVER"]:
             self._emit_action_needed()


    def _move_player(self, steps):
        """ Перемещает игрока и обрабатывает проход 'Вперед' """
        player = self.current_player
        old_pos = player.position
        passed_go = player.move(steps, BOARD_SIZE)
        self.player_moved.emit(player, old_pos, player.position, passed_go)

        if passed_go:
            self.log_message.emit(f"{player.name} прошел поле 'Вперед' и получает ${PASS_GO_MONEY}.")
            self._receive_money(player, PASS_GO_MONEY, "проход Вперед")

        # Действие на новой клетке
        self._land_on_tile(player, player.position, steps) # Передаем шаги для утилит

    def _land_on_tile(self, player, position, dice_roll_total):
        """ Обрабатывает попадание игрока на клетку """
        tile = self.board.get_tile(position)
        self.log_message.emit(f"{player.name} попал на '{tile.name}' ({tile.type})")

        # Обработка разных типов клеток
        if tile.type in ['street', 'railroad', 'utility']:
            self._handle_property_landing(player, tile, dice_roll_total)
        elif tile.type == 'community_chest' or tile.type == 'chance':
            self._handle_card_landing(player, tile.type)
        elif tile.type == 'income_tax':
            self.log_message.emit(f"Нужно заплатить подоходный налог ${INCOME_TAX_AMOUNT}")
            self._request_payment(player, INCOME_TAX_AMOUNT, "bank", "подоходный налог")
        elif tile.type == 'luxury_tax':
            self.log_message.emit(f"Нужно заплатить налог на роскошь ${LUXURY_TAX_AMOUNT}")
            self._request_payment(player, LUXURY_TAX_AMOUNT, "bank", "налог на роскошь")
        elif tile.type == 'go_to_jail':
            self._send_to_jail(player)
            # Ход немедленно заканчивается после отправки в тюрьму
            # self.next_turn() # Вызывается из _send_to_jail
        elif tile.type == 'jail':
            self.log_message.emit("Просто посетили тюрьму.")
            # Действий нет
        elif tile.type == 'free_parking':
            self.log_message.emit("Бесплатная стоянка. Отдыхайте.")
            # Действий нет (по классическим правилам)
        elif tile.type == 'go':
            # Уже обработано в _move_player, если прошли
            self.log_message.emit("На поле Вперед.")
        else:
             self.log_message.emit(f"Неизвестный тип клетки: {tile.type}")

        # Если после действия на клетке игрок не банкрот и не ждет аукциона/оплаты,
        # а фаза позволяет завершить ход (ACTION или ROLLED_DOUBLE), обновляем действия
        if not player.is_bankrupt and self.game_phase not in ["AUCTION", "BANKRUPTCY_RESOLUTION", "GAME_OVER"] :
             self._emit_action_needed()


    def _handle_property_landing(self, player, prop, dice_roll_total):
        """ Обработка попадания на собственность """
        if prop.owner is None:
            # Ничья собственность - предложить купить или аукцион
            if player.can_afford(prop.price):
                self.log_message.emit(f"Собственность '{prop.name}' ничья. Цена: ${prop.price}. Можете купить или выставить на аукцион.")
                self.game_phase = "ACTION" # Ожидание решения игрока
                self._emit_action_needed(add_actions=['buy', 'auction']) # Добавляем кнопки Buy/Auction
            else:
                self.log_message.emit(f"Собственность '{prop.name}' ничья (Цена: ${prop.price}), но у вас недостаточно средств (${player.money}). Выставляется на аукцион.")
                self.start_auction(prop)
        elif prop.owner == player:
            # Собственность игрока
            self.log_message.emit("Это ваша собственность.")
            # Действий нет
        elif prop.is_mortgaged:
            # Заложена владельцем
            self.log_message.emit(f"Собственность '{prop.name}' принадлежит {prop.owner.name}, но заложена. Рента не платится.")
        else:
            # Собственность другого игрока - платить ренту
            rent = prop.get_rent(dice_roll_total, self.board)
            self.log_message.emit(f"Собственность принадлежит {prop.owner.name}. Нужно заплатить ренту ${rent}.")
            self._request_payment(player, rent, prop.owner, f"рента за '{prop.name}'")

    def _handle_card_landing(self, player, deck_type):
        """ Обработка попадания на клетку Шанс/Казна """
        card = self.board.draw_card(deck_type)
        if card:
            self.log_message.emit(f"Карта '{deck_type.replace('_',' ').title()}': {card.text}")
            self.card_drawn.emit(player, deck_type, card.text)
            self._execute_card_action(player, card)
        else:
            self.log_message.emit(f"Колода '{deck_type}' пуста!")

    def _execute_card_action(self, player, card):
        """ Выполнение действия карты """
        action = card.action
        amount = card.amount
        position = card.position
        prop_type = card.type

        card_source_text = f"карта '{card.deck or 'карта'}'" # Источник для логов

        if action == "get_money":
            self._receive_money(player, amount, card_source_text)
        elif action == "pay_money":
            self._request_payment(player, amount, "bank", card_source_text)
        elif action == "go_to":
            # Определяем, нужно ли собирать деньги за проход GO
            collect_go = False
            if not player.in_jail: # Не собираем, если в тюрьме
                # Собираем, если новая позиция меньше старой (пересекли 0)
                # или если новая позиция равна 0
                if position < player.position or position == 0:
                    collect_go = True
            self._move_player_to(position, collect_go) # Перемещаем игрока
        elif action == "go_to_jail":
            self._send_to_jail(player)
            # self.next_turn() # Вызывается из _send_to_jail
            return # Выходим, т.к. ход завершен
        elif action == "get_out_of_jail_free":
            player.add_jail_card(card)
            self.log_message.emit(f"{player.name} получил карту 'Бесплатный выход из тюрьмы'.")
            self.force_ui_update.emit() # Обновить UI для отображения карты
        elif action == "move_relative":
            # Относительное перемещение, GO не собирается при движении назад
            self._move_player(amount) # Используем _move_player, он обработает GO если нужно (при движении вперед)
            return # _move_player вызовет _land_on_tile и _emit_action_needed
        elif action == "go_to_nearest":
            nearest_pos = self.board.get_nearest_property_index(player.position, prop_type)
            self.log_message.emit(f"Переход на ближайшую '{prop_type}' на позиции {nearest_pos}.")

            # Определяем, нужно ли собирать деньги за проход GO
            collect_go = False
            if not player.in_jail and nearest_pos < player.position:
                collect_go = True

            # Перемещаем игрока без вызова _land_on_tile из _move_player_to
            old_pos = player.position
            player.position = nearest_pos
            self.player_moved.emit(player, old_pos, player.position, collect_go)

            if collect_go:
                 self._receive_money(player, PASS_GO_MONEY, "проход Вперед по карте")

            nearest_prop = self.board.get_tile(nearest_pos)

            # Особые правила для ЖД и Коммунальных по картам
            if nearest_prop.owner is None:
                self.log_message.emit(f"'{nearest_prop.name}' не куплена.")
                self._handle_property_landing(player, nearest_prop, 0) # Предложить купить/аукцион
            elif nearest_prop.is_mortgaged:
                 self.log_message.emit(f"'{nearest_prop.name}' принадлежит {nearest_prop.owner.name}, но заложена.")
            else:
                if prop_type == 'railroad':
                    rent = nearest_prop.get_rent(0, self.board) * 2 # Двойная рента
                    self.log_message.emit(f"'{nearest_prop.name}' принадлежит {nearest_prop.owner.name}. Платите двойную ренту: ${rent}.")
                    self._request_payment(player, rent, nearest_prop.owner, f"двойная рента за '{nearest_prop.name}' по карте")
                elif prop_type == 'utility':
                    # Запросить бросок кубиков у игрока
                    self.log_message.emit(f"'{nearest_prop.name}' принадлежит {nearest_prop.owner.name}. Бросьте кубики, чтобы определить ренту (10x).")
                    self.game_phase = "ACTION" # Ожидание броска
                    self.pending_card_action = {'type': 'utility_rent', 'property': nearest_prop}
                    self._emit_action_needed(add_actions=['roll_for_utility']) # Нужна спец. кнопка
                    return # Выходим, т.к. ждем действия игрока
        elif action == "pay_repairs":
            cost = 0
            for prop in player.properties:
                if isinstance(prop, Street) and not prop.is_mortgaged:
                    if prop.num_houses == HOTEL_LEVEL: cost += card.hotel_rate
                    else: cost += prop.num_houses * card.house_rate
            if cost > 0:
                self.log_message.emit(f"Оплата ремонта: ${cost}")
                self._request_payment(player, cost, "bank", "ремонт по карте")
            else:
                 self.log_message.emit("Нет собственности для ремонта.")
        elif action == "pay_players":
             total_payment = 0
             active_opponents = [p for p in self.players if p != player and not p.is_bankrupt]
             payment_per_player = card.amount
             payments_ok = True
             for opponent in active_opponents:
                 # Пытаемся заплатить каждому
                 if not self._request_payment(player, payment_per_player, opponent, f"выплата по карте от {player.name}"):
                     # Если не смогли заплатить одному, прерываем
                     self.log_message.emit(f"Не удалось заплатить {opponent.name}, требуется сбор средств.")
                     payments_ok = False
                     break # Прерываем цикл выплат, игрок должен собрать средства
                 else:
                      total_payment += payment_per_player

             if payments_ok and total_payment > 0:
                 self.log_message.emit(f"{player.name} заплатил ${total_payment} другим игрокам.")
             elif not payments_ok:
                  return # Выходим, т.к. игрок должен собрать средства

        elif action == "collect_from_players":
             total_collected = 0
             active_opponents = [p for p in self.players if p != player and not p.is_bankrupt]
             collection_per_player = card.amount
             all_paid = True
             for opponent in active_opponents:
                 # Запрашиваем платеж от оппонента к текущему игроку
                 if self._request_payment(opponent, collection_per_player, player, f"сбор по карте для {player.name}"):
                     total_collected += collection_per_player
                 else:
                      # Если оппонент не может заплатить, он должен собрать средства или обанкротиться
                      self.log_message.emit(f"{opponent.name} не может заплатить {player.name}. Требуется разрешение долга.")
                      all_paid = False
                      # Здесь игра должна перейти в ожидание разрешения долга оппонента.
                      # Это сложная логика, пока просто логгируем.
                      # В идеале, нужно приостановить ход текущего игрока и переключиться
                      # на разрешение долга оппонента.
                      # Пока пропускаем и продолжаем ход текущего игрока.
                      pass

             if total_collected > 0:
                 self.log_message.emit(f"{player.name} получил ${total_collected} от других игроков.")
             if not all_paid:
                  self.log_message.emit("Не все игроки смогли заплатить.")
                  # Ход текущего игрока продолжается, но ситуация с должниками не разрешена (упрощение)


        # После выполнения карты (если не было return раньше)
        if self.game_phase not in ["AUCTION", "BANKRUPTCY_RESOLUTION", "GAME_OVER", "JAIL_TURN"]:
             # Определяем следующую фазу
             if self.doubles_count > 0:
                 self.game_phase = "ROLLED_DOUBLE"
             else:
                 self.game_phase = "ACTION"
             self._emit_action_needed()


    def roll_for_utility_rent(self):
        """ Игрок бросает кубики для определения ренты за утилиту по карте """
        if not self.pending_card_action or self.pending_card_action['type'] != 'utility_rent':
             self.log_message.emit("Ошибка: Не ожидался бросок для утилиты.")
             return

        prop = self.pending_card_action['property']
        player = self.current_player
        owner = prop.owner

        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        roll_total = die1 + die2
        rent = roll_total * 10 # 10x по карте Шанс

        self.log_message.emit(f"{player.name} выбросил {die1} и {die2} (Всего: {roll_total}) для оплаты ренты за '{prop.name}'.")
        self.dice_rolled.emit(player, die1, die2, False) # Это не считается за дубль для хода
        self.log_message.emit(f"Рента составляет 10 * {roll_total} = ${rent}.")

        self.pending_card_action = None # Сбрасываем ожидание
        payment_successful = self._request_payment(player, rent, owner, f"рента за '{prop.name}' (10x по карте)")

        # После оплаты (или запроса оплаты) нужно обновить доступные действия
        # Только если платеж прошел или не требуется сбор средств
        if payment_successful and not player.is_bankrupt and self.game_phase not in ["AUCTION", "BANKRUPTCY_RESOLUTION", "GAME_OVER"]:
             if self.doubles_count == 0: self.game_phase = "ACTION"
             else: self.game_phase = "ROLLED_DOUBLE"
             self._emit_action_needed()
        # Если платеж не прошел и требуется сбор средств, _request_payment уже установил фазу BANKRUPTCY_RESOLUTION


    def _request_payment(self, payer, amount, receiver, reason=""):
        """ Запрашивает платеж, обрабатывает нехватку средств и банкротство """
        receiver_name = receiver.name if isinstance(receiver, Player) else "Банк"
        self.log_message.emit(f"{payer.name} должен заплатить {receiver_name} ${amount}" + (f" ({reason})" if reason else ""))

        if payer.can_afford(amount):
            self._process_payment(payer, amount, receiver)
            return True
        else:
            self.log_message.emit(f"У {payer.name} недостаточно денег (${payer.money}). Необходимо собрать средства.")
            # Проверяем, может ли игрок вообще собрать нужную сумму
            if payer.total_assets(self.board) < amount:
                self.log_message.emit(f"У {payer.name} недостаточно активов для покрытия долга ${amount}.")
                self._handle_bankruptcy(payer, receiver)
                return False
            else:
                # Игрок может собрать деньги, переводим игру в ожидание
                self.game_phase = "BANKRUPTCY_RESOLUTION" # Используем эту фазу для сбора средств
                self.pending_rent = {'payer': payer, 'receiver': receiver, 'amount': amount, 'reason': reason}
                self.log_message.emit(f"{payer.name}, используйте 'Управление Имуществом', чтобы продать дома/заложить собственность для оплаты ${amount}.")
                self._emit_action_needed() # Даем доступ к управлению имуществом
                return False # Платеж пока не прошел

    def _process_payment(self, payer, amount, receiver):
        """ Непосредственно выполняет перевод денег """
        payer.change_money(-amount)
        self.money_changed.emit(payer)
        receiver_name = "Банк"
        if isinstance(receiver, Player):
            receiver.change_money(amount)
            self.money_changed.emit(receiver)
            receiver_name = receiver.name

        self.log_message.emit(f"{payer.name} заплатил {receiver_name} ${amount}. Баланс {payer.name}: ${payer.money}" + (f", Баланс {receiver_name}: ${receiver.money}" if isinstance(receiver, Player) else ""))

        # Если это был отложенный платеж, сбрасываем его и восстанавливаем фазу
        if self.pending_rent and self.pending_rent['payer'] == payer and self.pending_rent['amount'] <= amount : # <= на случай переплаты
             original_payer = self.pending_rent['payer']
             self.pending_rent = None
             # После успешной оплаты долга, возвращаемся к нормальному ходу
             # ТОЛЬКО если долг платил ТЕКУЩИЙ игрок
             if self.game_phase == "BANKRUPTCY_RESOLUTION" and original_payer == self.current_player:
                  # Определяем, какая фаза должна быть следующей
                  if self.doubles_count > 0:
                       self.game_phase = "ROLLED_DOUBLE" # Если был дубль до долга
                  else:
                       self.game_phase = "ACTION" # Стандартная фаза после действия
                  self.log_message.emit("Долг погашен.")
                  self._emit_action_needed()
             # Если долг платил НЕ текущий игрок (напр. по карте сбора), фаза текущего игрока не меняется


    def _receive_money(self, player, amount, reason=""):
        """ Игрок получает деньги """
        player.change_money(amount)
        self.money_changed.emit(player)
        self.log_message.emit(f"{player.name} получил ${amount}" + (f" ({reason})" if reason else "") + f". Баланс: ${player.money}")

    def _send_to_jail(self, player):
        """ Отправляет игрока в тюрьму """
        if player.in_jail: return # Уже там
        self.log_message.emit(f"{player.name} отправляется в тюрьму!")
        player.position = JAIL_POSITION
        player.in_jail = True
        player.jail_turns = 0
        self.doubles_count = 0 # Сбрасываем дубли при попадании в тюрьму
        self.player_jailed.emit(player)
        self.player_moved.emit(player, player.position, JAIL_POSITION, False) # Сообщаем UI о перемещении в тюрьму

        # Ход немедленно заканчивается
        self.game_phase = "ACTION" # Просто чтобы не было START_TURN или ROLLED_DOUBLE
        self.next_turn()


    def _release_from_jail(self, move_after=False, roll_total=0):
        """ Освобождает игрока из тюрьмы """
        player = self.current_player
        if not player.in_jail: return

        player.in_jail = False
        player.jail_turns = 0
        self.player_released.emit(player)
        self.log_message.emit(f"{player.name} вышел из тюрьмы.")

        if move_after and roll_total > 0:
            # Двигаемся на roll_total шагов ПОСЛЕ выхода
            self.log_message.emit("Движение после выхода из тюрьмы...")
            # Важно: фаза должна позволять движение
            self.game_phase = "ACTION" # Устанавливаем фазу для движения
            self._move_player(roll_total)
            # _move_player вызовет _land_on_tile и _emit_action_needed
        else:
             # Если не двигаемся после выхода (заплатили штраф / карта до броска)
             self.game_phase = "START_TURN" # Готовы к обычному броску
             self._emit_action_needed()


    # --- Действия игрока (вызываются из UI) ---

    def attempt_pay_jail_fine(self):
        """ Попытка заплатить штраф за выход из тюрьмы """
        player = self.current_player
        if not player.in_jail or self.game_phase != "JAIL_TURN":
            self.log_message.emit("Нельзя заплатить штраф сейчас.")
            return

        self.log_message.emit(f"{player.name} пытается заплатить штраф ${JAIL_FINE}.")
        if self._request_payment(player, JAIL_FINE, "bank", "штраф за выход из тюрьмы"):
             # Успешно оплатил
             self._release_from_jail(move_after=False) # Выходит, но не двигается сразу
             # Теперь игрок может бросить кубики в обычном режиме
        # else: обработка нехватки средств уже в _request_payment

    def attempt_use_jail_card(self):
        """ Попытка использовать карту выхода из тюрьмы """
        player = self.current_player
        if not player.in_jail or self.game_phase != "JAIL_TURN":
            self.log_message.emit("Нельзя использовать карту сейчас.")
            return

        card = player.use_jail_card()
        if card:
            self.log_message.emit(f"{player.name} использует карту 'Бесплатный выход из тюрьмы'.")
            self.board.return_jail_card(card) # Возвращаем карту в сброс
            self._release_from_jail(move_after=False) # Выходит, но не двигается сразу
            self.force_ui_update.emit() # Обновить UI (кол-во карт)
            # Теперь игрок может бросить кубики в обычном режиме
        else:
            self.log_message.emit(f"У {player.name} нет карт выхода из тюрьмы.")

    def buy_property(self):
        """ Игрок покупает текущую собственность """
        player = self.current_player
        prop = self.board.get_tile(player.position)

        # Можно купить только если фаза ACTION и собственность доступна
        can_buy_now = (self.game_phase == "ACTION" and
                       isinstance(prop, Property) and
                       prop.owner is None and
                       prop.price > 0)

        if not can_buy_now:
            self.log_message.emit("Нельзя купить эту собственность сейчас.")
            return

        if player.can_afford(prop.price):
            self._process_payment(player, prop.price, "bank")
            player.add_property(prop)
            self.log_message.emit(f"{player.name} купил '{prop.name}' за ${prop.price}.")
            self.property_changed.emit(prop)
            # После покупки ход обычно продолжается (если был дубль) или заканчивается
            if self.doubles_count > 0:
                 self.game_phase = "ROLLED_DOUBLE"
            else:
                 self.game_phase = "ACTION" # Остается ACTION, чтобы можно было завершить ход
            self._emit_action_needed()
        else:
            self.log_message.emit("Недостаточно средств для покупки.")
            # По правилам, если не покупаешь или не можешь, идет аукцион
            self.start_auction(prop)

    def decline_buy_property(self):
        """ Игрок отказывается покупать, запускается аукцион """
        player = self.current_player
        prop = self.board.get_tile(player.position)

        can_decline_now = (self.game_phase == "ACTION" and
                           isinstance(prop, Property) and
                           prop.owner is None and
                           prop.price > 0)

        if not can_decline_now:
            self.log_message.emit("Нельзя отказаться от покупки сейчас.")
            return

        self.log_message.emit(f"{player.name} отказался покупать '{prop.name}'. Начинается аукцион.")
        self.start_auction(prop)

    def manage_properties(self):
         """ Игрок хочет управлять собственностью (залог, дома) """
         if self.game_phase in ["START_TURN", "ACTION", "ROLLED_DOUBLE", "JAIL_TURN", "BANKRUPTCY_RESOLUTION"]:
              self.log_message.emit("Открыто управление имуществом.")
              # UI должен показать диалог управления
              self.request_human_action.emit("show_manage_properties", {'player': self.current_player})
              # Фаза игры не меняется, пока игрок управляет
         else:
              self.log_message.emit("Нельзя управлять имуществом сейчас.")


    def mortgage_property(self, prop_index):
        """ Заложить собственность """
        player = self.current_player
        prop = self._get_property_by_index(prop_index)
        if not prop or prop.owner != player or prop.is_mortgaged:
            self.log_message.emit(f"Нельзя заложить '{prop.name if prop else 'неизвестно'}'.")
            return
        if isinstance(prop, Street) and prop.num_houses > 0:
            self.log_message.emit(f"Нельзя заложить '{prop.name}', пока на ней есть дома/отели.")
            return

        # Проверяем, есть ли дома на других улицах этого цвета (нельзя закладывать, если есть)
        if isinstance(prop, Street):
             color_group = self.board.get_properties_by_color(prop.color_key)
             if any(p.num_houses > 0 for p in color_group):
                  self.log_message.emit(f"Нельзя заложить '{prop.name}', пока есть дома на других улицах цвета '{prop.color_key}'.")
                  return


        amount = prop.mortgage_value
        prop.is_mortgaged = True
        self._receive_money(player, amount, f"залог '{prop.name}'")
        self.log_message.emit(f"{player.name} заложил '{prop.name}' за ${amount}.")
        self.property_changed.emit(prop)
        self._check_pending_payment_after_manage() # Проверить, не погашен ли долг
        self.force_ui_update.emit()

    def unmortgage_property(self, prop_index):
        """ Выкупить заложенную собственность """
        player = self.current_player
        prop = self._get_property_by_index(prop_index)
        if not prop or prop.owner != player or not prop.is_mortgaged:
            self.log_message.emit(f"Нельзя выкупить '{prop.name if prop else 'неизвестно'}'.")
            return

        cost = int(prop.mortgage_value * (1 + MORTGAGE_INTEREST_RATE))
        if player.can_afford(cost):
            self._process_payment(player, cost, "bank")
            prop.is_mortgaged = False
            self.log_message.emit(f"{player.name} выкупил '{prop.name}' за ${cost}.")
            self.property_changed.emit(prop)
            self.force_ui_update.emit()
        else:
            self.log_message.emit(f"Недостаточно средств (${player.money}) для выкупа '{prop.name}' за ${cost}.")

    def build_house(self, prop_index):
        """ Построить дом/отель """
        player = self.current_player
        prop = self._get_property_by_index(prop_index)
        if not isinstance(prop, Street) or not self.board.can_build_house(player, prop):
            self.log_message.emit(f"Нельзя строить дом на '{prop.name if prop else 'неизвестно'}'. Проверьте монополию, равномерность застройки и наличие средств.")
            return

        cost = prop.house_cost
        if player.can_afford(cost):
            self._process_payment(player, cost, "bank")
            prop.num_houses += 1
            house_type = "Отель" if prop.num_houses == HOTEL_LEVEL else f"{prop.num_houses}-й дом"
            self.log_message.emit(f"{player.name} построил {house_type} на '{prop.name}' за ${cost}.")
            self.property_changed.emit(prop)
            self._check_pending_payment_after_manage() # Проверить долг
            self.force_ui_update.emit()
        else:
            self.log_message.emit(f"Недостаточно средств (${player.money}) для постройки дома за ${cost}.")

    def sell_house(self, prop_index):
        """ Продать дом/отель """
        player = self.current_player
        prop = self._get_property_by_index(prop_index)
        if not isinstance(prop, Street) or not self.board.can_sell_house(player, prop):
            self.log_message.emit(f"Нельзя продать дом с '{prop.name if prop else 'неизвестно'}'. Проверьте наличие домов и равномерность продажи.")
            return

        amount = prop.house_cost // 2
        house_type = "Отель" if prop.num_houses == HOTEL_LEVEL else "Дом"
        prop.num_houses -= 1
        self._receive_money(player, amount, f"продажа {house_type.lower()} с '{prop.name}'")
        self.log_message.emit(f"{player.name} продал {house_type.lower()} с '{prop.name}' за ${amount}.")
        self.property_changed.emit(prop)
        self._check_pending_payment_after_manage() # Проверить долг
        self.force_ui_update.emit()

    def _check_pending_payment_after_manage(self):
         """ Проверяет, достаточно ли денег для погашения долга после управления имуществом """
         if self.game_phase == "BANKRUPTCY_RESOLUTION" and self.pending_rent:
              payer = self.pending_rent['payer']
              amount_needed = self.pending_rent['amount']
              if payer == self.current_player and payer.can_afford(amount_needed):
                   self.log_message.emit(f"Собрано достаточно средств (${payer.money}) для погашения долга ${amount_needed}.")
                   # Автоматически погашаем долг
                   receiver = self.pending_rent['receiver']
                   # Важно: сохраняем текущее состояние дублей перед погашением
                   doubles_before_payment = self.doubles_count
                   self._process_payment(payer, amount_needed, receiver)
                   # _process_payment сбросит pending_rent и восстановит фазу,
                   # но может сбросить doubles_count, если он был > 0. Восстановим его.
                   self.doubles_count = doubles_before_payment
                   # Переопределим фазу на основе дублей
                   if self.doubles_count > 0:
                        self.game_phase = "ROLLED_DOUBLE"
                   else:
                        self.game_phase = "ACTION"
                   self._emit_action_needed() # Обновляем действия после погашения

              elif payer == self.current_player: # Все еще не хватает
                   self.log_message.emit(f"Все еще нужно ${amount_needed - payer.money} для погашения долга.")
                   self._emit_action_needed() # Обновляем доступные действия (вдруг что-то еще можно продать/заложить)


    def end_turn(self):
        """ Завершает ход текущего игрока """
        # Нельзя завершить ход, если нужно сделать действие (купить/аукцион, оплатить долг)
        # или если выпал дубль и можно/нужно бросить еще раз
        if self.game_phase == "ROLLED_DOUBLE":
             self.log_message.emit("Вы выбросили дубль, бросайте еще раз!")
             self._emit_action_needed()
             return
        if self.game_phase == "BANKRUPTCY_RESOLUTION":
             self.log_message.emit("Нельзя завершить ход, пока не погашен долг!")
             return
        if self.game_phase == "AUCTION":
             self.log_message.emit("Нельзя завершить ход во время аукциона!")
             return
        # Проверка, не нужно ли купить/отказаться
        current_tile = self.board.get_tile(self.current_player.position)
        if current_tile.owner is None and current_tile.price > 0 and self.game_phase == "ACTION":
             # Проверяем, были ли уже предложены кнопки buy/auction
             # Если да, то игрок должен выбрать
             # (Простой способ: если фаза ACTION и есть кнопки buy/auction, не даем завершить)
             # Более точный способ: добавить флаг ожидания решения buy/auction
             # Пока используем простой:
             self.log_message.emit("Нужно решить: купить собственность или выставить на аукцион.")
             self._emit_action_needed(add_actions=['buy', 'auction'])
             return

        # Если все проверки пройдены, завершаем ход
        if self.game_phase != "GAME_OVER":
            self.next_turn()
        else:
             self.log_message.emit("Игра уже окончена.")


    # --- Аукцион ---
    def start_auction(self, prop):
        """ Начинает аукцион за собственность """
        if self.game_phase == "AUCTION":
             self.log_message.emit("Аукцион уже идет!")
             return

        self.log_message.emit(f"--- Аукцион за '{prop.name}' ---")
        bidders = [p for p in self.players if not p.is_bankrupt]
        if not bidders:
             self.log_message.emit("Нет участников для аукциона.")
             # Возвращаемся к нормальному ходу
             if self.doubles_count > 0: self.game_phase = "ROLLED_DOUBLE"
             else: self.game_phase = "ACTION"
             self._emit_action_needed()
             return

        self.game_phase = "AUCTION"
        # Определяем, с кого начать аукцион (следующий после текущего игрока)
        start_bidder_index_in_players = (self.current_player_index + 1) % len(self.players)
        while self.players[start_bidder_index_in_players].is_bankrupt:
             start_bidder_index_in_players = (start_bidder_index_in_players + 1) % len(self.players)

        start_bidder = self.players[start_bidder_index_in_players]
        start_bidder_index_in_list = bidders.index(start_bidder) if start_bidder in bidders else 0


        self.auction_state = {
            'property': prop,
            'bidders': bidders, # Список Player объектов
            'current_bid': 0,
            'highest_bidder': None,
            'current_bidder_index': start_bidder_index_in_list, # Индекс в списке bidders
            'passes_in_a_row': 0 # Счетчик пасов подряд
        }
        self.auction_started.emit(prop, bidders)
        self._process_auction_turn()

    def _process_auction_turn(self):
        """ Обрабатывает ход в аукционе """
        if not self.auction_state: return

        state = self.auction_state
        active_bidders = state['bidders']

        # Проверяем, остался ли один участник ИЛИ все спасовали после последней ставки
        if len(active_bidders) == 1:
             # Если остался один, он победитель (даже если ставка 0)
             state['highest_bidder'] = active_bidders[0]
             # Если ставка была 0, он получает бесплатно? По правилам - да, если никто не поставил $1.
             # Но если он сам не ставил, а все остальные спасовали, он все равно выигрывает по последней ставке.
             self._end_auction()
             return
        if len(active_bidders) > 1 and state['passes_in_a_row'] >= len(active_bidders) -1 and state['highest_bidder'] is not None:
             # Если больше одного участника, но все, кроме лидера, спасовали подряд
             self._end_auction()
             return


        # Определяем текущего участника
        # Убедимся, что индекс в пределах списка
        state['current_bidder_index'] %= len(active_bidders)
        current_bidder = active_bidders[state['current_bidder_index']]


        self.log_message.emit(f"Аукцион: Ставка ${state['current_bid']}" + (f" (Лидер: {state['highest_bidder'].name})" if state['highest_bidder'] else ""))
        self.auction_update.emit(f"Ход {current_bidder.name}. Текущая ставка: ${state['current_bid']}. Ваш баланс: ${current_bidder.money}")

        # Запрашиваем ставку у UI
        self.request_human_action.emit("get_auction_bid", {
             'player': current_bidder,
             'property': state['property'],
             'current_bid': state['current_bid'],
             'highest_bidder': state['highest_bidder']
        })
        self._emit_action_needed() # Показываем кнопки Bid/Pass

    def place_auction_bid(self, amount):
        """ Игрок делает ставку на аукционе """
        if self.game_phase != "AUCTION" or not self.auction_state: return

        state = self.auction_state
        active_bidders = state['bidders']
        bidder_index = state['current_bidder_index'] % len(active_bidders)
        bidder = active_bidders[bidder_index]


        if amount <= state['current_bid']:
            self.log_message.emit(f"Ставка ${amount} должна быть больше текущей (${state['current_bid']}).")
            self.request_human_action.emit("get_auction_bid", {'player': bidder, 'property': state['property'], 'current_bid': state['current_bid'], 'highest_bidder': state['highest_bidder'], 'error': 'Ставка слишком мала'})
            return
        if not bidder.can_afford(amount):
            self.log_message.emit(f"{bidder.name} не может позволить ставку ${amount} (Баланс: ${bidder.money}).")
            self.request_human_action.emit("get_auction_bid", {'player': bidder, 'property': state['property'], 'current_bid': state['current_bid'], 'highest_bidder': state['highest_bidder'], 'error': 'Недостаточно средств'})
            return

        state['current_bid'] = amount
        state['highest_bidder'] = bidder
        state['passes_in_a_row'] = 0 # Сбрасываем счетчик пасов
        self.log_message.emit(f"Аукцион: {bidder.name} ставит ${amount}.")
        self.auction_update.emit(f"{bidder.name} ставит ${amount}.")

        # Переход к следующему участнику
        state['current_bidder_index'] = (bidder_index + 1) % len(active_bidders)
        self._process_auction_turn()

    def pass_auction_bid(self):
        """ Игрок пасует на аукционе """
        if self.game_phase != "AUCTION" or not self.auction_state: return

        state = self.auction_state
        active_bidders = state['bidders']
        bidder_index = state['current_bidder_index'] % len(active_bidders)
        bidder = active_bidders.pop(bidder_index) # Удаляем из активных участников

        self.log_message.emit(f"Аукцион: {bidder.name} пасует.")
        self.auction_update.emit(f"{bidder.name} пасует.")

        state['passes_in_a_row'] += 1 # Увеличиваем счетчик пасов

        # Если после удаления индекс указывает за пределы нового списка, сбрасываем на 0
        # или оставляем как есть, т.к. он будет взят по модулю в _process_auction_turn
        # state['current_bidder_index'] %= len(active_bidders) # Обновится в _process_auction_turn

        # Проверяем завершение аукциона (сделано в начале _process_auction_turn)
        self._process_auction_turn()


    def _end_auction(self):
        """ Завершает аукцион """
        if not self.auction_state: return

        state = self.auction_state
        prop = state['property']
        winner = state['highest_bidder']
        price = state['current_bid']

        # Если остался только один участник, он победитель
        if len(state['bidders']) == 1:
             winner = state['bidders'][0]
             # Если ставок не было, а он остался один, он забирает бесплатно?
             # По правилам - если никто не предложил даже $1, то собственность не продается.
             # Значит, если price == 0, победителя нет.
             if price == 0:
                  winner = None

        if winner and price > 0:
            self.log_message.emit(f"--- Аукцион завершен! '{prop.name}' продана игроку {winner.name} за ${price}. ---")
            # Списываем деньги и передаем собственность
            # Проверяем платежеспособность на всякий случай
            if winner.can_afford(price):
                 self._process_payment(winner, price, "bank")
                 winner.add_property(prop)
                 self.property_changed.emit(prop)
                 self.auction_ended.emit(prop, winner, price)
            else:
                 # Этого не должно произойти, если проверка была в place_auction_bid
                 self.log_message.emit(f"!!! Ошибка аукциона: {winner.name} не может оплатить ставку ${price}!")
                 # Откатываем аукцион? Или банкротим? Пока просто лог.
                 self.auction_ended.emit(prop, None, 0) # Считаем, что не продано

        else:
             # Ситуация, когда все спасовали сразу или остался 1 без ставки > 0
             self.log_message.emit(f"--- Аукцион завершен! '{prop.name}' не продана. ---")
             self.auction_ended.emit(prop, None, 0)


        self.auction_state = None
        # Возвращаемся к нормальному ходу
        if self.doubles_count > 0:
             self.game_phase = "ROLLED_DOUBLE"
        else:
             self.game_phase = "ACTION"
        self._emit_action_needed()

    # --- Банкротство ---
    def _handle_bankruptcy(self, bankrupt_player, creditor):
        """ Обрабатывает банкротство игрока """
        if bankrupt_player.is_bankrupt: return # Уже обрабатывается

        bankrupt_player.is_bankrupt = True
        creditor_name = creditor.name if isinstance(creditor, Player) else "Банк"
        self.log_message.emit(f"!!! {bankrupt_player.name} объявляется банкротом перед {creditor_name}! !!!")

        # Передача активов
        # 1. Деньги
        if bankrupt_player.money > 0:
            transfer_money = bankrupt_player.money
            bankrupt_player.change_money(-transfer_money)
            if isinstance(creditor, Player):
                creditor.change_money(transfer_money)
                self.money_changed.emit(creditor)
            self.log_message.emit(f"Передано ${transfer_money} от {bankrupt_player.name} к {creditor_name}.")
            self.money_changed.emit(bankrupt_player)


        # 2. Карты выхода из тюрьмы
        jail_cards = bankrupt_player.get_out_of_jail_cards[:] # Копируем список
        bankrupt_player.get_out_of_jail_cards.clear()
        for card in jail_cards:
             if isinstance(creditor, Player):
                  creditor.add_jail_card(card)
                  self.log_message.emit(f"Карта 'Выход из тюрьмы' передана {creditor_name}.")
             else: # Банку - карта возвращается в колоду
                  self.board.return_jail_card(card)
                  self.log_message.emit("Карта 'Выход из тюрьмы' возвращена в колоду.")

        # 3. Собственность
        properties_to_transfer = bankrupt_player.properties[:] # Копируем список
        bankrupt_player.properties.clear() # Очищаем у банкрота

        bank_properties_to_auction = [] # Список для аукциона при банкротстве перед банком

        for prop in properties_to_transfer:
            prop.owner = None # Сначала убираем владельца

            # Сбрасываем дома/отели при передаче
            if isinstance(prop, Street):
                 if prop.num_houses > 0:
                      # Возвращаем полцены домов банку (не кредитору!)
                      money_back = prop.num_houses * (prop.house_cost // 2)
                      # bankrupt_player.change_money(money_back) # Деньги уже ушли кредитору
                      self.log_message.emit(f"Сброшены дома/отели с '{prop.name}'.")
                      prop.num_houses = 0


            if isinstance(creditor, Player):
                # Передаем собственность кредитору
                creditor.add_property(prop)
                self.log_message.emit(f"Собственность '{prop.name}' передана {creditor_name}.")
                # Если собственность была заложена, кредитор должен СРАЗУ решить:
                # 1. Выкупить, заплатив 10% банку.
                # 2. Оставить заложенной, заплатив 10% банку.
                # 3. Заложить снова (если не была заложена), получив полцены от банка.
                # Упрощение: Передаем как есть. Кредитор разберется позже.
                # Если заложена, он должен будет заплатить проценты при выкупе.
                self.property_changed.emit(prop)
            else:
                # Банкротство перед банком - собственность выставляется на аукцион
                self.log_message.emit(f"Собственность '{prop.name}' возвращена банку и будет выставлена на аукцион.")
                prop.is_mortgaged = False # Продается незаложенной
                bank_properties_to_auction.append(prop)
                self.property_changed.emit(prop) # Обновить вид без владельца

        self.player_bankrupt.emit(bankrupt_player, creditor)
        self.force_ui_update.emit()

        # Запускаем аукционы для собственности, переданной банку
        if bank_properties_to_auction:
             # TODO: Реализовать очередь аукционов. Пока запускаем только первый.
             self.log_message.emit("Запуск аукциона для возвращенной собственности...")
             # Важно: Аукцион должен начаться ПОСЛЕ завершения текущего хода/действия.
             # Возможно, лучше добавить их в очередь и запустить в начале следующего хода.
             # Пока упрощенно - запускаем сразу первый попавшийся.
             self.start_auction(bank_properties_to_auction[0])
             return # Выходим, т.к. игра перешла в фазу аукциона


        # Проверяем, не закончилась ли игра (если не было аукционов)
        active_players = [p for p in self.players if not p.is_bankrupt]
        if len(active_players) <= 1:
            self.game_phase = "GAME_OVER"
            winner = active_players[0] if active_players else None
            if winner:
                self.log_message.emit(f"Игра окончена! Победитель: {winner.name}")
                self.game_over.emit(winner)
            else:
                 self.log_message.emit("Игра окончена! Нет победителя.")
            self._emit_action_needed()
        else:
             # Если игра продолжается, и банкротство произошло во время чьего-то хода,
             # нужно корректно передать ход или продолжить текущий.
             # Если банкрот - текущий игрок, передаем ход.
             if bankrupt_player == self.current_player:
                  self.next_turn()
             else:
                  # Если обанкротился не текущий игрок (например, при сборе денег по карте),
                  # текущий игрок продолжает свой ход.
                  self.log_message.emit(f"Игра продолжается. Ход игрока {self.current_player.name}.")
                  # Восстанавливаем фазу, которая была до банкротства (если возможно)
                  # Или просто переходим к стандартной фазе ACTION/ROLLED_DOUBLE
                  if self.doubles_count > 0 and self.game_phase != "ROLLED_DOUBLE":
                       self.game_phase = "ROLLED_DOUBLE"
                  elif self.doubles_count == 0 and self.game_phase != "ACTION":
                       self.game_phase = "ACTION"
                  # Если фаза уже была правильной, не меняем ее
                  self._emit_action_needed()


    # --- Вспомогательные методы ---
    def _emit_action_needed(self, add_actions=None):
        """ Определяет доступные действия и отправляет сигнал UI """
        if not self.current_player: # Если нет текущего игрока (например, при ошибке загрузки)
             self.action_needed.emit(None, [])
             return

        player = self.current_player
        phase = self.game_phase
        actions = []

        # Действия доступны только если игрок не банкрот
        if player.is_bankrupt:
             phase = "GAME_OVER" # Считаем игру оконченной для банкрота

        if phase == "GAME_OVER":
            # Для всех игроков только 'new_game'
            actions = ['new_game']
            # Сигнал отправляется без игрока, т.к. действие общее
            self.action_needed.emit(None, actions)
            return

        elif phase == "AUCTION":
            actions.append('manage_props') # Разрешим управление во время аукциона
            # Определяем, кто ходит в аукционе
            if self.auction_state:
                 active_bidders = self.auction_state['bidders']
                 if active_bidders: # Проверка, что список не пуст
                      current_auction_player_index = self.auction_state['current_bidder_index'] % len(active_bidders)
                      current_auction_player = active_bidders[current_auction_player_index]
                      # Только текущий участник аукциона может делать ставку/пас
                      if current_auction_player == player:
                           actions.extend(['bid', 'pass_bid'])
                 else: # Если список участников пуст (ошибка?)
                      self.log_message.emit("Ошибка аукциона: нет участников.")
                      self._end_auction() # Пытаемся завершить аукцион
                      return # Выходим, т.к. аукцион завершен

        elif phase == "BANKRUPTCY_RESOLUTION":
             # Доступно только игроку, который должен собрать средства
             if self.pending_rent and self.pending_rent['payer'] == player:
                  actions = ['manage_props'] # Только управление для сбора средств
                  actions.append('declare_bankruptcy') # Кнопка "Сдаться"
             # Другие игроки ничего не делают

        elif phase == "JAIL_TURN":
            actions = ['manage_props']
            if player.get_out_of_jail_cards:
                actions.append('use_jail_card')
            if player.can_afford(JAIL_FINE):
                actions.append('pay_jail_fine')
            if player.jail_turns < 3:
                actions.append('roll_dice') # Попытка выбросить дубль
        elif phase == "START_TURN":
            actions = ['roll_dice', 'manage_props']
        elif phase == "ROLLED_DOUBLE":
             actions = ['roll_dice', 'manage_props'] # Бросить еще раз или управлять
             # Нельзя завершить ход после дубля
        elif phase == "ACTION":
            actions = ['manage_props', 'end_turn']
            # Дополнительные действия в зависимости от клетки
            tile = self.board.get_tile(player.position)
            if tile.type in ['street', 'railroad', 'utility'] and tile.owner is None and tile.price > 0:
                 actions.extend(['buy', 'auction']) # Кнопки появляются при попадании на клетку
                 if 'end_turn' in actions: actions.remove('end_turn') # Нельзя закончить, пока не решил
            # Если ожидаем бросок для утилиты по карте
            if self.pending_card_action and self.pending_card_action['type'] == 'utility_rent':
                 actions = ['roll_for_utility'] # Только спец. бросок
                 if 'end_turn' in actions: actions.remove('end_turn')
                 if 'manage_props' in actions: actions.remove('manage_props')


        # Добавляем дополнительные действия, если они были переданы
        if add_actions:
            for act in add_actions:
                if act not in actions:
                    actions.append(act)
            # Если добавили 'buy' или 'auction', убираем 'end_turn'
            if ('buy' in add_actions or 'auction' in add_actions) and 'end_turn' in actions:
                 actions.remove('end_turn')


        # Убираем 'manage_props', если нет собственности для управления
        can_manage = any(isinstance(p, Street) or p.is_mortgaged or not p.is_mortgaged for p in player.properties)
        if not can_manage and 'manage_props' in actions:
             actions.remove('manage_props')


        self.log_message.emit(f"Доступные действия для {player.name}: {', '.join(actions)}")
        self.action_needed.emit(player, actions)

    def _get_property_by_index(self, index):
        """ Безопасно получает объект Property по индексу """
        if 0 <= index < len(self.board.tiles):
            return self.board.tiles[index]
        return None

    def _move_player_to(self, position, collect_go=True):
         """ Перемещает игрока на конкретную позицию """
         player = self.current_player
         old_pos = player.position
         passed_go = player.move_to(position, collect_go, BOARD_SIZE)
         self.player_moved.emit(player, old_pos, player.position, passed_go)

         if passed_go:
             self._receive_money(player, PASS_GO_MONEY, "проход Вперед при перемещении")

         # Действие на новой клетке
         self._land_on_tile(player, player.position, 0) # Dice roll 0 для этого случая


    def declare_bankruptcy_action(self):
         """ Игрок решает сдаться при нехватке средств """
         if self.game_phase == "BANKRUPTCY_RESOLUTION" and self.pending_rent:
              payer = self.pending_rent['payer']
              receiver = self.pending_rent['receiver']
              amount = self.pending_rent['amount']
              # Только игрок, который должен платить, может сдаться
              if payer == self.current_player and not payer.can_afford(amount):
                   self.log_message.emit(f"{payer.name} сдается и объявляет банкротство перед {receiver.name if isinstance(receiver, Player) else 'Банком'}.")
                   self._handle_bankruptcy(payer, receiver)
              elif payer == self.current_player and payer.can_afford(amount):
                   self.log_message.emit("Нельзя объявить банкротство, если вы можете заплатить.")
              else:
                   self.log_message.emit("Сейчас не ваша очередь объявлять банкротство по этому долгу.")
         else:
              self.log_message.emit("Нельзя объявить банкротство сейчас.")


    # --- Сохранение/Загрузка (упрощенно) ---
    def get_game_state(self):
        """ Собирает состояние игры для сохранения """
        state = {
            'players': [p.to_dict() for p in self.players],
            'board': self.board.to_dict(),
            'current_player_index': self.current_player_index,
            'game_phase': self.game_phase,
            'doubles_count': self.doubles_count,
            'pending_rent': None, # Сбрасываем при сохранении для упрощения
            'auction_state': None, # Сбрасываем при сохранении для упрощения
            'pending_card_action': None # Сбрасываем при сохранении
        }
        # Примечание: Сброс pending_rent, auction_state, pending_card_action означает,
        # что игра не может быть сохранена и корректно загружена посреди аукциона,
        # ожидания платежа или ожидания броска для утилиты. Это значительное упрощение.
        # Для полной реализации нужно сериализовать ссылки на игроков/свойства внутри этих состояний.

        # Пример более полной сериализации (но все еще требует осторожности при загрузке):
        # if self.pending_rent:
        #      state['pending_rent'] = {
        #           'payer_idx': self.pending_rent['payer'].index,
        #           'receiver_idx': self.pending_rent['receiver'].index if isinstance(self.pending_rent['receiver'], Player) else 'bank',
        #           'amount': self.pending_rent['amount'],
        #           'reason': self.pending_rent.get('reason', '')
        #      }
        # if self.auction_state:
        #      state['auction_state'] = {
        #           'property_idx': self.auction_state['property'].index,
        #           'bidders_indices': [p.index for p in self.auction_state['bidders']],
        #           'current_bid': self.auction_state['current_bid'],
        #           'highest_bidder_idx': self.auction_state['highest_bidder'].index if self.auction_state['highest_bidder'] else None,
        #           'current_bidder_list_idx': self.auction_state['current_bidder_index'] # Индекс в списке bidders
        #      }
        # if self.pending_card_action:
        #     state['pending_card_action'] = {
        #         'type': self.pending_card_action['type'],
        #         'property_idx': self.pending_card_action['property'].index
        #     }

        return state

    def set_game_state(self, state):
        """ Восстанавливает состояние игры из данных """
        try:
            # 1. Восстанавливаем игроков (без свойств пока)
            self.players = [Player.from_dict(p_data) for p_data in state['players']]

            # 2. Восстанавливаем доску (тайлы, карты) и связываем владельцев
            self.board = GameBoard.from_dict(state['board'], self.players)

            # 3. Связываем свойства с игроками (теперь тайлы и игроки существуют)
            self._link_properties_to_players()

            # 4. Восстанавливаем остальное состояние
            self.current_player_index = state['current_player_index']
            if 0 <= self.current_player_index < len(self.players):
                 self.current_player = self.players[self.current_player_index]
            else:
                 # Ошибка в индексе, берем первого активного
                 active_players = [p for p in self.players if not p.is_bankrupt]
                 self.current_player = active_players[0] if active_players else None
                 self.current_player_index = self.players.index(self.current_player) if self.current_player else 0


            self.game_phase = state['game_phase']
            self.doubles_count = state['doubles_count']

            # Восстановление сложных состояний (если бы они сохранялись)
            self.pending_rent = None # Сброшено при сохранении
            self.auction_state = None # Сброшено при сохранении
            self.pending_card_action = None # Сброшено при сохранении

            # TODO: Реализовать восстановление pending_rent, auction_state, pending_card_action, если они сохраняются

            self.log_message.emit("Игра успешно загружена.")
            self.player_turn_changed.emit(self.current_player)
            self.force_ui_update.emit() # Обновить весь UI
            self._emit_action_needed() # Определить действия для текущего состояния
            return True

        except Exception as e:
            self.log_message.emit(f"Ошибка загрузки игры: {e}")
            print(f"Load error: {e}") # Для отладки
            # В случае ошибки лучше начать новую игру
            return False


# --- Виджет для отрисовки доски ---
class BoardWidget(QWidget):
    def __init__(self, game_manager, parent=None):
        super().__init__(parent)
        self.game_manager = game_manager
        self.setMinimumSize(600, 600)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tile_rects = {} # Словарь для хранения геометрии клеток {index: QRectF}
        self.player_positions = {} # Словарь для хранения экранных координат игроков {player_index: QPointF}

    def update_board(self):
        """ Вызывает перерисовку доски """
        self.update()

    def paintEvent(self, event):
        """ Отрисовка игрового поля """
        if not self.game_manager:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        board_size = min(self.width(), self.height())
        margin = 10
        board_rect = QRectF(margin, margin, board_size - 2 * margin, board_size - 2 * margin)

        # Рисуем фон доски (необязательно)
        painter.fillRect(self.rect(), QColor("#CDE6D0")) # Светло-зеленый фон

        # Рисуем клетки
        self._draw_tiles(painter, board_rect)

        # Рисуем фишки игроков
        self._draw_player_tokens(painter, board_rect)

        # Рисуем центр доски (логотип, карты и т.д.)
        self._draw_center(painter, board_rect)


    def _draw_tiles(self, painter, board_rect):
        """ Рисует клетки по периметру доски """
        num_tiles_side = BOARD_SIZE // 4 # 10 клеток на стороне (не считая угловых)
        corner_size = board_rect.width() * 0.15 # Размер угловой клетки
        tile_width = (board_rect.width() - 2 * corner_size) / num_tiles_side
        tile_height = corner_size # Высота боковых клеток = ширине угловых

        self.tile_rects.clear() # Очищаем перед перерисовкой

        font = painter.font()
        small_font_size = max(6, int(tile_height * 0.12)) # Динамический размер шрифта
        font.setPointSize(small_font_size)
        painter.setFont(font)
        fm = QFontMetrics(font)

        pen = QPen(Qt.GlobalColor.black, 1)
        painter.setPen(pen)

        current_x, current_y = board_rect.left(), board_rect.top()

        # Проходим по всем 40 клеткам
        for i in range(BOARD_SIZE):
            tile_data = self.game_manager.board.get_tile(i)
            rect = QRectF()

            # Определяем положение и размер клетки
            if i == 0: # Нижний правый угол (GO)
                rect = QRectF(board_rect.right() - corner_size, board_rect.bottom() - corner_size, corner_size, corner_size)
                current_x = rect.left() - tile_width
                current_y = rect.top()
            elif i < num_tiles_side + 1: # Нижняя сторона
                rect = QRectF(current_x, current_y, tile_width, tile_height)
                current_x -= tile_width
            elif i == num_tiles_side + 1: # Нижний левый угол (Jail)
                rect = QRectF(board_rect.left(), board_rect.bottom() - corner_size, corner_size, corner_size)
                current_x = rect.left()
                current_y = rect.top() - tile_width # Двигаемся вверх
            elif i < 2 * num_tiles_side + 2: # Левая сторона
                rect = QRectF(current_x, current_y, tile_height, tile_width) # Ширина=высота, Высота=ширина
                current_y -= tile_width
            elif i == 2 * num_tiles_side + 2: # Верхний левый угол (Free Parking)
                rect = QRectF(board_rect.left(), board_rect.top(), corner_size, corner_size)
                current_x = rect.right()
                current_y = rect.top()
            elif i < 3 * num_tiles_side + 3: # Верхняя сторона
                rect = QRectF(current_x, current_y, tile_width, tile_height)
                current_x += tile_width
            elif i == 3 * num_tiles_side + 3: # Верхний правый угол (Go to Jail)
                rect = QRectF(board_rect.right() - corner_size, board_rect.top(), corner_size, corner_size)
                current_x = rect.left()
                current_y = rect.bottom()
            else: # Правая сторона (i до 39)
                rect = QRectF(current_x, current_y, tile_height, tile_width) # Ширина=высота, Высота=ширина
                current_y += tile_width

            self.tile_rects[i] = rect # Сохраняем геометрию

            # Рисуем клетку
            painter.setBrush(QColor("#F2F2F7")) # Фон клетки
            painter.drawRect(rect)

            # Рисуем цветную полоску для улиц
            color = self.game_manager.board.color_map.get(tile_data.color_key, None)
            if color:
                color_strip_height = rect.height() * 0.2
                color_rect = QRectF()
                if 0 < i < num_tiles_side + 1: # Низ
                    color_rect = QRectF(rect.left(), rect.top(), rect.width(), color_strip_height)
                elif num_tiles_side + 1 < i < 2 * num_tiles_side + 2: # Лево
                     color_rect = QRectF(rect.right() - color_strip_height, rect.top(), color_strip_height, rect.height())
                elif 2 * num_tiles_side + 2 < i < 3 * num_tiles_side + 3: # Верх
                    color_rect = QRectF(rect.left(), rect.bottom() - color_strip_height, rect.width(), color_strip_height)
                elif 3 * num_tiles_side + 3 < i < BOARD_SIZE: # Право
                    color_rect = QRectF(rect.left(), rect.top(), color_strip_height, rect.height())

                if not color_rect.isNull():
                    painter.setBrush(color)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawRect(color_rect)
                    painter.setPen(pen) # Возвращаем перо

            # Рисуем текст (упрощенно, с переносом)
            text_rect = rect.adjusted(3, color_strip_height if color else 3, -3, -3) # Отступы
            # Ориентация текста
            painter.save()
            text = tile_data.name
            if tile_data.price > 0: text += f"\n${tile_data.price}"

            if num_tiles_side + 1 <= i <= 2 * num_tiles_side + 1: # Левая сторона
                 painter.translate(rect.left(), rect.bottom())
                 painter.rotate(-90)
                 text_rect = QRectF(3, 3, rect.height() - 6, rect.width() - color_strip_height - 3) # Повернутые размеры
            elif 3 * num_tiles_side + 3 <= i < BOARD_SIZE: # Правая сторона
                 painter.translate(rect.right(), rect.top())
                 painter.rotate(90)
                 text_rect = QRectF(3, color_strip_height if color else 3, rect.height() - 6, rect.width() - color_strip_height - 3) # Повернутые размеры
            else: # Верх и низ
                 painter.translate(rect.left(), rect.top())
                 text_rect = QRectF(3, color_strip_height if color else 3, rect.width() - 6, rect.height() - color_strip_height - 6)


            # Ограничиваем текст по высоте/ширине
            elided_text = fm.elidedText(text.replace("\n", " "), Qt.TextElideMode.ElideRight, int(text_rect.width() * 2)) # Примерно 2 строки
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, elided_text)

            painter.restore()

            # Рисуем дома/отели (очень упрощенно)
            if isinstance(tile_data, Street) and tile_data.num_houses > 0:
                 house_size = min(rect.width(), rect.height()) * 0.1
                 house_y = 0
                 house_x_start = 0
                 if 0 < i < num_tiles_side + 1: # Низ
                      house_y = rect.top() + color_strip_height + 1
                      house_x_start = rect.left() + 2
                 # TODO: Добавить отрисовку для других сторон

                 if house_y > 0:
                     if tile_data.num_houses == HOTEL_LEVEL: # Отель
                          painter.setBrush(Qt.GlobalColor.red)
                          painter.drawRect(QRectF(house_x_start, house_y, house_size * 2, house_size))
                     else: # Дома
                          painter.setBrush(Qt.GlobalColor.green)
                          for h in range(tile_data.num_houses):
                               painter.drawRect(QRectF(house_x_start + h * (house_size + 1), house_y, house_size, house_size))


    def _draw_player_tokens(self, painter, board_rect):
        """ Рисует фишки игроков на их клетках """
        if not self.tile_rects: return

        token_size = 10 # Размер фишки
        positions_occupied = {} # {tile_index: count}

        for player in self.game_manager.players:
            if player.is_bankrupt: continue

            tile_index = player.position
            if tile_index not in self.tile_rects: continue

            tile_rect = self.tile_rects[tile_index]
            center = tile_rect.center()

            # Смещаем фишки, если на клетке несколько игроков
            offset_index = positions_occupied.get(tile_index, 0)
            offset_x = (offset_index % 3 - 1) * (token_size * 1.2) # -1, 0, 1
            offset_y = (offset_index // 3 - 1) * (token_size * 1.2)
            positions_occupied[tile_index] = offset_index + 1

            token_pos = center + QPointF(offset_x, offset_y)
            self.player_positions[player.index] = token_pos # Сохраняем позицию

            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.setBrush(player.color)
            painter.drawEllipse(token_pos, token_size / 2, token_size / 2)

    def _draw_center(self, painter, board_rect):
         """ Рисует центральную часть доски """
         num_tiles_side = BOARD_SIZE // 4
         corner_size = board_rect.width() * 0.15
         tile_height = corner_size

         center_rect = board_rect.adjusted(corner_size, corner_size, -corner_size, -corner_size)
         painter.setBrush(QColor("#DAF0DD"))
         painter.setPen(Qt.PenStyle.NoPen)
         painter.drawRect(center_rect)

         # Placeholder для лого/карт
         painter.setPen(Qt.GlobalColor.darkGray)
         font = painter.font()
         font.setPointSize(20)
         font.setBold(True)
         painter.setFont(font)
         painter.drawText(center_rect, Qt.AlignmentFlag.AlignCenter, "МОНОПОЛИЯ")

         # Места для карт
         card_width = center_rect.width() * 0.3
         card_height = center_rect.height() * 0.2
         chance_rect = QRectF(center_rect.left() + center_rect.width() * 0.1,
                              center_rect.top() + center_rect.height() * 0.2,
                              card_width, card_height)
         chest_rect = QRectF(center_rect.right() - center_rect.width() * 0.1 - card_width,
                             center_rect.bottom() - center_rect.height() * 0.2 - card_height,
                             card_width, card_height)

         painter.setBrush(QColor("#FFA500")) # Orange for Chance
         painter.drawRect(chance_rect)
         painter.setBrush(QColor("#ADD8E6")) # LightBlue for Community Chest
         painter.drawRect(chest_rect)

         font.setPointSize(12)
         font.setBold(False)
         painter.setFont(font)
         painter.setPen(Qt.GlobalColor.black)
         painter.drawText(chance_rect, Qt.AlignmentFlag.AlignCenter, "Шанс")
         painter.drawText(chest_rect, Qt.AlignmentFlag.AlignCenter, "Казна")


# --- Виджеты экранов ---
class MainMenuWidget(QWidget):
    # Сигналы для навигации
    new_game_requested = pyqtSignal()
    load_game_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Монополия")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_new_game = QPushButton("Новая Игра")
        btn_load_game = QPushButton("Загрузить Игру")
        btn_quit = QPushButton("Выход")

        btn_new_game.setFixedWidth(200)
        btn_load_game.setFixedWidth(200)
        btn_quit.setFixedWidth(200)

        layout.addWidget(title)
        layout.addSpacing(40)
        layout.addWidget(btn_new_game, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_load_game, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(btn_quit, 0, Qt.AlignmentFlag.AlignCenter)

        # Подключения
        btn_new_game.clicked.connect(self.new_game_requested)
        btn_load_game.clicked.connect(self.load_game_requested)
        btn_quit.clicked.connect(QApplication.instance().quit)


class GameBoardWidget(QWidget):
    """ Виджет, содержащий элементы игрового экрана """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent_window = parent  # Сохраняем ссылку на родительский виджет

        # Создаем основную компоновку
        self.main_layout = QHBoxLayout(self)  # Горизонтальная компоновка

        # --- Левая панель (Информация и Лог) ---
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_panel.setFixedWidth(350)

        # Группа "Игроки"
        self.players_info_group = QGroupBox("Игроки")
        self.players_info_layout = QVBoxLayout()
        self.players_info_group.setLayout(self.players_info_layout)
        self.player_labels = []
        self.left_layout.addWidget(self.players_info_group)

        # Группа "Лог Игры"
        self.log_group = QGroupBox("Лог Игры")
        self.log_layout = QVBoxLayout(self.log_group)
        self.game_log = QTextEdit()
        self.game_log.setReadOnly(True)
        self.log_layout.addWidget(self.game_log)
        self.left_layout.addWidget(self.log_group)

        self.main_layout.addWidget(self.left_panel)

        # --- Правая панель (Доска и Управление) ---
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)

        # Виджет доски
        self.board_widget = BoardWidget(None)  # GameManager передается позже
        self.right_layout.addWidget(self.board_widget, 1)

        # Панель управления
        self.controls_group = QGroupBox("Управление")
        self.controls_layout = QHBoxLayout(self.controls_group)

        # Кнопки управления
        self.btn_save_game = QPushButton("Сохранить")  # Добавляем кнопку сохранения
        self.btn_load_game = QPushButton("Загрузить")  # Добавляем кнопку загрузки
        self.btn_main_menu = QPushButton("В меню")    # Добавляем кнопку "В меню"
        self.btn_roll_dice = QPushButton("Бросить кубики")
        self.btn_buy = QPushButton("Купить")
        self.btn_auction = QPushButton("Аукцион")  # Отказ от покупки
        self.btn_manage = QPushButton("Упр. Имущ.")
        self.btn_end_turn = QPushButton("Завершить ход")
        self.btn_pay_fine = QPushButton("Заплатить $50")
        self.btn_use_card = QPushButton("Исп. Карту")
        self.bid_input = QSpinBox()
        self.bid_input.setRange(1, 10000)
        self.bid_input.setPrefix("$ ")
        self.btn_place_bid = QPushButton("Ставка")
        self.btn_pass_bid = QPushButton("Пас")
        self.btn_declare_bankruptcy = QPushButton("Сдаться")
        self.btn_roll_for_utility = QPushButton("Бросок (Утилита)")  # Новая кнопка

        # Кнопка паузы
        self.btn_pause = QPushButton("Пауза")
        self.controls_layout.addWidget(self.btn_pause)

        # Подключаем сигнал для кнопки паузы
        self.btn_pause.clicked.connect(self.show_pause_settings)

        # Добавляем остальные кнопки
        self.controls_layout.addWidget(self.btn_save_game)  # Добавляем кнопку "Сохранить"
        self.controls_layout.addWidget(self.btn_load_game)  # Добавляем кнопку "Загрузить"
        self.controls_layout.addWidget(self.btn_main_menu)  # Добавляем кнопку "В меню"
        self.controls_layout.addWidget(self.btn_roll_dice)
        self.controls_layout.addWidget(self.btn_roll_for_utility)  # Для карты утилиты
        self.controls_layout.addWidget(self.btn_buy)
        self.controls_layout.addWidget(self.btn_auction)
        self.controls_layout.addWidget(self.btn_manage)
        self.controls_layout.addWidget(self.btn_pay_fine)
        self.controls_layout.addWidget(self.btn_use_card)
        self.controls_layout.addWidget(self.bid_input)
        self.controls_layout.addWidget(self.btn_place_bid)
        self.controls_layout.addWidget(self.btn_pass_bid)
        self.controls_layout.addWidget(self.btn_declare_bankruptcy)
        self.controls_layout.addStretch(1)

        # Кнопка завершения хода
        self.controls_layout.addWidget(self.btn_end_turn)

        self.right_layout.addWidget(self.controls_group)
        self.main_layout.addWidget(self.right_panel, 1)

    def show_pause_settings(self):
        """ Переход на экран паузы через главное окно """
        if self.parent_window:
            self.parent_window.show_pause_settings()

    def set_game_manager(self, game_manager):
        """ Передает GameManager виджету доски """
        self.board_widget.game_manager = game_manager



# --- Виджет для настройки игры ---
class GameSetupWidget(QWidget):
    # Сигнал с настройками игры
    game_start_requested = pyqtSignal(list)  # list of player configs

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Настройка Игры")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)

        self.num_players_spin = QSpinBox()
        self.num_players_spin.setRange(2, 6)  # От 2 до 6 игроков
        self.num_players_spin.setValue(2)
        self.num_players_spin.valueChanged.connect(self.update_player_inputs)
        form_layout.addRow("Количество игроков:", self.num_players_spin)

        self.player_name_inputs = []
        self.player_inputs_widget = QWidget()  # Виджет для имен игроков
        self.player_inputs_layout = QVBoxLayout(self.player_inputs_widget)
        form_layout.addRow(self.player_inputs_widget)

        self.update_player_inputs(self.num_players_spin.value())  # Создаем начальные поля

        layout.addLayout(form_layout)
        layout.addStretch(1)

        button_layout = QHBoxLayout()
        btn_back = QPushButton("Назад")
        btn_start = QPushButton("Начать Игру")
        button_layout.addWidget(btn_back)
        button_layout.addStretch(1)
        button_layout.addWidget(btn_start)
        layout.addLayout(button_layout)

        # Подключения
        btn_start.clicked.connect(self.start_game)
        # Сигнал для кнопки "Назад" должен быть подключен в главном окне

    def update_player_inputs(self, num_players):
        """ Обновляет поля для ввода имен игроков """
        # Удаляем старые поля
        for i in reversed(range(self.player_inputs_layout.count())):
            widget = self.player_inputs_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.player_name_inputs = []

        # Создаем новые поля
        for i in range(num_players):
            hbox = QHBoxLayout()
            label = QLabel(f"Имя игрока {i + 1}:")
            line_edit = QLineEdit(f"Игрок {i + 1}")
            hbox.addWidget(label)
            hbox.addWidget(line_edit)
            self.player_inputs_layout.addLayout(hbox)
            self.player_name_inputs.append(line_edit)

    

    def start_game(self):
        """ Собирает конфигурацию и отправляет сигнал """
        player_configs = []
        for i, line_edit in enumerate(self.player_name_inputs):
            name = line_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Ошибка", f"Введите имя для Игрока {i + 1}")
                return
            player_configs.append({"name": name})

        if player_configs:
            self.game_start_requested.emit(player_configs)

class MonopolyGameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Монополия (PyQt6)")
        self.setWindowState(Qt.WindowState.WindowMaximized)  # Полноэкранный режим
        self.setStyleSheet(APPLE_STYLE)

        self.game_manager = None

        # Создаем QStackedWidget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Создаем экраны
        self.main_menu_widget = MainMenuWidget()
        self.game_setup_widget = GameSetupWidget()
        self.game_board_widget = GameBoardWidget(self)  # Передаем ссылку на родительский виджет
        self.pause_settings_widget = PauseSettingsWidget(self)  # Передаем ссылку на родительский виджет

        # Добавляем экраны в QStackedWidget
        self.stacked_widget.addWidget(self.main_menu_widget)  # index 0
        self.stacked_widget.addWidget(self.game_setup_widget)  # index 1
        self.stacked_widget.addWidget(self.game_board_widget)  # index 2
        self.stacked_widget.addWidget(self.pause_settings_widget)  # index 3

        # Подключаем сигналы навигации
        self.main_menu_widget.new_game_requested.connect(self.show_game_setup)
        self.main_menu_widget.load_game_requested.connect(self.load_game)  # Загрузка из главного меню
        self.game_setup_widget.game_start_requested.connect(self.start_new_game)

        # Подключение кнопок на игровом экране
        self.game_board_widget.btn_save_game.clicked.connect(self.save_game)
        self.game_board_widget.btn_load_game.clicked.connect(self.load_game)
        self.game_board_widget.btn_main_menu.clicked.connect(self.go_to_main_menu)

        back_button = self.game_setup_widget.findChild(QPushButton, "Назад")  # Ищем по тексту (не лучший способ)
        if back_button:  # Проверка, что кнопка найдена
            back_button.clicked.connect(self.show_main_menu)
        else:
            print("Warning: Кнопка 'Назад' в настройках не найдена.")

        
        # Показываем главный экран при запуске
        self.show_main_menu()

    def load_game(self):
        """ Метод загрузки игры """
        print("Загрузка игры...")  # Добавьте отладочное сообщение
        # Здесь нужно добавить логику для загрузки сохраненной игры
        # Например, открыть диалоговое окно, выбрать файл и загрузить состояние игры

        file_path, _ = QFileDialog.getOpenFileName(self, "Загрузить игру", SAVE_DIR, "Monopoly Saves (*.msave)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    game_state = json.load(f)
                # Здесь предполагаем, что game_state содержит данные о состоянии игры
                # После загрузки создаем новый GameManager и передаем его в game_board_widget
                self.game_manager = GameManager(game_state['players'])
                self.game_board_widget.set_game_manager(self.game_manager)
                self.show_game_board()  # Переходим к игровому экрану после загрузки игры
                print(f"Игра загружена из {file_path}")
            except Exception as e:
                print(f"Ошибка загрузки игры: {e}")
                QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось загрузить игру:\n{str(e)}")

    def save_game(self):
        """ Метод для сохранения игры """
        print("Сохранение игры...")  # Отладочное сообщение
        # Логика сохранения игры
        if not self.game_manager:
            QMessageBox.warning(self, "Ошибка", "Нет активной игры для сохранения.")
            return

        # Запрос имени файла для сохранения
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить игру", "", "Monopoly Saves (*.msave)")
        if file_path:
            try:
                game_state = self.game_manager.get_game_state()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(game_state, f, indent=4, ensure_ascii=False)
                QMessageBox.information(self, "Сохранение", f"Игра сохранена в {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить игру:\n{str(e)}")

    def load_game(self):
        """ Метод для загрузки игры """
        print("Загрузка игры...")  # Отладочное сообщение
        # Логика загрузки игры
        file_path, _ = QFileDialog.getOpenFileName(self, "Загрузить игру", "", "Monopoly Saves (*.msave)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    game_state = json.load(f)
                # Восстановление состояния игры
                self.game_manager = GameManager(game_state['players'])
                self.game_board_widget.set_game_manager(self.game_manager)
                self.show_game_board()  # Переход к игровому экрану после загрузки игры
                QMessageBox.information(self, "Загрузка", f"Игра загружена из {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось загрузить игру:\n{str(e)}")

    def add_log_message(self, message):
        """ Добавляет сообщение в лог игры на игровом экране """
        self.game_board_widget.game_log.append(message)  # Добавляем сообщение в поле лога игры

    def update_ui_on_turn_change(self, player):
        """ Обновляет UI при смене хода игрока """
        # Обновляем отображение игроков
        self.update_all_player_displays()

        # Дополнительное обновление UI можно добавить здесь
        # Например, обновление информации о текущем игроке или других данных
        print(f"Смена хода! Теперь ходит игрок {player.name}")

    def show_manage_properties_dialog(self):
        """ Показывает диалог управления собственностью """
        if not self.game_manager:
            return

        player = self.game_manager.current_player  # Получаем текущего игрока
        dialog = ManagePropertiesDialog(player, self.game_manager.board, self)  # Создаем диалог
        dialog.exec()  # Показываем диалог

    def show_main_menu(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_game_setup(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_game_board(self):
        self.stacked_widget.setCurrentIndex(2)

    def show_pause_settings(self):
        """ Переход на экран паузы """
        self.stacked_widget.setCurrentIndex(3)

    def start_new_game(self, player_configs):
        """ Начинает новую игру с заданными настройками """
        try:
            if not player_configs or len(player_configs) < 2:
                raise ValueError("Необходимо минимум 2 игрока")

            # Создаем GameManager
            self.game_manager = GameManager(player_configs)
            print("GameManager создан")

            # Инициализация UI
            self.connect_game_signals()
            print("Сигналы подключены")

            self.game_board_widget.set_game_manager(self.game_manager)
            print("GameManager передан в виджет доски")

            self.initialize_player_displays_on_board()
            print("Интерфейс игроков инициализирован")

            self.show_game_board()
            print("Игровой экран показан")

            self.game_board_widget.board_widget.update_board()
            print("Доска обновлена")

            QTimer.singleShot(100, self.safe_start_turn)
        except Exception as e:
            print(f"Ошибка при запуске игры: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать игру:\n{str(e)}")
            self.show_main_menu()

    def connect_game_signals(self):
        """ Подключает сигналы GameManager к слотам UI на игровом экране """
        gm = self.game_manager
        ui = self.game_board_widget  # Используем виджет игрового экрана

        try:
            if not self.game_manager:
                raise RuntimeError("GameManager не существует")

            # Отключаем старые соединения, если они были
            try:
                gm.log_message.disconnect()
                gm.player_turn_changed.disconnect()
                gm.money_changed.disconnect()
                gm.property_changed.disconnect()
                gm.player_jailed.disconnect()
                gm.player_released.disconnect()
                gm.player_bankrupt.disconnect()
                gm.game_over.disconnect()
                gm.action_needed.disconnect()
                gm.force_ui_update.disconnect()
                gm.auction_update.disconnect()
                gm.player_moved.disconnect()
                gm.dice_rolled.disconnect()
                gm.request_human_action.disconnect()
            except TypeError:
                pass  # Сигналы еще не были подключены

            # Подключаем сигналы менеджера к слотам UI
            self.game_manager.log_message.connect(self.add_log_message)
            self.game_manager.player_turn_changed.connect(self.update_ui_on_turn_change)

            # Подключаем кнопки UI к слотам менеджера
            ui.btn_roll_dice.clicked.connect(gm.roll_dice)
            ui.btn_end_turn.clicked.connect(gm.end_turn)
            ui.btn_buy.clicked.connect(gm.buy_property)
            ui.btn_auction.clicked.connect(gm.decline_buy_property)
            ui.btn_manage.clicked.connect(self.show_manage_properties_dialog)
            ui.btn_pay_fine.clicked.connect(gm.attempt_pay_jail_fine)
            ui.btn_use_card.clicked.connect(gm.attempt_use_jail_card)
            ui.btn_place_bid.clicked.connect(lambda: gm.place_auction_bid(ui.bid_input.value()))
            ui.btn_pass_bid.clicked.connect(gm.pass_auction_bid)
            ui.btn_declare_bankruptcy.clicked.connect(gm.declare_bankruptcy_action)
            ui.btn_roll_for_utility.clicked.connect(gm.roll_for_utility_rent)

            print("Сигналы успешно подключены")
        except Exception as e:
            print(f"Ошибка подключения сигналов: {str(e)}")
            raise

    def safe_start_turn(self):
        """ Безопасный запуск первого хода с проверкой """
        try:
            if self.game_manager and not self.game_manager.players[0].is_bankrupt:
                self.game_manager._start_player_turn()
                print("Первый ход запущен")
            else:
                raise RuntimeError("Игроки не инициализированы правильно")
        except Exception as e:
            print(f"Ошибка при запуске хода: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при старте игры:\n{str(e)}")
            self.show_main_menu()

    def initialize_player_displays_on_board(self):
        """ Инициализирует отображение игроков с проверками """
        try:
            ui = self.game_board_widget

            # Очистка предыдущих элементов
            for label in ui.player_labels:
                ui.players_info_layout.removeWidget(label)
                label.deleteLater()
            ui.player_labels = []

            # Проверка наличия игроков
            if not self.game_manager or not self.game_manager.players:
                raise ValueError("Нет данных об игроках")

            # Создание новых меток
            for player in self.game_manager.players:
                label = QLabel()
                label.setWordWrap(True)
                ui.players_info_layout.addWidget(label)
                ui.player_labels.append(label)
                self.update_player_display(player)

            ui.players_info_layout.addStretch(1)
            print("Интерфейс игроков создан")

        except Exception as e:
            print(f"Ошибка инициализации игроков: {str(e)}")
            raise

    def update_player_display(self, player):
        """ Обновляет информацию для конкретного игрока на игровом экране """
        if not self.game_manager or player.index >= len(self.game_board_widget.player_labels):
            return

        label = self.game_board_widget.player_labels[player.index]
        status = ""
        font_weight = "normal"
        border_color = player.color.name()
        text_color = "black"

        if player.is_bankrupt:
            status = " [БАНКРОТ]"
            text_color = "grey"
            border_color = "grey"
        elif player.in_jail:
            status = f" [В ТЮРЬМЕ {player.jail_turns}/3]"
            text_color = "#D9480F"  # Orange
        elif player == self.game_manager.current_player:
            status = " [ХОДИТ]"
            font_weight = "bold"

        cards_text = f", 🃏x{len(player.get_out_of_jail_cards)}" if player.get_out_of_jail_cards else ""
        label.setText(f"{player.name}: ${player.money}{cards_text}{status}")
        label.setStyleSheet(f"color: {text_color}; border-left: 5px solid {border_color}; padding-left: 5px; font-weight: {font_weight};")
        self.game_board_widget.board_widget.update_board()  # Обновляем доску для фишек

    def update_player_display_from_prop(self, prop):
        """ Обновляет дисплей игрока, которому принадлежит свойство """
        if prop and prop.owner:
            self.update_player_display(prop.owner)
        self.game_board_widget.board_widget.update_board()  # Обновляем доску

    def update_all_player_displays(self):
        """ Обновляет информацию для всех игроков """
        if not self.game_manager:
            return
        for i, player in enumerate(self.game_manager.players):
            if i < len(self.game_board_widget.player_labels):
                self.update_player_display(player)
        self.game_board_widget.board_widget.update_board()  # Обновляем доску
    
    def go_to_main_menu(self):
        """ Возвращает в главное меню """
        self.stacked_widget.setCurrentIndex(0)  # Переход на главный экран

# --- Диалог управления собственностью (ManagePropertiesDialog - без изменений, предполагается здесь) ---
class ManagePropertiesDialog(QDialog):
    # Сигналы для отправки запросов в GameManager
    request_mortgage = pyqtSignal(int)
    request_unmortgage = pyqtSignal(int)
    request_build_house = pyqtSignal(int)
    request_sell_house = pyqtSignal(int)

    def __init__(self, player, board, parent=None):
        super().__init__(parent)
        self.player = player
        self.board = board
        self.setWindowTitle(f"Управление имуществом - {player.name}")
        self.setMinimumWidth(500)
        self.setStyleSheet(APPLE_STYLE) # Наследуем стиль

        self.layout = QVBoxLayout(self)

        self.property_list = QListWidget()
        self.populate_property_list()
        self.property_list.currentItemChanged.connect(self.update_buttons)
        self.layout.addWidget(self.property_list)

        self.button_layout = QHBoxLayout()
        self.btn_mortgage = QPushButton("Заложить")
        self.btn_unmortgage = QPushButton("Выкупить")
        self.btn_build = QPushButton("Построить Дом")
        self.btn_sell = QPushButton("Продать Дом")
        self.btn_close = QPushButton("Закрыть")

        self.button_layout.addWidget(self.btn_mortgage)
        self.button_layout.addWidget(self.btn_unmortgage)
        self.button_layout.addWidget(self.btn_build)
        self.button_layout.addWidget(self.btn_sell)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.btn_close)

        self.layout.addLayout(self.button_layout)

        # Подключаем кнопки
        self.btn_mortgage.clicked.connect(self.on_mortgage)
        self.btn_unmortgage.clicked.connect(self.on_unmortgage)
        self.btn_build.clicked.connect(self.on_build)
        self.btn_sell.clicked.connect(self.on_sell)
        self.btn_close.clicked.connect(self.accept)

        self.update_buttons(None) # Начальное состояние кнопок

    def populate_property_list(self):
        """ Заполняет список собственностью игрока """
        self.property_list.clear()
        for prop in sorted(self.player.properties, key=lambda p: p.index):
            item_text = f"{prop.name}"
            if isinstance(prop, Street):
                item_text += f" ({prop.color_key})" # Используем color_key
                if prop.num_houses == HOTEL_LEVEL: item_text += " [ОТЕЛЬ]"
                elif prop.num_houses > 0: item_text += f" [{prop.num_houses}Д]"
            if prop.is_mortgaged:
                item_text += " (ЗАЛОЖЕНО)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, prop.index) # Сохраняем индекс в данных элемента
            self.property_list.addItem(item)

    def get_selected_property(self):
        """ Возвращает выбранный объект Property или None """
        current_item = self.property_list.currentItem()
        if current_item:
            prop_index = current_item.data(Qt.ItemDataRole.UserRole)
            # Используем board для получения объекта по индексу
            if self.board and 0 <= prop_index < len(self.board.tiles):
                 return self.board.tiles[prop_index]
        return None


    def update_buttons(self, current_item=None): # current_item может быть None
        """ Обновляет доступность кнопок в зависимости от выбранного свойства """
        prop = self.get_selected_property()
        can_mortgage = False
        can_unmortgage = False
        can_build = False
        can_sell = False

        if prop and prop.owner == self.player:
            # Проверка возможности залога
            can_mortgage = not prop.is_mortgaged and \
                           (not isinstance(prop, Street) or prop.num_houses == 0)
            if isinstance(prop, Street) and can_mortgage:
                 # Дополнительная проверка: нельзя заложить, если есть дома в группе
                 color_group = self.board.get_properties_by_color(prop.color_key)
                 if any(p.num_houses > 0 for p in color_group):
                      can_mortgage = False

            # Проверка возможности выкупа
            can_unmortgage = prop.is_mortgaged and self.player.can_afford(int(prop.mortgage_value * (1 + MORTGAGE_INTEREST_RATE)))

            # Проверка возможности строительства/продажи (только для улиц)
            if isinstance(prop, Street):
                can_build = self.board.can_build_house(self.player, prop) and self.player.can_afford(prop.house_cost)
                can_sell = self.board.can_sell_house(self.player, prop)

        self.btn_mortgage.setEnabled(can_mortgage)
        self.btn_unmortgage.setEnabled(can_unmortgage)
        self.btn_build.setEnabled(can_build)
        self.btn_sell.setEnabled(can_sell)

        # Обновляем текст кнопок Строить/Продать
        if prop and isinstance(prop, Street):
             if prop.num_houses == MAX_HOUSES:
                  self.btn_build.setText("Построить Отель")
             else:
                  self.btn_build.setText("Построить Дом")

             if prop.num_houses == HOTEL_LEVEL:
                  self.btn_sell.setText("Продать Отель")
             else:
                  self.btn_sell.setText("Продать Дом")


    def on_mortgage(self):
        prop = self.get_selected_property()
        if prop:
            self.request_mortgage.emit(prop.index)
            # Обновляем список и кнопки ПОСЛЕ того, как GameManager обработает сигнал
            # Это лучше делать через сигнал force_ui_update или обновление по property_changed
            # Пока оставим так для простоты, но это может вызвать рассинхрон
            self.populate_property_list()
            self.update_buttons()

    def on_unmortgage(self):
        prop = self.get_selected_property()
        if prop:
            self.request_unmortgage.emit(prop.index)
            self.populate_property_list()
            self.update_buttons()

    def on_build(self):
        prop = self.get_selected_property()
        if prop:
            self.request_build_house.emit(prop.index)
            self.populate_property_list()
            self.update_buttons()

    def on_sell(self):
        prop = self.get_selected_property()
        if prop:
            self.request_sell_house.emit(prop.index)
            self.populate_property_list()
            self.update_buttons()


# --- Запуск приложения ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Убедимся, что папка для сохранений существует
    if not os.path.exists(SAVE_DIR):
        try:
            os.makedirs(SAVE_DIR)
        except OSError as e:
            print(f"Не удалось создать папку для сохранений '{SAVE_DIR}': {e}")
            # Можно показать QMessageBox пользователю

    window = MonopolyGameWindow()
    window.show()
    sys.exit(app.exec())