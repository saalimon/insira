import pandas as pd
import numpy as np
import math

# Note: function with _ infront of function name indicated that it is a function for internal use only

class Data_prep:
    def __init__(self, df):
        self.df = df
        self.df = self._data_conversion()
        self.data_type = self._data_separator()
        self.data_comb = self._data_combinator()
        self.cat_count = self._cat_unique_count()
        self.na_warn = self._find_na()
        
    def _data_separator (self):
        '''
        This function is used to seperate & convert data into proper category
        '''
        
        #Init list for checking ordinal and returning list
        ordinal_list = ['day','month','year','time_from_date','date','time']
        unique_list = ['id','no.','code']
        col_type = [] 

        #lower case column name
        self.df.columns = map(str.lower, self.df.columns)

        for col in self.df.columns:
            d_type = self.df[col].dtype
            unique_value = self.df[col].unique().size / self.df.index.size

            #check unqiue name
            unique_name = [x in col for x in unique_list]

            if unique_value == 1 or True in unique_name:
                col_type.append('unique')
            elif col in ordinal_list:
                col_type.append('ordinal')
            elif d_type == 'int64' or d_type == 'float64':
                col_type.append('numeric')
            elif d_type == 'object':
                col_type.append('category')

        #Init list of Dataframe
        data_type_init = {'col_name':list(self.df.columns), 'col_type':col_type} 

        # Create DataFrame 
        data_type = pd.DataFrame(data_type_init) 
        return data_type

    def _data_conversion(self):
        '''
        This function attempt to correct type of data of given dataframe
        '''
        
        #Attempt to correct data type from object to ordinal     
        try:
            self.df[self.df.select_dtypes(['object']).columns] = self.df[self.df.select_dtypes(['object']).columns].apply(pd.to_datetime)
        except:
            pass

        #Attempt to correct data type from object to numeric and seperate date-timestamp to day, month, and year column
        for col in self.df.select_dtypes(['datetime','object']).columns:
            try:
                if self.df[col].dtypes == 'O':
                    self.df[col] = self.df[col].apply(pd.to_numeric)
                else :
                    self.df['new_date'] = [d.date() for d in self.df[col]]
                    self.df['time_from_date'] = [d.time() for d in self.df[col]]
            except:
                pass
            
        # #Seperate date colum to day, month, and year
        try:
            self.df['year'] = pd.DatetimeIndex(self.df['new_date']).year
            self.df['month'] = pd.DatetimeIndex(self.df['new_date']).month
            self.df['day'] = pd.DatetimeIndex(self.df['new_date']).day
            # df.drop(columns=['new_date'])
        except:
            pass
        
        return self.df
        
    def _data_combinator(self):
        '''
        This function return a combination of column with column type
        '''
        
        #init list of dataframe
        row_1_list, row_2_list, col_1_type, col_2_type = ([] for i in range(4))

        #for sending cross column 
        for index_outer,row_outer in self.data_type.iterrows():
            for index_inner,row_inner in self.data_type.iterrows():
                if index_inner > index_outer:
                    row_1_list.append(row_outer['col_name'])
                    row_2_list.append(row_inner['col_name'])
                    col_1_type.append(row_outer['col_type'])
                    col_2_type.append(row_inner['col_type'])
                    
        #construct list for dataframe and convert to dataframe
        send_list = {'col_1_name':row_1_list, 'col_2_name':row_2_list, 'col_1_type': col_1_type, 'col_2_type': col_2_type}
        df_send = pd.DataFrame(send_list) 
        
        return df_send

    def _cat_unique_count(self):
        '''
        This function return a dictionary that contain
        dataframes of category type column. The key of dictionary is column name and the value
        of dictionary is dataframe of those column. Each dataframe contain a column with a list 
        unqiue value and a column with a count of each value
        '''

        dict_dataframe_collection = {}

        df_send_filter_cat = self.data_type.loc[(self.data_type.col_type == 'category')]
        cat_col = [col for col in df_send_filter_cat['col_name']] 

        for cat in cat_col:
            df_aggregate = self.df.groupby(cat)[cat].count().to_frame()
            del df_aggregate.index.name
            dict_dataframe_collection[cat] = pd.DataFrame(df_aggregate, columns=[cat])

        return dict_dataframe_collection

    def _find_na(self):
        '''
        This function return infrom value that indicate 
        too many NA/NaN values are presented in any columns or not. It also returns
        dataframe of column with high NA value that contains ratio of na if any is existed
        '''
        na = self.df.isna().sum() 
        inform = 0
        col_index, na_ratio = ([] for i in range(2))
        data_length = len(self.df)
        
        for index,value in na.iteritems():
            if value/data_length > 0.05:
                col_index.append(index)
                na_ratio.append(value/data_length)
                inform = 1
                
        if inform == 1:
            na_list = {'col_name':col_index, 'na_ratio': na_ratio}
            df_na = pd.DataFrame(na_list)
            return inform, df_na

        return inform, None

        import pandas as pd

    def prep_ecdf(self, col_name):
        ''' 
        This function is used to prepare a ecdf taking a column name as input
        and return dataframe contain axis & yaxis for ploting graph. Also return percentage & 
        value of data & argument for use in NLG and
        score for selecting graph
        Recommended graph label: title = "ECDF Plot", xlabel = 'Data Values', ylabel = 'Percentage'
        '''
        
        temp = 0
        data_length = len(self.df[col_name])
        xaxis = np.sort(self.df[col_name])
        yaxis = np.arange(1, data_length+1)/data_length
        
        for i,v in enumerate(xaxis):

            ecdf_axis = {'xaxis':xaxis, 'yaxis':yaxis}
            df_ecdf = pd.DataFrame(ecdf_axis)

            if i > 0:
                if v/temp > 2.0:
                    if i < data_length/2:
                        return (1, df_ecdf, (i/data_length)*100, v, 'less_than')
                    else:
                        return (1, df_ecdf, (1-i/data_length)*100, v, 'more_than')
            temp = v
            
        
        return (0, df_ecdf, 50, xaxis[int(data_length/2)], 'less_than')
    
    def numercial_data_distribution(self, col_name):
        '''
        This function recieve a column name and output a
        dataframe of graph skewness of each numerical column in original dataframe
        '''
        
        score = 0
        column_skew = []
        
        mean = self.df[col_name].mean()
        med = self.df[col_name].median()

        if math.isclose(mean, med, rel_tol=1e-1):
            column_skew = 'Symmetric'
        elif mean > med:
            column_skew = 'Right skewed'
        elif med > mean:
            column_skew = 'Left skewed'
        else:
            column_skew = 'fail to process'
        
        return score, column_skew

    def dominated_category(self, col_name):
        '''
        This function receive a column name and return an binary value indicated anomaly value
        presented (1 if true, 0 otherwise), attribute that dominated, the value of anomaly, percent dominate,
        and score that use for selecting graph
        '''
        
        score = 0
        
        #init list
        anomal = []
        
        #list for holding value of current column
        temp_value = []

        #append each value in each row
        for index,row in self.cat_count[col_name].iterrows():
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
    
    def find_binomal(self, col_name):
        '''
        This function is used to detect a binomal distribution presented in data and
        return a binary value (1 if there is a binomal presented in received column, 0 otherwise)
        '''

        df_mode = self.df.mode()
        # df_mode = self.df.mode(numeric_only=True)

        number_of_mode = len(df_mode[col_name].dropna())

        if number_of_mode == 2:
            return 1

        return 0
