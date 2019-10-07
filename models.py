from sqlalchemy.sql import func
from app import db


class Bill(db.Model):

    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    # JACKSON CREATED BELOW LINE
    uid = db.Column(db.String(128), nullable=False)
    items = db.relationship('Item', backref='bill', lazy=True)

    def __init__(self, uid):
        # JACKSON CREATED BELOW LINE
        self.uid = uid
        # pass


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(128), nullable=False)
    # JACKSON CREATED BELOW THREE LINE
    uid = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    items = db.relationship('Item', backref='user', lazy=True)
    full_name = db.column_property(first_name + " " + last_name)
    
    def __init__(self, email, uid, first_name, last_name):
        self.email = email
        # JACKSON CREATED BELOW THREE LINE
        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name


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
            'unit_price': self.unit_price,
            'is_checked': self.user_id != None 
        }

class Balance(db.Model):

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
            'unit_price': self.unit_price,
            'is_checked': self.user_id != None 
        }




