import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# db_drop_and_create_all()

## ROUTES


@app.route('/drinks')
def get_drinks():
    drink=Drink.query.all()
    drinks=[]
    for drink1 in drink:
        drinks.append(drink1.short())
       
    
    return jsonify({
          'success': True,
          'drinks':drinks
          })
          

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(token):
    drinks=Drink.query.all()
    
    return jsonify({
          'drinks':[drink.long() for drink in drinks],
          'success': True
          })

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(token):
    data=request.get_json()
    title=data['title']
    recipe=json.dumps(data['recipe'])
   
    drink = Drink(title=title, recipe=recipe)
    
    drink.insert()
    
    return jsonify({
          'success': True,
          'drinks':drink.long()
          })


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(token,id):
    data=request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    
    drink.title = data['title']
   
    drink.update()
    

    return jsonify({
          'success': True,
          'drinks':drink.long()
          })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(token,id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)

    drink.delete()
   
    return jsonify({
          'success': True,
          'delete':id
          })


# ## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Resource Not found"
        }), 404

@app.errorhandler(AuthError)
def handle_auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response


