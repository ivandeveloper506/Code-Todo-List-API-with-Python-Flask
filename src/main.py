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

#import JWT for tokenization
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "Secr3tKeyAppT10n-TodoList"
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

jwt = JWTManager(app)

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

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/users/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if email is None:
        return jsonify({"msg": "No email was provided."}), 400

    if password is None:
        return jsonify({"msg": "No password was provided."}), 400
    
    user = User.query.filter_by(email=email, password=password).first()
    
    if user is None:
        # the user was not found on the database
        return jsonify({"msg": "Invalid email or password, no autorizado."}), 401
    else:
        access_token = create_access_token(identity=user.id)
        return jsonify({ "token": access_token, "user_id": user.id }), 200

# [POST] - Ruta para registro de un [user]
@app.route('/users/register', methods=['POST'])
def register():

    data_request = request.get_json()

    user = User.query.filter_by(email=data_request["email"]).first()
    
    # Se valida que el email no haya sido registrado.
    if user:
        return jsonify({"msg": "El email ya fue registrado."}), 401
    
    user = User(email=data_request["email"], password=data_request["password"], is_active=data_request["is_active"])

    try: 
        db.session.add(user) 
        db.session.commit()
        
        return jsonify(User.serialize(user)), 201
    
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    return jsonify({"id": user.id, "email": user.email }), 200

# INICIO - Definición de EndPoints para el Modelo User - INICIO
# [GET] - Ruta para obtener todos los [user]
@app.route('/user', methods=['GET'])
# @jwt_required()
def indexUser():

    results = User.query.all()

    return jsonify(list(map(lambda x: x.serialize(), results))), 200

# [POST] - Ruta para crear un [user]
@app.route('/user', methods=['POST'])
@jwt_required()
def storeUser():

    data_request = request.get_json()
    user = User(email=data_request["email"], password=data_request["password"], is_active=data_request["is_active"])

    try: 
        db.session.add(user) 
        db.session.commit()
        
        return jsonify(User.serialize(user)), 201
    
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400

# [PUT] - Ruta para modificar un [user]
@app.route('/user/<int:id>', methods=['PUT'])
@jwt_required()
def updateUser(id):

    user = User.query.get(id)

    if user is None:
        raise APIException('User is not found.',status_code=403)

    data_request = request.get_json()

    user.password = data_request["password"]
    user.is_active = data_request["is_active"]

    try: 
        db.session.commit()
        
        return jsonify(User.serialize(user)), 200
    
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400

# [DELETE] - Ruta para eliminar un [user]
@app.route('/user/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteUser(id):

    user = User.query.get(id)

    if user is None:
        raise APIException('User is not found.',status_code=403)

    try:
        db.session.delete(user)
        db.session.commit()
        
        return jsonify('User was successfully eliminated.'), 200
    
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400
# FIN - Definición de EndPoints para el Modelo User - FIN

# INICIO - Definición de EndPoints para el Modelo Todo - INICIO
# [GET] - Ruta para obtener todas las [todo]
@app.route('/todo', methods=['GET'])
@jwt_required()
def indexTodo():

    results = Todo.query.all()

    return jsonify(list(map(lambda x: x.serialize(), results))), 200

# [POST] - Ruta para crear un [todo]
@app.route('/todo', methods=['POST'])
@jwt_required()
def storeTodo():

    data_request = request.get_json()
    todo = Todo(done=data_request["done"], label=data_request["label"])

    try: 
        db.session.add(todo) 
        db.session.commit()
        
        return jsonify(Todo.serialize(todo)), 201
    
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400

# [PUT] - Ruta para modificar un [todo]
@app.route('/todo/<int:id>', methods=['PUT'])
@jwt_required()
def updateTodo(id):

    todo = Todo.query.get(id)

    if todo is None:
        raise APIException('Todo is not found.',status_code=403)

    data_request = request.get_json()

    todo.done = data_request["done"]
    todo.label = data_request["label"]

    try: 
        db.session.commit()
        
        return jsonify(Todo.serialize(todo)), 200
    
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400

# [DELETE] - Ruta para eliminar un [todo]
@app.route('/todo/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteTodo(id):

    todo = Todo.query.get(id)

    if todo is None:
        raise APIException('Todo is not found.',status_code=403)

    try:
        db.session.delete(todo)
        db.session.commit()
        
        return jsonify('Todo was successfully eliminated.'), 200
    
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400
# FIN - Definición de EndPoints para el Modelo Todo - FIN

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
