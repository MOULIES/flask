from userorder import app, db

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key = True)

    username = db.Column(db.String(100), unique = True, nullable = False )
    ssn = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    mobilenum = db.Column(db.String(100),  nullable = False)
    password =  db.Column(db.String(200),  nullable = False)
    is_admin= db.Column(db.Boolean(),  nullable = False)
    orders = db.relationship("Order", backref= 'users', lazy = 'dynamic')


    def __init__(self, data):
        self.username = data['username']
        self.ssn = data['ssn']
        self.email = data['email']
        self.mobilenum = data['mobilenum']
        self.password = data['password']
        self.is_admin = data['is_admin']

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def toJSON(self):
        return {'username':self.username, "email":self.email , "mobilenum" = self.mobilenum }


class Order(db.Model):
        __tablename__ = "users"

        id = db.Column(db.Integer, primary_key = True)
        order_desc = db.Column(db.String(100), unique = True, nullable = False )
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = True)

        def __init__(self, data):
                # self.id = data['username']
                self.order_desc = data['order_desc']
                self.user_id = data['user_id']

        def save(self):
            db.session.add(self)
            db.session.commit()

        def delete(self):
            db.session.delete(self)
            db.session.commit()

        def toJSON(self):
            return {'id':self.id, "order_desc":self.order_desc  }
