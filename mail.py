import requests

def new_email(email, pin):
    resp = requests.post(
        "https://api.mailgun.net/v3/apply-ai.online/messages",
        auth=("api", open("mail-key.txt","r").read()),
        files=[("inline", open("templates/blue-text-removebg.png", 'rb'))],
        data={
            "from": "ApplyAI <no-reply@apply-ai.online>",
            "to": email,
            "subject": "Verify your pin",
            "text": "Hi {}, and welcome to ApplyAI!\n\nTo continue setting up your account, please \
            enter the following pin: {}\n\nThanks,\nThe ApplyAI Team".format(email, pin),
            "html": load_html(0, email, pin)
        }
    )
    print(resp.text)

def existing_email(email, huid):
    url = "https://apply-ai.web.app/update?uid={}".format(huid)
    resp = requests.post(
        "https://api.mailgun.net/v3/apply-ai.online/messages",
        auth=("api", open("mail-key.txt","r").read()),
        files=[("inline", open("templates/blue-text-removebg.png", 'rb'))],
        data={
            "from": "ApplyAI <no-reply@apply-ai.online>",
            "to": email,
            "subject": "Log in to ApplyAI",
            "text": "Hi {},\n\nTo view your account settings and open jobs, please \
            visit: {}\n\nThanks,\nThe ApplyAI Team".format(email, url),
            "html": load_html(2, email, url)
        }
    )
    print(resp.text)

def new_jobs(email, huid):
    url = "https://apply-ai.web.app/update?uid={}".format(huid)
    resp = requests.post(
        "https://api.mailgun.net/v3/apply-ai.online/messages",
        auth=("api", open("mail-key.txt","r").read()),
        files=[("inline", open("templates/blue-text-removebg.png", 'rb'))],
        data={
            "from": "ApplyAI <no-reply@apply-ai.online>",
            "to": email,
            "subject": "Log in to ApplyAI",
            "text": "Hi {},\n\nWe found new jobs that match your skillset, to view them an auto-apply, please \
            visit: {}\n\nThanks,\nThe ApplyAI Team".format(email, url),
            "html": load_html(2, email, url)
        }
    )
    print(resp.text)

def load_html(form, email, msg):
    if form == 0:
        return open('templates/pin.html', 'r').read().replace('==email==', email.split('@')[0]).replace('==pin==', msg)
    elif form == 1:
        return open('templates/new_jobs.html', 'r').read().replace('==email==', email.split('@')[0]).replace('==msg==', msg)
    else:
        return open('templates/account.html', 'r').read().replace('==email==', email.split('@')[0]).replace('==msg==', msg)
