from flask import request , jsonify , session
from carreseller import app, db
from werkzeug.security import generate_password_hash , check_password_hash
import datetime
import jwt
import json
import os
from functools import wraps
from .models import Car,User

# db.drop_all()

def token_required(f):
    @wraps(f)
    def decorated( *args , **kwargs ):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token' ]
        if not token :
            return jsonify({'Message': 'Token is missing'}) , 401
        try:
            data = jwt.decode(token , app.config['SECRET_KEY'], algorithms = 'HS256')
            current_user = User.query.filter_by(id = data['id']).first()
        except:
            return jsonify({'Message': 'Token is invalid'}) , 401
        return  f( current_user ,*args , **kwargs)
    return decorated


@app.route('/register' , methods = ['GET', "POST"])
def register():
    data = request.get_json()
    print(data)
    record = User.query.filter_by( name = data['name'] ).first()
    if not record:
        data['password']  = generate_password_hash(data['password'] , method = 'sha256')
        try :
            user = User( data )
            user.save()
        except Exception as e  :
            print("failed" , e)
            return jsonify({'Message': 'Registration failed'}), 401
        return jsonify({'Message': 'User registration successful'}), 201

    return jsonify({'Message': 'Registration failed'}), 401


@app.route('/login' , methods = ['GET', "POST"])
def login():
    auth = request.authorization
    record = User.query.filter_by( name = auth.username ).first()
    if  record:
        if check_password_hash( record.password   , auth.password ):
            token = jwt.encode( { 'id': record.id ,
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds = 60)
                                } , app.config['SECRET_KEY'] )
            return jsonify({ 'token' : token,
                        'Message': 'JWT Token for a successful login'}) , 200
    return jsonify({'Message': 'Could not verify'}) , 401,{'WWW-Authenticate' : 'Basic realm ="Login required !!"'}

@app.route('/user/update' , methods = [ 'PUT'])
@token_required
def user_update(current_user):
    data = request.get_json()

    try:
        current_user.name = data['name']
        current_user.mobile = data['mobile']
        current_user.license = data['license']
        current_user.save()
    except:
            msg = { 'Message': 'Profile update failed'}
            return jsonify( msg ) , 401
    return jsonify({'Message': 'Profile update success'}), 200


@app.route('/user/delete' , methods = [ 'DELETE'])
@token_required
def user_delete(current_user):

    try:
        current_user.delete()
    except:
            return jsonify({ 'Message': 'Profile delete failed'}) , 401
    return jsonify({'Message': 'No response with appropriate status code'}), 204



@app.route('/car/create' , methods = ['GET', "POST"])
@token_required
def car_create(current_user):
    data = request.get_json()
    data['user_id'] = current_user.id
    try :
        car = Car( data )
        car.save()
    except :
        return jsonify({'Message': 'Car Registration failed'}), 401
    return jsonify({'Message': 'Car registration successful'}), 201
@app.route('/car/delete/<car_id>', methods= ['DELETE'])
@token_required
def car_deletedd(current_user , car_id):
    car = Car.query.filter_by(id = car_id).first()
    try:
        car.delete()
    except:
        return jsonify({ 'Message': 'Profile delete failed'}) , 401
    return jsonify({'Message': 'No response with appropriate status code'}), 204


@app.route('/car/search' , methods = ['GET' ])
@token_required
def car_search(current_user):
    p = request.args
    for k,v in p.items():
        key = v
    records = Car.query.filter_by(registration = key).all()
    if  records:
        lst = [ i.toJSON() for i in record]
        return jsonify({'Message': lst }), 200
    return jsonify({'Message': 'Cannot find any car with that details'}), 401

@app.route('/car/filter' , methods = [ 'GET' ] )
@token_required
def car_filter(current_user):
    model = request.args.get("model")
    maker = request.args.get("maker")
    cars = Car.query.filter_by(model = model , maker = maker ).all()
    if  cars:
        lst = [ i.toJSON() for i in record]
        return jsonify({'Message': lst }), 200
    return jsonify({'Message': 'Cannot find any car with that details'}), 401


@app.route('/car/update' , methods = [ 'PUT'])
@token_required
def car_update(current_user):
    data = request.get_json()
    car = Car.query.filer_by(id = data['id']).first()
    try:
        if data.get('id'):
            car.id = data['id']
        car.maker = data['maker']
        car.user_id = data['user_id']
        car.model = data['model']
        car.subModel = data['subModel']
        car.price = data['price']
        car.yearOfMaking = data['yearOfMaking']
        car.registartion = data['registartion']
        car.save()
    except:
        return jsonify({ 'Message': 'Profile update failed'}) , 401
    return jsonify(jsonify({'Message': 'Profile update success'}), 200
