from flask import Flask, jsonify, request, render_template
from flask_restful import Resource, Api
import numpy as np
import pandas as pd
app = Flask(__name__)
api = Api(app)

df = pd.read_csv('mtcars.csv')

data_columns = []

#root 
@app.route('/')
def home():
    return render_template('index.html')

#test pandas show
@app.route('/pandas')
def pandas_show():
    return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
#RESTful API 
class Data(Resource):
    def get(self, name):
        pass
        # return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
        # return jsonify({'name': name})
    def post(self, name): 
        pass
# for Upload CSV data
class Upload(Resource):
    def get(self):
        pass
    def post(self):
        file = request.files['file']
        data = pd.read_csv(file)
        print(data.dtypes)
        print(data.corr())
        print(data.describe())
        data_columns = data.columns.tolist()
        print(data_columns)
        return 'success'

api.add_resource(Upload, '/data')
api.add_resource(Data, '/data/<string:name>')

app.run(port=5000)