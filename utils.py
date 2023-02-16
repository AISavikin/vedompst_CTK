from typing import Union
from datetime import datetime
import os
import yaml
from calendar import Calendar, day_abbr
from database import Student, Attendance
from customtkinter.windows import widgets
import customtkinter as ctk


class Mixin:
    MONTH_NAMES = ['Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь']
    MONTH_NUMS = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    date = datetime.now()

    @staticmethod
    def get_settings():
        if not os.path.exists('settings.yaml'):
            settings = {'DB': 'database.db',
                        'PATH_SCREENSHOT': 'Скриншоты/',
                        'PATH_SHEET': 'Ведомости/',
                        'WORK_DAYS': [2, 4],
                        'YEARS': [2022, 2023],
                        'FONT_SIZE': 20,
                        'WEEKENDS': {}
                        }
            for num in Mixin.MONTH_NUMS:
                year = settings['YEARS'][0] if num in (9, 10, 11, 12) else settings['YEARS'][1]
                settings['WEEKENDS'][num] = Mixin.get_weekend(year, num)

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

    def set_geometry(self: ctk.CTk, w):
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
        work_days_without_holiday = [day[0] for day in Calendar().itermonthdays2(year, month_num) if
                                     day[0] != 0 and day[1] in self.get_settings()['WORK_DAYS']]
        holidays = self.get_settings()['WEEKENDS'][month_num]
        work_days = set(work_days_without_holiday) - set(holidays)
        return list(work_days)

    @staticmethod
    def get_weekend(year, month_num: int):
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


class CalendarVed(Mixin, ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.weekends = self.get_settings()['WEEKENDS']
        self.title('Календарь')
        self.set_geometry(400)
        self.month_index = parent.MONTH_NUMS.index(parent.date.month)
        self.day_frames = [DayFrame(self, self.get_year(mon), mon) for mon in self.MONTH_NUMS]
        self.control_frame = ControlFrame(self)
        self.control_frame.grid(row=0, sticky='n')
        self.day_frames[self.month_index].grid(row=1)


class ControlFrame(ctk.CTkFrame):

    def __init__(self, master: CalendarVed):
        super().__init__(master)

        ctk.CTkButton(self, text='<', command=lambda: self.switch_month('<'), width=30).grid(row=0, column=0, padx=3)
        self.label = ctk.CTkLabel(self, text=f'{master.date:%B}', width=100)
        self.label.grid(row=0, column=1, padx=50)
        ctk.CTkButton(self, text='>', command=lambda: self.switch_month('>'), width=30).grid(row=0, column=2, padx=3)
        self.month_names = master.MONTH_NAMES
        self.day_frames = master.day_frames
        self.month_index = master.month_index

    def switch_month(self, direction: str):
        self.day_frames[self.month_index].grid_forget()
        if direction == '>':
            if self.month_index < len(self.day_frames) - 1:
                self.month_index += 1
        else:
            if self.month_index > 0:
                self.month_index -= 1
        self.label.configure(text=self.month_names[self.month_index])
        self.day_frames[self.month_index].grid(row=1)


class DayFrame(ctk.CTkFrame):
    def __init__(self, master: CalendarVed, year, month):
        super().__init__(master)
        self.month_num = month
        self.year = year
        self.weekends = master.weekends
        self.main_frame = ctk.CTkFrame(self)
        [ctk.CTkLabel(self.main_frame, text=name).grid(row=0, column=col, padx=7) for col, name in enumerate(day_abbr)]
        self.gen_label(self.year, self.month_num)
        self.colorize_label(self.month_num)
        self.main_frame.pack()

    def gen_label(self, year, month):
        self.labels = []
        days = [i for i in Calendar().itermonthdays(year, month)]
        row = len(days) // 7
        day = 0
        for i in range(row):
            for j in range(7):
                if days[day] == 0:
                    day += 1
                    continue
                label = ctk.CTkLabel(self.main_frame, text=str(days[day]), width=40)
                label.grid(row=i + 1, column=j, padx=7)
                self.labels.append(label)
                day += 1

    def colorize_label(self, month):
        for day in self.weekends[month]:
            self.labels[day - 1].configure(text_color='red')


class Node:
    def __init__(self, element):
        self.prev_node = None
        self.next_node = None
        self.element = element
        self.state = element.cget('state')


class CustomFocus:
    def __init__(self, elements):
        self.start_node = None
        self.focus_node = None
        self.btns = []
        self.setup(elements)
        self.start_focus()

    def set(self):
        [i.configure(fg_color='#1f538d') for i in self.btns]
        self.focus_node.element.focus()
        if type(self.focus_node.element) == widgets.CTkButton:
            self.focus_node.element.configure(fg_color='#08359D')

    def setup(self, elements: list[widgets]):
        for i in elements:
            self.add_node(i)
            if type(i) == widgets.CTkButton:
                self.btns.append(i)

    def start_focus(self):
        node = self.start_node
        while node.state == 'disabled':
            node = node.next_node
        self.focus_node = node

    def next(self):
        node = cur = self.focus_node
        if node.next_node:
            while node.next_node.state == 'disabled':
                node = node.next_node
                if node.next_node is None:
                    break
            node = node.next_node
            self.focus_node = node
        if node is None:
            self.focus_node = cur

    def prev(self):
        node = cur = self.focus_node
        if node.prev_node:
            while node.prev_node.state == 'disabled':
                node = node.prev_node
                if node.prev_node is None:
                    break
            node = node.prev_node
            self.focus_node = node
        if node is None:
            self.focus_node = cur

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
