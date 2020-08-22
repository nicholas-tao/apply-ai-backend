from flask import Flask, jsonify, request, redirect
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import uuid
import filestorage
import re
from db import get_user, create_user, check_for_email
from email import new_email, existing_email

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'doc', 'rtf'}

app = Flask(__name__)
cors = CORS(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return True if re.search(regex, email) else False

@app.route('/')
def home():
    return redirect('https://google.com') # this will be the frontend URL

@app.route('/start', methods=['GET', 'POST'])
def get_email():
    if request.method == 'GET':
        email = request.args.get('email', default='invalid email')
        if check(email):
            uid = check_for_email(email)
            if uid:
                huid = uid
                existing_email(email, huid)
                return jsonify({'success': False, 'message': 'This email address is already in use. We have sent you an email to log in to access your info'})
            # send email with random 6 digit code
            # add email and 6 digit code to db
            return jsonify({'success': True, 'message': 'Please enter the 6-digit email sent to you to continue.'})
        else:
            return jsonify({'success': False, 'message': 'Please enter a valid email address'})
    else:
        email = request.form.get('email', default="nope")
        pin = request.form.get('pin', default=123456)
        if email: # check db for email with matching pin
            uid = uuid.uuid4().hex # user's unique identifier
            # add uid to database with email element
            huid = uid # hash it and stuff before sending it back to the user
            return jsonify({'success': True, 'uid': huid})
        return jsonify({'success': False, 'message': '6 digit pin does not match. Please try again.'})


@app.route('/upload', methods=['POST'])
def resume_upload():
    huid = request.form.get('uid', default='nope')
    uid = huid # unhash huid
    if uid: # if user in user db with mathcing uid
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No files uploaded'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Unable to detect filetype'})
        if file and allowed_file(file.filename):
            file_name = uuid.uuid4().hex + file.filename.split('.')[-1]
            file.save('uploads/' + file_name)
            # run pdf parser and get JSON data
            resume_data = {}
            file_url = filestorage.upload(file_name)
            # update db with uid, file_name, resume_data, file_url
            return jsonify({'success': True, 'data': resume_data})
    return jsonify({'success': False, 'message': 'Invalid user ID.'})

@app.route('/update', methods=['POST', 'GET'])
def update_resume():
    if request.method == 'POST':
        uid = request.form.get('uid', default='nope')
        data = request.form.get('data', default={})
        if uid: # if uid in user db
            # update the user data in db
            return jsonify({'success': True, 'message': 'User data has been updated.'})
        return jsonify({'success': False, 'message': 'Invalid user ID.'})
    else:
        huid = request.args.get('uid', default='nope')
        uid = huid # unhash huid
        if uid: # if uid in user db
            # parse stuff whatever
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid user ID.'})

@app.route('/jobs', methods=['GET'])
def get_jobs():
    huid = request.args.get('uid', default='nope')
    uid = huid # unhash huid
    if uid: # if uid in user db
        # parse stuff whatever
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid user ID.'})

        


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)