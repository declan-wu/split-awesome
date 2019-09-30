import os
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin
import json
import base64

app = Flask(__name__)
cors = CORS(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'this_is_a_secret_key'

socketio = SocketIO(app)
db = SQLAlchemy(app)

from models import Bill, Item, User
from util import img_to_json
from action_types import action_types

@app.route('/', methods=['GET'])
@cross_origin()
def index():
    return "Hello, it's me. Split-awesome"

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    try: 
        #TODO: actual login
        res = {"type" : action_types["REDIRECT"], "payload": "/snap"}
        return jsonify(res)
    except:
        res = {"type" : "ERROR", "payload": "Fail to log in"} 
        return jsonify(res)

@app.route('/signup', methods=['POST'])
@cross_origin()
def signup():
    try:
        #TODO: actual signup
        res = {"type" : action_types["REDIRECT"], "payload": "/snap"}
        return jsonify(res)
    except:
        res = {"type" : "ERROR", "payload": "Fail to sign up"} 
        return jsonify(res)

@app.route('/snap', methods=['POST'])
@cross_origin()
def snap():
    try:
        base64_str = request.form.get('image_data', '')
        parsed_res = img_to_json(base64_str)
        new_bill = Bill()
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
        res = {str(item.id): item.to_json() for item in food_items}
        return jsonify(res)
    except:
        res = {"type" : "ERROR", "payload": "The room has not been created"} 
        return jsonify(res)

@socketio.on('check')
def handle_check(json, methods=['GET', 'POST']):
    request = json.loads(json)
    user_id = request["user_id"]
    item_id = request["item_id"]
    bill_id = request["bill_id"]
    # change target item.user_id to be user id
    target_user = User.query.filter_by(id=user_id).first()
    target_item = Item.query.filter_by(id=item_id).first()
    target_user.items.append(target_item)
    db.session.add(target_user)
    db.session.commit()
    action = {"type": "check", "item_id": item_id}
    socketio.emit('check', action)

@socketio.on('uncheck')
def handle_uncheck(json, methods=['GET', 'POST']):
    request = json.loads(json)
    user_id = request["user_id"]
    item_id = request["item_id"]
    bill_id = request["bill_id"]
    # set item.user_id = Null 
    target_item = Item.query.filter_by(id=item_id).first()
    target_item.user_id = None
    db.session.add(target_item)
    db.session.commit()
    action = {"type": "uncheck", "item_id": item_id}
    socketio.emit('uncheck', action)

if __name__ == '__main__':
    socketio.run(app)