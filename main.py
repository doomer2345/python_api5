import requests
from pprint import pprint

#base_url = "https://api.hh.ru/"


def vacancies(language):
    url = 'https://api.hh.ru/vacancies'
    page = 0
    quantity_pages = 1
    salarys = []
    while page < quantity_pages:
        params = {
            'area': 1,
            'period': 30,
            'text': language,
            'page': page
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        vacancies = response.json()["items"]
        vacancies_found = response.json()["found"]
        quantity_pages = response.json()["pages"]
        page += 1
        print(page)
        for vacanci in vacancies:
            salary = vacanci["salary"]
            if salary:
                predicted_salary = predict_rub_salary(vacanci["salary"].get("from"), vacanci["salary"].get("to"), vacanci["salary"].get("currency"))
                if predicted_salary:
                    salarys.append(predicted_salary)
    return{
        "average_salary": sum(salarys) // len(salarys),
        "vacancies_processed": len(salarys),
        "vacancies_found": vacancies_found
    }


def predict_rub_salary(salary_from, salary_to, salary_currency):
    if salary_currency != "RUR":
        return None
    if  salary_from and salary_to:
        return (salary_from+salary_to)/2
    if salary_from:
        return salary_from*1.2
    if salary_to:
        return salary_to*0.8


if __name__ == '__main__':
    languages = [
        "Python",
        "Java",
        "Javascript"
    ]
    languages_params = {}


    for language in languages:
        languages_params[language] = vacancies(language)
    pprint(languages_params)
