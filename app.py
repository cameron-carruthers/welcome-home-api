from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

# Models
favorites = db.Table('favorites',
                     db.Column('user_id', db.Integer, db.ForeignKey(
                         'user.id'), primary_key=True),
                     db.Column('house_id', db.Integer, db.ForeignKey(
                         'house.id'), primary_key=True)
                     )


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    favorites = db.relationship(
        'House', secondary=favorites, lazy='subquery', backref=db.backref('followers', lazy=True)
    )

    def __init__(self, email):
        self.email = email


class House(db.Model):
    __tablename__ = 'house'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.String(200), unique=True)
    price = db.Column(db.Integer)
    city = db.Column(db.String(200))
    state_code = db.Column(db.String(2))
    beds = db.Column(db.Integer)
    baths = db.Column(db.Integer)
    prop_type = db.Column(db.String(200))
    thumbnail = db.Column(db.String(200))

    def __init__(self, property_id, price, city, state_code, bedrooms, bathrooms, property_type, thumbnail):
        self.property_id = property_id
        self.price = price
        self.city = city
        self.state_code = state_code
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.property_type = property_type
        self.thumbnail = thumbnail


# Schemas
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email')


user_schema = UserSchema()


class FavoriteSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_id', 'house_id')


favorite_schema = FavoriteSchema()
favorites_schema = FavoriteSchema(many=True)


class HouseSchema(ma.Schema):
    class Meta:
        fields = ('id', 'price', 'city', 'state_code', 'bedrooms',
                  'bathrooms', 'property_type', 'thumbnail')


house_schema = HouseSchema()
houses_schema = HouseSchema(many=True)


# Routes

@app.route('/user', methods=['POST'])
def add_user():

    email = request.json['email']

    new_user = User(email)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)


@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return houses_schema.jsonify(user.favorites)


@app.route('/favorite/<user_id>', methods=['POST'])
def add_house(user_id):

    property_id = request.json['property_id']
    price = request.json['price']
    city = request.json['city']
    state_code = request.json['state_code']
    beds = request.json['beds']
    baths = request.json['baths']
    prop_type = request.json['prop_type']
    thumbnail = request.json['thumbnail']

    new_house = House(property_id, price, city, state_code,
                      beds, baths, prop_type, thumbnail)

    user = User.query.get(user_id)

    db.session.add(new_house)
    new_house.followers.append(user)
    db.session.commit()

    return house_schema.jsonify(new_house)


# Run server
if __name__ == '__main__':
    app.run(debug=True)
