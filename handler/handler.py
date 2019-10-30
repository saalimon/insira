from flask import request
from flask_restful import Resource
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '../functions')
from dataprep import data_separator,data_conversion 

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
        #Explore current dataframe
        pass
    def post(self):
        file = request.files['file']
        data = pd.read_csv(file)
        print(data)
        df = data_separator(data_conversion(data))
        print(df)
        return 'success'