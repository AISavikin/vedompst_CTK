import customtkinter as ctk
from tkinter import LEFT, END, messagebox
from utils import *
import os
from PIL import ImageGrab


class MarkKidsWindow(Mixin, ctk.CTkToplevel):
    def __init__(self, parent, group: str, month):

        super().__init__(parent)
        self.group = group
        self.month = month
        self.month_num = self.get_month_num(month)
        self.year = self.get_year(self.month_num)
        self.font = parent.font
        self.kids = [student for student in Student.select().where(Student.group == self.group).order_by(Student.name)]

        # Настройка окна
        self.title("Отметить")
        w = 255
        self.set_geometry(w)

        self.kids_frame = KidsFrame(self)
        self.info_frame = InfoFrame(self)

        self.info_frame.pack(padx=10)
        self.kids_frame.pack(pady=10, padx=15)

        self.bind('<Down>', self.kids_frame.navigation)
        self.bind('<Up>', self.kids_frame.navigation)
        self.bind('<Left>', self.kids_frame.navigation)
        self.bind('<Right>', self.kids_frame.navigation)
        self.bind('<Return>', self.mark_kids)

    def mark_kids(self, *event):
        absents = self.kids_frame.get_absents()
        if not all(absents):
            confirm = messagebox.askyesno(title='Вы уверены?', message='Вы отметили не всех! Сохранить?')
            if not confirm:
                return

        day = self.info_frame.get_date()
        for indx, kid in enumerate(self.kids):
            attendance = Attendance.select().filter(day=day, student_id=kid.id, year=self.year, month=self.month_num)
            if not len(attendance):
                Attendance.create(absent=absents[indx], day=day, month=self.month_num, year=self.year,
                                  student_id=kid.id)
            else:
                Attendance.update({Attendance.absent: absents[indx]}).where(Attendance.id == attendance[0].id).execute()
        self.make_screenshot()
        self.destroy()

    def make_screenshot(self):
        path_screenshot = self.get_settings()['PATH_SCREENSHOT']
        path = os.path.join(path_screenshot, self.month)
        if not os.path.exists(path):
            os.makedirs(path)
        w, h, x, y = self.get_window_size(self)
        scr = ImageGrab.grab(bbox=(x, y, x + w, y + h + 50))
        date = self.info_frame.get_date()
        path += f'/{date}-Группа_{self.group}.jpg'
        if os.path.exists(path):
            if not messagebox.askyesno(title='Внимание!',
                                       message='Скриншот с отмеченными учениками уже существует! Перезаписать?'):
                return
        scr.save(path)


class InfoFrame(ctk.CTkFrame):
    def __init__(self, master: MarkKidsWindow):
        super().__init__(master)
        work_days = [str(i) for i in master.get_work_days(master.month)]

        cmb_frame = ctk.CTkFrame(self)
        ctk.CTkLabel(cmb_frame, text='Число', font=master.font).pack(side=LEFT)
        self.cmb_date = ctk.CTkComboBox(cmb_frame, values=work_days, state='readonly', width=70,
                                        font=master.font, command=master.kids_frame.paste_absents)
        self.cmb_date.pack(side=LEFT, padx=10)
        ctk.CTkLabel(cmb_frame, text=f'{master.month}', font=master.font).pack(side=LEFT)
        self.cmb_date.set(f'{master.date:%d}')
        ctk.CTkLabel(self, text=f'Группа {master.group}', font=master.font).pack(pady=10)
        cmb_frame.pack(pady=10)

    def get_date(self):
        return self.cmb_date.get().strip()


class KidsFrame(ctk.CTkFrame):

    def __init__(self, master: MarkKidsWindow):
        super().__init__(master)
        self.font = master.font
        self.month_num = master.month_num
        self.year = master.year
        self.kids = master.kids
        self.get_absents_from_db = master.get_absents_from_db
        self.entrys = []
        self.create_entry()
        self.btn = ctk.CTkButton(self, text='Отметить', command=master.mark_kids, font=self.font)
        self.btn.grid(row=len(self.entrys) + 1, columnspan=2, pady=3)
        self.setup_focus()
        self.paste_absents(f'{master.date:%d}')
        self.after(150, lambda: self.custom_focus.set())

    def create_entry(self):
        for ind, kid in enumerate(self.kids):
            label = ctk.CTkLabel(self, text=f'{kid.name}', font=self.font)
            label.grid(row=ind, column=0, sticky='w')
            entry = ctk.CTkEntry(self, width=28, font=self.font)
            entry.grid(row=ind, column=1, sticky='e', padx=10, pady=3)
            if not kid.active:
                entry.insert(0, 'н')
                entry.configure(state='disabled', text_color='#4a83b2')
                label.configure(text_color='#4a83b2')
            self.entrys.append(entry)

    def setup_focus(self):
        elements = self.entrys + [self.btn]
        self.custom_focus = CustomFocus(elements)

    def paste_absents(self, day):
        absents = self.get_absents_from_db(self.kids, day, self.month_num, self.year)
        for i, entry in enumerate(self.entrys):
            if absents[i]:
                entry.configure(state='normal')
            entry.delete(0, END)
            entry.insert(0, absents[i])

    def get_absents(self):
        return [i.get() for i in self.entrys]

    def navigation(self, event):
        custom_focus = self.custom_focus
        if event.keysym == 'Down':
            custom_focus.next()
        if event.keysym == 'Up':
            custom_focus.prev()
        if event.keysym == 'Left':
            custom_focus.focus_node.element.delete(0, END)
            custom_focus.focus_node.element.insert(0, 'н')
        if event.keysym == 'Right':
            custom_focus.focus_node.element.delete(0, END)
            custom_focus.focus_node.element.insert(0, 'б')
        custom_focus.set()
