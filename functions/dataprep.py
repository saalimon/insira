import pandas as pd
import numpy as np

def data_separator (df):
    '''This function recieve a dataframe that will seperate & convert data into proper category'''
    
    #Init list for checking ordinal and returning list
    ordinal_list = ['day','month','year']
    col_type = []
        
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