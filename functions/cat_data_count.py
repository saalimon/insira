from data_sep_and_con import data_separator, data_conversion
from data_combinator import data_combinator
import pandas as pd
import numpy as np

def cat_unique_count(df, df_type):
    '''
    This function recieve a data type dataframe and original dataframe which return a dictionary that contain
    dataframes of category type column. The key of dictionary is column name and the value
    of dictionary is dataframe of those column. Each dataframe contain a column with a list 
    unqiue value and a column with a count of each value
    '''

    #init dictionary
    dict_dataframe_collection = {}

    #filter category
    df_send_filter_cat = df_type.loc[(df_type.col_type == 'category')]
    cat_col = [col for col in df_send_filter_cat['col_name']] 

    #count each unique value from filtered dataframe
    for cat in cat_col:
        df_aggregate = df.groupby(cat)[cat].count().to_frame()
        del df_aggregate.index.name
        dict_dataframe_collection[cat] = pd.DataFrame(df_aggregate, columns=[cat])

    #for debugging purpose
    # for key in dataframe_collection.keys():
    # print("\n" +"="*40)
    # print(key)
    # print("-"*40)
    # print(dataframe_collection[key])

    return dict_dataframe_collection
