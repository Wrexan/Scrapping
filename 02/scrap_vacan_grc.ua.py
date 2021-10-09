# Вариант 1
# Необходимо собрать информацию о вакансиях на вводимую должность
# (используем input или через аргументы получаем должность) с сайтов HH(обязательно)
# и/или Superjob(по желанию). Приложение должно анализировать несколько страниц сайта
# (также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
#    Наименование вакансии.
#    Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
#    Ссылку на саму вакансию.
#    Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов.
# Общий результат можно вывести с помощью dataFrame через pandas. Сохраните в json либо csv.
# https://grc.ua/search/vacancy?st=searchVacancy&text=Python+junior
# https://rabota.ua/zapros/python-разработчик/украина
import requests
import json
from bs4 import BeautifulSoup as bs


def get_user_needs():
    err = True
    while err:
        vac_name = input('Данный скрипт ищет вакансии на сайте grc.ua.\nНазвание вакансии: ')
        vac_amt = int(input('Количество предложений: '))
        if vac_name != '' and vac_amt > 0:
            return vac_name, vac_amt


def get_vacancies_1(vac_name, vac_amt):
    url = 'https://grc.ua/search/vacancy'
    params = {
        'st': 'searchVacancy',
        'text': vac_name,
        'area': '5',
        'page': 0}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
    vac = 1
    vacancies = []
    while True:
        response = requests.get(url, params=params, headers=headers)
        response.encoding = 'UTF-8'
        soup = bs(response.text, 'html.parser')

        vacancy_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item__row_header'})
        if not vacancy_list or not response.ok:
            return ''
        for vacancy in vacancy_list:
            vacancy_data = {}
            vacancy_info = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})
            vac_name = str(vacancy_info.text)
            vac_link = str(vacancy_info['href'])
            vac_salary = vacancy.find('span',
                                      attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            if vac_salary is None:
                vac_salary_l = '0'
                vac_salary_h = '0'
                vac_salary_unit = 'USD'
            else:
                vac_salary = vac_salary.text
                pos = vac_salary.rfind(' ') + 1
                if pos > 0:
                    vac_salary_unit = vac_salary[pos:]
                    s = vac_salary[:pos].replace(u'\u202f', '').split()
                    if len(s) == 3:
                        vac_salary_l = s[0]
                        vac_salary_h = s[2]
                    else:
                        if s[0] == 'от':
                            vac_salary_l = s[1]
                            vac_salary_h = s[1]
                        else:
                            vac_salary_l = '0'
                            vac_salary_h = s[1]
                else:
                    vac_salary_l = '0'
                    vac_salary_h = '0'
                    vac_salary_unit = 'error'

            vacancy_data['name'] = str(vac) + ') ' + vac_name
            vacancy_data['sal'] = vac_salary_l
            vacancy_data['sah'] = vac_salary_h
            vacancy_data['sau'] = vac_salary_unit
            vacancy_data['url'] = vac_link
            vacancy_data['src'] = 'grc.ua'

            vacancies.append(vacancy_data)
            # print(vacancy_data)
            if vac < vac_amt:
                vac += 1
            else:
                return vacancies
        params['page'] += 1


def save_json(name, j):
    with open(name + '_vacancies.json', 'w') as outfile:
        json.dump(j, outfile)


va, am = get_user_needs()
save_json('grc.ua', get_vacancies_1(va, am))
