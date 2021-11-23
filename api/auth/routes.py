##############################################
################# IMPORTS ####################
##############################################


import datetime
from flask import Blueprint, jsonify, request, make_response, url_for, abort, current_app
from flask_bcrypt import check_password_hash, generate_password_hash
from api.models import Task, Timer, TokenBlocklist, User
from api.decorators import admin_required
from itsdangerous import URLSafeTimedSerializer
from api import db, jwt, mail, ACCESS_EXPIRES
from flask_mail import Message
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt

auth = Blueprint('auth', __name__)


# FUNCTION TO SEND MAIL
def send_email(to_email, subject, body):
  msg = Message(subject, recipients=[to_email])
  msg.html = body
  mail.send(msg)
  
  
# LOGIN A USER
@auth.route('/login', methods=['POST'])
def login():

    request_data = request.get_json()

    username = request_data['username']
    password = request_data['password']

    user = User.query.filter_by(username=username).first()

    if not user:
        return make_response('no user found', 401, {'WWW-Authenticate' : 'Basic realm= "Login required!"'})

    # CHECK IF PASSWORD IS VALID
    if user and check_password_hash(user.password, password):

        token = create_access_token(identity=username, expires_delta=ACCESS_EXPIRES)
        return jsonify({ 'token': token })

    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login required!"'})


# LOGOUT A USER
@auth.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():

    # To check for the token and to delete the token
    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None

    #To remove the access token from the database
    jti =get_jwt()['jti']
    now = datetime.datetime.utcnow()
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()

    return jsonify({"message": "Successfully logged out"})


# FORGOT PASSWORD
@auth.route('/forgot-password', methods=['POST'])
def forgot_password():
    
    # GET THE DATA FROM THE REQUEST
    email = request.json['email']

    # CHECK IF USER EXISTS
    user = User.query.filter_by(email=email).first()
    
    # IF USER EXISTS
    if user:

        # GENERATE THE TOKEN
        subject = "Password reset requested"
        ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = ts.dumps(email, salt=current_app.config["SECURITY_PASSWORD_SALT"])
        recover_url = url_for("auth.reset_password", token=token,  _external=True)

        # SEND THE EMAIL
        text = f"Hi {user.username}, Thanks for using our app! Please reset " + \
              f"your password by clicking on the link: {recover_url} " + \
            f"If you didn't ask for a password reset, ignore the mail."

        send_email(to_email=user.email, subject=subject, body=text)
        return jsonify({ "msg": "succesfully sent the reset mail to your email"}), 200 


# RESET PASSWORD 
@auth.route('/reset/<token>', methods=['PATCH'])
def reset_password(token):

    ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    # GET THE DATA FROM THE REQUEST
    password = request.json['password']

    # CHECK FOR THE EMAIL AND TOKEN
    try:
        email = ts.loads(token, salt=current_app.config["SECURITY_PASSWORD_SALT"], max_age=3600)
    except:
        abort(404)

    if email is False:
        return jsonify({"message": "Invalid token or token expired"}), 401
    
    user = User.query.filter_by(email=email).first()    
    if not user:
        return jsonify({"message": "User not found"}), 404  

    # IF THE USER EXISTS 
    if user:
        user.password = generate_password_hash(password)
        db.session.commit()
        return jsonify({'message': 'Your password has been reset!'})

    else:
        return {"message": "An error occured"},   400