import customtkinter as ctk
from calendar import Calendar
from datetime import datetime
import yaml

with open('settings.yaml', encoding='utf-8') as f:
    settings = yaml.safe_load(f)

class BaseWindowClass(ctk.CTkToplevel):
    settings = settings
    MONTH_NAMES = settings['MONTH_NAMES']
    MONTH_NUMS = settings['MONTH_NUMS']
    YEARS = settings['YEARS']
    WORK_DAYS = settings['WORK_DAYS']
    PATH_SHEET = settings['PATH_SHEET']
    PATH_SCREENSHOT = settings['PATH_SCREENSHOT']

    def __init__(self, parent):
        super().__init__(parent)
        self.w_screen = self.winfo_screenwidth()
        self.h_screen = self.winfo_screenheight()
        self.date_now = datetime.now()
        self.font = ctk.CTkFont(family='Times New Roman', size=settings['font_size'])

    def set_geometry(self, w, h):
        self.geometry(f'+{self.w_screen // 2 - w // 2}+30')

    def get_work_days(self, month: str):
        month_num = self.get_month_num(month)
        year = self.get_year(month_num)
        return [day[0] for day in Calendar().itermonthdays2(year, month_num) if
                day[0] != 0 and day[1] in self.WORK_DAYS]

    @classmethod
    def get_year(cls, month_num: int) -> int:
        return cls.YEARS[0] if month_num in (9, 10, 11, 12) else cls.YEARS[1]

    @classmethod
    def get_month_num(cls, month: str) -> int:
        index = cls.MONTH_NAMES.index(month)
        return cls.MONTH_NUMS[index]

    @classmethod
    def get_weekend(cls, month_num: int):
        year = cls.get_year(month_num)
        return [day[0] for day in Calendar().itermonthdays2(year, month_num) if day[0] != 0 and day[1] in (5, 6)]

