##############################################
################# IMPORTS ####################
##############################################

import datetime
from flask import Blueprint, jsonify, request, make_response, url_for, abort, current_app
from flask_bcrypt import check_password_hash, generate_password_hash
from .models import Task, Timer, TokenBlocklist, User
from .decorators import admin_required
from itsdangerous import URLSafeTimedSerializer
from api import db, jwt, mail, ACCESS_EXPIRES
from flask_mail import Message
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt

main = Blueprint('main', __name__)

# FUNCTION TO SEND MAIL
def send_email(to_email, subject, body):
  msg = Message(subject, recipients=[to_email])
  msg.html = body
  mail.send(msg)



# HOME PAGE
@main.route('/')
def index():

    return jsonify({"message":"Welcome to the Pomodoroll APi"})



# LOGIN A USER
@main.route('/login', methods=['POST'])
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
@main.route('/logout', methods=['DELETE'])
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
 


#CREATE A NEW USER
@main.route("/user", methods=["POST"])
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



# ADMiN SiGN UP ROUTE
@main.route('/admin', methods=['POST'])
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
@main.route('/users', methods=["GET"])
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
@main.route("/user/<id>", methods=["GET"])
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



# UPDATE A USER
@main.route("/user/<id>", methods=["PUT"])
@jwt_required()
@admin_required
def user_update(id):

    user = User.query.filter_by(id=id).first()
    
    if user:

        try:

            username = request.json['username']
            email = request.json['email']

            user.username = username
            user.email = email

            db.session.commit()

            return jsonify({"message": "User updated successfully!"}), 200

        except Exception as e:
            
            response = {
                "message": str (e)
            }
            return jsonify(response), 500

    else:
        
        response = {
            'message' : 'This user does not exist.'
        }
        return jsonify(response), 404



# DELETE A USER
@main.route("/user/<id>", methods=["DELETE"])
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
    


# FORGOT PASSWORD
@main.route('/forgot-password', methods=['POST'])
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
        recover_url = url_for("main.reset_password", token=token,  _external=True)

        # SEND THE EMAIL
        text = f"Hi {user.username}, Thanks for using our app! Please reset " + \
              f"your password by clicking on the link: {recover_url} " + \
            f"If you didn't ask for a password reset, ignore the mail."

        send_email(to_email=user.email, subject=subject, body=text)
        return jsonify({ "msg": "succesfully sent the reset mail to your email"}), 200 



# RESET PASSWORD 
@main.route('/reset/<token>', methods=['PATCH'])
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



# CREATE A NEW TASK
@main.route('/task', methods=["POST"])
@jwt_required()
def create_tasks():

    text = request.json['text']

    current_user = get_jwt_identity()

    new_task = Task(text=text, complete=False, user_id=current_user)

    db.session.add(new_task)
    db.session.commit()

    return jsonify({'message': 'Task added!'}), 201



# GET ALL TASKS OF A USER 
@main.route('/tasks', methods=["GET"])
@jwt_required()
def get_all_tasks():

    current_user = get_jwt_identity()

    tasks = Task.query.filter_by(user_id=current_user).all()

    all_tasks = []

    for task in tasks:
        task_data = {}
        task_data['task_id'] = task.task_id
        task_data['text'] = task.text
        task_data['complete'] = task.complete
        
        all_tasks.append(task_data)

    return jsonify({'tasks' : all_tasks}), 200



# GET ONE TASK
@main.route('/task/<task_id>', methods=["GET"])
@jwt_required()
def get_one_task(task_id):

    current_user = get_jwt_identity()

    task = Task.query.filter_by(task_id=task_id, user_id=current_user).first()

    if not task:
        return jsonify({'message' : 'No task found!'}), 404

    task_data = {}
    task_data['task_id'] = task.task_id
    task_data['text'] = task.text
    task_data['complete'] = task.complete
    
    return jsonify({'task' : task_data}), 200



# COMPLETE A TASK
@main.route('/task/<task_id>', methods=["PUT"])
@jwt_required()
def complete_task(task_id):

    current_user = get_jwt_identity()
    task = Task.query.filter_by(task_id=task_id, user_id=current_user).first()

    if not task:
        return jsonify({'message' : 'No task found!'}), 404

    task.complete = True
    db.session.commit()

    return jsonify({'message' : 'Task completed!'}), 200



# EDIT A TASK
@main.route('/task/<task_id>', methods=["PATCH"])
@jwt_required()
def edit_task(task_id):

    current_user = get_jwt_identity()
    text = request.json['text']
    task = Task.query.filter_by(task_id=task_id, user_id=current_user).first()

    if not task:
        return jsonify({'message' : 'No task found!'}), 404

    else:
        task.text = text
        db.session.commit()

    return jsonify({'message' : 'Task edited!'}), 200



# DELETE A TASK
@main.route('/task/<task_id>', methods=["DELETE"])
@jwt_required()
def delete_task(task_id):

    current_user = get_jwt_identity()
    task = Task.query.filter_by(task_id=task_id, user_id=current_user).first()

    if not task:
        return jsonify({'message' : 'No task found!'}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message' : 'Task deleted!'}), 200




# TIMER CONSTANTS
work = 40*60
short_break = 5*60
long_break = 15*60


# POMODORO
@main.route('/pomodoro', methods=["POST"])
@jwt_required()
def pomodoro():

    count = work
    return jsonify({'count in secs' : count}), 200

# SHORT BREAK
@main.route('/short_break', methods=["POST"])
@jwt_required()
def shortbreak():

    count = short_break
    return jsonify({'count in secs' : count}), 200

# LONG BREAK
@main.route('/long_break', methods=["POST"])
@jwt_required()
def longbreak():

    count = long_break
    return jsonify({'count in secs' : count}), 200



#START A POMODORO
@main.route('/start', methods=["POST"])
@jwt_required()
def start_timer():
        
        current_user = get_jwt_identity()

        pomodoro_count = 0

        new_pomodoro = Timer(pomodoro_count=pomodoro_count, pomodoro_complete=False, user_id=current_user)

        db.session.add(new_pomodoro)
        db.session.commit()

        pomodoro_id = new_pomodoro.pomodoro_id

        return jsonify({
            'message': 'Timer started!',
            'pomodoro_id' : pomodoro_id
            }), 200



# COMPLETE A POMODORO
@main.route('/pomodoro/<pomodoro_id>', methods=["PUT"])
@jwt_required()
def complete_timer(pomodoro_id):

    current_user = get_jwt_identity()
    timer = Timer.query.filter_by(user_id=current_user, pomodoro_id=pomodoro_id).first()

    if not timer:
        return jsonify({'message' : 'No pomodoro found!'}), 404

    timer.pomodoro_complete = True
    timer.pomodoro_count = +1
    db.session.commit()

    return jsonify({'message' : 'Pomodoro completed!'}), 200



# GET ALL POMODOROS OF A USER
@main.route('/pomodoros', methods=["GET"])
@jwt_required()
def get_all_pomodoros():

    current_user = get_jwt_identity()
    pomodoros = Timer.query.filter_by(user_id=current_user).all()

    all_pomodoros = []

    for pomodoro in pomodoros:
        pomodoro_data = {}
        pomodoro_data['pomodoro_id'] = pomodoro.pomodoro_id
        pomodoro_data['pomodoro_count'] = pomodoro.pomodoro_count
        pomodoro_data['pomodoro_complete'] = pomodoro.pomodoro_complete
        
        all_pomodoros.append(pomodoro_data)


    return jsonify({'pomodoros' : all_pomodoros}), 200



# TOTAL POMODOROS COMPLETED BY A USER
@main.route('/complete', methods=["GET"])
@jwt_required()
def get_total_pomodoros():

    current_user = get_jwt_identity()
    pomodoros = Timer.query.filter_by(user_id=current_user, pomodoro_complete=True).all()

    total = len(pomodoros)
    return jsonify ({"pomodoros completed" : total}), 200



# COMPLETE POMODOROS ON THE APP
@main.route('/all', methods=["GET"])
def all():

    pomodoros = Timer.query.filter_by(pomodoro_complete=True).all()
    
    total = len(pomodoros)
    return jsonify ({"pomodoros completed" : total}), 200

