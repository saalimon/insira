from flask import request,jsonify,session,render_template
from flask_restful import Resource,reqparse
import numpy as np
import pandas as pd
import sys
import json
sys.path.insert(0, './functions')
from dataprep import data_separator,data_conversion,data_combinator

blank = []
df = pd.DataFrame(blank, columns=['A', 'B', 'C'])
data = pd.DataFrame(blank, columns=['A', 'B', 'C'])

class Data(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('arg1', type=str)
        # parser.add_argument('arg2', type=str)
        args = parser.parse_args()
        args1 = args['arg1'] 
        # args2 = args['arg2'] 
        # print("arg1 = %s arg2 = %s "%(args['arg1'] , args['arg2']))
        # if args2 == None:
        #     newdata = data.filter([args['arg1']], axis=1)
        # else:
        #     newdata = data[[args1,args2]]
        # print(newdata)
        if args1 == 'distribution':
            newdata = data[df[df.col_type == "numeric"].col_name.to_list()]
        elif args1 == '2corr':
            tempdict = {}
            corrlist = data_type[(data_type.col_1_type == "numeric") & (data_type.col_2_type == "numeric")].loc[:, ['col_1_name','col_2_name']].values.tolist()
            for corr in corrlist:
                str1 = ','.join([str(elem) for elem in corr]) 
                temp = data[corr].to_dict(orient='records')
                tempdict[str1] = temp
            # newdata = data[corrlist[0]]
            return tempdict
            # return corrlist[0]
            # newdata = data[df[df.col_type == "numeric"].col_name.to_list()]
        return jsonify(newdata.to_dict(orient='records'))
    def post(self): 
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
        global data_type
        data_type = data_combinator(df)
        print(data_type)
        print(data_type[(data_type.col_1_type == "numeric") & (data_type.col_2_type == "numeric")])
        print(data_type[(data_type.col_1_type == "numeric") & (data_type.col_2_type == "numeric")].loc[:, ['col_1_name','col_2_name']].values.tolist())
        # show numeric type columns
        print(df[df.col_type == "numeric"].col_name.to_list())
        data_to_session = df.to_dict(orient='records')
        session['data'] = data_to_session
        return "success",200