import pandas as pd
import numpy as np

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