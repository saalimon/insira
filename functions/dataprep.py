import pandas as pd
import numpy as np

def data_separator (df):
    '''This function recieve a dataframe that will seperate & convert data into proper category'''
    
    #Init list for checking ordinal and returning list
    ordinal_list = ['day','month','year','time_from_date','date','time']
    col_type = [] 

    #lower case column name
    df.columns = map(str.lower, df.columns)

    for col in df.columns:
        d_type = df[col].dtype
        unique_value = df[col].unique().size / df.index.size
        if unique_value == 1:
            col_type.append('unique')
        elif col in ordinal_list:
            col_type.append('ordinal')
        elif d_type == 'int64' or d_type == 'float64':
            col_type.append('numeric')
        elif d_type == 'object':
            col_type.append('category')

    #Init list of Dataframe
    data_type_init = {'col_name':list(df.columns), 'col_type':col_type} 

    # Create DataFrame 
    data_type = pd.DataFrame(data_type_init) 
    return data_type

def data_conversion(df):
    '''This function attempt to correct type of data of given dataframe'''
    
     #Attempt to correct data type from object to ordinal     
    try:
        df[df.select_dtypes(['object']).columns] = df[df.select_dtypes(['object']).columns].apply(pd.to_datetime)
    except:
        pass

    #Attempt to correct data type from object to numeric and seperate date-timestamp to day, month, and year column
    for col in df.select_dtypes(['datetime','object']).columns:
        try:
            if df[col].dtypes == 'O':
                 df[col] = df[col].apply(pd.to_numeric)
            else :
                df['new_date'] = [d.date() for d in df[col]]
                df['time_from_date'] = [d.time() for d in df[col]]
        except:
            pass
        
    # #Seperate date colum to day, month, and year
    try:
        df['year'] = pd.DatetimeIndex(df['new_date']).year
        df['month'] = pd.DatetimeIndex(df['new_date']).month
        df['day'] = pd.DatetimeIndex(df['new_date']).day
        df.drop(columns=['new_date'])
    except:
        pass
    
    return df
    
def data_combinator(df_type):
    '''This function receive data type dataframe and will return a combination of column with column type'''
    
    #init list of dataframe
    row_1_list, row_2_list, col_1_type, col_2_type = ([] for i in range(4))

    #for sending cross column 
    for index_outer,row_outer in df_type.iterrows():
        for index_inner,row_inner in df_type.iterrows():
            if index_inner > index_outer:
                row_1_list.append(row_outer['col_name'])
                row_2_list.append(row_inner['col_name'])
                col_1_type.append(row_outer['col_type'])
                col_2_type.append(row_inner['col_type'])
                
    #construct list for dataframe and convert to dataframe
    send_list = {'col_1_name':row_1_list, 'col_2_name':row_2_list, 'col_1_type': col_1_type, 'col_2_type': col_2_type}
    df_send = pd.DataFrame(send_list) 
    
    return df_send

def cat_unique_count(df, df_type):
    '''This function recieve a data type dataframe and original dataframe which return a dictionary that contain
    dataframes of category type column. The key of dictionary is column name and the value
    of dictionary is dataframe of those column. Each dataframe contain a column with a list 
    unqiue value and a column with a count of each value'''

    dict_dataframe_collection = {}

    df_send_filter_cat = df_type.loc[(df_type.col_type == 'category')]
    cat_col = [col for col in df_send_filter_cat['col_name']] 

    for cat in cat_col:
        df_aggregate = df.groupby(cat)[cat].count().to_frame()
        del df_aggregate.index.name
        dict_dataframe_collection[cat] = pd.DataFrame(df_aggregate, columns=[cat])

    return dict_dataframe_collection