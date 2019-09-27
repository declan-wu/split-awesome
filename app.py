import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Bill, Item, User
from util import img_to_json
from action_types import action_types
from fake_response import fake_response

@app.route('/', methods=['GET'])
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
def login():
    try: 
        res = {"type" : action_types["GOTO_SNAP_PAGE"]}
        return jsonify(res)
    except:
        res = {"type" : "LOGIN_FAILED"} #FIXME: 
        return jsonify(res)

@app.route('/signup', methods=['POST'])
def signup():
    try:
        #TODO: handle input form data and insert it into our database
        res = {"type" : action_types["GOTO_SNAP_PAGE"]}
        return jsonify(res)
    except:
        res = {"type" : "SIGNUP_FAILED"} #FIXME:
        return jsonify(res)


@app.route('/snap', methods=['POST'])
def snap():
    try:
        base64_str = request.form['image_data']
        img_path = "./static/images/example.png"
        new_img_path = "./static/images/new_image.png"
        bucket = "split-wise-receipts-lhl"
        s3_filename = "new_image.png"
        parsed_res = img_to_json(base64_str, img_path, new_img_path, bucket, s3_filename)
        # parsed_res = fake_response #FIXME:
        new_bill = Bill()
        new_bill.items = []
        
        for line in parsed_res:
            temp_item = Item(line["quantity"], line["name"], line["unit_price"])
            new_bill.items.append(temp_item)
            db.session.add(temp_item)
        
        db.session.add(new_bill)
        db.session.flush()
        db.session.refresh(new_bill)
        db.session.commit()
        room_id = new_bill.id 
        res = {"type": action_types["GOTO_ROOM"], "payload": room_id}
        return jsonify(res)
    except:
        #FIXME: this should handle wrong input form data
        res = {"type": action_types["FORM_DATA_FIELD_INCORRECT"]}
        return jsonify(res)

#FIXME: we don't have a seperate route for the room QR page yet.  
@app.route('/room/<int:room_id>/', methods=['GET', 'POST'])
def room_instance(room_id):
    if request.method == 'POST':
        #TODO: using websocket, or dynamically update the menu items / database
        pass
    else:
        food_items = db.session.query(Item) \
            .join(Bill) \
            .filter(Bill.id == room_id) \
            .all()
        res = {"food_items" : [item.to_json() for item in food_items]}
        return jsonify(res)

if __name__ == '__main__':
    app.run()