# !/usr/bin/python
# coding=utf-8
from flask import request,jsonify,session,render_template
from flask_restful import Resource,reqparse
import numpy as np
import pandas as pd
import math
import sys
import json
from datetime import datetime
# sys.path.insert(0, './functions')
sys.path.insert(0, './module')
import functions
def distribution():
    # show data distribution of single numerical data 
    result = df_obj.graph_selector('histogram')
    print("result his",result)
    distribution = {'Colnames':[],'Values':[],'Descriptions':[]}
    # colname = df_obj.data_type[df_obj.data_type.col_type == "numeric"].col_name.to_list()
    if result is not None:
        colname = result['col_name']
        for x in colname:
            description = 'กราฟนี้คือการกระจายตัวของ{}'.format(x)
            distribution['Colnames'].append(x)
            distribution_df = df_obj.df.filter([x], axis=1)
            distribution_df.columns = ['value']
            distribution['Values'].append({x:distribution_df.to_dict(orient='records')})
            # description session 
            # print(result[result.col_name==x].dis_type.values[0])
            if result[result.col_name==x].dis_type.values[0] is not None:
                description_dis_type = ' โดยกราฟมีลักษณะ{}'.format(result[result.col_name==x].dis_type.values[0])
                description = description+description_dis_type
            if result[result.col_name==x].mode_type.values[0] is not None:
                description_mode_type = 'และมีลักษณะการกระจายตัวแบบ{}'.format(result[result.col_name==x].mode_type.values[0])
                description = description+description_mode_type

            distribution['Descriptions'].append({x:description})
    return distribution
def scatter():
     # show correlation between 2 numerical data
    result = df_obj.graph_selector('scatter')
    # print(result)
    scatter = {'Colnames':[],'Values':[],'Descriptions':[]}

    # corrlist = df_obj.data_comb[(df_obj.data_comb.col_1_type == "numeric") & (df_obj.data_comb.col_2_type == "numeric")].loc[:, ['col_1_name','col_2_name']].values.tolist()
    # print(result)
    if result is not None:
        corrlist = result[['col_1_name','col_2_name']].values.tolist()
        for corr in corrlist:
            description = 'กราฟนี้คือการความสัมพันธ์ระหว่าง {} และ​ {} '.format(corr[0],corr[1])
            str1 = ','.join([str(elem) for elem in corr]) 
            temp = df_obj.df[corr]
            temp.columns = ['x','y']
            temp = temp.to_dict(orient='records')
            scatter['Colnames'].append(str1)
            scatter['Values'].append({str1:temp})
            # description
            if result[(result.col_1_name==corr[0]) & (result.col_2_name==corr[1])].corr_type.values[0] is not None:
                description_corr_type = result[(result.col_1_name==corr[0]) & (result.col_2_name==corr[1])].corr_type.values[0]
                if description_corr_type == 'strong postive':
                    description_corr_type ='มีลักษณะความสัมพันธ์มากในเชิงบวก'
                elif description_corr_type == 'strong negative':
                    description_corr_type ='มีลักษณะความสัมพันธ์มากในเชิงลบ'
                elif description_corr_type == 'moderate postive':
                    description_corr_type ='มีลักษณะความสัมพันธ์ในเชิงบวก'
                elif description_corr_type == 'moderate negative':
                    description_corr_type ='มีลักษณะความสัมพันธ์ในเชิงลบ'
                description = description + description_corr_type
            scatter['Descriptions'].append({str1: description})
    return scatter
def heatmap():
    heat = df_obj.df.corr()
    a = heat.unstack().to_dict()
    heat = {'Colnames':[],'Values':[],'Descriptions':[]}
    for a_i in a:
        heat['Values'].append({'x':a_i[0],'y':a_i[1],'value':a[a_i]})
    colname = df_obj.data_type[df_obj.data_type.col_type == "numeric"].col_name.to_list()
    for x in colname:
        heat['Colnames'].append(x)
    heat['Descriptions'].append("กราฟนี้แสดง")
    return heat
def boxplot():
    # show data qualtile and outliner of single data
    result = df_obj.graph_selector('box')
    # print(result)
    boxplot = {'Colnames':[],'Values':[],'Descriptions':[]}
    # colname = df_obj.data_type[df_obj.data_type.col_type == "numeric"].col_name.to_list()
    # print(result)
    if result is not None:
        colname = result['col_name']
        for x in colname:
            description = 'กราฟนี้เป็นกราฟของ {0} โดยแสดงถึงค่าการกระจายตัวของกลุ่ม ซึ่งจากกราฟพบว่าค่าเฉลี่ยของข้อมูลอยู่ที่ {1:.2f} มีค่าต่ำสุดคือ {2:.2f} และค่าสูงสุดคือ {3:.2f}'.format(x,result[result.col_name == x]['mean'].values[0],result[result.col_name == x]['min'].values[0],result[result.col_name == x]['max'].values[0])
            boxplot['Colnames'].append(x)
            boxplot_df = df_obj.df.filter([x], axis=1)
            boxplot['Values'].append({x:boxplot_df[x].to_list()})
            # description 
            if result[result.col_name == x].outlier_percent.values[0] is not None:
                description_outlier_percent = 'ปริมาณข้อมูลที่อยู่ห่างจากกลุ่มมาก ๆ มีอยู่ {0:.2f} % ซึ่งเป็นปริมาณที่{1}'.format(result[result.col_name == x].outlier_percent.values[0]*100,result[result.col_name == x].argument.values[0])
                description = description+description_outlier_percent
            boxplot['Descriptions'].append({x:description}) 
    return boxplot
def bar_cat():
    result = df_obj.graph_selector('bar')
    bar_cat = {'Colnames':[],'Values':[],'Descriptions':[]}
    print(result)
    if result is not None:
        colname = result['col_name']
        for x in colname:
            description = 'กราฟนี้เป็นแสดงการเปรียบเทียบปริมาณของ{} '.format(x)
            bar_cat['Colnames'].append(x)
            tempT = df_obj.cat_count[x].T.to_dict(orient='records')[0]
            bar = []
            for i in tempT:
                bar.append({'name':i,'value':tempT[i]})
            bar_cat['Values'].append({x:bar})
            if result[result.col_name == x].argument.values[0] is not None:
                description = description + 'ซึ่งมีลักษณะของข้อมูลอยู่ในรูปแบบที่เป็น{} '.format(result[result.col_name == x].argument.values[0])
            if result[result.col_name == x].anomal_attribute.values[0] is not None:
                description = description + 'มี anomal attribute {} '.format(result[result.col_name == x].anomal_attribute.values[0])
            if result[result.col_name == x].anomal_value.values[0] is not None and not math.isnan(result[result.col_name == x].anomal_value.values[0]):
                description = description + 'มี anomal value {} '.format(result[result.col_name == x].anomal_value.values[0])
            if result[result.col_name == x].percent_dominate.values[0] is not None and not math.isnan(result[result.col_name == x].percent_dominate.values[0]):
                description = description + 'มี percent dominate อยู่ที่ {0:.2f} % '.format(result[result.col_name == x].percent_dominate.values[0]*100 )
            bar_cat['Descriptions'].append({x:description})
    return bar_cat
def ecdf():
    result = df_obj.graph_selector('ecdf')
    # print(result)
    ecdf = {'Colnames':[],'Values':[],'Descriptions':[]}
    # colname = df_obj.data_type[df_obj.data_type.col_type == "numeric"].col_name.to_list()
    if result is not None:
        colname = result['col_name']
        for x in colname:
            # print(x)
            description = 'กราฟนี้เป็นกราฟแจกแจงสะสมเชิงประจักษ์ของ {} '.format(x)
            _ecdf = df_obj._prep_ecdf(x)
            # print(_ecdf[0])
            if _ecdf[0] > 0:
                _ecdf = _ecdf[1].to_dict(orient='records')
                
                ecdf['Colnames'].append(x)
                ecdf['Values'].append({x:_ecdf})
                # descriptions

                if result[result.col_name == x].break_percent.values[0] is not None:
                    description = description + 'ซึ่งมีค่าอัตราการการกระจายของข้อมูลอยู่ที่ {0:.2f} %'.format(result[result.col_name == x].break_percent.values[0])
                ecdf['Descriptions'].append({x:description})
    return ecdf
def time():
    # do time series analysis
    # test with supermarket dataset
    time = {'Colnames':[],'Values':[],'Descriptions':[]}
    # print("time")
    col = df_obj.data_type
    # create new best solution later 
    time_col = col[(col.col_type == 'date')].col_name.values
    numeric_col = col[(col.col_type == 'numeric')].col_name.values
    # print(time_col)
    # print(numeric_col)
    

    for t in time_col:
        for n in numeric_col:
            name = t+','+n
            temp = df_obj.df[[t,n]]
            temp.columns = ['x','y']
            temp['x']= temp['x'].dt.strftime('%Y-%m-%d')
            # print(temp.head())
            test_time = functions.Timeanalyze(temp)
            # print(test_time.x)
            print(name+' is '+str(test_time._isStationarity()))
            test_time._ETS()
            temp = temp.to_dict(orient='records')
            time['Colnames'].append(name)
            time['Values'].append({name:temp})
            time['Descriptions'].append({name:"กราฟนี้แสดงการเปลี่ยนแปลงตามเวลา"})
            # return time, {'Access-Control-Allow-Origin': '*'}
    return time
class Data(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('arg1', type=str)
        args = parser.parse_args()
        args1 = args['arg1'] 
        if args1 == 'distribution':
            return distribution(), {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'scatter':
            return scatter(), {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'heatmap':
            return heatmap(), {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'boxplot':
            return boxplot(), {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'bar_cat':
            return bar_cat(), {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'ecdf':
            return ecdf(), {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'time':
            return time(), {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'bar_num':
            #not finished
            bar_num = {'Colnames':[],'Values':[],'Descriptions':[]}

            return bar_num, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'line':
            #not finished
            line = {'Colnames':[],'Values':[],'Descriptions':[]}
            
            return line, {'Access-Control-Allow-Origin': '*'}
        elif args1 == 'test':
            test = {'Test':''}
            return test, {'Access-Control-Allow-Origin': '*'}
        else:
            all_graph = {
                            'Heatmap':{'Colnames':[],'Values':[],'Descriptions':[]},
                            'Distribution':{'Colnames':[],'Values':[],'Descriptions':[]},
                            'Scatter':{'Colnames':[],'Values':[],'Descriptions':[]},
                            'Boxplot':{'Colnames':[],'Values':[],'Descriptions':[]},
                            'Bar_cat':{'Colnames':[],'Values':[],'Descriptions':[]},
                            'Ecdf':{'Colnames':[],'Values':[],'Descriptions':[]},
                            'Time':{'Colnames':[],'Values':[],'Descriptions':[]}
                        }
            all_graph['Heatmap'] = heatmap()
            all_graph['Heatmap']['Values'] = []
            all_graph['Distribution'] = distribution()
            all_graph['Distribution']['Values'] = []
            all_graph['Scatter'] = scatter()
            all_graph['Scatter']['Values'] = []
            all_graph['Boxplot'] = boxplot()
            all_graph['Boxplot']['Values'] = []
            all_graph['Bar_cat'] = bar_cat()
            all_graph['Bar_cat']['Values'] = []
            all_graph['Ecdf'] = ecdf()
            all_graph['Ecdf']['Values'] = []
            all_graph['Time'] = time()
            all_graph['Time']['Values'] = []
            return all_graph, {'Access-Control-Allow-Origin': '*'}
        # next step is time series variable 

        return "success", {'Access-Control-Allow-Origin': '*'}
    def post(self): 
        # print(request.is_json)
        data = json.loads(request.get_data().decode("utf-8"))
        # data = pd.DataFrame(list(data.items()), columns=df_obj.data_type.columns)
        df_obj.data_type = pd.DataFrame(data['data'])
        if "target" in data:
            print("have target")
            df_obj.target = data['target']
        else:
            print("not have target")
        df_obj.data_comb = df_obj._data_combinator()
        df_obj.cat_count = df_obj._cat_unique_count()
        # print(df_obj.data_comb)
        # print(df_obj.cat_count)
        return "success", {'Access-Control-Allow-Origin': '*'}
# for Upload CSV data
class Upload(Resource):
    def get(self):
        # print(df_obj.data_type.to_dict(orient='records'))
        return df_obj.data_type.to_dict(orient='records'), {'Access-Control-Allow-Origin': '*'}
        # return jsonify({'status': 'ok', 'data': df_obj.df.to_dict(orient='split')}), {'Access-Control-Allow-Origin': '*'}
    def post(self):
        file = request.files['file']
        # global data
        data = pd.read_csv(file)
        # global df
        global df_obj
        df_obj = functions.Data_prep(data)
        # print(df_obj.data_comb[(df_obj.data_comb.col_1_type == "numeric") & (df_obj.data_comb.col_2_type == "numeric")])
        # print("scatter plot length is %d"%len(df_obj.data_comb[(df_obj.data_comb.col_1_type == "numeric") & (df_obj.data_comb.col_2_type == "numeric")].loc[:, ['col_1_name','col_2_name']].values.tolist()))
        # show numeric type columns
        # print("histogram length is %d"%len(df_obj.data_type[df_obj.data_type.col_type == "numeric"].col_name.to_list()))
        data_to_session = df_obj.data_comb.to_dict(orient='records')
        session['data'] = data_to_session
        return "success", {'Access-Control-Allow-Origin': '*'}