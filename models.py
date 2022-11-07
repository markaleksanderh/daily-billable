from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass


db = SQLAlchemy(app)


@dataclass
class Employee(db.Model):
    __tablename__ = "employee"
    id: int = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    name: str = db.Column(db.String, nullable=False, unique=True)

    absence: str = db.Column(db.String, default='-')
    billable_hours: int = db.Column(db.Integer, default=0)
    non_billable_hours: int = db.Column(db.Integer, default=0)


    def __repr__(self):
        return f'<Employee: {self.name}>'


