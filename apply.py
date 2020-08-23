import db

def submit(uid, link):
    user = db.get_resume_data(uid)
    