import pyrebase
import json
import uuid
import base64

def db():
    config = open('firebase.json', 'r').read()
    firebase = pyrebase.initialize_app(json.loads(config))
    return firebase.database()

def get_db():
    return json.loads(json.dumps(db().get().val()))

def check_for_email(email):
    # checks if email exists in user db and returns uid if it does
    try:
        users = get_db()['users']
        for user in users:
            if users[user]['email'] == email:
                return users[user]['uid']
        return False
    except:
        return False

def get_resume_data(uid):
    # gets the resume_data json from a uid
    try:
        users = get_db()['users']
        for user in users:
            if user['uid'] == uid:
                return user['resume_data']
        return False
    except:
        return False

def get_user(uid):
    # check if a user with uid exists or not
    try:
        user = get_db()['users'][uid]
        return user
    except:
        return False

def create_user(uid, email):
    # creates user of uid with email
    db().child('users').child(uid).set({'email': email, 'uid': uid})

def add_to_user(uid, filename, file_url, resume_data):
    # adds resume to user db
    db().child('users').child(uid).update({'filename': filename, 'file_url': file_url, 'resume_data': resume_data})

def update_user(uid, resume_data):
    # updates resume information
    db().child('users').child(uid).update({'resume_data': resume_data})

def new_user(email, pin):
    # add email and pin to verification list
    urlsafe_email = base64.b64encode(email.encode("ascii")).decode("ascii")
    db().child('verification').child(urlsafe_email).set({'email': email, 'pin': pin})

def validate_user(email, pin):
    # check if email exists in verification db with matching pin
    try:
        users = get_db()['verification']
        for user in users:
            if users[user]['email'] == email:
                if users[user]['pin'] == pin:
                    return True
                else:
                    return False
        return False
    except:
        return False