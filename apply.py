import db
import mail

def submit(uid, link):
    users = db.get_db()['users']
    for user in users:
        if user['uid'] == uid:
            mail.applied(user['email'], link)