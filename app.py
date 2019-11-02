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
    return render_template('index.html')
@app.route('/d3')
def d3():
    return render_template('d3.html')
@app.route('/d3_2')
def d3_2():
    return render_template('d3_2.html')

api.add_resource(Upload, '/upload')
api.add_resource(Data, '/data')

app.secret_key = "Miyawaki Sakura"
app.run(port=5000)