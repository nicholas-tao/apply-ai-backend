import requests
from bs4 import BeautifulSoup
import json
from db import add_job, remove_jobs

class Scraper:

    def __init__(self, location='All', department='All', commitment='All'):
        self.location = location
        self.department = department
        self.commitment = commitment
        self.url = 'https://jobs.lever.co/lever'
        self.page = None
        self.jobs = list()

    def generate_url(self):
        query_params = '?'
        if self.location is not 'All':
            self.location.replace(" ", "%20")
            query_params+=f'location={self.location}&'
        if self.department is not 'All':
            self.department.replace(" ", "%20")
            query_params+=f'department={self.department}&'
        if self.commitment is not 'All':
            self.commitment.replace(" ", "%20")
            query_params+=f'commitment={self.commitment}'
        self.page = requests.get(self.url+query_params)

    def search_jobs(self):
        soup = BeautifulSoup(self.page.content, 'html.parser')
        search_results = soup.findAll("div", {"class": "posting"})
        for result in search_results:
            job = {
                'title': result.find("h5").text,
                'company': 'Lever',
                'link': result.find("a", {"class": "posting-title"})['href'],
                'location': None,
                'description': None
            }
            job_page = requests.get(job['link'])
            job_soup = BeautifulSoup(job_page.content, 'html.parser')
            location = job_soup.find("div", {"class":"sort-by-time posting-category medium-category-label"})
            if location is not None:
                job['location'] = location.text.replace(' /', '')
            skills = job_soup.find("ul", {"class": "posting-requirements plain-list"})
            if skills is not None:
                skill_list = skills.find_all("li")
                skill_list = [skill.text for skill in skill_list]
                job['description'] = ", ".join(skill_list)
            self.jobs += [job]

    def get_jobs(self):
        self.generate_url()
        self.search_jobs()
        return self.jobs


new_jobs = []
for job in Scraper().get_jobs():
    add_job(job['link'], job['title'], job['location'], job['description'], job['company'])
    new_jobs.append(job['link'])
remove_jobs(new_jobs)