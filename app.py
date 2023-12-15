from functions import get_top_headlines
from functions import what_time_date_is_it_at
from flask import Flask, render_template, request
import urllib.request
import urllib.parse

# Create an instance of Flask
app = Flask(__name__)



@app.route("/")
def index():
    return render_template('index.html')

@app.route("/results", methods=["GET", "POST"])
def results():
    if request.method == "POST":
        #get the time/date (as LIST) from given location from user
        city = request.form["city"]
        keyword = request.form["keyword"]
        try:
            time_date = what_time_date_is_it_at(city) #returns [time, date]
            top_headlines = get_top_headlines(city, keyword) #USE ORIGIONAL USER LOCATION i.e "Seattle"
            return render_template('results.html', city=city, time=time_date[0],date=time_date[1], result=top_headlines, keyword=keyword)
        except urllib.error.HTTPError as e:
            print(e)
    else:
        return "Wrong HTTP method"



