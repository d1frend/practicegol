import fake_useragent
from bs4 import BeautifulSoup
import requests
import time
from fastapi import FastAPI
from src.database import session_factory
from src.models import Vacancies
from src.tables import create_tables


app = FastAPI()


#парсер
def get_links(text: str, salary: str = None):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=f"https://hh.ru/search/vacancy?text={text}&area=113&page=0&salary={salary}",
        headers={"user-agent": ua.random}
    )
    data.raise_for_status()
    soup = BeautifulSoup(data.content, "lxml")
    try:
        page_count = int(
            soup.find("div", attrs={"class": "pager"}).find_all("span", recursive=False)[-1].find("a").find(
                "span").text)
    except:
        return
    c = 0
    linki = []
    for i in range(page_count):
        try:
            data = requests.get(
                url=f"https://hh.ru/search/vacancy?text={text}&area=113&page={i}&salary={salary}",
                headers={"user-agent": ua.random}
            )
            data.raise_for_status()
            soup = BeautifulSoup(data.content, "lxml")
            for link in soup.find_all('a', attrs={'class': 'bloko-link'}):
                if '/vacancy/' in f"{link.attrs['href'].split('?')[0]}":
                    linki.append(f"{link.attrs['href'].split('?')[0]}")
                    c += 1
                    if c == 20:
                        return linki

        except Exception as e:
            print(f"{e}")
            time.sleep(1)
    else:
        return linki


def get_vacancies(link):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=link,
        headers={"user-agent": ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    with session_factory() as session:
        vacansii = Vacancies()#объект класса и я его заполняю
        try:
            name = soup.find("h1", attrs={"class": "bloko-header-section-1"}).text
            vacansii.name = name
        except:
            return
        try:
            salary = soup.find("div", attrs={'data-qa': 'vacancy-salary'}).find("span").text.replace("\xa0", '')
            vacansii.salary = salary
        except:
            salary = "Уровень дохода не указан"
            vacansii.salary = salary
        skills = [skill.find("div", recursive=False).find("div").text for skill in soup.find_all("li", attrs={"data-qa": "skills-element"})]
        if not skills:
            skills = "Уточняются на собеседовании"
            vacansii.skills = skills
        else:
            skills = ", ".join(skills)
            vacansii.skills = skills
        try:
            schedule = soup.find(attrs={"data-qa": "vacancy-view-employment-mode"}).text
            vacansii.schedule = schedule
        except:
            schedule = "График работы не указан"
            vacansii.schedule = schedule
        try:
            experience = soup.find(attrs={"data-qa": "vacancy-experience"}).text
            vacansii.experience = experience
        except:
            experience = "Не имеет значения"
            vacansii.experience = experience
        try:
            region = soup.find(attrs={"data-qa": "vacancy-view-location"}).text
            vacansii.region = region
        except:
            region = ""
            vacansii.region = region
        try:
            address = soup.find(attrs={"data-qa": "vacancy-view-raw-address"}).text
            vacansii.address = address
        except:
            address = ""
            vacansii.address = address
        session.add(vacansii)
        session.commit()#комит в бд


#роут ввода данных для парсинга
@app.get("/parsing")
def start(name: str, salary: str = None):
    data = {"items": [], "error": 1}#словарик для того, чтобы передать вакансии с базы данных на фронт (на сво)
    create_tables()#дропаю и сразу создаю бд перед началом парсинга
    try:
        for i in get_links(name, salary):
            get_vacancies(i)
            time.sleep(1)
        with session_factory() as session:
            vacs = session.query(Vacancies).all()#query это синтаксис алхимии, чтобы не писать запросы на языке sql, query параметр/query запрос, возвращает значения из всех колонок
            for vac in vacs:
                value_area = ""
                if vac.region:
                    value_area = vac.region
                else:
                    value_area = vac.address
                data["items"].append(
                    {
                        "name": vac.name,
                        "salary": vac.salary,
                        "skills": vac.skills,
                        "schedule": vac.schedule,
                        "experience": vac.experience,
                        "area": value_area,
                    }
                )

            return data
    except:
        data["error"] = 2
        return data

#фильтрация
def filtid(serch: str, colum: str):
    with session_factory() as session:
        if colum == "skills":#ДЛЯ СЕБЯ
            normvalues = session.query(Vacancies.id, Vacancies.skills).all()
        elif colum == "schedule":
            normvalues = session.query(Vacancies.id, Vacancies.schedule).all()
        elif colum == "area":
            normvalues = session.query(Vacancies.id, Vacancies.region, Vacancies.address).all()
        elif colum == "experience":
            normvalues = session.query(Vacancies.id, Vacancies.experience).all()

        normid = []
        for i in normvalues:
            if colum == "area":
                if serch in i[1] or serch in i[2]:
                    normid.append(i[0])
            else:
                if serch in i[1]:
                    normid.append(i[0])
        return normid


@app.get("/filt")
def filter(area: str = None, skills: str = None, schedule: str = None, experience: str = None):
    correct_id = set()
    correct_id_list = []
    data = {"items": [], "error": 1}
    count = 0
    with session_factory() as session:
        if area:
            norm_area_id = filtid(area, "area")
            correct_id_list += norm_area_id
            count += 1
        if skills:
            norm_skills_id = filtid(skills, "skills")
            correct_id_list += norm_skills_id
            count += 1
        if schedule:
            norm_schedule_id = filtid(schedule, "schedule")
            correct_id_list += norm_schedule_id
            count += 1
        if experience:
            norm_experience_id = filtid(experience, "experience")
            correct_id_list += norm_experience_id
            count += 1
        if count > 0:
            for i in correct_id_list:
                if correct_id_list.count(i) == count:
                    correct_id.add(i)
            vacs = session.query(Vacancies).filter(Vacancies.id.in_(list(correct_id))).all()
            for vac in vacs:
                value_area = ""
                if vac.region:
                    value_area = vac.region
                else:
                    value_area = vac.address
                data["items"].append(
                    {
                        "name": vac.name,
                        "salary": vac.salary,
                        "skills": vac.skills,
                        "schedule": vac.schedule,
                        "experience": vac.experience,
                        "area": value_area,
                    }
                )
        else:
            vacs = session.query(Vacancies).all()
            for vac in vacs:
                value_area = ""
                if vac.region:
                    value_area = vac.region
                else:
                    value_area = vac.address
                data["items"].append(
                    {
                        "name": vac.name,
                        "salary": vac.salary,
                        "skills": vac.skills,
                        "schedule": vac.schedule,
                        "experience": vac.experience,
                        "area": value_area,
                    }
                )
    if len(data["items"]) == 0:
        data["error"] = 3

    return data



"""    with session_factory() as session:
        vacs = session.query(Vacancies).filter(Vacancies.id.in_(list(correct_id))).all()
        for vac in vacs:
            value_area = ""
            if vac.region:
                value_area = vac.region
            else:
                value_area = vac.address
            data["items"].append(
                {
                    "name": vac.name,
                    "salary": vac.salary,
                    "skills": vac.skills,
                    "schedule": vac.schedule,
                    "experience": vac.experience,
                    "area": value_area,
                }
            )
        return data"""



