from flask import Flask, render_template, session
from flask_restful import Resource, Api
import sys
sys.path.insert(0, './handler')
from handler import Data, Upload
from uuid import uuid4

app = Flask(__name__)
api = Api(app)
def random():
    session['number'] = str(uuid4())
    return None

@app.route('/')
def home():
    random()
    # return session['number']
    return render_template('index.html')

api.add_resource(Upload, '/data')
api.add_resource(Data, '/data/<string:name>')

app.secret_key = ".."
app.run(port=5000)