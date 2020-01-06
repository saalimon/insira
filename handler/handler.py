# !/usr/bin/python
# coding=utf-8
from flask import request,jsonify,session,render_template
from flask_restful import Resource,reqparse
import numpy as np
import pandas as pd
import sys
import json
sys.path.insert(0, './functions')
from dataprep import data_separator,data_conversion,data_combinator,cat_unique_count

class Data(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('arg1', type=str)
        args = parser.parse_args()
        args1 = args['arg1'] 
        if args1 == 'distribution':
            # show data distribution of single numerical data 
            distribution = {'Colnames':[],'Values':[],'Descriptions':[]}
            colname = df[df.col_type == "numeric"].col_name.to_list()
            for x in colname:
                distribution['Colnames'].append(x)
                distribution_df = data.filter([x], axis=1)
                distribution_df.columns = ['value']
                distribution['Values'].append({x:distribution_df.to_dict(orient='records')})
                distribution['Descriptions'].append({x:"กราฟนี้แสดง"})
            return distribution, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'scatter':
            # show correlation between 2 numerical data
            scatter = {'Colnames':[],'Values':[],'Descriptions':[]}
            corrlist = data_type[(data_type.col_1_type == "numeric") & (data_type.col_2_type == "numeric")].loc[:, ['col_1_name','col_2_name']].values.tolist()
            for corr in corrlist:
                str1 = ','.join([str(elem) for elem in corr]) 
                temp = data[corr]
                temp.columns = ['x','y']
                temp = temp.to_dict(orient='records')
                scatter['Colnames'].append(str1)
                scatter['Values'].append({str1:temp})
                scatter['Descriptions'].append({str1:"กราฟนี้แสดง"})
            return scatter, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'heatmap':
            # heatmap is not success now will complete within 15 dec 2019
            print(data.corr())
            heat = data.corr()
            a = heat.unstack().to_dict()
            heat = {'Colnames':[],'Values':[],'Descriptions':[]}
            for a_i in a:
                print("%s %s %f"%(a_i[0],a_i[1],a[a_i]))
                heat['Values'].append({'x':a_i[0],'y':a_i[1],'value':a[a_i]})
            colname = df[df.col_type == "numeric"].col_name.to_list()
            for x in colname:
                heat['Colnames'].append(x)
            heat['Descriptions'].append("กราฟนี้แสดง")
            return heat, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'boxplot':
            # show data qualtile and outliner of single data
            boxplot = {'Colnames':[],'Values':[],'Descriptions':[]}
            colname = df[df.col_type == "numeric"].col_name.to_list()
            for x in colname:
                boxplot['Colnames'].append(x)
                boxplot_df = data.filter([x], axis=1)
                boxplot['Values'].append({x:boxplot_df[x].to_list()})
                boxplot['Descriptions'].append({x:"กราฟนี้แสดง"}) 
            return boxplot, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'bar_cat':
            temp = cat_unique_count(data,df)
            bar_cat = {'Colnames':[],'Values':[],'Descriptions':[]}
            for x in temp:
                bar_cat['Colnames'].append(x)
                tempT = temp[x].T.to_dict(orient='records')[0]
                print("this is tempT")
                print(tempT)
                bar = []
                for i in tempT:
                    bar.append({'name':i,'value':tempT[i]})
                bar_cat['Values'].append({x:bar})
                bar_cat['Descriptions'].append({x:"กราฟนี้แสดง"})
            return bar_cat, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'bar_num':
            bar_num = {'Colnames':[],'Values':[],'Descriptions':[]}

            return bar_num, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'line':
            line = {'Colnames':[],'Values':[],'Descriptions':[]}
            
            return line, {'Access-Control-Allow-Origin': '*'}
        else:
            return "success", {'Access-Control-Allow-Origin': '*'}
        # next step is time series variable 

        return "success", {'Access-Control-Allow-Origin': '*'}
    def post(self): 
        pass
# for Upload CSV data
class Upload(Resource):
    def get(self):
        return jsonify({'status': 'ok', 'data': data.to_dict(orient='split')}), {'Access-Control-Allow-Origin': '*'}
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
        print("scatter plot length is %d"%len(data_type[(data_type.col_1_type == "numeric") & (data_type.col_2_type == "numeric")].loc[:, ['col_1_name','col_2_name']].values.tolist()))
        # show numeric type columns
        print("histogram length is %d"%len(df[df.col_type == "numeric"].col_name.to_list()))
        data_to_session = df.to_dict(orient='records')
        session['data'] = data_to_session
        return "success", {'Access-Control-Allow-Origin': '*'}