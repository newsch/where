#!/usr/bin/env python3
""" main webapp for project """
import os, re
from flask import Flask, request, jsonify
from flask import render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from locations import sample_locations

import pdb


PROTECTED_NAMES = [
    'add',
    'admin',
    'remove',
    '404'
]

app = Flask(__name__)
if os.path.isfile('config.py'):
    app.config.from_object('config')
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


class InvalidName(Exception):
    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidName)
def handle_invalid_name(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    link = db.Column(db.Text())
    public = db.Column(db.Boolean(), default=True)

    def __init__(self, name, link, public=True):
        if name.lower() in PROTECTED_NAMES:
            raise InvalidName('Given name is protected.')

        self.name = name.lower()  # set name to lowercase
        self.link = link
        self.public = public

    def __repr__(self):
        return '<{} --> {}>'.format(self.name, self.link)

def str_to_bool(data):
    if data.lower() == 'true':
        return True
    elif data.lower() == 'false':
        return False
    else:
        return None

@app.route('/', methods=['POST', 'GET'])
def index():
    print(request.method)
    if request.method == 'POST':  # handle additions to list
        print(request)
        print(request.form)
        new_location = Location(
            request.form['name'],
            request.form['link'],
            str_to_bool(request.form['public'])
        )
        print('New location: {}'.format(new_location))
        try:
            db.session.add(new_location)
            db.session.commit()
        except exc.IntegrityError as err:
            db.session.rollback()
            raise InvalidName('Name already exists.',payload={'message':err})
        finally:
            db.session.close()
        print('added {name}: {link}'.format(**request.form))
        return redirect('/')
    else:  # return index page
        locations = Location.query.filter_by(public=True).order_by(Location.name)
        print('locations: {}'.format(locations))
        return render_template('index.html', locations=locations)


@app.route('/<location>')
def find_route(location):
    result = Location.query.filter_by(name=location.lower()).first()
    if result:
        return redirect(result.link)
    else:
        return render_template('404.html'), 404


@app.route('/add')
def add_route():
    return render_template('add_route.html')


@app.route('/remove', methods=['POST', 'GET'])
def remove_routes():
    if request.method == 'POST':  # remove items
        print(request.method)
        request_dict = dict(request.form)
        for name, value in request_dict.items():
            print('removing {}'.format(name))
            Location.query.filter_by(name=name).delete()
        db.session.commit()
        return redirect('/')
    else:
        locations = Location.query.order_by(Location.name).all()
        return render_template('remove_routes.html', locations=locations)


@app.route('/404')
def no_page():
    return render_template('404.html')


if __name__ == '__main__':
    app.debug = True  # updates the page as the code is saved
    HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    PORT = int(os.environ.get('PORT', 9001))
    app.run(host='0.0.0.0', port=PORT)
