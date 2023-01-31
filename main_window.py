import customtkinter as ctk
import tkinter
from tkinter import messagebox
from database import Student
from kids_window import KidsWindow
from mark_kids_window import MarkKidsWindow
from sheet_window import SheetWindow
from datetime import datetime
from database import create_database
from PIL import Image

class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()
        # Настройка окна
        ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("dark-blue")
        w = 300
        h = 250
        self.w_screen = self.winfo_screenwidth()
        self.h_screen = self.winfo_screenheight()
        self.geometry(f'+{self.w_screen // 2 - w // 2}+{self.h_screen // 2 - h // 2}')
        self.font = ctk.CTkFont(family='Times New Roman', size=20)

        self.title("Ведомости")
        self.main_frame = MainFrame(self)
        self.main_frame.pack()
        self.update_idletasks()

    def kids(self, group=None):
        self.withdraw()
        if group is None:
            group = self.main_frame.get_group()
        window = KidsWindow(self, group)
        window.grab_set()
        window.wait_window()
        groups = [f'Группа {num}' for num in set(i.group for i in Student.select())]
        self.main_frame.combo_frame.cmb_group.configure(values=groups)
        self.deiconify()

    def add_group(self):
        group = AddGroup(self).open()
        if not group:
            return
        if not group.isdigit():
            messagebox.showerror(message="Только цифры!")
            return
        self.kids(group)

    def mark_kids(self):
        self.withdraw()
        group = self.main_frame.get_group()
        month = self.main_frame.get_month()
        window = MarkKidsWindow(self, group, month)
        window.grab_set()
        window.wait_window()
        self.deiconify()

    def sheet(self):
        self.withdraw()
        group = self.main_frame.get_group()
        month = self.main_frame.get_month()
        window = SheetWindow(self, group, month)
        window.grab_set()
        window.wait_window()
        self.deiconify()


class AddGroup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.group = ctk.StringVar()
        self.geometry(f'180x120+{parent.winfo_screenwidth() // 2}+{parent.winfo_screenheight() // 2}')
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
        self.font = master.font
        self.combo_frame = ComboFrame(self)

        label_frame = ctk.CTkFrame(self)
        img = ctk.CTkImage(dark_image=Image.open('settings.png'))
        ctk.CTkLabel(label_frame, text='Ведомости детский сад', font=self.font).pack(side=tkinter.LEFT, padx=30)
        ctk.CTkButton(label_frame, image=img, text='', width=30).pack(side=tkinter.RIGHT, padx=5)
        label_frame.pack(pady=3, ipady=4, fill=tkinter.X)

        ctk.CTkButton(self, text='Добавить группу',
                      font=self.font, command=master.add_group).pack(fill=tkinter.X, padx=3, pady=3, ipady=4)
        ctk.CTkButton(self, text='Ученики', font=self.font,
                      command=master.kids).pack(fill=tkinter.X, padx=3, pady=3, ipady=4)
        self.combo_frame.pack(pady=4)

        ctk.CTkButton(self, text='Отметить', font=self.font,
                      command=master.mark_kids).pack(fill=tkinter.X, padx=3, pady=3, ipady=4)
        ctk.CTkButton(self, text='Ведомости', font=self.font, command=master.sheet).pack(fill=tkinter.X, padx=3, pady=3, ipady=4)

    def get_group(self):
        return self.combo_frame.cmb_group.get().split()[-1]

    def get_month(self):
        return self.combo_frame.cmb_month.get()


class MainFrame1(ctk.CTkFrame):

    def __init__(self, master: MainWindow):
        super().__init__(master)
        self.font = master.font
        self.combo_frame = ComboFrame(self)
        ctk.CTkLabel(self, text='Ведомости детский сад',
                     font=self.font).pack(pady=3, ipady=4)
        ctk.CTkButton(self, text='Добавить группу',
                      font=self.font, command=master.add_group).pack(fill=tkinter.X, padx=3, pady=3, ipady=4)
        ctk.CTkButton(self, text='Ученики', font=self.font,
                      command=master.kids).pack(fill=tkinter.X, padx=3, pady=3, ipady=4)
        self.combo_frame.pack(pady=4)

        ctk.CTkButton(self, text='Отметить', font=self.font,
                      command=master.mark_kids).pack(fill=tkinter.X, padx=3, pady=3, ipady=4)
        ctk.CTkButton(self, text='Ведомости', font=self.font,
                      command=master.sheet).pack(fill=tkinter.X, padx=3, pady=3, ipady=4)

    def get_group(self):
        return self.combo_frame.cmb_group.get().split()[-1]

    def get_month(self):
        return self.combo_frame.cmb_month.get()


class ComboFrame(ctk.CTkFrame):
    def __init__(self, master: MainFrame):
        super().__init__(master)
        self.font = master.font
        groups = [f'Группа {num}' for num in set(i.group for i in Student.select())]
        self.MONTH_NAMES = ('Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май')
        self.MONTH_NUMS = (9, 10, 11, 12, 1, 2, 3, 4, 5)
        self.cmb_month = ctk.CTkComboBox(self, values=[i for i in self.MONTH_NAMES], font=self.font)
        self.cmb_month.set(self.get_month_now())
        self.cmb_group = ctk.CTkComboBox(self, values=groups if groups else ['Пусто'], font=self.font)
        self.cmb_group.pack(side=tkinter.LEFT, padx=3)
        self.cmb_month.pack(side=tkinter.LEFT, padx=3)

    def get_month_now(self):
        month_index = self.MONTH_NUMS.index(datetime.now().month)
        return self.MONTH_NAMES[month_index]


if __name__ == '__main__':
    create_database()
    MainWindow().mainloop()
    # test()
