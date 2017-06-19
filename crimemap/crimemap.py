import datetime
import json
import string

import dateparser
from flask import Flask
from flask import render_template
from flask import request

import dbconfig

if dbconfig.test:
    from mockdbhelper import MockDBHelper as DBHelper
else:
    from dbhelper import DBHelper


app = Flask(__name__)
DB = DBHelper()

categories = ['mugging', 'break-in']


@app.route("/")
def home(error_message=None):
    crimes = DB.get_all_crimes()
    crimes = json.dumps(crimes)

    return render_template("home.html", crimes=crimes, categories=categories,
                           error_message=error_message)


@app.route("/submitcrime", methods=['POST'])
def submit_crime():
    category = request.form.get("category")
    if category not in categories:
        return home()

    date = format_date(request.form.get("date"))
    if not date:
        return home("Invalid date. Please use yyyy-mm-dd format")

    try:
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
    except ValueError:
        return home()

    description = sanitize_string(request.form.get("description"))

    DB.add_crime(category, date, latitude, longitude, description)

    return home()


def format_date(user_date):
    date = dateparser.parse(user_date)
    try:
        return datetime.datetime.strftime(date, "%Y-%m-%d")
    except (ValueError, TypeError) as _:
        return None


def sanitize_string(user_input):
    white_list = string.letters + string.digits + " !?$.,;:-'()&"
    return filter(lambda x: x in white_list, user_input)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
