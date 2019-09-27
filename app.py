import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Bill, Item, User
from util import img_to_text
from action_types import action_types

#FIXME: 
from fake_response import fake_response

@app.route('/', methods=['GET'])
def index():
    return "hello"

@app.route('/login', methods=['POST'])
def login():
    #FIXME: need to add error handling here, right now, it's we just redirect user to snap page
    res = {"type" : action_types["GOTO_SNAP_PAGE"]}
    return jsonify(res)

@app.route('/signup', methods=['POST'])
def signup():
    #TODO: handle input form data and insert it into our database
    res = {"type" : action_types["GOTO_SNAP_PAGE"]}
    return jsonify(res)

@app.route('/snap', methods=['POST'])
def snap():
    try:
        # base64_str = request.form['image_data']
        # img_path = "./static/images/example.png"
        # new_img_path = "./static/images/new_image.png"
        # bucket = "split-wise-receipts-lhl"
        # s3_filename = "new_image.png"
        # parsed_res = img_to_text(base64_str, img_path, new_img_path, bucket, s3_filename)
        # #FIXME:
        parsed_res = fake_response
        # create new room instance in our database 
        new_bill = Bill(date.today())
        new_bill.items = []
        
        for line in parsed_res:
            temp_item = Item(line["quantity"], line["name"], line["unit_price"])
            new_bill.items.append(temp_item)
            session.add(temp_item)
        
        session.add(new_bill)
        session.flush()
        session.refresh(new_bill)
        room_id = new_bill.id 
        res = {"type": action_types["GOTO_ROOM"], "payload": room_id}
        # res = {"type": action_types["GOTO_ROOM"], "payload": "need to parse the response string"}
        return jsonify( res )
    except:
        #FIXME: this should be handling input form not correct 
        res = {"type": action_types["BAD_REQUEST"]}
        return jsonify( res )

#FIXME: RN we say ROOM/QR page is in the same page as the food items page. 
@app.route('/room/<int:room_id>/', methods=['GET', 'POST'])
def room_instance(room_id):
    if request.method == 'POST':
        #TODO: using websocket, or dynamically update the menu items / database
        pass
    else:
        food_items = session.query(Item) \
            .join(Bill) \
            .filter(Bill.id == room_id) \
            .all()
        res = {"food_items" : []}
        for item in food_items:
            line = {"quantity": item.quantity, "name": item.name, "unit_price": item.unit_price}
            res["food_items"].append(line)
        print(res)
        return jsonify(res)

if __name__ == '__main__':
    app.run()