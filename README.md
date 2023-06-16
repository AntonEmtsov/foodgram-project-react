# Foodgram - Продуктовый помощник
![foodgram_project_react_workflow](https://github.com/russ044/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

### Тенологии используемые в проекте:
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
scp ./docker-compose.yml russ044@158.160.38.190:/home/russ044/
scp ./nginx.conf russ044@158.160.38.190:/home/russ044/nginx.conf
```
В репозитории на GitHub необходимо прописать Secrets. Переменые прописаны в yamdb_workflow.yaml.
Выполнить push в ветку main. Приложение само пройдет тесты, обновит образ на DockerHub и выполнит деплой на сервер

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
