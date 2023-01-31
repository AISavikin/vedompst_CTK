# import pip
import os
import yaml

def create_settings():
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

create_settings()
# pip.main(['install', '-r', 'requirements.txt'])
os.system('python -m pip install -r requirements.txt')