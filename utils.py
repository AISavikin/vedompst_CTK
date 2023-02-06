from typing import Union
from datetime import datetime
import os
import yaml
from calendar import Calendar
from database import Student, Attendance
from customtkinter.windows import widgets


class Mixin:
    MONTH_NAMES = ['Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май']
    MONTH_NUMS = [9, 10, 11, 12, 1, 2, 3, 4, 5]
    date = datetime.now()

    @staticmethod
    def get_settings():
        if not os.path.exists('settings.yaml'):
            settings = {'DB': 'database.db',
                        'PATH_SCREENSHOT': 'Скриншоты/',
                        'PATH_SHEET': 'Ведомости/',
                        'WORK_DAYS': [2, 4],
                        'YEARS': [2022, 2023],
                        'FONT_SIZE': 20}

            with open('settings.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(settings, f, allow_unicode=True)
        with open('settings.yaml', encoding='utf-8') as f:
            settings = yaml.safe_load(f)
        return settings

    @staticmethod
    def get_window_size(window):
        w, h = map(int, window.geometry().split('+')[0].split('x'))
        x, y = map(int, window.geometry().split('+')[1:])
        return w, h, x, y

    def set_geometry(self, w):
        w_screen = self.winfo_screenwidth()
        self.geometry(f'+{w_screen // 2 - w // 2}+30')

    def get_month_num(self, month: str):
        return self.MONTH_NUMS[self.MONTH_NAMES.index(month)]

    def get_year(self, month_num: int):
        year = self.get_settings()['YEARS']
        return year[0] if month_num in (9, 10, 11, 12) else year[1]

    def get_work_days(self, month: str):
        month_num = self.get_month_num(month)
        year = self.get_year(month_num)
        return [day[0] for day in Calendar().itermonthdays2(year, month_num) if
                day[0] != 0 and day[1] in self.get_settings()['WORK_DAYS']]

    def get_weekend(self, month_num: int):
        year = self.get_year(month_num)
        return [day[0] for day in Calendar().itermonthdays2(year, month_num) if day[0] != 0 and day[1] in (5, 6)]

    @staticmethod
    def get_absents_from_db(kids: list[Student], day: Union[int, str], month_num: Union[int, str],
                            year: Union[int, str]):
        absents = []
        for kid in kids:
            tmp = ''
            for i in Attendance.filter(student_id=kid.id, day=day, month=month_num, year=year):
                tmp = i.absent
            absents.append(tmp)
        return absents


class Node:
    def __init__(self, element):
        self.focus = False
        self.prev_node = None
        self.next_node = None
        self.element = element
        self.state = element.cget('state')


class CustomFocus:
    def __init__(self, elements):
        self.start_node = None
        self.elements = elements
        self.setup()

    def set(self):
        [i.configure(fg_color='#1f538d') for i in self.btns]
        self.focus_element.focus()
        if type(self.focus_element) == widgets.CTkButton:
            self.focus_element.configure(fg_color='#08359D')

    def setup(self):
        self.btns = []
        for i in self.elements:
            self.add_node(i)
            if type(i) == widgets.CTkButton:
                self.btns.append(i)
        self.focus_element = self.start_node.element

    def find_focus(self):
        node = self.start_node
        while not node.focus:
            node = node.next_node
        return node

    def next(self):
        node = self.find_focus()
        if node.next_node:
            node.focus = False
            while node.next_node.state == 'disabled':
                node = node.next_node
            node.next_node.focus = True
            self.focus_element = self.find_focus().element

    def prev(self):
        node = self.find_focus()
        if node.prev_node:
            node.focus = False
            while node.prev_node.state == 'disabled':
                node = node.prev_node
            node.prev_node.focus = True
            self.focus_element = self.find_focus().element

    def add_node(self, element):
        new_node = Node(element)
        if self.start_node is None:
            self.start_node = new_node
            self.start_node.focus = True
            return
        n = self.start_node
        while n.next_node is not None:
            n = n.next_node
        n.next_node = new_node
        new_node.prev_node = n
