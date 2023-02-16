import customtkinter as ctk
from tkinter import messagebox, LEFT, RIGHT, X
from database import create_database
from utils import *
from kids_window import KidsWindow
from mark_kids_window import MarkKidsWindow
from sheet_window import SheetWindow
from setting_window import SettingsWindow
from PIL import Image
import locale

locale.setlocale(locale.LC_TIME, 'RU')


class MainWindow(Mixin, ctk.CTk):

    def __init__(self):
        super().__init__()
        # Настройка окна
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")
        w = 300
        self.set_geometry(w)
        font_size = self.get_settings()['FONT_SIZE']
        self.font = ctk.CTkFont(family='Times New Roman', size=font_size)
        self.title("Ведомости")

        self.main_frame = MainFrame(self)
        self.main_frame.pack()

    def get_group(self):
        group = self.main_frame.get_group()
        if group == 'Пусто':
            messagebox.showerror(title='Ошибка', message='База данных пуста!')
            return
        return group

    def open_toplevel(self, window):
        self.withdraw()
        window.grab_set()
        window.wait_window()
        self.deiconify()

    def kids_window(self, group=None):
        if group is None:
            group = self.main_frame.get_group()
        window = KidsWindow(self, group)
        self.open_toplevel(window)

    def add_group(self):
        group = AddGroup(self).open()
        if not group:
            return
        if not group.isdigit():
            messagebox.showerror(message="Только цифры!")
            return
        self.kids_window(group)
        self.main_frame.refresh_groups()

    def mark_kids_window(self):
        group = self.get_group()
        if not group:
            return
        month = self.main_frame.get_month()
        window = MarkKidsWindow(self, group, month)
        self.open_toplevel(window)

    def sheet_window(self):
        group = self.get_group()
        if not group:
            return
        month = self.main_frame.get_month()
        window = SheetWindow(self, group, month)
        self.open_toplevel(window)

    def calendar_window(self):
        window = CalendarVed(self)

    def settings_window(self):
        window = SettingsWindow(self)
        self.open_toplevel(window)


class AddGroup(ctk.CTkToplevel):
    def __init__(self, parent: MainWindow):
        super().__init__(parent)
        self.group = ctk.StringVar()
        w, h, x, y = parent.get_window_size(parent)
        self.geometry(f'180x120+{x + w // 4}+{y + h // 4}')
        ctk.CTkLabel(self, text='Номер группы', font=parent.font).pack(pady=5, padx=5)
        ctk.CTkEntry(self, textvariable=self.group, font=parent.font).pack(pady=5, padx=5)
        ctk.CTkButton(self, text="Ok", command=self.destroy, font=parent.font).pack(padx=10, pady=5)
        self.bind('<Return>', self.custom_destroy)

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.group.get()

    def custom_destroy(self, *args):
        self.destroy()


class MainFrame(ctk.CTkFrame):

    def __init__(self, master: MainWindow):
        super().__init__(master)
        # Переменные
        self.master: MainWindow = master
        self.font = master.font
        img_settings = ctk.CTkImage(dark_image=Image.open('icons/settings.png'))
        img_calendar = ctk.CTkImage(dark_image=Image.open('icons/calendar.png'))
        # фреймы
        combo_frame = ctk.CTkFrame(self)
        label_frame = ctk.CTkFrame(self)
        # Элементы
        label = ctk.CTkLabel(label_frame, text='Ведомости детский сад')
        btn_settings = ctk.CTkButton(label_frame, image=img_settings, text='', width=30, command=master.settings_window)
        btn_calendar = ctk.CTkButton(label_frame, image=img_calendar, text='', width=30, command=master.calendar_window)
        btn_add_group = ctk.CTkButton(self, text='Добавить группу', command=master.add_group)
        btn_kids = ctk.CTkButton(self, text='Ученики', command=master.kids_window)
        btn_mark = ctk.CTkButton(self, text='Отметить', command=master.mark_kids_window)
        btn_sheet = ctk.CTkButton(self, text='Ведомости', command=master.sheet_window)
        self.cmb_month = ctk.CTkComboBox(combo_frame, values=master.MONTH_NAMES)
        self.cmb_group = ctk.CTkComboBox(combo_frame, values=["Пусто"])
        # Упаковка label_frame
        label.pack(side=LEFT, padx=5)
        btn_calendar.pack(side=RIGHT, padx=5)
        btn_settings.pack(side=RIGHT, padx=5)
        # Упаковка combo_frame
        self.cmb_group.pack(side=LEFT, padx=3)
        self.cmb_month.pack(side=RIGHT, padx=3)

        self.elements_for_pack = [label_frame, btn_add_group, btn_kids, combo_frame, btn_mark, btn_sheet]
        self.elements_for_configure = [label, btn_add_group, btn_kids, self.cmb_month,
                                       self.cmb_group, btn_mark, btn_sheet]
        self.pack_elements()
        self.configure_elements()
        self.refresh_groups()

    def configure_elements(self):
        for element in self.elements_for_configure:
            element.configure(font=self.font)
        month_index = self.master.MONTH_NUMS.index(self.master.date.month)
        self.cmb_month.set(self.master.MONTH_NAMES[month_index])

    def pack_elements(self):
        for element in self.elements_for_pack:
            element.pack(fill=X, padx=3, pady=3, ipady=4)

    def refresh_groups(self):
        groups = [f'Группа {num}' for num in set(i.group for i in Student.select())]
        self.cmb_group.configure(values=groups)
        if groups:
            self.cmb_group.set(groups[0])

    def get_group(self):
        return self.cmb_group.get().split()[-1]

    def get_month(self):
        return self.cmb_month.get()


if __name__ == '__main__':
    create_database()
    MainWindow().mainloop()
