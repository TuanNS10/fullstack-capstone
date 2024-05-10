# FSND: Capstone Project

## Project Motivation
The Casting Agency Project models a company that is responsible for creating movies and managing and assigning actors to those movies. You are an Executive Producer within the company and are creating a system to simplify and streamline your process. 

This project is simply a workspace for practicing and showcasing different set of skills related with web development. These include data modelling, API design, authentication and authorization and cloud deployment.

### Key Dependencies & Platforms

This is the last project of the `Udacity-Full-Stack-Nanodegree` Course.
It covers following technical topics in 1 app:

1. Database modeling with `postgres` & `sqlalchemy` (see `models.py`)
2. API to performance CRUD Operations on database with `Flask` (see `app.py`)
3. Automated testing with `Unittest` (see `test_app`)
4. Authorization & Role based Authentification with `Auth0` (see `auth.py`)
5. Deployment on `Render`

### Running Locally

#### Installing Dependencies

##### Python 3.9.10

To start and run the local development server,

1. Initialize and activate a virtualenv:
  ```bash
  $ python -m venv env
  $ source env_capstone/scripts/activate
  ```

2. Install the dependencies:
```bash
$ pip install -r requirements.txt
```

#### Database Setup
With Postgres running, set up env DATABASE_URL="postgresql://postgres:password@localhost:5432/postgres":


#### Running Tests
To run the tests, run
```bash
python test_app.py
```

##### Roles

Create three roles for users under `Users & Roles` section in Auth0

* Casting Assistant
	* Can view actors and movies
* Casting Director
	* All permissions a Casting Assistant has and…
	* Add or delete an actor from the database
	* Modify actors or movies
* Executive Producer
	* All permissions a Casting Director has and…
	* Add or delete a movie from the database

##### Set JWT Tokens in `config.py`

Use the following link to create users and sign them in. This way, you can generate 

```
https://{{YOUR_DOMAIN}}/authorize?audience={{API_IDENTIFIER}}&response_type=token&client_id={{YOUR_CLIENT_ID}}&redirect_uri={{YOUR_CALLBACK_URI}}
```
## API Documentation
<a name="api"></a>

Here you can find all existing endpoints, which methods can be used, how to work with them & example responses you´ll get.

### Base URL

**_https://fullstack-capstone.onrender.com_**

### Models
There are two models:
* Movie
	* title
	* release_date
* Actor
	* name
	* age
	* gender

### Error Handling

Errors are returned as JSON objects in the following format:
```json
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Resource Not Found
- 422: Not Processable 
- 500: Internal Server Error

# <a name="get-actors"></a>
### 1. GET /actors
Get all actors

* Requires `view:actors` permission

* **Example Request:** `curl -X GET https://fullstack-capstone.onrender.com/actors`

* **Expected Result:**
```json
    {
    "actors": [
        {
            "age": 25,
            "gender": "M",
            "id": 1,
            "movie_id": 1,
            "name": "Donna"
        },
        {
            "age": 25,
            "gender": "M",
            "id": 2,
            "movie_id": 1,
            "name": "Sanh Tuan"
        }
    ],
    "success": true
}
```

# <a name="post-actors"></a>
### 2. POST /actors

Insert new actor into database.
* Requires `create:actors` permission

* Requires the name, age and gender of the actor.

* **Example Request:** (Create)
    ```json
	curl -X POST https://fullstack-capstone.onrender.com/actors \
		--header 'Content-Type: application/json' \
		--data-raw '{
			"name": "Sanh Tuan",
			"age": "25",
			"gender": "M",
            "movie_id": 1
        }'
    ```
    
* **Example Response:**
```json
    {
    "created": 1,
    "success": true
}
```

# <a name="patch-actors"></a>
### 3. PATCH /actors

Edit an existing Actor
* Require `edit:actors`

* Responds with a 404 error if <actor_id> is not found

* Update the given fields for Actor with id <actor_id>

* **Example Request:** 
	```json
    curl -X PATCH https://fullstack-capstone.onrender.com/actors/1 \
		--header 'Content-Type: application/json' \
		--data-raw '{
			"name": "Update name"
        }'
  ```

* **Example Response:**
    ```json
    {
    "actor": {
        "age": 25,
        "gender": "M",
        "id": 1,
        "movie_id": null,
        "name": "Update name"
    },
    "success": true,
    "updated": 1
}
    ```

# <a name="delete-actors"></a>
### 4. DELETE /actors

Delete an existing Actor
* Require `delete:actors` permission

* **Example Request:** `curl -X DELETE https://fullstack-capstone.onrender.com/actors/1'`

* **Example Response:**
    ```json
	{
    "deleted": 1,
    "success": true
    }
    ```

# <a name="get-movies"></a>
### 5. GET /movies

Query paginated movies.

* Require `view:movies` permission

* **Example Request:** `curl -X GET https://fullstack-capstone.onrender.com/movies'`

* **Expected Result:**
```json
    {
    "movies": [
        {
            "actors": [
                {
                    "age": 25,
                    "gender": "M",
                    "id": 2,
                    "movie_id": 1,
                    "name": "Sanh Tuan"
                }
            ],
            "id": 1,
            "release_date": "Sat, 05 Oct 2024 00:00:00 GMT",
            "title": "With you <3"
        }
    ],
    "success": true
}
```

# <a name="post-movies"></a>
### 6. POST /movies

Insert new Movie into database.

* Requires `create:movies` permission

* Requires the title and release date.

* **Example Request:** (Create)
    ```bash
	curl -X POST https://fullstack-capstone.onrender.com/movies \
		--header 'Content-Type: application/json' \
		--data-raw '{
			"title": "With you",
			"release_date": "12-05-2024"
		}'
    ```
    
* **Example Response:**
    ```bash
	{
    "created": 1,
    "success": true
    }
    ```
# <a name="patch-movies"></a>
### 7. PATCH /movies

Edit an existing Movie

* Require `edit:movies` permission

* Responds with a 404 error if <movie_id> is not found

* Update the corresponding fields for Movie with id <movie_id>

* **Example Request:** 
	```json
    curl -X PATCH https://fullstack-capstone.onrender.com/movies/1' \
		--header 'Content-Type: application/json' \
		--data-raw '{
			"title": "With you forrever"
        }'
  ```
  
* **Example Response:**
    ```json
	{
    "edited": 1,
    "movie": {
        "actors": [
            {
                "age": 25,
                "gender": "M",
                "id": 2,
                "movie_id": 1,
                "name": "Sanh Tuan"
            }
        ],
        "id": 1,
        "release_date": "Sat, 05 Oct 2024 00:00:00 GMT",
        "title": "With you forrever"
    },
    "success": true
}
    ```

# <a name="delete-movies"></a>
### 8. DELETE /movies

Delete an existing movie

* Require `delete:movies` permission

* **Example Request:** `curl -X DELETE https://fullstack-capstone.onrender.com/movies/1'`

* **Example Response:**
    ```json
	{
		"deleted": 1,
		"success": true
    }
    ```