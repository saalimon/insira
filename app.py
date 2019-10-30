from flask import Flask, jsonify, render_template
from flask_restful import Resource, Api
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, './handler')
from handler import Data, Upload

app = Flask(__name__)
api = Api(app)
#root for test upload
@app.route('/')
def home():
    return render_template('index.html')

api.add_resource(Upload, '/data')
api.add_resource(Data, '/data/<string:name>')

app.run(port=5000)