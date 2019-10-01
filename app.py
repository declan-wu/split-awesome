import os
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin
import json
import base64

import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
cors = CORS(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'this_is_a_secret_key'

socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')

db = SQLAlchemy(app)

# from models import Bill, Item, User
from util import img_to_json
from action_types import action_types

from sqlalchemy.sql import func

#FIXME: -----FIXME:---------FIXME:-------FIXME:--------FIXME:----------FIXME:----------- FIXME:

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
    email = db.Column(db.String(128), nullable=False)
    items = db.relationship('Item', backref='user', lazy=True)
    
    def __init__(self, email):
        self.email = email


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

#FIXME: -----FIXME:---------FIXME:-------FIXME:--------FIXME:----------FIXME:----------- FIXME:


@app.route('/', methods=['GET'])
@cross_origin()
def index():
    return "Hello, it's me. Split-awesome"

@app.route('/signup', methods=['POST'])
@cross_origin()
def signup():
    try:
        email = request.get_json()['user_email']
        new_user = User(email)
        db.session.add(new_user)
        db.session.commit()
        res = {"type" : action_types["REDIRECT"], "payload": "/snap"}
        return jsonify(res)
    except:
        res = {"type" : "ERROR", "payload": "Fail to sign up"} 
        return jsonify(res)

#FIXME: this route doesn't work
@app.route('/snap', methods=['POST'])
@cross_origin()
def snap():
    base64_str = request.form.get('image_data', '')
    print(base64_str)
    parsed_res = img_to_json(base64_str)
    new_bill = Bill()
    new_bill.items = []
    print("--------")
    print(parsed_res)
    print("--------")

    # try:
    #     base64_str = request.form.get('image_data', '')
    #     parsed_res = img_to_json(base64_str)
    #     new_bill = Bill()
    #     new_bill.items = []
    #     print("--------")
    #     print(parsed_res)
    #     print("--------")
    #     for line in parsed_res:
    #         quantity = line["quantity"]
    #         unit_price = round(float(line["price"]) / float(quantity), 2)
    #         name = line["item"]
    #         for i in range(int(quantity)):
    #             temp_item = Item(name, unit_price)
    #             new_bill.items.append(temp_item)
    #             db.session.add(temp_item)

    #     db.session.add(new_bill)
    #     db.session.flush()
    #     db.session.refresh(new_bill)
    #     db.session.commit()
    #     room_id = new_bill.id 
    #     res = {"type" : action_types["REDIRECT"], "payload": room_id}
    #     return jsonify(res)
    # except:
    #     res = {"type" : "ERROR", "payload": "Image cannot be detected by AWS"} 
    #     return jsonify(res)

@app.route('/room/<int:room_id>/', methods=['GET'])
@cross_origin()
def room_instance(room_id):
    try:
        food_items = db.session.query(Item) \
            .join(Bill) \
            .filter(Bill.id == room_id) \
            .all()
        res = {str(item.id): item.to_json() for item in food_items}
        return jsonify(res)
    except:
        res = {"type" : "ERROR", "payload": "The room has not been created"} 
        return jsonify(res)

@socketio.on('connect')
def handle_connect():
    print("---------------------------")
    print("connect established")
    print("---------------------------")

@socketio.on('disconnect')
def test_disconnect():
    print("---------------------------")
    print('Client disconnected')
    print("---------------------------")

@socketio.on('check')
def handle_check(request, methods=['GET', 'POST']):
    item_id = request["item_id"]
    user_email = request["user_email"]
    # change target item.user_id to be user id
    target_user = User.query.filter_by(email=user_email).first()
    target_item = Item.query.filter_by(id=item_id).first()
    target_user.items.append(target_item)
    db.session.add(target_user)
    db.session.commit()
    action = {"type": "check", "item_id": item_id}
    socketio.emit('check', action)

@socketio.on('uncheck')
def handle_uncheck(request, methods=['GET', 'POST']):
    user_email = request["user_email"]
    item_id = request["item_id"]
    # set item.user_id = Null 
    target_item = Item.query.filter_by(id=item_id).first()
    target_item.user_id = None
    db.session.add(target_item)
    db.session.commit()
    action = {"type": "uncheck", "item_id": item_id}
    socketio.emit('uncheck', action)

if __name__ == '__main__':
    socketio.run(app)