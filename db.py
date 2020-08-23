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
    update_skills(uid)

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

def update_skills(uid):
    resume_data = get_resume_data(uid)
    try:
        skills = resume_data['skills'].split(', ')
        titles = []
        for job in resume_data['jobs']:
            titles.append(job['title'])
        db().child('users').child(uid).update({'skills': skills, 'jobs': titles})
    except KeyError:
        pass

def match_jobs(uid):
    resume_data = get_resume_data(uid)
    skills = resume_data['skills'].split(', ')
    titles = []
    for job in resume_data['jobs']:
        titles.append(job['title'])
    jobs = get_db()['jobs']
    top_picks = []
    for job in jobs:
        # confidence = check_similarity(skills, titles, jobs[job]['title'], jobs[job]['description'])
        # if confidence > .75:
        #      top_picks.append(jobs[job])
        # below is temporary placeholder:
        for skill in skills:
            if skill in jobs[job]['description']:
                top_picks.append(jobs[job])
    return top_picks

class JobScraper:
    def init(self):
        self.link_list = []
    def add_job(self, link, title, location, description):
        self.link_list.append(link)
        safe_link = base64.b64encode(link.encode("ascii")).decode("ascii")
        data = {
            "link": link,
            "title": title,
            "location": location,
            "description": description
        }
        db().child('jobs').child(safe_link).set(data)
    def remove_jobs(self):
        jobs = get_db()['jobs']
        for job in jobs:
            if jobs[job]['link'] not in self.link_list:
                safe_link = base64.b64encode(jobs[job]['link'].encode("ascii")).decode("ascii")
                db().child('jobs').child(safe_link).remove()