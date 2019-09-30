import os
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import base64

app = Flask(__name__)
cors = CORS(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Bill, Item, User
from util import img_to_json
from action_types import action_types
from fake_response import fake_response

@app.route('/', methods=['GET'])
@cross_origin()
def index():
    res = {"Methods allowed on this API server" : {
        "POST /login": "response with an action type, if no error, should be 'GOTO_SNAP_PAGE'",
        "POST /signup": "response with an action type, if no error, should be 'GOTO_SNAP_PAGE'", 
        "POST /snap": "form data field expecting: 'image_data', response with action types, with payload as room number",
        "GET /room/<room_id>": "response with JSON data with items information, right now it's fake data as we are working on regex parsing"
        }
    }
    return jsonify(res)

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
        #TODO: randomize image name
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

if __name__ == '__main__':
    app.run()