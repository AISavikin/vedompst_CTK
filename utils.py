from datetime import datetime
import os
import yaml

class Mixin:
    MONTH_NAMES = ['Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май']
    MONTH_NUMS = [9, 10, 11, 12, 1, 2, 3, 4, 5]
    date = datetime.now()

    def get_settings(self):
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

    def get_window_size(self):
        return self.geometry()

    def set_geometry(self, w):
        w_screen = self.winfo_screenwidth()
        self.geometry(f'+{w_screen // 2 - w // 2}+30')
