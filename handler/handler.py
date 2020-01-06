from flask import request,jsonify,session,render_template
from flask_restful import Resource,reqparse
import numpy as np
import pandas as pd
import sys
import json
# sys.path.insert(0, './functions')
sys.path.insert(0, './module')
import functions

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
            # newdata = data.filter([args['arg1']], axis=1)
            distribution = {'Colnames':[],'Values':[],'Descriptions':[]}
            colname = df_obj.data_type[df_obj.data_type.col_type == "numeric"].col_name.to_list()
            for x in colname:
                distribution['Colnames'].append(x)
                distribution_df = df_obj.df.filter([x], axis=1)
                distribution_df.columns = ['value']
                distribution['Values'].append({x:distribution_df.to_dict(orient='records')})
                distribution['Descriptions'].append({x:"This graph show"})
            # newdata = data[df[df.col_type == "numeric"].col_name.to_list()]
            # use by path /d3
            return distribution, {'Access-Control-Allow-Origin': '*'}

        elif args1 == 'scatter':
            scatter = {'Colnames':[],'Values':[],'Descriptions':[]}
            corrlist = df_obj.data_comb[(df_obj.data_comb.col_1_type == "numeric") & (df_obj.data_comb.col_2_type == "numeric")].loc[:, ['col_1_name','col_2_name']].values.tolist()
            for corr in corrlist:
                str1 = ','.join([str(elem) for elem in corr]) 
                temp = df_obj.df[corr]
                temp.columns = ['x','y']
                temp = temp.to_dict(orient='records')
                scatter['Colnames'].append(str1)
                scatter['Values'].append({str1:temp})
                scatter['Descriptions'].append({str1:"This graph show"})
            return scatter, {'Access-Control-Allow-Origin': '*'}

        elif args1 == 'heatmap':
            print(df_obj.df.corr())
            heat = df_obj.df.corr()
            a = heat.unstack().to_dict()
            heat = {'Colnames':[],'Values':[],'Descriptions':[]}
            for a_i in a:
                print("%s %s %f"%(a_i[0],a_i[1],a[a_i]))
                heat['Values'].append({'x':a_i[0],'y':a_i[1],'value':a[a_i]})
            colname = df_obj.data_type[df_obj.data_type.col_type == "numeric"].col_name.to_list()
            for x in colname:
                heat['Colnames'].append(x)
            heat['Descriptions'].append("This graph show")
            return heat, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'boxplot':
            boxplot = {'Colnames':[],'Values':[],'Descriptions':[]}
            colname = df_obj.data_type[df_obj.data_type.col_type == "numeric"].col_name.to_list()
            for x in colname:
                boxplot['Colnames'].append(x)
                boxplot_df = df_obj.df.filter([x], axis=1)
                boxplot['Values'].append({x:boxplot_df[x].to_list()})
                boxplot['Descriptions'].append({x:"This graph show"}) 
            return boxplot, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'bar_cat':
            bar_cat = {'Colnames':[],'Values':[],'Descriptions':[]}
            for x in df_obj.cat_count:
                bar_cat['Colnames'].append(x)
                tempT = df_obj.cat_count[x].T.to_dict(orient='records')[0]
                print("this is tempT")
                print(tempT)
                bar = []
                for i in tempT:
                    bar.append({'name':i,'value':tempT[i]})
                bar_cat['Values'].append({x:bar})
                bar_cat['Descriptions'].append({x:"This graph show"})
            return bar_cat, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'bar_num':
            bar_num = {'Colnames':[],'Values':[],'Descriptions':[]}

            return bar_num, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'line':
            line = {'Colnames':[],'Values':[],'Descriptions':[]}
            
            return line, {'Access-Control-Allow-Origin': '*'}
        else:
            pass
        return jsonify(newdata.to_dict(orient='records')), {'Access-Control-Allow-Origin': '*'}
    def post(self): 
        pass
# for Upload CSV data
class Upload(Resource):
    def get(self):
        return jsonify({'status': 'ok', 'data': df_obj.df.to_dict(orient='split')}), {'Access-Control-Allow-Origin': '*'}
    def post(self):
        file = request.files['file']
        # global data
        data = pd.read_csv(file)
        # global df
        global df_obj
        df_obj = functions.Data_prep(data)
        print(df_obj.data_comb[(df_obj.data_comb.col_1_type == "numeric") & (df_obj.data_comb.col_2_type == "numeric")])
        print("scatter plot length is %d"%len(df_obj.data_comb[(df_obj.data_comb.col_1_type == "numeric") & (df_obj.data_comb.col_2_type == "numeric")].loc[:, ['col_1_name','col_2_name']].values.tolist()))
        # show numeric type columns
        print("histogram length is %d"%len(df_obj.data_type[df_obj.data_type.col_type == "numeric"].col_name.to_list()))
        data_to_session = df_obj.data_comb.to_dict(orient='records')
        session['data'] = data_to_session
        return "success", {'Access-Control-Allow-Origin': '*'}