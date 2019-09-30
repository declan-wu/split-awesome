from sqlalchemy.sql import func
from app import db


class Bill(db.Model):

    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    items = db.relationship('Item', backref='bill', lazy=True)

    def __init__(self):
        pass


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    hased_password = db.Column(db.String(128), nullable=False)
    items = db.relationship('Item', backref='user', lazy=True)
    
    def __init__(self, name, hashed_password):
        self.name = name
        self.hashed_password = hashed_password


class Item(db.Model):

    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __init__(self, name, unit_price):
        self.name = name
        self.unit_price = unit_price
    
    def to_json(self):
        return {
            'id': self.id, 
            'name': self.name,
            'unit_price': self.unit_price
        }