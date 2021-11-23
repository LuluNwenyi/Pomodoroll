##############################################
################# IMPORTS ####################
##############################################

import datetime
from flask import Blueprint, jsonify, request
from flask_bcrypt import generate_password_hash
from api.models import User
from api import db

user = Blueprint('user', __name__)

#CREATE A NEW USER
@user.route("/user", methods=["POST"])
def add_user():

    # Query to see if user exists
    user = User.query.filter_by(email=request.json['email']).first()

    if not user:

        try:
            # Register the user
            username = request.json['username']
            email = request.json['email']
            password = request.json['password']
            password = generate_password_hash(password)

            new_user = User(username=username, email=email, password=password, admin=False)

            db.session.add(new_user)
            db.session.commit()

            response = {
                "message" : "You have registered this user successfully!"
            }

            return jsonify(response)

        except Exception as e:
            
            response = {
                "message": str (e)
            }
            return jsonify(response)

    else:
        
        response = {
            'message' : 'This user already exists.'
        }
        return jsonify(response)