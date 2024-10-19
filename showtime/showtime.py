from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

# get welcome message
@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

# get full times.json JSON
@app.route("/showtimes", methods=['GET'])
def get_schedule():
    res = make_response(jsonify(schedule), 200)
    return res

# get movies on air by date
@app.route("/showmovies/<date>", methods=['GET'])
def get_movies_bydate(date):
    for sch in schedule:
        if str(sch["date"]) == str(date):
            res = make_response(jsonify(sch),200)
            return res
    return make_response(jsonify({"error":"Date not found"}),400)

# help endpoint : displays all available endpoints for the showtime service
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
