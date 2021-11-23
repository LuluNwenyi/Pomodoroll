#----- IMPORTS -----#

from flask import Blueprint, jsonify, request
from flask_bcrypt import generate_password_hash
from api.models import User
from api import db
from api.decorators import admin_required
from flask_jwt_extended import jwt_required

admin = Blueprint('admin', __name__)

# ADMiN SiGN UP ROUTE
@admin.route('/admin', methods=['POST'])
def create_admin():

    # QUERY IF USER EXISTS
    user = User.query.filter_by(email=request.json['email']).first()

    if not user:

        try:
            # REGISTER THE USER
            username = request.json['username']
            email = request.json['email']
            password = request.json['password']
            password = generate_password_hash(password)

            new_admin = User(username=username, email=email, password=password, admin=True)

            db.session.add(new_admin)
            db.session.commit()

            response = {
                "message" : "You have registered this admin successfully!"
            }

            return jsonify(response), 201

        except Exception as e:
            
            response = {
                "message": str (e)
            }
            return jsonify(response), 400

    else:
        
        response = {
            'message' : 'This user already exists.'
        }
        return jsonify(response), 401


# TO GET ALL USERS
@admin.route('/users', methods=["GET"])
@jwt_required()
@admin_required
def users():

    all_users = User.query.all()

    app_users = []

    for user in all_users:

        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username
        user_data['email'] = user.email

        app_users.append(user_data)

    return jsonify({'users' : app_users}), 200


# TO GET ONE USER
@admin.route("/user/<id>", methods=["GET"])
@jwt_required()
@admin_required
def user_detail(id):

    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message' : 'No user found!'}), 404

    user_data = {}
    user_data['id'] = user.id
    user_data['username'] = user.username
    user_data['email'] = user.email
    
    
    return jsonify({'user' : user_data}), 200


# DELETE A USER
@admin.route("/user/<id>", methods=["DELETE"])
@jwt_required()
@admin_required
def user_delete(id):

    user = User.query.filter_by(id=id).first()

    if user:
        db.session.delete(user)
        db.session.commit()

        response = {
                "message" : "You have deleted this user successfully!"
                }     
        return jsonify(response), 200
    
    # IF USER DOESN'T EXIST
    else:
        return jsonify({'message' : 'This user does not exist.'}), 404
