
import pandas as pd
import numpy as np

def numercial_data_distribution(df, df_type):
    '''This function recieve original dataframe & data type and output a
    dataframe of graph skewness of each numerical column in original dataframe'''
    
    column_skew = []
    
    data_send_filter_num = df_type.loc[(df_type.col_type == 'numeric')]
    num_col = [col for col in data_send_filter_num['col_name']]
    
    for col in num_col:
        mean = df[col].mean()
        med = df[col].median()

        if math.isclose(mean, med, rel_tol=0.1e-1):
            column_skew.append('Symmetric')
        elif mean > med:
            column_skew.append('Right skewed')
        elif med > mean:
            column_skew.append('Left skewed')
        else:
            column_skew.append('fail to process')
            
    skew_list = {'col_name':num_col, 'skewness':column_skew}
    df_send = pd.DataFrame(skew_list) 
    
    return df_send