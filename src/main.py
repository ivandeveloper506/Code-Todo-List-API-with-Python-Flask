"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import json
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

class BaseObject:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# [GET] - Ruta para obtener todas las TODOS
@app.route('/todo', methods=['GET'])
def index():

    results = Todo.query.all()

    # all_todos = list(map(lambda x: x.serialize(), results))

    return jsonify(list(map(lambda x: x.serialize(), results))), 200

# [POST] - Ruta para crear un TODO
@app.route('/todo', methods=['POST'])
def store():

    request_body = request.get_json()
    todo = Todo(done=request_body["done"], label=request_body["label"])

    try: 
        db.session.add(todo) 
        db.session.commit()
        
        return jsonify(Todo.serialize(todo)), 201
    
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400

# [PUT] - Ruta para modificar un TODO
@app.route('/todo/<int:id>', methods=['PUT'])
def update(id):

    todo = Todo.query.get(id)

    if todo is None:
        raise APIException('Todo is not found.',status_code=403)

    request_body = request.get_json()

    todo.done = request_body["done"]
    todo.label = request_body["label"]

    try: 
        db.session.commit()
        
        return jsonify(Todo.serialize(todo)), 200
    
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400

# [DELETE] - Ruta para eliminar un TODO
@app.route('/todo/<int:id>', methods=['DELETE'])
def delete(id):

    todo = Todo.query.get(id)

    if todo is None:
        raise APIException('Todo is not found.',status_code=403)

    try:
        db.session.delete(todo)
        db.session.commit()
        
        return jsonify('Todo was successfully eliminated.'), 200
    
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
