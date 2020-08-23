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
        file_obj = open(self.resume_file, 'rb')
        self.fo = file_obj
        pdf_reader = PyPDF2.PdfFileReader(file_obj)
        for page_number in range(pdf_reader.numPages):
            page_obj = pdf_reader.getPage(page_number)
            self.resume_text += page_obj.extractText()
        self.resume_text = self.resume_text.replace("\n", "")
        self.resume_text = self.resume_text.lower()

    def extract_name(self):
        nlp_text = self.nlp(self.resume_text)
        pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
        self.matcher.add('NAME', None, pattern)
        matches = self.matcher(nlp_text)
        for match_id, start, end in matches:
            span = nlp_text[start:end]
            return span.text

    def extract_phone_number(self):
        phone = re.findall(re.compile(
            r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'),
            self.resume_text)
        try:
            return phone[0]
        except:
            return None

    def extract_email(self):
        email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", self.resume_text)
        if email:
            try:
                return email[0].split()[0].strip(';')
            except IndexError:
                return None

    def extract_locations(self):
        locs = list()
        doc = self.nlp(self.resume_text)
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                locs.append(ent.text)
        locations = list()
        for loc in locs:
            if loc not in locations:
                locations.append(loc)
        return locations

    def extract_degree(self):

        STOPWORDS = set(stopwords.words('english'))

        EDUCATION = [
            'BE', 'B.E.', 'B.E', 'BS', 'B.S',
            'ME', 'M.E', 'M.E.', 'MS', 'M.S',
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH',
            'ICSE', 'ISC'
        ]
        nlp_text = self.nlp(self.resume_text)

        # Sentence Tokenizer
        nlp_text = [sent.string.strip() for sent in nlp_text.sents]

        edu = {}
        # Extract education degree
        for index, text in enumerate(nlp_text):
            for tex in text.split():
                # Replace all special symbols
                tex = re.sub(r'[?|$|.|!|,]', r'', tex)
                if tex.upper() in EDUCATION and tex not in STOPWORDS:
                    edu[tex] = text + nlp_text[index + 1]
        try:
            return list(edu.keys())[0]
        except:
            return None

    def extract_skills(self):
        orgs = list()
        doc = self.nlp(self.resume_text)
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                orgs.append(ent.text)
        organizations = list()
        for org in orgs:
            if org not in organizations:
                organizations.append(org)
        return organizations

    def extract_jobs(self):
        url = "https://jobs.lever.co/parseResume"
        payload = {}
        files = [
        ('resume', self.fo)
        ]
        headers= {}

        response = requests.request("POST", url, headers=headers, data = payload, files = files)
        print(response.text)
        try:
            jobs = response.json()['positions']
            positions = []
            for job in jobs:
                position = {}
                position['title'] = job['title']
                position['company'] = job['org']
                position['description'] = job['summary']
                try:
                    start = "{}-{}".format(job['start']['year'], job['start']['month'])
                    end = "{}-{}".format(job['end']['year'], job['end']['month'])
                    position['dates'] = '{} - {}'.format(start, end)
                except KeyError:
                    position['dates'] = ""
        except KeyError:
            return {'jobs': None}

    def extract_socials(self):
        socials = dict()
        linkedin = re.findall("linkedin.com/[a-z,A-Z,0-9,\-,\\,\/]*", self.resume_text)
        github = re.findall("[https://]*github.com[a-z,A-Z,0-9,\-,\\,\/]*", self.resume_text)
        socials = {'linkedin':linkedin[0] if len(linkedin)>0 else None,
                   'github':github[0] if len(github)>0 else None}
        return socials


    def extract_data(self):
        self.read_resume()
        self.resume['name'] = self.extract_name()
        self.resume['phone_number'] =self.extract_phone_number()
        self.resume['email'] = self.extract_email()
        self.resume['degree'] = self.extract_degree()
        self.resume['locations'] = self.extract_locations()
        self.resume['skills'] = self.extract_skills()
        self.resume['jobs'] = self.extract_jobs()
        self.resume['socials'] = self.extract_socials()
        return json.dumps(self.resume, indent=4)