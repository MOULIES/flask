from flask import request , jsonify , session, make_response, redirect, url_for
from carreseller import app, db
from werkzeug.security import generate_password_hash , check_password_hash
import datetime
import jwt
import json
import os
import random
import string
from functools import wraps
from .models import Car,User
from .models import CarSchema , UserSchema

us = UserSchema(many = True)
# word = ''.join( random.choice(string.ascii_lowercase)  for i in range(10) )
# data= eval('{"name": "'+word +'", "password": "' + word + '","license": "' +word + '", "mobile":"'+ word+'"}')
# u1 = User(data)
# u1.save()

# db.drop_all()
# https://stackoverflow.com/questions/54221636/updating-database-with-for-loop-in-flask
@app.errorhandler(404)
def errorpage(e):
    return {"Message": "Please check url"},404

@app.route("/")
def index():
    db.drop_all()
    db.create_all()

    word = ''.join( random.choice(string.ascii_lowercase)  for i in range(10) )
    r1 = random.randint(0,10)
    word = ''.join( random.choice(string.ascii_lowercase)  for i in range(10) )
    data= eval('{"name": "'+word +'", "password": "' + word + '","license": "' +word + '", "mobile":"'+ word+'"}')
    u1 = User(data)
    u1.save()

    word = ''.join( random.choice(string.ascii_lowercase)  for i in range(10) )
    data= eval('{"name": "'+word +'", "password": "' + word + '","license": "' +word + '", "mobile":"'+ word+'"}')
    u1 = User(data)
    u1.save()

    payload = eval('{"maker":"'+ word + '" , "model":"' +word + '" , "subModel":"' + word + '" , "yearOfMaking":"'+ str(r1) + '" , "price":"' + str(r1)+ '" , "registration":"' + word +'"}' )
    payload['user_id'] = 1
    c1 = Car(payload)
    c1.save()

    # word = ''.join( random.choice(string.ascii_lowercase)  for i in range(10) )
    # payload = eval('{"maker":"'+ word + '" , "model":"' +word + '" , "subModel":"' + word + '" , "yearOfMaking":"'+ str(r1) + '" , "price":"' + str(r1)+ '" , "registration":"' + word +'"}' )
    # payload['user_id'] = 1
    # c1 = Car(payload)
    # c1.save()

    print( " " ,  User.query.all())
    users = User.query.all()
    output = us.dump(users)
    return jsonify({ "hello":"Moulies" ,
                    "users": output ,
                    "u1" : UserSchema().dump( User.query.get(1) ) ,
                    "car" : CarSchema().dump( Car.query.get(1) ),
                    "cars" : CarSchema(many= True).dump( Car.query.all() )
                    }  )

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
    #line36
    # import base64
    # headers = request.headers.get("Authorization")
    # headers_basic_split = headers.split("Basic ")[1]
    # colon_split = base64.b64decode(headers_basic_split).decode('UTF-8').split(":")
    # # colon_split = str( base64.b64decode(headers_basic_split) , 'UTF-8' ).split(":")
    # username = colon_split[0]
    # password = colon_split[1]

    auth = request.authorization
    record = User.query.filter_by( name = auth.username ).first()
    if  record:
        if check_password_hash( record.password   , auth.password ):
            token = jwt.encode( { 'id': record.id ,
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds = 60)
                                } , app.config['SECRET_KEY'] )
            return jsonify({ 'token' : token,
                        'Message': 'JWT Token for a successful login'}),200

    return jsonify({'Message': 'Could not verify'}) , 401,{'WWW-Authenticate' : 'Basic realm ="Login required !!"'}

@app.route('/user/update' , methods = [ 'PUT'])
@token_required
def user_update(current_user):
    data = request.get_json()
    # record = User.query.filter_by(id = id).first()
    try:
        # current_user.name = data['name']
        # current_user.mobile = data['mobile']
        # current_user.license = data['license']
        for k,v in data.items():
            setattr(current_user,k,v)

        current_user.save()
    except:
            msg = { 'Message': 'Profile update failed'}
            return jsonify( msg ) , 401

    resp = make_response(jsonify({'Message': 'Profile update success'}))
    return resp, 200


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
    except ex as e:
        return jsonify({'Message': 'Car Registration failed'}), 401
    return jsonify({'Message': 'Car registration successful'}), 201

@app.route('/car/update', methods= ['PUT'])
@token_required
def car_update(current_user):
    # id = current_user.id
    data = request.get_json()
    print(data, " car update")
    car = Car.query.filter_by(id = data['id']).first()


    try:
        car.maker = data['maker']
        car.model = data['model']
        car.subModel = data['subModel']
        car.yearOfMaking = data['yearOfMaking']
        car.price = data['price']
        car.registration = data['registration']
        db.session.commit()
    except:
        return jsonify( { "Message" : "Profile update failed" } ) , 401
    return  jsonify( { "Message" : "Profile update success" }),200

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
    print("  pppp", p ,"key", key)
    records = Car.query.filter_by(registration = key).all()
    if  records:
        lst = [ i.toJSON() for i in records ]
        return jsonify({'Message': lst }), 200
    return jsonify({'Message': 'Cannot find any car with that details'}), 401

@app.route('/car/filter' , methods = [ 'GET' ] )
@token_required
def car_filter(current_user):
    model = request.args.get("model")
    maker = request.args.get("maker")
    cars = Car.query.filter_by(model = model , maker = maker ).all()
    if  cars:
        lst = [ i.toJSON() for i in cars]
        return jsonify({'Message': lst }), 200
    return jsonify({'Message': 'Cannot find any car with that details'}), 401
