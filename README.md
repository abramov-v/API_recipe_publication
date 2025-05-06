# Foodgram API — Recipe Sharing Platform

## About the Project

This API service allows users to:

- Publish Recipes: Share your favorite recipes.
- Add Recipes to Favorites: Find and save recipes from other users to easily access them in the future.
- Subscribe to Authors: Stay updated on new publications from your favorite cooks.
- Create a Shopping List: Organize your shopping and ensure you have all the necessary ingredients for your favorite dishes.


## Startup instructions

1. Clone the repository and navigate to it in the command line:

  `git@github.com:abramov-v/API_recipe_publication.git`
  
  `cd API_recipe_publication`

2. Create a file named .env and fill it with the necessary data. All required variables are available in the sample file .env.example, located in the project's root directory.

### Deployment on the server:

1. Connect to your remote server:

 `ssh -i PATH_TO_SSH_KEY/SSH_KEY_NAME YOUR_USERNAME@SERVER_IP_ADDRESS`

2. Create a directory for application on the server:

  `mkdir API_recipe_publication`

3. Install Docker Compose on the server:
   
```
  sudo apt update
  sudo apt install curl
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo apt install docker-compose
```

4. Copy the file docker-compose.yml from the directory API_recipe_publication/infra and the file .env to the directory API_recipe_publication/ on the server:

5. Run Docker Compose

   `sudo docker-compose -f /home/YOUR_USERNAME/API_recipe_publication/docker-compose.yml up -d`

6. Access the backend container using the command:

   `docker exec -it foodgram-backend-1 bash`
   
  Run migrations, collect static files, and load data into the database
  
  ```
  python manage.py makemigrations

  python manage.py migrate
  
  python manage.py collectstatic

  python manage.py loaddata tags.json

  python manage.py importingredients
  ```

7. Create a superuser

  `python manage.py createsuperuser`

8. Configure the Nginx configuration file using the nano editor:

 `sudo nano /etc/nginx/sites-enabled/default`

9. Modify the settings and save the file:

```
    server {
    index  index.html index.htm;
    client_max_body_size 50m;
    server_name [your server address] [your URL];

    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000/;
    }
```

10. Test and reload Nginx configurations

```
 sudo nginx -t
 sudo service nginx reload
```


## Technologies Stack Used in the Project:
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


## Examples of API Requests:

API Redoc Documentation is located in the project's docs directory


**List of Users GET Method**

`/api/users/`

Example Response:

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
      "first_name": "John",
      "last_name": "Smith",
      "is_subscribed": false
    }
  ]
}
```

**User Registration POST Method**
   
`/api/users/`

Example Request:
   
```json
{
  "email": "vSmith@yandex.ru",
  "username": "john.smith",
  "first_name": "John",
  "last_name": "Smith",
  "password": "Qwerty123"
}
```

Example Response:

```json
{
  "email": "vSmith@yandex.ru",
  "id": 0,
  "username": "john.smith",
  "first_name": "John",
  "last_name": "Smith"
}
```

**User Profile GET Method**

`/api/users/{id}/`

Example Response:

```json
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "John",
  "last_name": "Smith",
  "is_subscribed": false
}
```

**Tag list GET Method**

`/api/tags/`

Example Response:

```json
[
  {
    "id": 0,
    "name": "Breakfast",
    "color": "#E26C2D",
    "slug": "breakfast"
  }
]
```

**Recipes list GET Method**

`/api/recipes/`

Example Response:

```json
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Breakfast",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "John",
        "last_name": "Smith",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Boiled potatoes",
          "measurement_unit": "g",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```

**Create recipe POST Method**

`/api/recipes/`

Example Request:

```json
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Example Response:

```json
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Breakfast",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "John",
    "last_name": "Smith",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Boiled potatoes",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

## Author
**Valeriy Abramov**
- GitHub: [@abramov-v](https://github.com/abramov-v) 
- email: abramov.valeriy@hotmail.com
