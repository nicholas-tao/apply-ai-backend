import PyPDF2
import spacy
from spacy.matcher import Matcher
import re
import json
from nltk.corpus import stopwords
import requests


class ResumeParser:

    def __init__(self, resume_file):
        self.resume_file = resume_file
        self.resume_text = ''
        self.nlp = spacy.load('en_core_web_sm')
        self.matcher = Matcher(self.nlp.vocab)
        self.resume = dict()

    def read_resume(self):
        url = "https://jobs.lever.co/parseResume"
        payload = {}
        files = [
        ('resume', open(self.resume_file, 'rb'))
        ]
        headers= {}

        response = requests.request("POST", url, headers=headers, data = payload, files = files)
        print(response.text)
        self.fo = response.json()

    def extract_name(self):
        return self.fo['names'][0]

    def extract_phone_number(self):
        return self.fo['phones'][0]['value']

    def extract_email(self):
        return self.fo['emails'][0]['value']

    def extract_locations(self):
        return self.fo['location']['name']

    def extract_degree(self):
        return self.fo['schools'][0]['org']

    def extract_skills(self):
        return self.fo['summary']['skills']

    def extract_jobs(self):
        jobs = self.fo['positions']
        all_work = []
        for job in jobs:
            parsed = {}
            parsed['title'] = job['title']
            parsed['company'] = job['org']
            parsed['description'] = job['summary']
            try:
                start = "{}-{}".format(job['start']['year'], job['start']['month'])
                end = "{}-{}".format(job['end']['year'], job['end']['month'])
                parsed['dates'] = '{} - {}'.format(start, end)
            except KeyError:
                parsed['dates'] = ""
            all_work.append(parsed)
        return all_work

    def extract_socials(self):
        socials = {}
        for social in self.fo['links']:
            socials[social['domain'].split('.')[0]] = social['url']
        return socials


    def extract_data(self):
        self.read_resume()
        try:
            self.resume['name'] = self.extract_name()
        except:
            self.resume['name'] = ''
        try:
            self.resume['phone_number'] =self.extract_phone_number()
        except:
            self.resume['phone_number'] = ''
        try:
            self.resume['email'] = self.extract_email()
        except:
            self.resume['email'] = ''
        try:
            self.resume['degree'] = self.extract_degree()
        except:
            self.resume['degree'] = ''
        try:
            self.resume['locations'] = self.extract_locations()
        except:
            self.resume['locations'] = ''
        try:
            self.resume['skills'] = self.extract_skills()
        except:
            self.resume['skills'] = ''
        try:
            self.resume['jobs'] = self.extract_jobs()
        except:
            self.resume['jobs'] = ''
        try:
            self.resume['socials'] = self.extract_socials()
        except:
            self.resume['socials'] = ''
        return self.resume