import peewee
import customtkinter as ctk
from tkinter import ttk, LEFT, END, Entry, Event
from utils import *


class KidsWindow(Mixin, ctk.CTkToplevel):
    def __init__(self, parent, group="1"):
        super().__init__(parent)
        self.group = group

        # Настройка окна
        w = 800
        self.set_geometry(w)
        self.title("Ведомости")
        self.font = parent.font
        self.table_frame = TableFrame(self)
        self.control_frame = ControlFrame(self)

        self.control_frame.pack(side=LEFT, padx=20)
        self.table_frame.pack(side=LEFT)

        # Привязка событий
        self.bind('<<TreeviewSelect>>', self.table_frame.paste)
        self.bind('<space>', self.table_frame.change_active)
        self.bind('<Right>', self.control_frame.navigation)
        self.bind('<Left>', self.control_frame.navigation)
        self.bind('<Down>', self.control_frame.navigation)
        self.bind('<Return>', self.control_frame.navigation)
        self.bind('<Up>', self.control_frame.navigation)

    def refresh(self):
        self.table_frame.clean_table()
        self.control_frame.entry.delete(0, END)
        self.table_frame.gen_table()


class ControlFrame(ctk.CTkFrame):
    def __init__(self, master: KidsWindow):
        super().__init__(master)
        self.master: KidsWindow = master
        ctk.CTkLabel(self, text='Фамилия и имя', font=master.font).grid(row=0, columnspan=3)
        self.entry = ctk.CTkEntry(self, font=master.font, width=250)
        self.entry.grid(row=1, columnspan=3, pady=10)
        self.add_btn = ctk.CTkButton(self, text='Добавить', command=self.add_kid, width=10, font=master.font)
        self.add_btn.grid(row=2, column=0, padx=3)
        self.del_btn = ctk.CTkButton(self, text='Удалить', command=self.del_kid, width=10, font=master.font)
        self.del_btn.grid(row=2, column=1, padx=3)
        self.cng_btn = ctk.CTkButton(self, text='Исправить', command=self.change_kid, width=10, font=master.font)
        self.cng_btn.grid(row=2, column=2, padx=3)
        self.setup_focus()

    def setup_focus(self):
        elements = [self.add_btn, self.del_btn, self.cng_btn]
        self.custom_focus = CustomFocus(elements)

    def navigation(self, event: Event):
        if type(self.focus_get()) == KidsWindow:
            self.custom_focus.set()
            return
        if type(self.focus_get()) == Entry and event.keysym != 'Down':
            return
        if type(self.focus_get()) == ttk.Treeview and event.keysym in ['Down', 'Up']:
            return
        if event.keysym == 'Up':
            self.entry.focus()
            [i.configure(fg_color='#1f538d') for i in self.custom_focus.btns]
            return
        if event.keysym == 'Left':
            self.custom_focus.prev()
        if event.keysym == 'Right':
            self.custom_focus.next()
        if event.keysym == 'Return':
            self.custom_focus.focus_node.element.cget('command')()
        self.custom_focus.set()

    def add_kid(self):
        name = self.entry.get()
        name = ' '.join(map(str.capitalize, name.split()))
        if name:
            try:
                Student.create(name=name, group=self.master.group, added=self.master.date, active=True)
            except peewee.IntegrityError:
                messagebox.showerror(title='Ошибка', message='Ученик с таким именем уже существует!')
        self.master.refresh()

    def del_kid(self):
        name = self.master.table_frame.get_name_from_table()
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
        self.master.refresh()

    def change_kid(self):
        name = self.master.table_frame.get_name_from_table()
        if not name:
            messagebox.showerror(title='Ошибка', message='Введите имя!')
            return
        kids_id = Student.get(name=name)
        new_name = self.entry.get()
        Student.update({Student.name: new_name}).where(Student.id == kids_id).execute()
        self.master.refresh()


class TableFrame(ctk.CTkFrame):
    def __init__(self, master: KidsWindow):
        super().__init__(master)
        self.group = master.group
        self.master: KidsWindow = master
        s = ttk.Style()
        s.configure('Treeview', rowheight=25)
        ctk.CTkLabel(self, text=f"Группа {master.group}", font=master.font).pack(pady=10)
        columns = ('№', 'name', 'added')
        self.table = ttk.Treeview(master=self, columns=columns, show='headings', height=15)
        self.table.tag_configure('normal', foreground='white', background='#1a1a1a', font=master.font)
        self.table.tag_configure('mark', foreground='#4a83b2', background='#1a1a1a', font=master.font)
        self.table.heading('№', text='№')
        self.table.heading('name', text='Имя')
        self.table.heading('added', text='Добавлен')
        self.table.column('№', width=30, anchor='n')
        self.table.column('name', width=250, anchor='n')
        self.table.column('added', width=150, anchor='n')
        self.table.pack()
        self.gen_table()

    def gen_table(self):
        kids = [student for student in Student.select().where(Student.group == self.group).order_by(Student.name)]
        data = [(cnt, i.name, f'{i.added:%d.%m.%y}', i.active) for cnt, i in enumerate(kids, 1)]
        for kid in data:
            if kid[-1]:
                tag = 'normal'
            else:
                tag = 'mark'
            self.table.insert("", END, values=kid, tags=tag, )
        for space in range(15 - len(data)):
            self.table.insert("", END, values=('', '', ''), tags='normal')

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
            self.master.control_frame.entry.delete(0, END)
            self.master.control_frame.entry.insert(0, name)

    def change_active(self, event):
        name = self.get_name_from_table()
        if not name:
            return
        active = Student.get(Student.name == name).active
        Student.update(active=not active).where(Student.name == name).execute()
        self.master.refresh()
