from flask import Flask, render_template, request, jsonify, make_response
import json
import sys
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3200
HOST = '0.0.0.0'

with open('{}/databases/movies.json'.format("."), 'r') as jsf:
   movies = json.load(jsf)["movies"]

# utility function : write changes to movies.json database
def write(movies):
    with open('{}/databases/movies.json'.format("."), 'w') as f:
        json.dump({"movies" :movies}, f)


# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# get whole movies.json JSON 
@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(movies), 200)
    return res

# get a movie by its ID
@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            res = make_response(jsonify(movie),200)
            return res
    return make_response(jsonify({"error":"Movie ID not found"}),400)

# get a movie's title by a its ID
@app.route("/movietitlebyid", methods=['GET'])
def get_movietitle_byid():
    json = ""
    if request.args:
        req = request.args
        for movie in movies:
            if str(movie["id"]) == str(req["id"]):
                json = movie["title"]

    if not json:
        res = make_response(jsonify({"error":"movie id not found"}),400)
    else:
        res = make_response(jsonify(json),200)
    return res
 
# get a movie by its title
@app.route("/moviesbytitle", methods=['GET'])
def get_movie_bytitle():
    json = ""
    if request.args:
        req = request.args
        for movie in movies:
            if str(movie["title"]) == str(req["title"]):
                json = movie

    if not json:
        res = make_response(jsonify({"error":"movie title not found"}),400)
    else:
        res = make_response(jsonify(json),200)
    return res


# add a movie to movies.json database
@app.route("/addmovie/<movieid>", methods=['POST'])
def add_movie(movieid):
    req = request.get_json()

    for movie in movies:
        #checking for duplicates
        if str(movie["id"]) == str(movieid):
            return make_response(jsonify({"error":"movie ID already exists"}),409)

    movies.append(req)
    write(movies) 
    res = make_response(jsonify({"message":"movie added"}),200)
    return res

# updates a movie rating by providing its ID
@app.route("/movies/<movieid>/<rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movie["rating"] = rate
            res = make_response(jsonify(movie),200)
            return res

    res = make_response(jsonify({"error":"movie ID not found"}),201)
    return res

# delete a movie by providing its ID
@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            write(movies)
            return make_response(jsonify(movie),200)

    res = make_response(jsonify({"error":"movie ID not found"}),400)
    return res

## TP question1
# help endpoint : displays all available endpoints for the movie service
@app.route("/help", methods=['GET'])
def help():
    endpoints = {}
    for rule in app.url_map.iter_rules():
        # get the methods allowed for the route
        methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})  # Exclude HEAD and OPTIONS
        endpoints[str(rule)] = {
            "methods": methods,
            "endpoint": rule.endpoint
        }
    return make_response(jsonify(endpoints), 200)

# get all the movies whose rating is above the provided minimal rating
@app.route("/movies/by_rating", methods=['GET'])
def get_movies_by_rating():
    min_rating = request.args.get("min_rating", type=float)
    if min_rating is None:
        return make_response(jsonify({"error": "Minimum rating is required"}), 400)

    filtered_movies = [movie for movie in movies if float(movie["rating"]) >= min_rating]
    return make_response(jsonify(filtered_movies), 200) if filtered_movies else make_response(jsonify({"error": "No movies found with that rating or higher"}), 404)

# get movies by director
@app.route("/movies/by_director", methods=['GET'])
def get_movies_by_director():
    director_name = request.args.get("director")
    if not director_name:
        return make_response(jsonify({"error": "Director name is required"}), 400)

    filtered_movies = [movie for movie in movies if movie["director"].lower() == director_name.lower()]
    return make_response(jsonify(filtered_movies), 200) if filtered_movies else make_response(jsonify({"error": "No movies found for this director"}), 404)


if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
