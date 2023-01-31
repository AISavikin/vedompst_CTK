from main_window import MainWindow
from database import create_database

if __name__ == '__main__':
    create_database()
    MainWindow().mainloop()