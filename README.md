## Доступ к серверу и админ-зону

- **URL Фудграм:** [https://foodgram.servehttp.com/](https://foodgram.servehttp.com/)
- **Сервер:** [http://158.160.85.16:8000/](http://158.160.85.16:8000/)
- **Логин:** `admin@admin.net`
- **Пароль:** `admin`

# Фудграм

Добро пожаловать в проект «Фудграм» — ваш уникальный кулинарный мир в интернете. Это место, где кулинарное искусство встречается с технологиями, чтобы предоставить вам исключительный опыт обмена рецептами.

## О проекте

«Фудграм» — это интерактивный веб-сайт, предназначенный для кулинарных энтузиастов всех уровней. Наша платформа позволяет пользователям:

- **Публиковать рецепты:** Поделитесь своими любимыми блюдами с сообществом «Фудграм». Ваш рецепт может вдохновить тысячи других!
- **Добавлять рецепты в избранное:** Найдите и сохраните рецепты других пользователей, чтобы легко находить их в будущем.
- **Подписываться на авторов:** Оставайтесь в курсе новых публикаций от ваших любимых кулинаров.
- **Создавать список покупок:** Организуйте свои покупки и убедитесь, что у вас есть все необходимые ингредиенты для приготовления избранных блюд.

Наш уникальный сервис «Список покупок» поможет вам планировать свои покупки эффективно. Выбирайте рецепты, и система автоматически сгенерирует список необходимых продуктов. Таким образом, вы можете быть уверены, что ничего не забудете при следующем походе в магазин.

## Используемые технологии в проекте:
- **Django** 3.2
- **Djangorestframework** 3.12.4
- **Djoser** 2.1.0
- **Psycopg2** 2.9.3
- **Pillow** 9.0.0
- **Flake8** 5.0.4
- **Django-colorfield** 0.6.3
- **Django-cors-headers** 3.13.0
- **Django-filter** 23.3
- **Drf-extra-fields** 3.4.0
- **Django-extensions**
- **python-dotenv** 0.21
- **Gunicorn** 20.1.0

## Инструкция по запуску

1. Клонировать репозиторий и перейти в него в командной строке:

  `git@github.com:tsulaco/foodgram-project-react.git`
  
  `cd foodgram-project-react`

2. Создать файл **.env** и заполните его необходимыми данными. Все необходимые переменные есть в образце файле **.env.example,** находящемся в корневой директории проекта. 

### Деплой на сервере

1. Подключиться к вашему удаленному серверу

 `ssh -i PATH_TO_SSH_KEY/SSH_KEY_NAME YOUR_USERNAME@SERVER_IP_ADDRESS`

2. Создать на сервере директорию foodgram-project-react:

  `mkdir foodgram-project-react`

3. Установить Docker Compose на сервер:
   
```
  sudo apt update
  sudo apt install curl
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo apt install docker-compose
```

4. Скопировать файл из директории `foodgram-project-react/infra` **docker-compose.yml** и файл **.env** в директорию **foodgram-project-react/** на сервере:

5. Запустить Docker Compose

   `sudo docker-compose -f /home/YOUR_USERNAME/foodgram-project-react/docker-compose.yml up -d`

6. Зайдите в backend контейнер ипользуя команду

   `docker exec -it foodgram-backend-1 bash`
   
  Выполнить миграции, сбор статики и загрузите данные в базу данных
  
  ```
  python manage.py makemigrations

  python manage.py migrate
  
  python manage.py collectstatic

  python manage.py loaddata tags.json

  python manage.py importingredients
  ```

7. Создать суперпользователя

  `python manage.py createsuperuser`

8. Настроить конфигурационный файл Nginx в редакторе nano:

 `sudo nano /etc/nginx/sites-enabled/default`

9. Изменить настройки и сохраните файл:

```
    server {
    index  index.html index.htm;
    client_max_body_size 50m;
    server_name [адрес вашего сервера] [адрес вашего URL];

    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000/;
    }
```

10. Проверить и перезагрузить конфигурации Nginx

```
 sudo nginx -t
 sudo service nginx reload
```

## Примеры API запросов

API доступен по адресу [https://foodgram.servehttp.com/api/](https://foodgram.servehttp.com/api/)

Документация к API -> [https://foodgram.servehttp.com/api/docs/](https://foodgram.servehttp.com/api/docs/)



Список пользователей метод GET 

`https://foodgram.servehttp.com/api/users/`

Пример ответа:

```json
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/?page=4",
  "previous": "http://foodgram.example.org/api/users/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": false
    }
  ]
}
```

Регистрация пользователя метод POST
   
`https://foodgram.servehttp.com/api/users/`

Пример запроса:
   
```json
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "password": "Qwerty123"
}
```

Пример ответа статус 201:

```json
{
  "email": "vpupkin@yandex.ru",
  "id": 0,
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин"
}
```














## Автор

**Валерий Абрамов**
- GitHub: [@tsulaco](https://github.com/tsulaco)
- Электронная почта: v.abramov12@yandex.ru
- 2024
