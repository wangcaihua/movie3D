from os import environ

from flask import Flask, url_for
from flask import render_template

app = Flask(__name__)


'''
1. route
'''


@app.route('/')
def index():
    return render_template('index.html',
                           powered_by=environ.get('POWERED_BY', 'Deis'))

'''
2. path varables: /path/<converter:varname>
    - converter: string, int, float, path, any, uuid
    - varname: varable name
'''


@app.route('/<username>')
def name(username):
    return render_template('index.html',
                           powered_by=username)


'''
3. HTTP method
'''

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(environ.get('PORT', 5000))
    app.run(host='localhost', port=port)
