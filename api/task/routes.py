##############################################
################# IMPORTS ####################
##############################################

from flask import Blueprint, jsonify, request
from api.models import Task
from api import db
from flask_jwt_extended import get_jwt_identity, jwt_required

task = Blueprint('task', __name__)


# CREATE A NEW TASK
@task.route('/task', methods=["POST"])
@jwt_required()
def create_tasks():

    text = request.json['text']

    current_user = get_jwt_identity()

    new_task = Task(text=text, complete=False, user_id=current_user)

    db.session.add(new_task)
    db.session.commit()

    return jsonify({'message': 'Task added!'}), 201


# GET ALL TASKS OF A USER 
@task.route('/tasks', methods=["GET"])
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
@task.route('/task/<task_id>', methods=["GET"])
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
@task.route('/task/<task_id>', methods=["PUT"])
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
@task.route('/task/<task_id>', methods=["PATCH"])
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
@task.route('/task/<task_id>', methods=["DELETE"])
@jwt_required()
def delete_task(task_id):

    current_user = get_jwt_identity()
    task = Task.query.filter_by(task_id=task_id, user_id=current_user).first()

    if not task:
        return jsonify({'message' : 'No task found!'}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message' : 'Task deleted!'}), 200
