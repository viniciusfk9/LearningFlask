from celery import Celery
from flask import Flask, render_template, request, flash, session, redirect, \
    url_for
from flask import jsonify
from flask_admin import Admin
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

import config
from admin import AdminView, TopicView
from api.api import api
from models import db, Users, Polls, Topics, Options


def make_celery(app):
    celery = Celery(app.import_name, broker=config.CELERY_BROKER)
    celery.conf.update(votr.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    return celery


votr = Flask(__name__)

votr.register_blueprint(api)

# load config from the config file we created earlier
votr.config.from_object('config')

# create the database
db.init_app(votr)
db.create_all(app=votr)

migrate = Migrate(votr, db, render_as_batch=True)

# create celery object
celery = make_celery(votr)

admin = Admin(votr, name='Dashboard', index_view=TopicView(
    Topics, db.session, url='/admin', endpoint='admin'))
admin.add_view(AdminView(Users, db.session))
admin.add_view(AdminView(Polls, db.session))
admin.add_view(AdminView(Options, db.session))


@votr.route('/')
def home():
    return render_template('index.html')


@votr.route('/polls', methods=['GET'])
def polls():
    return render_template('polls.html')


@votr.route('/api/polls', methods=['GET', 'POST'])
def api_polls():
    if request.method == 'POST':
        # get the poll and save it in the database
        poll = request.get_json()

        # simple validation to check if all values are properly secret
        for key, value in poll.items():
            if not value:
                return jsonify({'error': 'value for {} is empty'.format(key)})

        title = poll['title']
        options_query = lambda option: \
            Options.query.filter(Options.name.like(option))

        options = [Polls(option=Options(name=option))
                   if options_query(option).count() == 0
                   else Polls(option=options_query(option).first()) for option
                   in poll['options']]

        new_topic = Topics(title=title, options=options)

        db.session.add(new_topic)
        db.session.commit()

        return jsonify({'message': 'Poll was created succesfully'})

    else:
        # it's a GET request, return dict representations of the API
        polls = Topics.query.join(Polls).all()
        all_polls = {'Polls':  [poll.to_json() for poll in polls]}

        return jsonify(all_polls)


@votr.route('/api/polls/options')
def api_polls_options():

    all_options = [option.to_json() for option in Options.query.all()]

    return jsonify(all_options)


@votr.route('/api/poll/vote', methods=['PATCH'])
def api_poll_vote():

    poll = request.get_json()

    poll_title, option = (poll['poll_title'], poll['option'])

    join_tables = Polls.query.join(Topics).join(Options)

    # filter options
    option = join_tables.filter(Topics.title.like(poll_title)).filter(Options.name.like(option)).first()

    # increment vote_count by 1 if the option was found
    if option:
        option.vote_count += 1
        db.session.commit()

        return jsonify({'message': 'Thank you for voting'})

    return jsonify({'message': 'option or poll was not found please try again'})


@votr.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        # get the user details from the form
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # hash the password
        password = generate_password_hash(password)

        user = Users(email=email, username=username, password=password)

        db.session.add(user)
        db.session.commit()

        flash('Thanks for signing up please login')

        return redirect(url_for('home'))

    # it's a GET request, just render the template
    return render_template('signup.html')


@votr.route('/login', methods=['POST'])
def login():
    # we don't need to check the request type as flask will raise a bad request
    # error if a request aside from POST is made to this url

    username = request.form['username']
    password = request.form['password']

    # search the database for the User
    user = Users.query.filter_by(username=username).first()

    if user:
        password_hash = user.password

        if check_password_hash(password_hash, password):
            # The hash matches the password in the database log the user in
            session['user'] = username

            flash('Login was succesfull')
    else:
        # user wasn't found in the database
        flash('Username or password is incorrect please try again', 'error')

    return redirect(request.args.get('next') or url_for('home'))


@votr.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')

        flash('We hope to see you again!')

    return redirect(url_for('home'))


@votr.route('/polls/<poll_name>')
def poll(poll_name):
    return render_template('index.html')
