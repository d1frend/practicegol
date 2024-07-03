from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from fastapi import FastAPI, Form
import requests
import os
from fastapi.staticfiles import StaticFiles

app2 = FastAPI()
#связь frontend и beckend
script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
st_abs_file_path_templates = os.path.join(script_dir, "templates/")

app2.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")
templates = Jinja2Templates(directory=st_abs_file_path_templates)
"""чисто чтобы запускался css и html"""


@app2.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(name="index.html", request=request)


@app2.post('/submit/{anychoice}', response_class=HTMLResponse)
def predict(request: Request,
            anychoice: str,
            name: str = Form(default=None),
            salary: str = Form(default=None),
            area: str = Form(default=None),
            skills: str = Form(default=None),
            schedule: str = Form(default=None),
            experience: str = Form(default=None),
            value_page: int = Form(default=1)
            ):
    global global_answer
    #из формочек на фронте я передал параметры сюда, а отсюда requests.get передает их на бэк, а в answer записывается ответ с бека
    answer = {"items": []}
    if anychoice == "vacancies_pars":
        params = {
            "name": name,
            "salary": salary
        }#query пфрметры, потому что передаются в URL после знака ?, то есть не в пути
        answer = requests.get("http://back_app:5252/parsing", params=params)#requests по URL отправляет запрос и добавляет параметры, 5252 для того, чтобы понять куда обращаться, /parsing для того, чтобы понять из какого роута брать данные.
        global_answer = answer
    if anychoice == "filters_on":
        params = {
            "area": area,
            "skills": skills,
            "schedule": schedule,
            "experience": experience
        }
        answer = requests.get("http://back_app:5252/filt", params=params)#по этой ссылке я передаю параметры
        global_answer = answer
    base = global_answer.json()#в answer записывается ответ с сервера, который включает в себя статус код и данные из роута (@app.get("/parsing") и чтобы
    #получить только джейсон, без статус кода я пишу answer.json )
    max_page = (len(base["items"]) // 5) + ((len(base["items"]) % 5 + 9) // 10)
    return templates.TemplateResponse("filters.html", {"request": request, "data": base["items"], "max_page": max_page, "values_page": value_page, "error": base["error"]})