#!/usr/bin/env python3
""" main webapp for project """
import os
from flask import Flask, request
from flask import render_template, redirect, url_for
import pdb

app = Flask(__name__)

from locations import sample_locations

test_locations = sample_locations.copy()

@app.route('/', methods=['POST', 'GET'])
def index():
    print(request.method)
    if request.method == 'POST':  # handle additions to list
        print(request)
        print(request.form)
        test_locations[request.form['name']] = request.form['link']
        # pdb.set_trace()
        print('added {name}: {link}'.format(**request.form))
        return redirect('/')
    else:
        return render_template('index.html', routes=test_locations)

@app.route('/<location>')
def find_route(location):
    if (location in test_locations):
        return redirect(test_locations[location])
    else:
        return "that's not in our database :("

@app.route('/add')
def add_route():
    return render_template('add_route.html')

@app.route('/remove', methods=['POST', 'GET'])
def remove_routes():
    if request.method == 'POST':  # remove items
        print(request.method)
        request_dict = dict(request.form)
        # pdb.set_trace()
        for name, value in request_dict.items():
            print('removing {}'.format(name))
            del test_locations[name]
        return redirect('/')
    else:
        return render_template('remove_routes.html', routes=test_locations)

if __name__ == '__main__':
    app.debug = True  # updates the page as the code is saved
    HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    PORT = int(os.environ.get('PORT', 443))
    app.run(host='0.0.0.0', port=PORT)
