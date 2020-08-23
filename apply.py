import db
import mail

def submit(uid, link):
    users = db.get_db()['users']
    for user in users:
        if users[user]['uid'] == uid:
            mail.applied(users[user]['email'], link)