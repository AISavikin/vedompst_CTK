from peewee import *
import yaml
import os

if not os.path.exists('settings.yaml'):
    DB = 'database.db'

else:
    with open('settings.yaml', encoding='utf-8') as f:
        DB = yaml.safe_load(f)['DB']

db = SqliteDatabase(DB, pragmas={'foreign_keys': 1})


class BaseModel(Model):
    class Meta:
        database = db


class Student(BaseModel):
    id = AutoField(primary_key=True, unique=True)
    name = CharField(null=False, unique=True)
    added = DateTimeField()
    group = IntegerField()
    active = BooleanField(default=True)

    class Meta:
        db_table = 'students'
        order_by = 'name'
        verbose_name = 'name'

    def __str__(self):
        return self.name


class Attendance(BaseModel):
    id = AutoField(primary_key=True, unique=True)
    student_id = ForeignKeyField(Student, on_delete='cascade')
    day = IntegerField()
    month = IntegerField()
    year = IntegerField()
    absent = CharField()

    class Meta:
        db_table = 'attendances'


def create_database():
    db.create_tables([Student, Attendance])


if __name__ == '__main__':
    create_database()
