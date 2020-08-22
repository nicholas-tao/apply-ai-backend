import pyrebase
import json
import uuid

def db():
    config = open('firebase.json', 'r').read()
    firebase = pyrebase.initialize_app(json.loads(config))
    return firebase.database()

def get_db():
    return json.loads(json.dumps(db().get().val()))

def check_for_email(email):
    try:
        users = get_db()['users']
        for user in users:
            if user['email'] == email:
                return True
        return False
    except KeyError:
        return False

def get_user(uid):
    try:
        user = get_db()['users'][uid]
        return user
    except KeyError:
        return False

def create_user(uid, email):
    db().child('users').child(uid).set({'email': email})
