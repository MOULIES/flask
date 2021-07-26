from flask import request,session, jsonify

from userorder import app, db
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User, Order


from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    record = User.query.filter_by(username = username).first()
    if  record:
        if check_password_hash(record.password, password):
            return record
    return "NO"


@auth.error_handler
def unauthorised():
    return {"Message":"Could not verify"}, 400

@app.route("/login", methods = ['GET',"POST"])
@auth.login_required
def login():
    if request.method == "POST:
        data = auth.current_user()
        if auth != "NO":
            session['username'] = data.Username

            return {"Message":"Login successful"}, 200
            # return {"Message": "Admin registration successful"},201
        return {"Message":"Could not verify"}, 400



@app.route("/register", methods = ['GET',"POST"])
def register():
    if request.method == "POST":
         data = request.get_json()
         record = User.query.filter_by(username = data['username']).first()

         if not record:
             data['password'] = generate_password_hash(data['password'], method = "sha256")
             data['is_admin'] = 0
             try :
                 user = User(data)
                 user.save()

            except Exception as e:
                return {"Message":"Check the fields entered"}, 400

            return {"Message": "Registration successful"},201
        return {"Message":"Username already exists"}, 400



@app.route("/admin/register", methods = ['GET',"POST"])
def register1():
    if request.method == "POST":
        data = request.get_json()
         record = User.query.filter_by(username = data['username']).first()

         if not record:
             data['password'] = generate_password_hash(data['password'], method = "sha256")
             data['is_admin'] = 1
             try :
                 user = User(data)
                 user.save()
             except Exception as e:
                return {"Message":"Check the fields entered"}, 400
            return {"Message": "Admin registration successful"},201
        return {"Message":"Username already exists"}, 400





@app.route("/login", methods = ['GET',"POST"])
def login():
    if request.method == "POST:
        data = request.get_json()
        record = User.query.filter_by(username = data['username']).first()

        if record:
             if check_password_hash(record.password, data['password']):
                 session['username'] = data['username']
                 return {"Message":"Login successful"}, 200
            # return {"Message": "Admin registration successful"},201
        return {"Message":"Could not verify"}, 400


@app.route("/logout", methods=['POST']):
def logout():
    if 'username' in session:
        session.pop("username", None)
        return {"Message":"Logout successful"}, 200
    return {"Message":"Already logged out"}, 400

@app.route("/list/users")
def list_users():
    if 'username' in session:
        record = User.query.filter_by(username = session['username']).first()
        # session.pop("username", None)
        if record.is_admin :
            l = [ i.toJSON() for i in User.query.all()]

            return {"Message":l}, 200
        return {"Message":"You have no rights to access"}, 400
    return {"Message":"Login to proceed"}, 400

@app.route("/user/<id>")
def list_use(id):
    if 'username' in session:
        record = User.query.filter_by(username = session['username']).first()
        # session.pop("username", None)
        if record.is_admin :
            log = User.query.filter_by(id  = id ).first()
            # l = [ i.toJSON() for i in User.query.all()]
            return { "Message":log.toJSON() }, 200
        return {"Message":"You have no rights to access"}, 400
    return {"Message":"Login to proceed"}, 400


@app.route("/user/delete/<id>", methods = ['DELETE'])
def delete_users(id):
    if isinstance(id, str):
        return {"Message":"Enter a valid user id"}, 400
    if 'username' in session:
        record = User.query.filter_by(username = session['username']).first()
        # session.pop("username", None)
        if record.is_admin :
            log = User.query.filter_by(id  = id ).first()
            # l = [ i.toJSON() for i in User.query.all()]
            return { "Message":log.toJSON() }, 200
        return {"Message":"You have no rights to access"}, 400
    return {"Message":"Login to proceed"}, 400


@app.route("user/createorder", methods=['GET', "POST"])
def createorder():
    if request.method == "POST" :
        if 'username' in session:
            record = User.query.filter_by(username = session['username']).first()
            data = request.get_json()
            data['user_id']= record.id
            try:
                o = Order(data)
                o.save()
            except Exception as e:
               return {"Message":"Check the fields entered"}, 400
            # session.pop("username", None)
            return {"Message":"Order completed"}, 200
        return {"Message":"Login to proceed"}, 400


@app.route("/user/orders")
def orders():
    if 'username' in session:
        record = User.query.filter_by(username = session['username']).first()
        logs = Order.query.filter_by(user_id = record.id ).all()
        res = [  i.toJSON() for i in logs ]
        return {"Message": register}, 200
    return {"Message":"Login to proceed"}, 400


@app.errorhandler(404)
def errorpage(e):
    return {"Message": "Please check url"},404
