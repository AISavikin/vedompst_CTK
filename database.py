from peewee import *

#TODO Переменную получать из настроек

DB = "database.db"
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
