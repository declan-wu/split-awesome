import os
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin
import json
import base64

# import gevent-websocket

from gevent import monkey
monkey.patch_all()

app = Flask(__name__)
cors = CORS(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'this_is_a_secret_key'

socketio = SocketIO(app, cors_allowed_origins='*', async_mode='gevent')

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
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    uid = db.Column(db.String(128), nullable=False)
    items = db.relationship('Item', backref='user', lazy=True)
    
    def __init__(self, email, uid, first_name, last_name):
        self.email = email
        # JACKSON CREATED BELOW LINE
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

#FIXME: -----FIXME:---------FIXME:-------FIXME:--------FIXME:----------FIXME:----------- FIXME:


@app.route('/', methods=['GET'])
@cross_origin()
def index():
    return "Hello, it's me. Split-awesome"

@app.after_request
def after_request(response):
    header = response.headers
    header[ 'Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/signup', methods=['POST'])
@cross_origin()
def signup():
    try:
        email = request.get_json()['user_email']
        # JACKSON CREATED THREE LINES BELOW AND EDITED 5TH LINE
        first_name = request.get_json()['first_name']
        last_name = request.get_json()['last_name']
        u_id = request.get_json()['u_id']
        new_user = User(email, u_id, first_name, last_name)
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
    try:
        u_id = request.form.get('u_id', '')
        base64_str = request.form.get('image_data', '')
        parsed_res = img_to_json(base64_str)
        new_bill = Bill(u_id)
        new_bill.items = []
        print("--------")
        print(parsed_res)
        print("--------")
        for line in parsed_res:
            quantity = line["quantity"]
            unit_price = round(float(line["price"]) / float(quantity), 2)
            name = line["item"]
            for i in range(int(quantity)):
                temp_item = Item(name, unit_price)
                new_bill.items.append(temp_item)
                db.session.add(temp_item)

        db.session.add(new_bill)
        db.session.flush()
        db.session.refresh(new_bill)
        db.session.commit()
        room_id = new_bill.id 
        res = {"type" : action_types["REDIRECT"], "payload": room_id}
        return jsonify(res)
    except:
        res = {"type" : "ERROR", "payload": "Image cannot be detected by AWS"} 
        return jsonify(res)

@app.route('/room/<int:room_id>/', methods=['GET'])
@cross_origin()
def room_instance(room_id):
    try:
        food_items = db.session.query(Item) \
            .join(Bill) \
            .filter(Bill.id == room_id) \
            .all()
        
        host_id = db.session.query(Bill) \
            .filter(Bill.id == room_id) \
            .all()

        res2 = host_id[0].uid
        res = {}
        res["items"] = {str(item.id): item.to_json() for item in food_items}
        res["host_id"] = res2
        return jsonify(res)
    except:
        res = {"type" : "ERROR", "payload": "The room has not been created"} 
        return jsonify(res)

# JACKSON CREATED BELOW ROUTE
@app.route('/users/<u_id>/room/<int:room_id>/', methods=['GET'])
@cross_origin()
def cart_instance(u_id, room_id):

    try:
        cart_items = db.session.query(Item) \
            .join(User) \
            .filter(User.uid == u_id) \
            .filter(Item.bill_id == room_id) \
            .all()

        res = {str(item.id): item.to_json() for item in cart_items}
        return jsonify(res)
    except:
        res = {"type" : "ERROR", "payload": "Cart has not been created"}
        return jsonify(res)

# # JACKSON CREATED BELOW ROUTE
@app.route('/kevin/', methods=['GET'])
@cross_origin()
def summary():

    try:
        print ("PRINT THIS SHIT")
        summary_items = db.session.query(Item.user_id, func.sum(Item.unit_price).label('total')) \
            .join(User) \
            .group_by(Item.user_id) \
            .all() 
        
        userDetails = []
        print ("PRINT THIS SHIT", summary_items[0][0])
        print ("PRINT THIS SHIT", summary_items[1][1])
        for user in summary_items:
            userTemp = {}
            userTemp['total'] = user.total
            userTemp['user_id'] = user.user_id
            # userTemp['user_bill'] = user.bill_id
            # userTemp['user_uid'] = user.uid
            # userTemp['first_name'] = user.first_name
            # userTemp['last_name'] = user.last_name
            # userTemp['email'] = user.email
            userDetails.append(userTemp)

        print(userDetails)
        # print(summary_items)
        res = {'users': userDetails}
        # res = {str(user): user.id.to_json() for user in summary_items}
        return jsonify(res)
    except:
        res = {"type" : "ERROR", "payload": "Cart has not been created"}
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
    socketio.emit('check', action, include_self=False)

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
    socketio.emit('uncheck', action, include_self=False)

if __name__ == '__main__':
    socketio.run(app)