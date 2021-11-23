###########################################
################ IMPORTS ##################
###########################################

from api import db


# USER TABLES
class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    admin = db.Column(db.Boolean, default=False)

    def __init__(self, email, username, password, admin):
        self.email = email
        self.username = username
        self.password = password
        self.admin = admin

    db.create_all()


# TASK TABLES   
class Task(db.Model):
    
    __tablename__ = 'tasks'

    task_id= db.Column(db.Integer, primary_key=True)
    text= db.Column(db.String(64))
    complete= db.Column(db.Boolean)
    user_id= db.Column(db.Integer)

    #to get the string repr
    def __str__(self):
        return f'{self.id} {self.task} {self.complete}'

    db.create_all()


# TOKEN BLOCKLIST
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    db.create_all()



# POMODORO TABLES
class Timer(db.Model):

    __tablename__ = 'timer'

    pomodoro_id = db.Column(db.Integer, primary_key=True)
    pomodoro_count = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    pomodoro_complete = db.Column(db.Boolean)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=True)

    #to get the string repr
    def __str__(self):
        return f'{self.pomodoro_id} {self.task_id} {self.pomodoro_complete}' 

    db.create_all()