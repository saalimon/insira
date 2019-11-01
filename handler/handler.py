from flask import request,jsonify,session,render_template
from flask_restful import Resource
import numpy as np
import pandas as pd
import sys
import json
sys.path.insert(0, './functions')
from dataprep import data_separator,data_conversion 

blank = []
df = pd.DataFrame(blank, columns=['A', 'B', 'C'])

class Data(Resource):
    def get(self, name):
        newdata = data.filter([name], axis=1)
        print(newdata)
        return jsonify(newdata.to_dict(orient='records'))
    def post(self, name): 
        pass
# for Upload CSV data
class Upload(Resource):
    def get(self):
        return jsonify({'status': 'ok', 'data': data.to_dict(orient='split')})
    def post(self):
        file = request.files['file']
        global data
        data = pd.read_csv(file)
        print(data)
        global df
        df = data_separator(data_conversion(data))
        print(df)
        data_to_session = df.to_dict(orient='records')
        session['data'] = data_to_session
        return "success",200