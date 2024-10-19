from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]


# utility function : write changes to bookings.json database
def write(bookings):
    with open('{}/databases/bookings.json'.format("."), 'w') as f:
        json.dump({"bookings" : bookings}, f)

# homepage for the Bookings service
@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

# get the full bookings.json JSON
@app.route("/bookings", methods=['GET'])
def get_json():
    res = make_response(jsonify(bookings), 200)
    return res

# get all bookings for a given user ID
@app.route("/bookings/<userid>", methods=['GET'])
def get_bookings_for_user(userid):
    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            res = make_response(jsonify(booking),200)
            return res
    return make_response(jsonify({"error":"User ID not found"}),400)

# get the movies on air at a given date - useful for user service
@app.route("/bookings/moviesbydate/<date>", methods=['GET'])
def get_movies_by_date(date):
    # Call Showtime service
    showmovie_req = requests.get('http://127.0.0.1:3202/showmovies/' + str(date))
    if showmovie_req.status_code != 200:
        return make_response(jsonify({"error":"No movies on air at this date"}),404)
    data = showmovie_req.json()
    return make_response(jsonify(data),200)

# add a booking for a given user ID
@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
    req = request.get_json()
    movie_id = req["movieid"]
    date = req["date"]

    flag = False

    # check that the given movie is on air at the given date
    # call the Showtime service
    showtime_req = requests.get('http://127.0.0.1:3202/showmovies/' + str(date))
    if showtime_req.status_code != 200:
        return make_response(jsonify({"error":"Date does not exist"}),412)

    showtime_data = showtime_req.json()
    if not (str(movie_id) in showtime_data["movies"]):
        return make_response(jsonify({"error":"Movie is not on show this day"}),411)

    for user in bookings:
        # in case the given user already has bookings in the db
        if str(user["userid"]) == str(userid):
            for element in user["dates"]:
                # in case a booking already exist for this user and date
                if str(element["date"]) == str(date):
                    # check for duplicates
                    if movie_id in element["movies"]:
                        return make_response(jsonify({"error":"User already booked this movie at this date"}),409)
                    else :
                    # if no duplicates, add it to the list movies
                        element["movies"].append(movie_id)
                        flag = True
            # in case no bookings already exist for this user and date, create the date key and add the movie title to the list movies for this date.
            if not flag:
                user["dates"].append({
                "date" : date,
                "movies" : [movie_id]
            })
                flag = True
    # in case the user did not have any bookings in the db
    if not flag:
        # create the user and date keys and add the movie title to the list movies
        bookings.append({
      "userid": userid,
      "dates": [
        {
          "date": date,
          "movies": [movie_id]
        }
      ]
    })

    write(bookings)
    res = make_response(jsonify({"message":"booking added"}),200)
    return res

# help endpoint : displays all available endpoints for the bookings service
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


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
