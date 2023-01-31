import customtkinter as ctk
import tkinter
from tkinter import messagebox, filedialog
from base_window import BaseWindowClass
import yaml


class SettingsWindow(BaseWindowClass):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Настройки')
        main_frame = MainFrame(self, self.settings)
        w = 500
        h = 500
        self.set_geometry(w, h)

        main_frame.pack()
        ctk.CTkButton(self, text='Сохранить', command=main_frame.save,
                      font=('', self.settings['font_size']), height=40).pack(pady=5, padx=5, fill=tkinter.X)


class MainFrame(ctk.CTkFrame):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings
        self.parent = parent
        self.data_base_frame = DataBaseFrame(self)
        self.data_base_frame.pack(padx=5, pady=5)
        self.folder_frame = FolderFrame(self)
        self.folder_frame.pack(padx=5, pady=5)
        self.screenshot_folder_frame = ScreenShotFrame(self)
        self.screenshot_folder_frame.pack(padx=5, pady=5)
        self.work_days_frame = WorkDaysFrame(self)
        self.work_days_frame.pack(side=tkinter.LEFT, anchor='n', padx=10)
        self.year_frame = YearFrame(self)
        self.year_frame.pack(side=tkinter.LEFT, anchor='n', padx=10)
        self.font_frame = FontFrame(self)
        self.font_frame.pack(side=tkinter.LEFT, anchor='n', padx=10)

    def save(self):
        res = {'DB': self.data_base_frame.get_data_base_path(),
               'MONTH_NAMES': ['Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь', 'Январь', 'Февраль', 'Март', 'Апрель',
                               'Май'],
               'MONTH_NUMS': [9, 10, 11, 12, 1, 2, 3, 4, 5],
               'PATH_SCREENSHOT': self.screenshot_folder_frame.get_folder_screenshot(),
               'PATH_SHEET': self.folder_frame.get_folder_sheet(),
               'WORK_DAYS': self.work_days_frame.get_work_days(),
               'YEARS': self.year_frame.get_year(),
               'font_size': self.font_frame.get_font_size()}

        with open('settings.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(res, f, allow_unicode=True)

        messagebox.showinfo(title='Настройки', message='Настройки вступят в силу после перезагрузки.')
        self.parent.destroy()


class DataBaseFrame(ctk.CTkFrame):
    def __init__(self, parent: MainFrame):
        super().__init__(parent)

        ctk.CTkLabel(self, text='Файл базы данных', font=('', parent.settings['font_size'])).pack()
        self.entry = ctk.CTkEntry(self, width=250, font=('', parent.settings['font_size']))
        self.entry.pack(side=tkinter.LEFT, padx=5, pady=3)
        self.entry.insert(0, parent.settings['DB'])
        self.entry.configure(state='readonly')
        ctk.CTkButton(self, text='Выбрать', command=self.btn_command, width=100,
                      font=('', parent.settings['font_size'])).pack(side=tkinter.RIGHT)

    def btn_command(self):
        self.entry.configure(state='normal')
        path = filedialog.askopenfilename()
        self.entry.delete(0, tkinter.END)
        self.entry.insert(0, path)
        self.entry.configure(state='readonly')

    def get_data_base_path(self):
        return self.entry.get()


class FolderFrame(ctk.CTkFrame):
    def __init__(self, parent: MainFrame):
        super().__init__(parent)

        ctk.CTkLabel(self, text='Папка ведомостей', font=('', parent.settings['font_size'])).pack()
        self.entry = ctk.CTkEntry(self, width=250, font=('', parent.settings['font_size']))
        self.entry.pack(side=tkinter.LEFT, padx=5, pady=3)
        self.entry.insert(0, parent.settings['PATH_SHEET'])
        self.entry.configure(state='readonly')
        ctk.CTkButton(self, text='Выбрать', command=self.btn_command, width=100,
                      font=('', parent.settings['font_size'])).pack(side=tkinter.RIGHT)

    def btn_command(self):
        self.entry.configure(state='normal')
        path = filedialog.askdirectory()
        self.entry.delete(0, tkinter.END)
        self.entry.insert(0, path)
        self.entry.configure(state='readonly')

    def get_folder_sheet(self):
        return self.entry.get()


class ScreenShotFrame(ctk.CTkFrame):
    def __init__(self, parent: MainFrame):
        super().__init__(parent)

        ctk.CTkLabel(self, text='Папка скриншотов', font=('', parent.settings['font_size'])).pack()
        self.entry = ctk.CTkEntry(self, width=250, font=('', parent.settings['font_size']))
        self.entry.pack(side=tkinter.LEFT, padx=5, pady=3)
        self.entry.insert(0, parent.settings['PATH_SCREENSHOT'])
        self.entry.configure(state='readonly')
        ctk.CTkButton(self, text='Выбрать', command=self.btn_command, width=100,
                      font=('', parent.settings['font_size'])).pack(side=tkinter.RIGHT)

    def btn_command(self):
        self.entry.configure(state='normal')
        path = filedialog.askdirectory()
        self.entry.delete(0, tkinter.END)
        self.entry.insert(0, path)
        self.entry.configure(state='readonly')

    def get_folder_screenshot(self):
        return self.entry.get()


class WorkDaysFrame(ctk.CTkFrame):
    def __init__(self, parent: MainFrame):
        super().__init__(parent)
        self.day_dict = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница'}
        ctk.CTkLabel(self, text=f'Рабочие дни', font=('', parent.settings['font_size'])).pack()
        self.checkboxes = [ctk.CTkCheckBox(self, text=self.day_dict[i], font=('', parent.settings['font_size'])) for i
                           in range(5)]
        [i.pack(padx=3, pady=3, anchor='w') for i in self.checkboxes]

        for day in parent.settings['WORK_DAYS']:
            self.checkboxes[day].select()

    def get_work_days(self):
        return [day for day, i in enumerate(self.checkboxes) if i.get()]


class YearFrame(ctk.CTkFrame):
    def __init__(self, parent: MainFrame):
        super().__init__(parent)
        ctk.CTkLabel(self, text=f'Учебный год', font=('', parent.settings['font_size'])).pack()
        self.entry = ctk.CTkEntry(self, width=70, font=('', parent.settings['font_size']))
        self.entry.pack(pady=20)
        self.entry.insert(0, parent.settings['YEARS'][0])

    def get_year(self):
        year = int(self.entry.get())
        return [year, year + 1]


class FontFrame(ctk.CTkFrame):
    def __init__(self, parent: MainFrame):
        super().__init__(parent)
        ctk.CTkLabel(self, text=f'Размер шрифта', font=('', parent.settings['font_size'])).pack()
        self.font_size = ctk.CTkComboBox(self, values=list(map(str, range(13, 31))), width=70,
                                         font=('', parent.settings['font_size']))
        self.font_size.pack(anchor='n', pady=20)
        self.font_size.set(parent.settings['font_size'])

    def get_font_size(self):
        return int(self.font_size.get())
