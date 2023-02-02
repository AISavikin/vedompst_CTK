import os
import yaml

if not os.path.exists('settings.yaml'):
    res = {'DB': 'database.db',
           'MONTH_NAMES': ['Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь', 'Январь', 'Февраль', 'Март', 'Апрель',
                           'Май'],
           'MONTH_NUMS': [9, 10, 11, 12, 1, 2, 3, 4, 5],
           'PATH_SCREENSHOT': 'Скриншоты/',
           'PATH_SHEET': 'Ведомости/',
           'WORK_DAYS': [2, 4],
           'YEARS': [2022, 2023],
           'font_size': 20}

    with open('settings.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(res, f, allow_unicode=True)

from main_window import MainWindow
from database import create_database

if __name__ == '__main__':
    create_database()
    MainWindow().mainloop()
