import os
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_socketio import SocketIO, join_room, leave_room
from flask_cors import CORS, cross_origin
import json
import base64

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

# ------------------------------------------------------------------------------------ 
#                           Model
# ------------------------------------------------------------------------------------ 

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

# ------------------------------------------------------------------------------------ 
#                           Helper Funcitons
# ------------------------------------------------------------------------------------ 

def find_name(user_id):
    try:
        name = db.session.query(User
        ).filter(User.id == user_id
        ).first()
        return name.full_name
    except:
        print("User doesn't exist!")

def find_user_bill_detail(user_id, bill_id):
    try:
        cart_items = db.session.query(Item
            ).filter(Item.bill_id == bill_id, Item.user_id == user_id
            ).all()
        host = db.session.query(Bill).filter(Bill.id == bill_id).first()
        group = db.session.query(
            func.count(Item.id).label('count')
        ).filter(Item.bill_id == bill_id
        ).group_by(Item.user_id
        ).all()
        group_size = len(group)

        ret = []
        subtotal = 0
        for item in cart_items:
            ret.append({'name': item.name, 'price': item.unit_price})
            subtotal += item.unit_price
        res = {'subtotal': subtotal, 'items': ret, 'host': host.uid, 'group_size': group_size }
        return res
    except:
        return jsonify({"error": "database error on find_user_bills"})

def find_bill_info(user_id, bill_id):
    try:
        bill = db.session.query(
            Bill.id,
            Bill.created_date
        ).filter(Bill.id == bill_id
        ).first()
        user_bills = find_user_bill_detail(user_id, bill_id)

        return {'id': bill_id, 'date': bill[1], 'items': user_bills['items'], 'subtotal': user_bills['subtotal'], 'host': user_bills['host'], 'group_size': user_bills['group_size']}
    except:
        return jsonify({"error": "database error on find_bill_info"})

# ------------------------------------------------------------------------------------ 
#                           Routes
# ------------------------------------------------------------------------------------ 

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

@app.route('/snap', methods=['POST'])
@cross_origin()
def snap():
    try:
        u_id = request.form.get('u_id', '')
        base64_str = request.form.get('image_data', '')
        parsed_res = img_to_json(base64_str)
        new_bill = Bill(u_id)
        new_bill.items = []
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

@app.route('/room/<int:room_id>/summary', methods=['GET'])
@cross_origin()
def room_summary(room_id):
    try:
        summary = db.session.query(
            Item.user_id,
            func.sum(Item.unit_price).label('sum')
        ).filter(Item.bill_id == room_id
        ).join( User
        ).group_by(Item.user_id
        ).all()
        return jsonify ([{'name': find_name(row[0]), 'amount': float(row[1])} for row in summary])
    except:
        return jsonify({"error": "database error on room_sumamry"})

@app.route('/user/<uid>/bills', methods=['GET'])
@cross_origin()
def user_bills(uid):
    try: 
        user = db.session.query(User).filter(User.uid == uid).first()
        user_id = user.id
        bills = db.session.query(
            Item.bill_id,
            func.count(Item.bill_id).label('count')
        ).filter(Item.user_id == user_id
        ).group_by(Item.bill_id
        ).all()
        bills_particiapted = [find_bill_info(user_id, bill[0]) for bill in reversed(bills)]
        return jsonify(bills_particiapted)
    except:
        return jsonify({"error": "database error on user_bills"})

@app.route('/rooms', methods=['GET'])
@cross_origin()
def get_all_rooms(): 
    try:
        bills = db.session.query(
            Bill.id
        ).all()
        return jsonify([bill[0] for bill in bills])
    except:
        return jsonify({"error": "database error on get_rooms"})

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


# ------------------------------------------------------------------------------------ 
#                           WebSockets
# ------------------------------------------------------------------------------------ 

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

@socketio.on('join')
def on_join(room):
    print('THIS IS THE JOIN ROOM', room)
    join_room(room)

@socketio.on('leave')
def on_leave(room):
    print('THIS IS THE LEAVE ROOM', room)
    leave_room(room)

@socketio.on('finalize')
def on_finalize(room):
    print('The host finalize the bill', room)
    socketio.emit('finalize', {'type': "redirect", 'payload': 'summary'}, include_self=False)

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
    socketio.emit('check', action, include_self=False, room=request["room_id"])
    print('THIS IS CHECK ROOM ID', request["room_id"])

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
    socketio.emit('uncheck', action, include_self=False, room=request["room_id"])
    print('THIS IS UNCHECK ROOM ID', request["room_id"])

if __name__ == '__main__':
    socketio.run(app)