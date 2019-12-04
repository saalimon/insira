
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

def dominated_category(cat_count):
    '''This function recieve a dictionary contained count value 
    of the category type column(from function cat_data_count.py) and
    return a dataframe of the dominated attribute of each column if existed'''
    
    #init list
    col_list, anomal, attribute, value, percent_dominate = ([] for i in range(5))
    
    #loop each column
    for col in cat_count.keys():
        col_list.append(col)
        
        #list for holding value of current column
        temp_value = []
        
        #append each value in each row
        for index,row in cat_count[col].iterrows():
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
            anomal.append(1)
            attribute.append(max_attribute)
            value.append(max_value)
            percent_dominate.append(max_value/sum(temp_value))
    #         print(str(max_col)+" in "+str(col)+" is anomalies")
        else:
            anomal.append(0)
            attribute.append(None)
            value.append(None)
            percent_dominate.append(None)
    #         print("No abnormalies is detected")

    abnormalies_list = {'col_name':col_list, 'anomaly_detected':anomal, 'attribute':attribute,
                        'value':value, 'percent_dominate': percent_dominate}
    df_anomaly = pd.DataFrame(abnormalies_list) 

    return df_anomaly