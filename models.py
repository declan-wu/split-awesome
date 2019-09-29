from sqlalchemy.sql import func
from app import db

bills_users_association = db.Table('bills_users',
    db.Column('bill_id', db.Integer, db.ForeignKey('bills.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('items.id'), primary_key=True)
)

class Bill(db.Model):

    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    items = db.relationship('Item', backref='bill', lazy=True)
    users = db.relationship('User', secondary=bills_users_association, lazy='subquery', backref=db.backref('bills', lazy=True))

    def __init__(self):
        pass


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    hased_password = db.Column(db.String(128), nullable=False)
    
    def __init__(self, name, hashed_password):
        self.name = name
        self.hashed_password = hashed_password


class Item(db.Model):

    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_checked = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)

    def __init__(self, name, unit_price, is_checked=False):
        self.is_checked = is_checked
        self.name = name
        self.unit_price = unit_price
    
    def to_json(self):
        return {
            'id': self.id, 
            'is_checked': self.is_checked,
            'name': self.name,
            'unit_price': self.unit_price
        }