import customtkinter as ctk
from calendar import Calendar
from datetime import datetime

# TODO Доставать переменные из ini
from conf import *


class BaseWindowClass(ctk.CTkToplevel):
    MONTH_NAMES = MONTH_NAMES
    MONTH_NUMS = MONTH_NUMS
    YEARS = YEARS
    WORK_DAYS = WORK_DAYS

    def __init__(self, parent):
        super().__init__(parent)
        self.w_screen = self.winfo_screenwidth()
        self.h_screen = self.winfo_screenheight()
        self.date_now = datetime.now()
        self.font = ctk.CTkFont(family='Times New Roman', size=20)

    def set_geometry(self, w, h):
        self.geometry(f'{w}x{h}+{self.w_screen // 2 - w // 2}+{self.h_screen // 2 - h // 2}')

    def get_work_days(self, month: str):
        month_num = self.get_month_num(month)
        year = self.get_year(month_num)
        return [str(day[0]) for day in Calendar().itermonthdays2(year, month_num) if
                day[0] != 0 and day[1] in WORK_DAYS]

    @classmethod
    def get_year(cls, month_num: int) -> int:
        return cls.YEARS[0] if month_num in (9, 10, 11, 12) else cls.YEARS[1]

    @classmethod
    def get_month_num(cls, month: str) -> int:
        index = cls.MONTH_NAMES.index(month)
        return cls.MONTH_NUMS[index]

    @staticmethod
    def get_month_now():
        month_index = MONTH_NUMS.index(datetime.now().month)
        return MONTH_NAMES[month_index]
