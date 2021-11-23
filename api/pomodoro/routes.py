#----- IMPORTS -----#

from flask import Blueprint, jsonify
from api.models import Timer
from api import db
from flask_jwt_extended import get_jwt_identity, jwt_required

timer = Blueprint('timer', __name__)

# TIMER CONSTANTS
work = 40*60
short_break = 5*60
long_break = 15*60


# POMODORO
@timer.route('/pomodoro', methods=["POST"])
@jwt_required()
def work_timer():

    count = work
    return jsonify({'count in secs' : count}), 200

# SHORT BREAK
@timer.route('/short_break', methods=["POST"])
@jwt_required()
def shortbreak():

    count = short_break
    return jsonify({'count in secs' : count}), 200

# LONG BREAK
@timer.route('/long_break', methods=["POST"])
@jwt_required()
def longbreak():

    count = long_break
    return jsonify({'count in secs' : count}), 200


#START A POMODORO
@timer.route('/start', methods=["POST"])
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
@timer.route('/pomodoro/<pomodoro_id>', methods=["PUT"])
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
@timer.route('/pomodoros', methods=["GET"])
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
@timer.route('/complete', methods=["GET"])
@jwt_required()
def get_total_pomodoros():

    current_user = get_jwt_identity()
    pomodoros = Timer.query.filter_by(user_id=current_user, pomodoro_complete=True).all()

    total = len(pomodoros)
    return jsonify ({"pomodoros completed" : total}), 200


# COMPLETE POMODOROS ON THE APP
@timer.route('/all', methods=["GET"])
def all_pomodoros():

    pomodoros = Timer.query.filter_by(pomodoro_complete=True).all()
    
    total = len(pomodoros)
    return jsonify ({"pomodoros completed" : total}), 200

