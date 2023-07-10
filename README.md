![foodgram_project_react_workflow](https://github.com/russ044/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
# Foodgram - Продуктовый помощник

![Снимок экрана 2023-07-10 082838](https://github.com/AntonEmtsov/foodgram-project-react/assets/93160961/cac90902-925e-4bc0-84f6-10f2aef00478)
![Снимок экрана 2023-07-10 082921](https://github.com/AntonEmtsov/foodgram-project-react/assets/93160961/a8ed9e25-cb33-4c14-be4c-53746250ed5c)
![Снимок экрана 2023-07-10 083206](https://github.com/AntonEmtsov/foodgram-project-react/assets/93160961/d0947b23-6481-4dbb-abae-696095c6dd4c)

### Технологии используемые в проекте:
- python 3.8
- django 4.1.3
- django-colorfield 0.8.0
- django-filter 22.1
- djangorestframework 3.14.0
- djangorestframework-simplejwt 4.8.0
- djoser 2.1.0
- Docker 20.10.20
- psycopg2-binary 2.9.5

### Как запустить проект:
Клонировать репозиторий и перейдти в него в командной строке с помощью команд:
```sh
git clone https://github.com/russ044/foodgram-project-react.git
cd foodgram-project-react
```

Подготовить сервер для развертывания приложения:
```
sudo apt update
sudo apt install docker.io
sudo apt-get install docker-compose-plugin
```
Скопируйте файлы docker-compose.yaml и nginx/default.conf из проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно:
```
scp ./docker-compose.yml user@host:/home/user/
scp ./nginx.conf user@host:/home/user/nginx.conf
```
В репозитории на GitHub необходимо прописать Secrets. Переменые прописаны в yamdb_workflow.yaml.
Выполнить push в ветку main.

Создание суперюзера:
```
ssh user@host
docker container exec -it <CONTAINER ID> bash
python manage.py createsuperuser
```
### Документация API
Документация доступна по этому [адресу](http://127.0.0.1/redoc).

### Автор проекта:
- Емцов А.В.  [russ044](https://github.com/russ044)
