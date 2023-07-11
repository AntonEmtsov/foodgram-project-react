![foodgram_project_react_workflow](https://github.com/russ044/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Foodgram - Продуктовый помощник
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Снимок экрана 2023-07-10 082838](https://github.com/AntonEmtsov/foodgram-project-react/assets/93160961/cac90902-925e-4bc0-84f6-10f2aef00478)
![Снимок экрана 2023-07-10 082921](https://github.com/AntonEmtsov/foodgram-project-react/assets/93160961/a8ed9e25-cb33-4c14-be4c-53746250ed5c)
![Снимок экрана 2023-07-10 083206](https://github.com/AntonEmtsov/foodgram-project-react/assets/93160961/d0947b23-6481-4dbb-abae-696095c6dd4c)

### Технологии используемые в проекте:
- Python 3.11
- Django 4.2.3
- Django Colorfield 0.9.0
- Django Filter 23.2
- Django REST Framework 3.14.0
- Django REST Framework SimpleJWT 5.2.2
- Djoser 2.2.0
- Docker
- Psycopg2-binary 2.9.6

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
Скопируйте файлы: 
- docker-compose.yaml
- nginx/default.conf

из проекта на сервер в:
- home/<ваш_username>/docker-compose.yaml
- home/<ваш_username>/nginx/default.conf
```
scp ./docker-compose.yml user@host:/home/user/
scp ./nginx.conf user@host:/home/user/nginx.conf
```
В репозитории на GitHub необходимо прописать Secrets: 
```dotenv
# Для подключения к удаленному серверу:
HOST=127.0.0.1
USER=admin
SSH_KEY=ssh 
PASSPHRASE=passphrase

# База Данных PostgreSQL:
DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_NAME=foodgram_db
DB_HOST=localhost
DB_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin

# Настройки Django:
SECRET_KEY=secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1

# Для обновления и скачивания образов с Docker Hub:
DOCKER_USERNAME=user
DOCKER_PASSWORD=pass
```
Выполнить push в ветку main.

Создание суперюзера:
```
ssh user@host
docker container exec -it <CONTAINER ID> bash
python manage.py createsuperuser
```
### Документация API
Документация доступна по этому [адресу](https://github.com/AntonEmtsov/foodgram-project-react/blob/master/docs/openapi-schema.yml).

### Автор проекта:
- Емцов А.В.  [russ044](https://github.com/russ044)
