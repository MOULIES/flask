from carreseller import app, db
from flask_marshmallow import Marshmallow
ma = Marshmallow(app)
class User(db.Model):

    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column( db.Integer , primary_key = True, nullable = False)
    name = db.Column( db.String(200) , nullable = False)
    password = db.Column( db.String(200) ,  nullable = False)
    mobile = db.Column( db.String(20) ,  nullable = False)
    license = db.Column( db.String(200) ,  nullable = False)
    cars = db.relationship( "Car", backref = 'userfff' , lazy='dynamic')

    # https://www.programmersought.com/article/6134597725/
    # https://colab.research.google.com/drive/1xRm-MSwUPUWNHUUKxtYs1lCu-MYxDOmC#scrollTo=YtEgNo6HrwcR
    
    # # image = db.Column(db.LargeBinary(length=2048))
    # file = request.files['file'].read()
    # image = file.read()
    # file_name =  file.filename #form.name.data
    # session.pop("username", None)
    # session['username'] = data['username']

    #retrieve file
    # import base64
    # base64.b64encode(image )

    # resp = make_response("<h2>cookie was successfully set.</h2>")
    # resp.set_cookie('usercount', str(visit))

    def __init__(self, data):
        self.name = data['name']
        self.password = data['password']
        self.mobile = data['mobile']
        self.license = data['license']


    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def toJSON(self):
        return { 'name': self.name , "password":"self.password", "cars":self.cars}

class Car(db.Model):

    # __tablename__ = 'cars'

    id = db.Column( db.Integer , primary_key = True, nullable = False)
    maker = db.Column( db.String(200) , unique = True, nullable = False)
    user_id = db.Column( db.Integer , db.ForeignKey('users.id') , nullable = False)
    model = db.Column( db.String(200) ,  nullable = False)
    subModel = db.Column( db.String(20) ,  nullable = False)
    price = db.Column( db.Float , nullable = False )
    yearOfMaking = db.Column( db.Integer , nullable = False )
    registration = db.Column( db.String(200) ,  nullable = False)

    def __init__(self, data):
        self.maker = data['maker']
        self.user_id = data['user_id']
        self.model = data['model']
        self.subModel = data['subModel']
        self.price = data['price']
        self.yearOfMaking = data['yearOfMaking']
        self.registration = data['registration']

    def save(self):
            db.session.add(self)
            db.session.commit()

    def delete(self):
            db.session.delete(self)
            db.session.commit()

    def toJSON(self):
        return {'maker' : self.maker  ,
        'user_id' : self.user_id,
        'model' : self.model,
        'subModel' : self.subModel,
        'price' : self.price,
        'yearOfMaking' : self.yearOfMaking,
        'registration' : self.registration
        }


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        # load_instance = True


class CarSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Car
        include_fk = True
        # load_instance = True
