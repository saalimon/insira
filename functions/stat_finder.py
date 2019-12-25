
import pandas as pd
import numpy as np
import math

def numercial_data_distribution(df, df_type, col_name):
    '''
    This function recieve original dataframe & data type and output a 
    score that use for selecting graph and graph skewness of each
    numerical column in original dataframe
    '''
    
    score = 0
    column_skew = []
    
    data_send_filter_num = df_type.loc[(df_type.col_type == 'numeric')]
    num_col = [col for col in data_send_filter_num['col_name']]
    
    mean = df[col_name].mean()
    med = df[col_name].median()

    if math.isclose(mean, med, rel_tol=1e-1):
        column_skew = 'Symmetric'
    elif mean > med:
        column_skew = 'Right skewed'
    elif med > mean:
        column_skew = 'Left skewed'
    else:
        column_skew = 'fail to process'
    
    return score, column_skew

def dominated_category_1(cat_count, col_name):
    '''
    This function recieve a dictionary contained count value 
    of the category type column(from function cat_data_count.py) and 
    column name. This function will return an boolean indicated anomaly value
    presented, attribute that dominated, the value of anomaly, percent dominate,
    and score that use for selecting graph
    '''
    
    score = 0
    
    #init list
    anomal = []
      
    #list for holding value of current column
    temp_value = []

    #append each value in each row
    for index,row in cat_count[col_name].iterrows():
        temp_value.append(row.item())

    #for checking if it is the dominate one in dataframe
    member = len(temp_value)         
    max_value = np.max(temp_value)
    threshold = 0

    for i in temp_value:
        if i != max_value:

            #if value of current attribute is lower than 35% when compared to maximum value existed in column
            if i/max_value < 0.35:
                #increase the number of normal value compared to anomaly
                threshold += 1

        #for store max value purpose
        else:
            max_attribute = index

    #if overall nomal value is equal to number of attribute exclude max value then that max value is certainly an anomaly
    if threshold == member-1:
        anomal = 1
        attribute = max_attribute
        value = max_value
        percent_dominate = (max_value/sum(temp_value))
        score = 1
#         print(str(max_col)+" in "+str(col_name)+" is anomalies")
    else:
        anomal = 0
        attribute = None
        value = None
        percent_dominate = None
#         print("No abnormalies is detected")

    return (score, anomal, attribute, value, percent_dominate)