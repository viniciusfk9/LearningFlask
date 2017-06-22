import datetime

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import LoginManager
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

import config
from bitlyhelper import BitlyHelper
from forms import CreateTableForm
from forms import LoginForm
from forms import RegistrationForm
from passwordhelper import PasswordHelper
from user import User

if config.test:
    from mockdbhelper import MockDBHelper as DBHelper
else:
    from dbhelper import DBHelper

app = Flask(__name__)
login_manager = LoginManager(app)

DB = DBHelper()
PH = PasswordHelper()
BH = BitlyHelper()


app.secret_key = 'tPXJY3X37Qybz4QykV+hOyUxVQeEXf1Ao2C8upz+fGQXKsM'


@app.route("/")
def home():
    registration_form = RegistrationForm()
    return render_template("home.html", loginform=LoginForm(),
                           registrationform=registration_form)


@app.route("/login", methods=["POST"])
def login():
    form = LoginForm(request.form)
    if form.validate():
        stored_user = DB.get_user(form.loginemail.data)
        if stored_user and PH.validate_password(form.loginpassword.data,
                                                stored_user['salt'],
                                                stored_user['hashed']):
            user = User(form.loginemail.data)
            login_user(user, remember=True)
            return redirect(url_for('account'))
        form.loginemail.errors.append("Email or password invalid")
        return render_template("home.html", loginform=form,
                               registrationform=RegistrationForm())


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)


@app.route("/account")
@login_required
def account():
    tables = DB.get_tables(current_user.get_id())
    return render_template("account.html",
                           createtableform=CreateTableForm(), tables=tables)


@app.route("/register", methods=["POST"])
def register():
    form = RegistrationForm(request.form)

    if form.validate():
        if DB.get_user(form.email.data):
            form.email.errors.append("Email address already registered")
            return render_template('home.html', loginform=LoginForm(),
                                   registrationform=form)

        salt = PH.get_salt()
        hashed = PH.get_hash(form.password2.data + salt)
        DB.add_user(form.email.data, salt, hashed)

        return render_template("home.html", loginform=LoginForm(),
                               registrationform=form,
                               onloadmessage="Registration successful. Please log in.")

    return render_template("home.html", loginform=LoginForm(),
                           registrationform=form)


@app.route("/dashboard")
@login_required
def dashboard():
    now = datetime.datetime.now()
    requests = DB.get_requests(current_user.get_id())
    for req in requests:
        delta_seconds = (now - req['time']).seconds
        req['wait_minutes'] = "{}.{}".format((delta_seconds / 60),
                                             str(delta_seconds % 60).zfill(2))
    return render_template("dashboard.html", requests=requests)


@app.route("/account/createtable", methods=["POST"])
@login_required
def account_createtable():
    form = CreateTableForm(request.form)
    if form.validate():
        tableid = DB.add_table(form.tablenumber.data, current_user.get_id())
        new_url = BH.shorten_url(config.base_url + "newrequest/" + str(tableid))
        DB.update_table(tableid, new_url)

        return redirect(url_for('account'))
    return render_template("account.html", createtableform=form,
                           tables=DB.get_tables(current_user.get_id()))


@app.route("/account/deletetable")
@login_required
def account_deletetable():
    table_id = request.args.get("tableid")
    DB.delete_table(table_id)

    return redirect(url_for('account'))


@app.route("/newrequest/<tid>")
def new_request(tid):
    if DB.add_request(tid, datetime.datetime.now()):
        return "Your request has been logged and a " \
               "waiter will be with you shortly"

    return "There is already a request pending for this table. " \
           "Please be patient, a waiter will be there ASAP"


@app.route("/dashboard/resolve")
@login_required
def dashboard_resolve():
    request_id = request.args.get("request_id")
    DB.delete_request(request_id)

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)