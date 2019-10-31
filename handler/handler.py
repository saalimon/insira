from flask import request,jsonify,session
from flask_restful import Resource
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, './functions')
from dataprep import data_separator,data_conversion 

blank = []
df = pd.DataFrame(blank, columns=['A', 'B', 'C'])

class Data(Resource):
    def get(self, name):
        pass
        # return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
        # return jsonify(df.to_json(orient='records'))
    def post(self, name): 
        pass
# for Upload CSV data
class Upload(Resource):
    def get(self):
        return jsonify({'status': 'ok', 'json_data': session['data']})
    def post(self):
        file = request.files['file']
        data = pd.read_csv(file)
        print(data)
        global df
        df = data_separator(data_conversion(data))
        print(df)
        data_to_session = df.to_dict(orient='records')
        session['data'] = data_to_session
        return "success",200