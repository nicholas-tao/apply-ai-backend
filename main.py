from flask import Flask, jsonify, request, redirect
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import uuid
import filestorage
import re
from db import get_user, create_user, check_for_email, add_to_user, update_user, get_resume_data, new_user, validate_user, match_jobs
from mail import new_email, existing_email, new_jobs
import hash
import random
import time
from resume_parser import ResumeParser
import apply
import json

app = Flask(__name__)
cors = CORS(app)

def check(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return True if re.search(regex, email) else False

@app.route('/')
def home():
    return redirect('https://apply-ai.online/')

@app.route('/start', methods=['GET', 'POST'])
def get_email():
    if request.method == 'GET':
        email = request.args.get('email', default='invalid email')
        if check(email):
            uid = check_for_email(email)
            if get_user(uid):
                huid = hash.user_safe_hash(uid)
                existing_email(email, huid)
                return jsonify({'success': False, 'message': 'This email address is already in use. We have \
                    sent you an email to log in to access your info'})
            pin = ''.join(random.choice('0123456789') for _ in range(6))
            new_email(email, pin)
            new_user(email, pin)
            return jsonify({'success': True, 'message': 'Please enter the 6-digit email sent to you to continue.'})
        else:
            return jsonify({'success': False, 'message': 'Please enter a valid email address'})
    else:
        email = request.form.get('email', default="nope")
        pin = request.form.get('pin', default=123456)
        if validate_user(email, pin):
            uid = uuid.uuid4().hex
            create_user(uid, email)
            huid = hash.user_safe_hash(uid)
            return jsonify({'success': True, 'uid': huid})
        return jsonify({'success': False, 'message': '6 digit pin does not match. Please try again.'})


@app.route('/upload', methods=['POST'])
def resume_upload():
    huid = request.form.get('uid', default='nope')
    uid = hash.database_safe_hash(huid)
    if get_user(uid):
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No files uploaded'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Unable to detect filetype'})
        if file and file.filename.split('.')[-1].lower() == 'pdf':
            original_name = secure_filename(file.filename)
            file_name = uuid.uuid4().hex + '.pdf'
            file.save('uploads/' + file_name)
            try:
                resume_data = ResumeParser('uploads/' + file_name).extract_data()
            except:
                resume_data = {}
            file_url = filestorage.upload(file_name)
            add_to_user(uid, original_name, file_url, resume_data)
            return jsonify({'success': True, 'data': resume_data})
    return jsonify({'success': False, 'message': 'Invalid user ID.'})

@app.route('/update', methods=['POST'])
def update_resume():
    huid = request.form.get('uid')
    uid = hash.database_safe_hash(huid)
    data = json.loads(request.form.get('data'))
    if get_user(uid):
        update_user(uid, data)
        return jsonify({'success': True, 'message': 'User data has been updated.'})
    return jsonify({'success': False, 'message': 'Invalid user ID.'})

@app.route('/resume', methods=['GET'])
def get_resume():
    huid = request.args.get('uid', default='nope')
    uid = hash.database_safe_hash(huid)
    if get_user(uid):
        resume_data = get_resume_data(uid)
        if resume_data:
            return jsonify({'success': True, 'data': resume_data})
        return jsonify({'success': False})
    return jsonify({'success': False, 'message': 'Invalid user ID.'})

@app.route('/jobs', methods=['GET'])
def get_jobs():
    huid = request.args.get('uid', default='nope')
    uid = hash.database_safe_hash(huid)
    if get_user(uid):
        return jsonify({'success': True, 'data': match_jobs(uid)})
    return jsonify({'success': False, 'message': 'Invalid user ID.'})

@app.route('/apply', methods=['POST'])
def auto_apply():
    huid = request.form.get('uid', default='nope')
    uid = hash.database_safe_hash(huid)
    links = request.form.get('links', default='google.com').split(', ')
    if get_user(uid):
        for link in links:
            apply.submit(uid, link)
        plural = '' if len(links) == 1 else 's'
        return jsonify({'success': True, 'message': 'You have successfully applied to {} job{}.'.format(len(links), plural)})
    return jsonify({'success': False, 'message': 'Invalid user ID.'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)