import os
from flask import Flask, jsonify
from flask_restful import Resource, Api


# instantiate the app
app = Flask(__name__)

api = Api(app)

# set config
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)    

# to see enviroment var
import sys
# print(app.config, file=sys.stderr)

class UsersPing(Resource):
    def get(self):
        return {
        'status': 'success',
        'message': 'pong pong pong!'
    }


api.add_resource(UsersPing, '/users/ping')