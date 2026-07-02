from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(100), nullable=False)


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    m1 = db.Column(db.Integer, nullable=False)

    m2 = db.Column(db.Integer, nullable=False)

    m3 = db.Column(db.Integer, nullable=False)

    average = db.Column(db.Float)

    grade = db.Column(db.String(5))