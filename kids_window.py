import peewee
import customtkinter as ctk
import tkinter
from tkinter import ttk, messagebox
from database import Student
from base_window import BaseWindowClass


class KidsWindow(BaseWindowClass):
    def __init__(self, parent, group="1"):
        super().__init__(parent)
        self.group = group
        # Настройка окна
        w = 800
        h = 500
        self.set_geometry(w, h)
        self.title("Ведомости")

        self.control_frame = ControlFrame(self)
        self.table_frame = TableFrame(self, self.group)

        self.control_frame.pack(side=tkinter.LEFT, padx=20)
        self.table_frame.pack(side=tkinter.LEFT)
        # Привязка событий
        self.bind('<<TreeviewSelect>>', self.table_frame.paste)
        self.bind('<space>', self.change_active)
        self.bind('<Right>', self.choose_button)
        self.bind('<Left>', self.choose_button)
        self.bind('<Return>', self.choose_button)

        self.index = -1
        self.focus_btn = None

    def choose_button(self, event):
        btns = [self.control_frame.add_btn, self.control_frame.del_btn, self.control_frame.cng_btn]
        [i.configure(fg_color='#1f538d') for i in btns]
        if event.keycode == 39:
            self.index += 1
            if self.index == 3:
                self.index = 0
            self.focus_btn = btns[self.index]
        if event.keycode == 37:
            self.index -= 1
            if self.index < 0:
                self.index = 2
            self.focus_btn = btns[self.index]
        if self.focus_btn:
            self.focus_btn.configure(fg_color='#08359D')
        if event.keycode == 13 and self.focus_btn:
            self.focus_btn.cget('command')()

    def refresh(self):
        self.table_frame.clean_table()
        self.control_frame.entry.delete(0, tkinter.END)
        self.table_frame.gen_table()

    def change_active(self, event):
        name = self.table_frame.get_name_from_table()
        if not name:
            return
        active = Student.get(Student.name == name).active
        Student.update(active=not active).where(Student.name == name).execute()
        self.refresh()

    def add_kid(self):
        name = self.control_frame.get_entry()
        name = ' '.join(map(str.capitalize, name.split()))
        if name:
            try:
                Student.create(name=name, group=self.group, added=self.date_now, active=True)
            except peewee.IntegrityError:
                messagebox.showerror(title='Ошибка', message='Ученик с таким именем уже существует!')
        self.refresh()

    def del_kid(self):
        name = self.control_frame.get_entry()
        try:
            kids_id = Student.get(name=name)
        except peewee.DoesNotExist:
            messagebox.showerror(title='Ошибка', message='Ученика с таким именем не существует')
            return
        if not name:
            messagebox.showerror(title='Ошибка', message='Введите имя!')
            return
        if not messagebox.askyesno(title='Вы уверены?', message='Данное действие не обратимо\nВсё равно выполнить?'):
            return
        Student.delete().where(Student.id == kids_id).execute()
        self.refresh()

    def change_kid(self):
        name = self.table_frame.get_name_from_table()
        if not name:
            messagebox.showerror(title='Ошибка', message='Введите имя!')
            return
        kids_id = Student.get(name=name)
        new_name = self.control_frame.get_entry()
        Student.update({Student.name: new_name}).where(Student.id == kids_id).execute()
        self.refresh()


class ControlFrame(ctk.CTkFrame):
    def __init__(self, master: KidsWindow):
        super().__init__(master)
        ctk.CTkLabel(self, text='Фамилия и имя', font=master.font).grid(row=0, columnspan=3)
        self.entry = ctk.CTkEntry(self, font=master.font, width=250)
        self.entry.grid(row=1, columnspan=3, pady=10)
        self.add_btn = ctk.CTkButton(self, text='Добавить', command=master.add_kid, width=10, font=master.font)
        self.add_btn.grid(row=2, column=0, padx=3)
        self.del_btn = ctk.CTkButton(self, text='Удалить', command=master.del_kid, width=10, font=master.font)
        self.del_btn.grid(row=2, column=1, padx=3)
        self.cng_btn = ctk.CTkButton(self, text='Исправить', command=master.change_kid, width=10, font=master.font)
        self.cng_btn.grid(row=2, column=2, padx=3)

    def get_entry(self):
        return self.entry.get()


class TableFrame(ctk.CTkFrame):
    def __init__(self, master: KidsWindow, group):
        super().__init__(master)
        self.group = group
        self.control_frame = master.control_frame
        s = ttk.Style()
        s.configure('Treeview', rowheight=25)
        ctk.CTkLabel(self, text=f"Группа {master.group}", font=master.font).grid(row=0, pady=10)
        columns = ('№', 'name', 'added')
        self.table = ttk.Treeview(master=self, columns=columns, show='headings', height=15)
        self.table.tag_configure('white', foreground='white', background='#1a1a1a', font=master.font)
        self.table.tag_configure('red', foreground='#4a83b2', background='#1a1a1a', font=master.font)
        self.table.heading('№', text='№')
        self.table.heading('name', text='Имя')
        self.table.heading('added', text='Добавлен')
        self.table.column('№', width=30, anchor='n')
        self.table.column('name', width=250, anchor='n', stretch=tkinter.NO)
        self.table.column('added', width=150, anchor='n')
        self.table.grid(row=1)
        self.gen_table()

    def gen_table(self):
        kids = [student for student in Student.select().where(Student.group == self.group).order_by(Student.name)]
        data = [(cnt, i.name, f'{i.added:%d.%m.%y}', i.active) for cnt, i in enumerate(kids, 1)]
        for kid in data:
            if kid[-1]:
                tag = 'white'
            else:
                tag = 'red'
            self.table.insert("", tkinter.END, values=kid, tags=tag, )
        for space in range(15 - len(data)):
            self.table.insert("", tkinter.END, values=('', '', ''), tags='white')

    def clean_table(self):
        for i in self.table.get_children():
            self.table.delete(i)

    def get_name_from_table(self):
        selected_item = self.table.selection()
        if not selected_item:
            return
        name = self.table.item(selected_item[0], option='value')[1]
        return name

    def paste(self, event):
        name = self.get_name_from_table()
        if name:
            self.control_frame.entry.delete(0, tkinter.END)
            self.control_frame.entry.insert(0, name)

