
from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from auth.auth import AuthError, requires_auth
from database.models import Actor, Movie
from database.models import setup_db

load_dotenv()

ITEMS_PER_PAGE = 10

# Helper functions
def paginate(request, items):
    """Paginates given items according to the page number from the request."""
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    return [item.format() for item in items[start:end]]

def raise_abort(status_code, message):
    """Raise an HTTP abort with a custom message."""
    abort(status_code, {"message": message})

def get_json_body(request):
    """Get the JSON body from a request, or raise an error if it's not valid."""
    body = request.get_json()
    if not body:
        raise_abort(400, "Request does not contain a valid JSON body.")
    return body

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    # Actor Endpoints
    @app.route('/actors', methods=['GET'])
    @requires_auth('view:actors')
    def get_actors(payload):
        actors = Actor.query.all()
        paginated_actors = paginate(request, actors)

        if not paginated_actors:
            raise_abort(404, "No actors found in database.")

        return jsonify({
            "success": True,
            "actors": paginated_actors
        })

    @app.route('/actors', methods=['POST'])
    @requires_auth('create:actors')
    def create_actor(payload):
        body = get_json_body(request)

        name = body.get("name")
        age = body.get("age")
        gender = body.get("gender", "Other")
        movie_id = body.get("movie_id")

        if not name or not age:
            raise_abort(422, "Name and age are required.")

        new_actor = Actor(name=name, age=age, gender=gender, movie_id=movie_id)
        new_actor.insert()

        return jsonify({
            "success": True,
            "created": new_actor.id
        })

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('edit:actors')
    def update_actor(payload, actor_id):
        body = get_json_body(request)

        actor = Actor.query.filter_by(id=actor_id).one_or_none()
        if not actor:
            raise_abort(404, f"Actor with id {actor_id} not found.")

        actor.name = body.get("name", actor.name)
        actor.age = body.get("age", actor.age)
        actor.gender = body.get("gender", actor.gender)

        actor.update()

        return jsonify({
            "success": True,
            "updated": actor.id,
            "actor": actor.format()
        })

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, actor_id):
        actor = Actor.query.filter_by(id=actor_id).one_or_none()
        if not actor:
            raise_abort(404, f"Actor with id {actor_id} not found.")

        actor.delete()

        return jsonify({
            "success": True,
            "deleted": actor_id
        })

    # Movie Endpoints
    @app.route('/movies', methods=['GET'])
    @requires_auth('view:movies')
    def get_movies(payload):
        movies = Movie.query.all()
        paginated_movies = paginate(request, movies)

        if not paginated_movies:
            raise_abort(404, "No movies found in database.")

        return jsonify({
            "success": True,
            "movies": paginated_movies
        })

    @app.route('/movies', methods=['POST'])
    @requires_auth('create:movies')
    def create_movie(payload):
        body = get_json_body(request)

        title = body.get("title")
        release_date = body.get("release_date")

        if not title or not release_date:
            raise_abort(422, "Title and release date are required.")

        new_movie = Movie(title=title, release_date=release_date)
        new_movie.insert()

        return jsonify({
            "success": True,
            "created": new_movie.id
        })

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('edit:movies')
    def update_movie(payload, movie_id):
        body = get_json_body(request)

        movie = Movie.query.filter_by(id=movie_id).one_or_none()
        if not movie:
            raise_abort(404, f"Movie with id {movie_id} not found.")

        movie.title = body.get("title", movie.title)
        movie.release_date = body.get("release_date", movie.release_date)

        movie.update()

        return jsonify({
            "success": True,
            "edited": movie.id,
            "movie": movie.format()
        })

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, movie_id):
        movie = Movie.query.filter_by(id=movie_id).one_or_none()
        if not movie:
            raise_abort(404, f"Movie with id {movie_id} not found.")

        movie.delete()

        return jsonify({
            "success": True,
            "deleted": movie_id
        })

    # Error Handlers
    def get_error_message(error, default_message):
        """Extracts error message or returns default."""
        if hasattr(error, 'description'):
            return error.description
        return default_message

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": get_error_message(error, "Unprocessable")
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": get_error_message(error, "Bad Request")
        }), 400

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": get_error_message(error, "Resource Not Found")
        }), 404

    @app.errorhandler(AuthError)
    def authentication_failed(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error.get("description", "Authentication failed")
        }), error.status_code

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
