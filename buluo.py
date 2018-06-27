import pymongo
import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from lxml.etree import XMLSyntaxError
from pyquery import PyQuery as pq
import re
from hashlib import md5
from json.decoder import JSONDecodeError
import csv
from multiprocess.pool import Pool

headers = {
    'Host': 'www.boolaw.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'

}

def get_page_index(page_number):
    param = '_%s.html'%(page_number)
    base_url = "http://www.boolaw.com/find/"
    url = base_url + param
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print("running get_parse_index")
        if response.status_code == 200:
            return url
        return None
    except ConnectionError:
        print('Error occured')
        return None


def parse_index(html):
    doc = pq(html)
    items = doc('#seanew_tion > h2 > a').items()
    for item in items:
        yield item.attr('href')


def get_detail(html):
    try:
        response = requests.get(html, headers=headers, timeout=10)
        print("running get_detail")
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def parse_detail(html):
    try:
        url = "http://www.boolaw.com" + html
        doc = pq(url)
        lawyer_id = doc('#lawhon_zz > div.horig_lificatll > dl > dt:nth-child(3) > span').text()
        name = doc('#lawhon_zz > div.horig_lificatll > dl > dt:nth-child(1) > span').text()
        start_time = doc('#lawhon_zz > div.horig_lificatll > dl > dd:nth-child(4) > span').text()
        status = doc('#lawhon_zz > div.horig_lificatll > dl > dt:nth-child(5) > span').text()
        office = doc('#lawhon_zz > div.horig_lificatll > dl > dd:nth-child(6) > span').text()
        location = doc('#lawhon_zz > div.horig_lificatll > dl > dd:nth-child(8) > span').text()
        skills = []
        for i in range(1, 10):
            skill = doc('#lawhon_zz > div.horig_lificatrig > ul > li:nth-child(%s) > button' %(i)).text()
            if skill:
                skills.append(skill)
            else:
                break
        return {
            'lawyer_id': lawyer_id,
            'name': name,
            'start_time': start_time,
            'status': status,
            'office': office,
            'location': location,
            'skills': skills
        }
    except XMLSyntaxError:
        return None

# def save_to_csv(data):
#     with open('lawyer.csv', 'w') as csvfile:
#         fieldnames = ['lawyer_id', 'name', 'start_time', 'status', 'office', 'location', 'skills']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#
#         writer.writeheader()
#         writer.writerow(data)

def main():
    with open('lawyer.csv', 'w') as csvfile:
        fieldnames = ['lawyer_id', 'name', 'start_time', 'status', 'office', 'location', 'skills']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for page in range(34, 51):
            print(page)
            html = get_page_index(page)
            if html:
                lawyer_urls = parse_index(html)
                for lawyer_url in lawyer_urls:
                    if lawyer_url:
                        lawyer_data = parse_detail(lawyer_url)
                        print(lawyer_data)
                        if lawyer_data:
                            writer.writeheader()
                            writer.writerow(lawyer_data)
if __name__ == "__main__":
    main()