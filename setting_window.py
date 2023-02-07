import customtkinter as ctk
from tkinter import filedialog, LEFT, RIGHT, END, messagebox
from utils import *
import yaml


class SettingsWindow(Mixin, ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Настройки')
        w = 500
        self.set_geometry(w)
        self.font = parent.font
        self.settings = self.get_settings()
        self.data_base_frame = DataBaseFrame(self)
        self.data_base_frame.grid(padx=5, pady=5, columnspan=3, row=0)
        self.folder_frame = FolderFrame(self, 'sheet')
        self.folder_frame.grid(padx=5, pady=5, columnspan=3, row=1)
        self.screenshot_folder_frame = FolderFrame(self, 'screenshot')
        self.screenshot_folder_frame.grid(padx=5, pady=5, columnspan=3, row=2)
        self.work_days_frame = WorkDaysFrame(self)
        self.work_days_frame.grid(row=3, column=0, sticky='n', padx=10)
        self.year_frame = YearFrame(self)
        self.year_frame.grid(row=3, column=1, sticky='n', padx=10)
        self.font_frame = FontFrame(self)
        self.font_frame.grid(row=3, column=2, sticky='n', padx=10)
        ctk.CTkButton(self, text='Обновить выходные', command=self.update_weekends,
                      font=self.font, height=40).grid(pady=5, padx=5, sticky='nesw', row=4, columnspan=3)
        ctk.CTkButton(self, text='Сохранить', command=self.save,
                      font=self.font, height=40).grid(pady=5, padx=5, sticky='nesw', row=5, columnspan=3)

    def save(self):
        settings = {'DB': self.data_base_frame.get_data_base_path(),
                    'PATH_SCREENSHOT': self.screenshot_folder_frame.get_folder(),
                    'PATH_SHEET': self.folder_frame.get_folder(),
                    'WORK_DAYS': self.work_days_frame.get_nums_work_days(),
                    'YEARS': self.year_frame.get_year(),
                    'FONT_SIZE': self.font_frame.get_font_size(),
                    'WEEKENDS': self.settings['WEEKENDS']}

        with open('settings.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(settings, f, allow_unicode=True)
        if self.settings['FONT_SIZE'] != settings['FONT_SIZE']:
            messagebox.showinfo(title='Настройки', message='Настройки вступят в силу после перезагрузки.')
        self.destroy()

    def update_weekends(self):
        for month_num in self.MONTH_NUMS:
            year = self.get_year(month_num)
            url = f'https://isdayoff.ru/api/getdata?year={year}&month={month_num:02}&delimeter=.'
            try:
                response = requests.get(url)
            except ConnectionError:
                messagebox.showerror(title='Ошибка соединения', message='Не удалось получить данные с сервера')
                return
            if response.status_code != 200:
                messagebox.showerror(title='Ошибка сервера', message=f'Код ошибки {response.status_code}'
                                                                     f'\nНе удалось получить данные с сервера')
                return
            self.settings['WEEKENDS'][month_num] = [day for day, i in enumerate(response.text.split('.'), 1) if i == '1']
        messagebox.showinfo(title='Успешно!', message='Данные о выходных успешно обновлены!')

class DataBaseFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text='Файл базы данных', font=parent.font).pack()
        self.entry = ctk.CTkEntry(self, width=250, font=parent.font)
        self.entry.pack(side=LEFT, padx=5, pady=3)
        self.entry.insert(0, parent.settings['DB'])
        self.entry.configure(state='readonly')
        ctk.CTkButton(self, text='Выбрать', command=self.btn_command, width=100, font=parent.font).pack(side=RIGHT)

    def btn_command(self):
        self.entry.configure(state='normal')
        path = filedialog.askopenfilename()
        if not path:
            return
        self.entry.delete(0, END)
        self.entry.insert(0, path)
        self.entry.configure(state='readonly')

    def get_data_base_path(self):
        return self.entry.get()


class FolderFrame(ctk.CTkFrame):
    def __init__(self, parent, typ: str):
        super().__init__(parent)
        if typ == 'sheet':
            text = 'Папка ведомостей'
            path = parent.settings['PATH_SHEET']
        else:
            text = 'Папка скриншотов'
            path = parent.settings['PATH_SCREENSHOT']

        ctk.CTkLabel(self, text=text, font=parent.font).pack()
        self.entry = ctk.CTkEntry(self, width=250, font=parent.font)
        self.entry.pack(side=LEFT, padx=5, pady=3)
        self.entry.insert(0, path)
        self.entry.configure(state='readonly')
        ctk.CTkButton(self, text='Выбрать', command=self.btn_command, width=100,
                      font=parent.font).pack(side=RIGHT)

    def btn_command(self):
        self.entry.configure(state='normal')
        path = filedialog.askdirectory()
        if not path:
            return
        self.entry.delete(0, END)
        self.entry.insert(0, path)
        self.entry.configure(state='readonly')

    def get_folder(self):
        folder = self.entry.get()
        if folder.endswith('/'):
            return folder
        return folder + '/'


class WorkDaysFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.day_dict = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница'}
        ctk.CTkLabel(self, text=f'Рабочие дни', font=parent.font).pack()
        self.checkboxes = [ctk.CTkCheckBox(self, text=self.day_dict[i], font=parent.font) for i in range(5)]
        [i.pack(padx=3, pady=3, anchor='w') for i in self.checkboxes]

        for day in parent.settings['WORK_DAYS']:
            self.checkboxes[day].select()

    def get_nums_work_days(self):
        return [day for day, i in enumerate(self.checkboxes) if i.get()]


class YearFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text=f'Учебный год', font=parent.font).pack()
        self.entry = ctk.CTkEntry(self, width=70, font=parent.font)
        self.entry.pack(pady=20)
        self.entry.insert(0, parent.settings['YEARS'][0])

    def get_year(self):
        year = int(self.entry.get())
        return [year, year + 1]


class FontFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text=f'Размер шрифта', font=parent.font).pack()
        self.font_size = ctk.CTkComboBox(self, values=list(map(str, range(13, 31))), width=70,
                                         font=parent.font)
        self.font_size.pack(anchor='n', pady=20)
        self.font_size.set(parent.settings['FONT_SIZE'])

    def get_font_size(self):
        return int(self.font_size.get())
