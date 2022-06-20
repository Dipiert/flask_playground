from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Sequence, Integer, String, Float, DateTime
from werkzeug.security import check_password_hash

Base = declarative_base()


class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    last_names = Column(String(35))
    names = Column(String(35))
    usd_monthly_salary = Column(Float())

    def __repr__(self):
        return f'{self.names}, {self.last_names} - USD Monthly salary: {self.usd_monthly_salary}'

    def serialize(self):
        return {
            'names': self.names,
            'last_names': self.last_names,
            'usd_monthly_salary': self.usd_monthly_salary
        }


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    user = Column(String(35))
    password = Column(String(88))
    registered_at = Column(DateTime())
    token = None

    def login(self, user, password):
        """Login a user"""
        if user and check_password_hash(user.password, password):
            return user

    def serialize(self):
        return {
            'names': self.user,
            'registered_at': self.registered_at,
            'token': self.token
        }

