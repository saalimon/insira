import pandas as pd
import numpy as np
import math

# Note: function with _ infront of function name indicated that it is a function for internal use only

class Data_prep:
    def __init__(self, df, target=None):
        self.df = df
        self.target = target
        self.df = self._data_conversion()
        self.data_type = self._data_separator()
        self.data_comb = self._data_combinator()
        self.cat_count = self._cat_unique_count()
        self.na_warn = self._find_na()

    def _data_separator(self):
        """
        This function is used to seperate & convert data into proper category
        """
        
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
        """
        This function attempt to correct type of data of given dataframe
        """
        
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
        """
        This function return a combination of column with column type
        """
        
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
        """
        This function return a dictionary that contain
        dataframes of category type column. The key of dictionary is column name and the value
        of dictionary is dataframe of those column. Each dataframe contain a column with a list 
        unqiue value and a column with a count of each value
        """

        dict_dataframe_collection = {}

        df_send_filter_cat = self.data_type.loc[(self.data_type.col_type == 'category')]
        cat_col = [col for col in df_send_filter_cat['col_name']] 

        for cat in cat_col:
            df_aggregate = self.df.groupby(cat)[cat].count().to_frame()
            del df_aggregate.index.name
            dict_dataframe_collection[cat] = pd.DataFrame(df_aggregate, columns=[cat])

        return dict_dataframe_collection

    def _find_na(self):
        """
        This function return infrom value that indicate 
        too many NA/NaN values are presented in any columns or not. It also returns
        dataframe of column with high NA value that contains ratio of na if any is existed
        """
        na = self.df.isna().sum() 
        inform = 0
        col_index, na_ratio = ([] for i in range(2))
        data_length = len(self.df)
        
        for index,value in na.iteritems():
            if value/data_length > 0.05:
                col_index.append(index)
                na_ratio.append(value/data_length)
                inform = 1
            elif value/data_length > 0.90:
                self.df.drop([index], axis=1)
                print("{0} has over 80% of null value contained, therefore it has to be dropped".format(index))
            elif len(self.df[index]) <= 1:
                self.df.drop([index], axis=1)
                print("{0} has only 1 or less value contained, therefore it has to be dropped".format(index))

        if inform == 1:
            na_list = {'col_name':col_index, 'na_ratio': na_ratio}
            df_na = pd.DataFrame(na_list)
            return inform, df_na

        return inform, None

    def prep_ecdf(self, col_name):
        """ 
        This function is used to prepare a ecdf taking a column name as input
        and return dataframe contain axis & yaxis for ploting graph. Also return percentage & 
        value of data & argument for use in NLG and
        score for selecting graph
        Recommended graph label: title = "ECDF Plot", xlabel = 'Data Values', ylabel = 'Percentage'
        """
        
        temp = 0
        data_length = len(self.df[col_name])
        xaxis = np.sort(self.df[col_name])
        yaxis = np.arange(1, data_length+1)/data_length
        
        for i,v in enumerate(xaxis):

            ecdf_axis = {'xaxis':xaxis, 'yaxis':yaxis}
            df_ecdf = pd.DataFrame(ecdf_axis)

            if i > 0:
                if v/temp > 1.5:
                    if i < data_length/2:
                        return (1, df_ecdf, (i/data_length)*100, v, 'น้อยกว่า')
                    else:
                        return (1, df_ecdf, (1-i/data_length)*100, v, 'มากกว่า')
            temp = v
            
        
        return (0, df_ecdf, 50, xaxis[int(data_length/2)], 'น้อยกว่า')
    
    def _numercial_data_distribution(self, col_name):
        """
        This function recieve a column name and output a
        dataframe of graph skewness of each numerical column in original dataframe
        """

        uniform_count = 0
        score = 0
        column_dis = []
        mean = self.df[col_name].mean()
        med = self.df[col_name].median()

        #for checking uniform distribution
        bins = int(math.sqrt(len(self.df[col_name])))
        counts, _ = np.histogram(self.df[col_name], bins=bins)
        for i,v in enumerate(counts):
            if i == 0:
                temp = v
            else:
                if math.isclose(v, temp ,rel_tol=5e-2):
                    uniform_count += 1

        if len(counts[counts != 0]) == 2:
            column_dis = 'Bernoulli'
            score = 1
        elif uniform_count == len(counts)-1:
            column_dis = 'Uniform'
            score = 1
        elif math.isclose(mean, med, rel_tol=1e-1):
            column_dis = 'Normal symmetric'
        elif mean > med:
            column_dis = 'Normal right skewed'
            score = 1
        elif med > mean:
            column_dis = 'Normal left skewed'
            score = 1
        else:
            column_dis = 'fail to process'
        
        return score, column_dis

    def _data_ratio(self, col_name):
        """
        This function receive a column name and return an argument for descripe, 
        attribute that dominated, the value of anomaly, percent dominate,
        and score that use for selecting graph
        """
        
        score = 0
        
        #list for holding value of current column
        temp_value = []

        #append each value in each row
        for index,row in self.cat_count[col_name].iterrows():
            temp_value.append(row.item())

        #for checking if it is the dominate one in dataframe
        member = len(temp_value)         
        max_value = np.max(temp_value)
        threshold = 0
        balanced_threshold = 0

        for i in temp_value:
            if i != max_value:

                #if value of current attribute is lower than 35% when compared to maximum value existed in column
                if i/max_value < 0.35:
                    #increase the number of normal value compared to anomaly
                    threshold += 1
                #if current value is approximated to max value, then add perfect data threshold
                elif i/max_value > 0.90:
                    balanced_threshold += 1

            #for store max value purpose
            else:
                max_attribute = index

        #if overall nomal value is equal to number of attribute exclude max value then that max value is certainly an anomaly
        if threshold == member-1:
            arg = "fragmented data"
            attribute = max_attribute
            value = max_value
            percent_dominate = (max_value/sum(temp_value))
            score = 1
    #         print(str(max_col)+" in "+str(col_name)+" is anomalies")

        #if overall nomal value is equal to number of attribute exclude max value then this data is perfectly balanced
        elif balanced_threshold == member-1:
            arg = "balanced data"
            attribute = None
            value = None
            percent_dominate = None
            score = 1
        
        else:
            arg = None
            attribute = None
            value = None
            percent_dominate = None
    #         print("No abnormalies is detected")

        return score, arg, attribute, value, percent_dominate
        
    def _find_multimodal(self, col_name):
        """
        This function is used to detect a binomal distribution presented in data and
        return a binary value (1 if there is a binomal presented in received column, 0 otherwise)
        """

        df_mode = self.df.mode()
        # df_mode = self.df.mode(numeric_only=True)

        number_of_mode = len(df_mode[col_name].dropna())

        if number_of_mode == 2:
            return 1, "bimodal"
        elif number_of_mode == 3:
            return 1, "trimodal"   
             
        return 0, None
    
    def _find_corr(self, df_corr, col_1, col_2):
        """
        This function is use to select interesting correlation found in data
        """

        corr_type_mod = ""
        corr_type_strong = ""
        corr_target = ""
        
        for i,r in df_corr.iterrows():
            for index_i, index_v in enumerate(r.values):
                #if current row is interested column
                if i == col_1 and r.index[index_i] == col_2:
                    #if it is not its own corr value
                    if r.index[index_i] != i:
                        #with target
                        if self.target != None:
                            #current interest is target
                            if self.target == i:
                                #for positive correlation
                                if index_v > 0:
                                    if index_v > 0.6 and index_v < 0.8:
                                            corr_type_mod = "moderate postive"
                                            corr_target = "correlate with target"
                                            break

                                    elif index_v > 0.8:
                                            corr_type_strong = "strong postive"
                                            corr_target = "correlate with target"
                                            break

                                #for negative correlation
                                elif index_v < 0:
                                    if index_v < -0.6 and index_v > -0.8:
                                            corr_type_mod = "moderate negative"
                                            corr_target = "correlate with target"
                                            break

                                    elif index_v < -0.8:
                                            corr_type_strong = "strong negative"
                                            corr_target = "correlate with target"
                                            break
                            else:
                                #for positive correlation
                                if index_v > 0:
                                    if index_v > 0.6 and index_v < 0.8:
                                            corr_type_mod = "moderate postive"
                                            corr_target = "correlate with each other"
                                            break

                                    elif index_v > 0.8:
                                            corr_type_strong = "strong postive"
                                            corr_target = "correlate with each other"
                                            break

                                #for negative correlation
                                elif index_v < 0:
                                    if index_v < -0.6 and index_v > -0.8:
                                            corr_type_mod = "moderate negative"
                                            corr_target = "correlate with each other"
                                            break

                                    elif index_v < -0.8:
                                            corr_type_strong = "strong negative"
                                            corr_target = "correlate with each other"
                                            break
                        #No target
                        else:
                            #for positive correlation
                            if index_v > 0:
                                if index_v > 0.6 and index_v < 0.8:
                                        corr_type_mod = "moderate postive"
                                        corr_target = None
                                        break

                                elif index_v > 0.8:
                                        corr_type_strong = "strong postive"
                                        corr_target = None
                                        break

                            #for negative correlation
                            elif index_v < 0:
                                if index_v < -0.6 and index_v > -0.8:
                                        corr_type_mod = "moderate negative"
                                        corr_target = None
                                        break

                                elif index_v < -0.8:
                                        corr_type_strong = "strong negative"
                                        corr_target = None
                                        break


        #prioritize strong correlation                  
        if len(corr_type_strong) != 0:
    #         if len(moderate) != 0:
    #             return 2, strong+moderate
    #         else:
    #             return 2, strong
            return 2, corr_type_strong, corr_target
                
        else:
            if len(corr_type_mod) != 0:
                return 1, corr_type_mod, corr_target
            else:
                return 0, None, None

    def _find_outlier_box(self, col):
    
        score = 0
        argument = None
        Q1 = self.df[col].quantile(.25)
        Q3 = self.df[col].quantile(.75)
        IQR = Q3 -Q1
        data_length = len(self.df[col])
        
        exceed_lower = len(self.df[col][((self.df[col] < (Q1 - 1.5 * IQR)))])
        exceed_upper = len(self.df[col][((self.df[col] > (Q3 + 1.5 * IQR)))])
        total = exceed_lower+exceed_upper
        percentage = total/data_length

        if total/data_length > 0.02 and total/data_length < 0.06:
            argument = "น้อย"
            score = 1
        elif total/data_length > 0.06 and total/data_length < 0.10:
            argument = "ปานหลาง"
            score = 2
        elif total/data_length > 0.10:
            argument = "สูง"
            score = 3
        else:
            exceed_lower = None
            exceed_upper = None
            total = None
            argument = None
            percentage = None
        
        return score, exceed_lower, exceed_upper, total, percentage, argument
    
    def _numerical_test(self, col, g_type):
        if g_type == 'ecdf':
            res_ecdf =  self.prep_ecdf(col)
            score = res_ecdf[0]
            if score == 1:
                return col, res_ecdf[2:5]
                
        elif g_type == 'histogram':
            score_his, dis_type = self._numercial_data_distribution(col)
            score_multi, mode_type = self._find_multimodal(col)
            score = score_his+score_multi
            if score >= 1:
    #             selected_histogram.append(col)
                return col, dis_type, mode_type

        elif g_type == 'box':
            res_box = self._find_outlier_box(col)
            score = res_box[0]
            if score >= 1:
                return col, res_box[1:6]

        return None

    def _categorical_test(self, col, g_type):
        if g_type == "bar":
            res_ratio = self._data_ratio(col)
            score = res_ratio[0]
    #         score_ratio, arg, attribute, value, percent_dominate = self._data_ratio(col)
            if score == 1:
                return col, res_ratio[1:5]
        return None

    def _num_num_test(self, col_1, col_2, g_type):
        if g_type == 'scatter':
            df_corr = self.df.corr(method ='pearson')
            score, corr_type, corr_target = self._find_corr(df_corr, col_1, col_2)
            if score >= 1:
    #             selected_scatter.append((col_1, col_2))
    #             corr_list.append(corr_type)
    #             flattened_list = [y for x in corr_list for y in x]

    #             corr_temp = {'col_name':selected_scatter, 'corr_type':flattened_list}
    #             df_send = pd.DataFrame(corr_temp)
                return col_1, col_2, corr_type, corr_target

        return None

    def _num_cat_test(self, col_1, col_2, g_type):
        #For future release
        return None

    def _cat_cat_test(self, col_1, col_2, g_type):
        #For future release
        return None

    def graph_selector(self, g_type):
        """
        This function is used to select interesting graph
        """
        
        single_col = ['histogram','bar','ecdf','box']
        double_col = ['scatter']
        df_return = None
        
        #histogram
        dis_type = []
        mode_type = []
        
        #general
        col_name = []
        argument = []
        value = []
        
        #ecdf_graph
        break_percent = []
        
        #box
        exceed_lower = []
        exceed_upper = []
        total = []
        outlier_percent = []

        #bar
        anomal_attribute = []
        percent_dominate = []
        
        #scatter 
        col_1_name, col_2_name, corr_type, corr_target = ([] for i in range(4))
        
        type_prefer = ['category','numeric']
        df_type_filter = self.data_type[self.data_type.col_type.isin(type_prefer)]
        df_combine_filter = self.data_comb[(self.data_comb.col_1_type.isin(type_prefer)) & (self.data_comb.col_2_type.isin(type_prefer))]
        
    #     num_list = numeric_only['col_name'].tolist()
    #     new_df_numeric = self.df[num_list] 

        switcher = {
            'numeric': self._numerical_test,
            'category': self._categorical_test,
            ('numeric','numeric'): self._num_num_test,
            ('numeric','category'): self._num_cat_test,
            ('category','numeric'): self._num_cat_test,
            ('category','category'): self._cat_cat_test,
        }

        if g_type in single_col:
            for i,r in df_type_filter.iterrows():
                func_single = switcher.get(r.values[1], lambda: "Error: Invalid column type presented")
                result_single = func_single(r.values[0], g_type)
                if result_single != None:
                    if g_type == "histogram":
                        col_name.append(result_single[0])
                        dis_type.append(result_single[1])
                        mode_type.append(result_single[2])
                        data_return = {'col_name':col_name, 'dis_type':dis_type, 'mode_type': mode_type}
                        df_return = pd.DataFrame(data_return)
                            
                    elif g_type == "ecdf":
                        col_name.append(result_single[0])
                        break_percent.append(result_single[1][0])
                        value.append(result_single[1][1])
                        argument.append(result_single[1][2])
                        data_return = {'col_name':col_name, 'break_percent':break_percent, 'value': value, 'argument': argument}
                        df_return = pd.DataFrame(data_return)
                        
                    elif g_type == "bar":
                        col_name.append(result_single[0])
                        argument.append(result_single[1][0])
                        anomal_attribute.append(result_single[1][1])
                        value.append(result_single[1][2])
                        percent_dominate.append(result_single[1][3])
                        data_return = {'col_name':col_name, 'argument':argument, 'anomal_attribute': anomal_attribute,
                                    'anomal_value': value, 'percent_dominate': percent_dominate}
                        df_return = pd.DataFrame(data_return)
                    
                    elif g_type == "box":
                        col_name.append(result_single[0])
                        exceed_lower.append(result_single[1][0])
                        exceed_upper.append(result_single[1][1])
                        total.append(result_single[1][2])
                        outlier_percent.append(result_single[1][3])
                        argument.append(result_single[1][4])
                        data_return = {'col_name':col_name, 'exceed_lower':exceed_lower, 'exceed_upper': exceed_upper,
                                    'total': total, 'outlier_percent': outlier_percent, 'argument': argument}
                        df_return = pd.DataFrame(data_return)


        elif g_type in double_col:
            for i,r in df_combine_filter.iterrows():
                func_double = switcher.get((r.values[2],r.values[3]), lambda: "Error: Invalid column type presented")
                result_double = func_double(r.values[0], r.values[1], g_type)
                if result_double != None:
                    if len(result_double) == 4:
                        if g_type == "scatter":
                            col_1_name.append(result_double[0])
                            col_2_name.append(result_double[1])
                            corr_type.append(result_double[2])
                            corr_target.append(result_double[3])
                            data_return = {'col_1_name':col_1_name, 'col_2_name':col_2_name, 'corr_type': corr_type, 'corr_target': corr_target}
                            df_return = pd.DataFrame(data_return)

                            
        return df_return
