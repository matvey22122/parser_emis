# -*- coding: utf-8 -*-
import sys
import bs4
import json
import re
import requests
from geopy.geocoders import Nominatim
from time import sleep
import traceback


def main():

    geolocator = Nominatim()

    for line in sys.stdin:

        site = json.loads(line)
        html = site['html']
        url = site['url']

        soup = bs4.BeautifulSoup(html, features="html.parser")
        info_item = soup.find('div', class_='cp-info-item spec-pad-3 ff-grbk')

        result = {
            'country': '',
            'industry': '',
            'name_company': '',
            'url': '',
            'about': '',
            'website': '',
            'incorporation_date': '',
            'country_headquarters': '',
            'operating_revenue': '',
            'russian_website': '',
            'interest_in_russia': '',
        }

        result['country'] = soup.find('a', href="/php/company-profile/IN/main.html").text
        result['industry'] = soup.find('div', class_='spec-pad-3').find_next('a').find_next('a').find_next('a').text
        result['name_company'] = soup.find('span', class_='cp-info-2').text.replace('Full name: ', '')
        result['url'] = url

        try:
            result['about'] = info_item.find('p', class_='c-66 ff-grbk').text
        except:
            sys.stderr.write('About info not found. ')

        try:
            result['website'] = info_item.find('a', target='_blank', rel='nofollow').get('href')
        except:
            sys.stderr.write('Website not found. ')

        try:
            result['incorporation_date'] = soup.find('div', class_='d-tc w-50', string=re.compile('ion Date')).parent.find('div', class_='d-tc w-50 ta-r').text
        except:
            sys.stderr.write('Incorporation Date not found. ')

        try:
            headquarters = info_item.find('span', class_='ff-grb', string=re.compile('Headquarters')).parent.text.replace('Headquarters', '').replace('  ', '').split('\n')
            town = headquarters[len(headquarters)-2].split(';')[0]
            while True:
                try:
                    location = geolocator.geocode(town)
                    country = str(location).split(', ')
                    if country[len(country)-1] == result['country']:
                        result['country_headquarters'] = '1'
                    else:
                        result['country_headquarters'] = '0'
                    break
                except:
                    sleep(1)
        except:
            sys.stderr.write('Country headquarters not found. ')

        if result['website']:
            try:
                rus = requests.get(result['website'] + '/ru', timeout=3)
                if rus.status_code == 200:
                    result['russian_website'] = '1'
                else:
                    result['russian_website'] = '0'
            except:
                sys.stderr.write('Website during connection. ')

        try:
            operating_revenue =  soup.find('div', class_='d-tc w-70', string=re.compile('operating revenue')).parent.text.replace('Total operating revenue', '')
            result['operating_revenue'] = operating_revenue[:operating_revenue.find('%')+1].replace(' ','').replace('\n', '')
        except:
            sys.stderr.write('Total operating revenue not found. ')


        if soup.find('div', class_='bgr-f6').text.count('RUS') != 0 or soup.find('div', class_='bgr-f6').text.count('Russia') != 0 or soup.find('div', class_='bgr-f6').text.count('RUSSIA') != 0 or soup.find('div', class_='es-container-cp').text.count('RUSSIA') != 0 or soup.find('div', class_='es-container-cp').text.count('RUS') != 0 or soup.find('div', class_='es-container-cp').text.count('Russia') != 0:
            result['interest_in_russia'] = '1'
        else:
            result['interest_in_russia'] = '0'


        print json.dumps(result, ensure_ascii=False).encode('utf-8')
    

if __name__ == '__main__':
    main()