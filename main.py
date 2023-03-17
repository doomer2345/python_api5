import os

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_vacancies_hh(language):
    url = 'https://api.hh.ru/vacancies'
    page = 0
    quantity_pages = 1
    salaries = []
    area_id = 1
    period_in_days = 30
    while page < quantity_pages:
        params = {
            'area': area_id,
            'period': period_in_days,
            'text': language,
            'page': page
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        response_content = response.json()
        vacancies = response_content["items"]
        vacancies_found = response_content["found"]
        quantity_pages = response_content["pages"]
        page += 1
        for vacancy in vacancies:
            salary = vacancy["salary"]
            if not salary:
                continue
            predicted_salary = predict_rub_salary(vacancy["salary"].get("from"), vacancy["salary"].get("to"), vacancy["salary"].get("currency"))
            if predicted_salary:
                salaries.append(predicted_salary)
    vacancies_processed = len(salaries)
    if vacancies_processed:
        average_salary = sum(salaries) // len(salaries)
    else:
        average_salary = 0
    return {
        "average_salary": average_salary,
        "vacancies_processed":  vacancies_processed,
        "vacancies_found": vacancies_found
    }


def get_vacancies_sj(sj_secret_key, language):
    url = '	https://api.superjob.ru/2.0/vacancies/'
    page = 0
    salarys = []
    while True:
        params = {
            'keyword': language,
            'town': 'Москва',
            'page': page
        }
        headers = {
            'X-Api-App-Id': sj_secret_key
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response_content = response.json()
        vacancies_sj = response_content['objects']
        vacancies_found = response_content['total']
        page += 1
        if not response_content['more']:
            break
        for vacancy_sj in vacancies_sj:
            payment_from = vacancy_sj["payment_from"]
            payment_to = vacancy_sj["payment_to"]
            payment_currency = vacancy_sj["currency"]
            predicted_salary = predict_rub_salary(payment_from, payment_to, payment_currency)
            if predicted_salary:
                salarys.append(predicted_salary)
    vacancies_processed = len(salarys)
    if vacancies_processed:
        average_salary = sum(salarys) // len(salarys)
    else:
        average_salary = 0
    return {
        "average_salary": average_salary,
        "vacancies_processed": vacancies_processed,
        "vacancies_found": vacancies_found
    }


def predict_rub_salary(salary_from, salary_to, salary_currency):
    if salary_currency != "RUR" and salary_currency != "rub":
        return None
    if  salary_from and salary_to:
        return (salary_from+salary_to)/2
    if salary_from:
        return salary_from*1.2
    if salary_to:
        return salary_to*0.8


def make_content(languages_params, title):
    table_content = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
    ]
    for language, language_params in languages_params.items():
        table_content.append([language, language_params["vacancies_found"], language_params["vacancies_processed"], language_params["average_salary"]])
    table = AsciiTable(table_content, title)
    return table.table


if __name__ == '__main__':
    load_dotenv()
    sj_secret_key = os.getenv("SUPERJOB_SECRET_KEY")
    languages = [
        "Python",
        "Java",
        "Javascript"
    ]
    languages_params_hh = {}
    languages_params_sj = {}

    for language in languages:
        languages_params_sj[language] = get_vacancies_sj(sj_secret_key, language)
        languages_params_hh[language] = get_vacancies_hh(language)
    print(make_content(languages_params_sj, title="SuperJob Moscow"))
    print(make_content(languages_params_hh, title="HeadHunter Moscow"))