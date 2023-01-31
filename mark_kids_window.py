from typing import Union
import customtkinter as ctk
import tkinter
from tkinter import messagebox
from database import Student, Attendance
from base_window import BaseWindowClass
import os
from PIL import ImageGrab

class MarkKidsWindow(BaseWindowClass):
    def __init__(self, parent: ctk.CTk, group: str, month):
        super().__init__(parent)
        self.group = group
        self.month = month
        self.month_num = self.get_month_num(month)
        self.year = self.get_year(self.month_num)
        # Настройка окна
        self.title("Отметить")
        w = 255
        h = 385
        self.set_geometry(w, h)
        self.kids = [student for student in Student.select().where(Student.group == self.group).order_by(Student.name)]

        self.info_frame = InfoFrame(self)
        self.kids_frame = KidsFrame(self)

        self.info_frame.pack(padx=10)
        self.kids_frame.pack(pady=10, padx=15)
        ctk.CTkButton(self, text='Отметить', command=self.mark_kids, font=self.font).pack(pady=10)

        self.day = self.info_frame.get_date()
        self.paste_absents(self.day)

        self.bind('<Down>', self.kids_frame.foc)
        self.bind('<Up>', self.kids_frame.foc)
        self.bind('<Left>', self.kids_frame.foc)
        self.bind('<Right>', self.kids_frame.foc)
        self.bind('<Return>', self.mark_kids)

    @staticmethod
    def get_absents_from_db(kids: list[Student], day: Union[int, str], month_num: Union[int, str],
                            year: Union[int, str]):
        absents = []
        for kid in kids:
            tmp = ''
            for i in Attendance.filter(student_id=kid.id, day=day, month=month_num, year=year):
                tmp = i.absent
            absents.append(tmp)
        return absents

    def paste_absents(self, day):
        absents = self.get_absents_from_db(self.kids, day, self.month_num, self.year)
        for i, entry in enumerate(self.kids_frame.entrys):
            if absents[i]:
                entry.configure(state='normal')
            entry.delete(0, tkinter.END)
            entry.insert(0, absents[i])

    def mark_kids(self, *event):
        absents = self.kids_frame.get_absents()

        if not all(absents):
            confirm = messagebox.askyesno(title='Вы уверены?', message='Вы отметили не всех! Сохранить?')
            if not confirm:
                return

        month_index = self.MONTH_NAMES.index(self.month)
        month_num = self.MONTH_NUMS[month_index]
        year = self.YEARS[0] if month_index < 4 else self.YEARS[1]
        day = self.info_frame.get_date()
        for indx, kid in enumerate(self.kids):
            attendance = Attendance.select().filter(day=day, student_id=kid.id, year=year, month=month_num)
            if not len(attendance):
                Attendance.create(absent=absents[indx], day=day, month=month_num, year=year, student_id=kid.id)
            else:
                Attendance.update({Attendance.absent: absents[indx]}).where(Attendance.id == attendance[0].id).execute()
        self.make_screenshot()
        self.destroy()

    def make_screenshot(self):
        if not os.path.exists(self.PATH_SCREENSHOT):
            os.mkdir(self.PATH_SCREENSHOT)
        otx, oty = map(int, self.geometry().split('+')[1:])
        width = int(self.geometry().split('x')[0]) + 10
        height = int(self.geometry().split('+')[0].split('x')[1]) + 30
        scr = ImageGrab.grab(bbox=(otx, oty, otx + width, oty + height))
        path = f'{self.PATH_SCREENSHOT}{self.group}_{self.month}_{self.day}.jpeg'
        if os.path.exists(path):
            if not messagebox.askyesno(title='Внимание!',
                                       message='Скриншот с отмеченными учениками уже существует! Перезаписать?'):
                return
        scr.save(path)


class InfoFrame(ctk.CTkFrame):
    def __init__(self, master: MarkKidsWindow):
        super().__init__(master)
        work_days = [str(i) for i in master.get_work_days(master.month)]
        self.date = ctk.StringVar()

        cmb_frame = ctk.CTkFrame(self)
        ctk.CTkLabel(cmb_frame, text='Число', font=master.font).pack(side=tkinter.LEFT)
        self.cmb_date = ctk.CTkComboBox(cmb_frame, values=work_days, state='readonly', variable=self.date, width=70,
                                        font=master.font, command=master.paste_absents)
        self.cmb_date.pack(side=tkinter.LEFT, padx=10)
        ctk.CTkLabel(cmb_frame, text=f'{master.month}', font=master.font).pack(side=tkinter.LEFT)
        self.date.set(f'{master.date_now: %d}')
        ctk.CTkLabel(self, text=f'Группа {master.group}', font=master.font).pack(pady=10)
        cmb_frame.pack(pady=10)

    def get_date(self):
        return self.date.get().strip()


class KidsFrame(ctk.CTkFrame):
    def __init__(self, master: MarkKidsWindow):
        super().__init__(master)
        self.entrys = []

        for ind, kid in enumerate(master.kids):
            label = ctk.CTkLabel(self, text=f'{kid.name}', font=master.font)
            label.grid(row=ind, column=0, sticky='w')
            entry = ctk.CTkEntry(self, width=28, font=master.font)
            entry.grid(row=ind, column=1, sticky='e', padx=10, pady=3)
            if not kid.active:
                entry.insert(0, 'н')
                entry.configure(state='disabled', text_color='#4a83b2')
                label.configure(text_color='#4a83b2')
            self.entrys.append(entry)

    def get_absents(self):
        return [i.get() for i in self.entrys]

    def foc(self, event):
        if type(self.focus_get()) == MarkKidsWindow:
            self.entrys[0].focus()
            return
        now_focus = self.focus_get()
        prev_focus = now_focus.tk_focusPrev()
        next_focus = now_focus.tk_focusNext()

        if event.keycode == 40:
            next_focus.focus()
        if event.keycode == 38:
            prev_focus.focus()
        if event.keycode == 37:
            now_focus.delete(0, tkinter.END)
            now_focus.insert(0, 'н')
        if event.keycode == 39:
            now_focus.delete(0, tkinter.END)
            now_focus.insert(0, 'б')
