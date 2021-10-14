# -*- coding: utf-8 -*-
# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию.
# Добавить в решение со сбором вакансий(продуктов) функцию,
# которая будет добавлять только новые вакансии/продукты в вашу базу.
# https://grc.ua/search/vacancy?st=searchVacancy&text=Python+junior
# https://rabota.ua/zapros/python-разработчик/украина
import requests
import json
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient


def save_json(name, j):
    with open(name + '_vacancies.json', 'w', encoding='utf8') as outfile:
        json.dump(j, outfile)


def save_log(name, data):
    with open(name + '.log', 'w', encoding='utf8') as outfile:
        outfile.write(data)


def get_user_needs():
    vac_name = input('Данный скрипт ищет вакансии на сайте grc.ua.\nНазвание вакансии: ')
    vac_amt = input('Количество предложений: ')
    vac_amt = int(vac_amt) if vac_amt.isdigit and vac_amt != '' else 0
    return vac_name, vac_amt


def add_to_db(db_vac, src_vac, src, log):
    not_empty = db_vac.estimated_document_count()
    for vac in src_vac:
        duplicate_found = False
        if not_empty == 0:  # if db collection is empty, add one to
            db_vac.insert_one(vac)
            not_empty = 1
            continue
        for doc in db_vac.find({'name': vac.get('name'), 'emp': vac.get('emp'), 'src': src}):  # search for duplicate
            # db_vac.insert_one(vac)
            duplicate_found = True
            if log:
                print('Duplicate_found ' + str(vac.get('name')))
            if doc is None:
                if log:
                    print('None doc found')
            else:
                ddate = doc.get('date').split('.')
                vdate = vac.get('date').split('.')
                if (int(ddate[1]) != int(vdate[1])) or \
                        int(ddate[1]) == int(vdate[1]) and \
                        int(ddate[0]) < int(vdate[0]):
                    db_vac.update_one({'_id': doc.get('_id')}, {'$set': {'sal': vac.get('sal'),
                                                                         'sah': vac.get('sah'),
                                                                         'sau': vac.get('sau'),
                                                                         'date': vac.get('date')}})
                    if log:
                        print('Item updated: ' + vac.get('name'))
                else:
                    if log:
                        print('... but they are the same, skip update')
            break
        if not duplicate_found:
            db_vac.insert_one(vac)
            if log:
                print('Add item ' + str(vac.get('name')))


def get_vacancies(db_vac, vac_name, vac_amt, src, log):
    url = 'https://grc.ua/search/vacancy'
    params = {
        'st': 'searchVacancy',
        'text': vac_name,
        'area': 5,
        'page': 0}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
    vac_num = 1
    response_is_ok = True
    db_coll_input_size = db_vac.estimated_document_count()
    while response_is_ok:
        response = requests.get(url, params=params, headers=headers)
        response.encoding = 'UTF-8'
        soup = bs(response.text, 'html.parser')
        vacancies = []
        vacancy_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})
        if not response.ok:
            if response.status_code == 404:
                return str(response) + ' on url:\n' + str(response.url) + '\n' + \
                       'Database collection src_vac updated from ' + \
                       str(db_coll_input_size) + ' to ' + \
                       str(db_vac.estimated_document_count())
            else:
                return 'ERROR: ' + str(response) + ' on url:\n' + str(response.url)
        if not vacancy_list:
            return 'ERROR: ' + str(f'{vacancy_list=}') + \
                   'ERROR: ' + str(f'\n{response.text=}') + \
                   'ERROR: ' + str(f'\n{soup=}')
        for vacancy in vacancy_list:
            vacancy_data = {}
            vacancy_info = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})
            vac_name = str(vacancy_info.text)
            vac_link = str(vacancy_info['href'])
            vac_salary = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            vac_date = vacancy.find('span', attrs={'class': 'vacancy-serp-item__publication-date'
                                                            ' vacancy-serp-item__publication-date_short'}).text
            vac_employer = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
            if vac_employer:
                vac_employer = vac_employer.text.replace(u'\xa0', ' ')
            if vac_salary is None:
                vac_salary_l = None
                vac_salary_h = None
                vac_salary_unit = None
            else:
                vac_salary = vac_salary.text
                pos = vac_salary.rfind(' ') + 1
                if pos > 0:
                    vac_salary_unit = vac_salary[pos:]
                    s = vac_salary[:pos].replace(u'\u202f', '').split()
                    if len(s) == 3:
                        vac_salary_l = int(s[0])
                        vac_salary_h = int(s[2])
                    else:
                        if s[0] == 'от':
                            vac_salary_l = int(s[1])
                            vac_salary_h = int(s[1])
                        else:
                            vac_salary_l = 0
                            vac_salary_h = int(s[1])
                else:
                    vac_salary_l = None
                    vac_salary_h = None
                    vac_salary_unit = None
            vacancy_data['name'] = vac_name
            vacancy_data['emp'] = vac_employer
            vacancy_data['sal'] = vac_salary_l
            vacancy_data['sah'] = vac_salary_h
            vacancy_data['sau'] = vac_salary_unit
            vacancy_data['date'] = vac_date
            vacancy_data['url'] = vac_link
            vacancy_data['src'] = src

            vacancies.append(vacancy_data)
            if vac_amt == 0 or vac_num < vac_amt:
                vac_num += 1
            else:
                add_to_db(db_vac, vacancies, src, log)
                return str(vac_num) + ' items processed.\n' + \
                       'Database collection src_vac updated from ' + \
                       str(db_coll_input_size) + ' to ' + \
                       str(db_vac.estimated_document_count())
        add_to_db(db_vac, vacancies, src, log)
        params['page'] += 1
        if params['page'] % 10 == 0:
            print('.', end='\n')
        else:
            print('.', end='')


def init(log):
    client = MongoClient('127.0.0.1', 27017)
    db = client['vacancies']
    db_vac = db.vacancies
    vacancy, amount = get_user_needs()
    resp = get_vacancies(db_vac, vacancy, amount, 'grc.ua', log)
    if type(resp) == str:
        print(resp)
        save_log('grc.ua', resp)


init(False)  # True to spam detailed logs to console
