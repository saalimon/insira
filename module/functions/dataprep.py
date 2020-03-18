import pandas as pd
import numpy as np
import math
from sklearn import feature_selection, preprocessing
from scipy import stats

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
            binary_category = self.df[col].values

            #check unqiue name
            unique_name = [x in col for x in unique_list]

            if unique_value == 1 or True in unique_name:
                col_type.append('unique')
            elif col in ordinal_list:
                col_type.append('ordinal')
            elif d_type == 'object' or len(self.df[col].unique()) == 2:
                col_type.append('category')
            elif d_type == 'int64' or d_type == 'float64':
                col_type.append('numeric')


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

        try:
            #for sending cross column 
            for index_outer,row_outer in self.data_type.iterrows():
                for index_inner,row_inner in self.data_type.iterrows():
                    if index_inner > index_outer:
                        row_1_list.append(row_outer['col_name'])
                        row_2_list.append(row_inner['col_name'])
                        col_1_type.append(row_outer['col_type'])
                        col_2_type.append(row_inner['col_type'])
        except:
            return 'Error: Failed to combine columns in _data_combinator function'
                    
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

        try:
            for cat in cat_col:
                df_aggregate = self.df.groupby(cat)[cat].count().to_frame()
                del df_aggregate.index.name
                dict_dataframe_collection[cat] = pd.DataFrame(df_aggregate, columns=[cat])
        except:
            return 'Error: Failed counting category in _cat_unique_count function'

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
        
        if self.target != None:
            #forcefully drop NA to prevent error in label encoding
            self.df.dropna()
            
        else:
            try:
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
            except:
                return 'Error: Failed to inform or remove null value in _find_na function'

        if inform == 1:
            na_list = {'col_name':col_index, 'na_ratio': na_ratio}
            df_na = pd.DataFrame(na_list)
            return inform, df_na

        return inform, None

    def _prep_ecdf(self, col_name):
        """ 
        This function is used to prepare a ecdf taking a column name as input
        and return dataframe contain axis & yaxis for ploting graph. Also return percentage & 
        value of data & argument for use in NLG and
        score for selecting graph
        Recommended graph label: title = "ECDF Plot", xlabel = 'Data Values', ylabel = 'Percentage'
        """
        
        try:
            temp = 0
            data_length = len(self.df[col_name])
            xaxis = np.sort(self.df[col_name])
            yaxis = np.arange(1, data_length+1)/data_length
        except:
            return 'Error: Failed to convert data to ecdf axis in _prep_ecdf function'
        
        for i,v in enumerate(xaxis):

            ecdf_axis = {'xaxis':xaxis, 'yaxis':yaxis}
            df_ecdf = pd.DataFrame(ecdf_axis)
            try:
                if i > 0:
                    if v/temp > 1.5:
                        if i < data_length/2:
                            return (1, df_ecdf, (i/data_length)*100, v, 'น้อยกว่า')
                        else:
                            return (1, df_ecdf, (1-i/data_length)*100, v, 'มากกว่า')
            except:
                return 'Error: error in _prep_ecdf function'
            temp = v
            
        
        return (0, df_ecdf, 50, xaxis[int(data_length/2)], 'น้อยกว่า')
    
    def _numercial_data_distribution(self, col_name):
        """
        This function recieve a column name and output a
        dataframe of graph skewness of each numerical column in original dataframe
        """
        score = 0
        column_dis = []

        kurb = self.df[col_name].kurtosis()
        skew = self.df[col_name].skew()

        if kurb < -1.0 and skew < 0.05 and skew > -0.05:
            column_dis = 'การแจกแจงแบบยูนิฟอร์ม'

        elif kurb < 0.05 and kurb > -0.05 and skew < 0.5 and skew > -0.5:
            column_dis = 'มีการแจกแจงแบบสมมาตร'

        elif skew > 0.5 and skew < 1.0:
            if kurb > 1.0:
                column_dis = 'เบ้ขวาปานกลางโดยมีค่าสุดโต่งเป็นจำนวนมาก'
                score = 1
            elif kurb < -1.0:
                column_dis = 'เบ้ขวาปานกลางโดยมีค่าสุดโต่งเป็นจำนวนน้อย'
                score = 1
            else:
                column_dis = 'เบ้ขวาปานกลาง'
                score = 1

        elif skew < -0.5 and skew > -1.0:
            if kurb > 0.05:
                column_dis = 'เบ้ซ้ายปานกลางโดยมีค่าสุดโต่งเป็นจำนวนมาก'
                score = 1
            elif kurb < -0.05:
                column_dis = 'เบ้ซ้ายปานกลางโดยมีค่าสุดโต่งเป็นจำนวนน้อย'
                score = 1
            else:
                column_dis = 'เบ้ซ้ายปานกลาง'
                score = 1

        elif skew > 1.0:
            if kurb > 0.05:
                column_dis = 'เบ้ขวาอย่างมากโดยมีค่าสุดโต่งเป็นจำนวนมาก'
                score = 1
            elif kurb < -0.05:
                column_dis = 'เบ้ขวาอย่างมากโดยมีค่าสุดโต่งเป็นจำนวนน้อย'
                score = 1
            else:
                column_dis = 'เบ้ขวาอย่างมาก'
                score = 1

        elif skew < -1.0:
            if kurb > 1.0:
                column_dis = 'เบ้ซ้ายอย่างมากโดยมีค่าสุดโต่งเป็นจำนวนมาก'
                score = 1
            elif kurb < -1.0:
                column_dis = 'เบ้ซ้ายอย่างมากโดยมีค่าสุดโต่งเป็นจำนวนน้อย'
                score = 1
            else:
                column_dis = 'เบ้ซ้ายอย่างมาก'
                score = 1
        
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
            # arg = "fragmented data"
            arg = 'ข้อมูลแตกเป็นหลายส่วน'
            attribute = max_attribute
            value = max_value
            percent_dominate = (max_value/sum(temp_value))
            score = 1
    #         print(str(max_col)+" in "+str(col_name)+" is anomalies")

        #if overall nomal value is equal to number of attribute exclude max value then this data is perfectly balanced
        elif balanced_threshold == member-1:
            # arg = "balanced data"
            arg = 'ข้อมูลสมดุล'
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
            # return 1, "bimodal"
            return 1, 'ทวิฐานนิยม'
        elif number_of_mode == 3:
            # return 1, "trimodal"
            return 1, 'ไตรฐานนิยม'   
             
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
                            if self.target == i or self.target == r.index[index_i]:
                                #for positive correlation
                                if index_v > 0:
                                    if index_v > 0.6 and index_v < 0.8:
                                            # corr_type_mod = "moderate postive
                                            # corr_target = "correlate with target"
                                            corr_type_mod = 'เชิงบวกปานกลาง'
                                            corr_target = 'มีความสัมพันธ์กับเป้าหมาย'
                                            break

                                    elif index_v > 0.8:
                                            # corr_type_strong = "strong postive"
                                            # corr_target = "correlate with target"
                                            corr_type_mod = 'เชิงบวกอย่างมาก'
                                            corr_target = 'มีความสัมพันธ์กับเป้าหมาย'
                                            break

                                #for negative correlation
                                elif index_v < 0:
                                    if index_v < -0.6 and index_v > -0.8:
                                            # corr_type_mod = "moderate negative"
                                            # corr_target = "correlate with target"
                                            corr_type_mod = 'เชิงลบปานกลาง'
                                            corr_target = 'มีความสัมพันธ์กับเป้าหมาย'
                                            break

                                    elif index_v < -0.8:
                                            # corr_type_strong = "strong negative"
                                            # corr_target = "correlate with target"
                                            corr_type_mod = 'เชิงลบอย่างมาก'
                                            corr_target = 'มีความสัมพันธ์กับเป้าหมาย'
                                            break
                            else:
                                #for positive correlation
                                if index_v > 0:
                                    if index_v > 0.6 and index_v < 0.8:
                                            # corr_type_mod = "moderate postive"
                                            # corr_target = "correlate with each other"
                                            corr_type_mod = 'เชิงบวกปานกลาง'
                                            corr_target = 'มีความสัมพันธ์กับตัวแปรอิสระ'
                                            break

                                    elif index_v > 0.8:
                                            # corr_type_strong = "strong postive"
                                            # corr_target = "correlate with each other"
                                            corr_type_mod = 'เชิงบวกอย่างมาก'
                                            corr_target = 'มีความสัมพันธ์กับตัวแปรอิสระ'
                                            break

                                #for negative correlation
                                elif index_v < 0:
                                    if index_v < -0.6 and index_v > -0.8:
                                            # corr_type_mod = "moderate negative"
                                            # corr_target = "correlate with each other"
                                            corr_type_mod = 'เชิงลบปานกลาง'
                                            corr_target = 'มีความสัมพันธ์กับตัวแปรอิสระ'
                                            break

                                    elif index_v < -0.8:
                                            # corr_type_strong = "strong negative"
                                            # corr_target = "correlate with each other"
                                            corr_type_mod = 'เชิงลบอย่างมาก'
                                            corr_target = 'มีความสัมพันธ์กับตัวแปรอิสระ'
                                            break
                        #No target
                        else:
                            #for positive correlation
                            if index_v > 0:
                                if index_v > 0.6 and index_v < 0.8:
                                        # corr_type_mod = "moderate postive"
                                        corr_type_mod = 'เชิงบวกปานกลาง'
                                        corr_target = None
                                        break

                                elif index_v > 0.8:
                                        # corr_type_strong = "strong postive"
                                        corr_type_mod = 'เชิงบวกอย่างมาก'
                                        corr_target = None
                                        break

                            #for negative correlation
                            elif index_v < 0:
                                if index_v < -0.6 and index_v > -0.8:
                                        # corr_type_mod = "moderate negative"
                                        corr_type_mod = 'เชิงลบปานกลาง'
                                        corr_target = None
                                        break

                                elif index_v < -0.8:
                                        # corr_type_strong = "strong negative"
                                        corr_type_mod = 'เชิงลบอย่างมาก'
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
        """
        This function is use to determine the outlier of box-plot
        """
        score = 0
        argument = None
        Q1 = self.df[col].quantile(.25)
        Q3 = self.df[col].quantile(.75)
        IQR = Q3 -Q1
        data_length = len(self.df[col])
        
        _min = self.df[col].min()
        _max = self.df[col].max()
        _mean = self.df[col].mean()

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
        
        return score, exceed_lower, exceed_upper, total, percentage, argument, _min, _max, _mean

    def _label_encoder(self): 
        """
        This is function for transform category type to numerical form 
        """

        le = preprocessing.LabelEncoder()
        data_label = {}
        df_label = pd.DataFrame(data_label) 
        
        for i,v in self.data_type.iterrows():
            if v.values[1] == 'category':
                le.fit(self.df[v.values[0]])
                label_list = le.transform(self.df[v.values[0]])
                df_label[v.values[0]] = label_list
            else:
                df_label[v.values[0]] = self.df[v.values[0]]

        return df_label  

    def _chi_sq(self, col_name):
        """
        This function is use to find the chi-sq and prioritize
        """
        
        is_sig = 0

        #encoded categorical to numeric
        df_label = self._label_encoder()

        try:
            try:
                dummy_list = []
                for i in df_label[col_name].values:
                    temp_list = []
                    temp_list.append(i)
                    dummy_list.append(temp_list)

            except ValueError:
                return 'Error: incorrect column name error in _chi_sq function'

            X = dummy_list
            y = df_label[self.target].values
            
            chi_score, p_value = feature_selection.chi2(X, y)

            if p_value > 0.001 and p_value < 0.005:
                stat_sig = p_value[0]
                stat_sig_argument = "มีความสัมพันธฺระหว่างตัวแปรอย่างมาก"
                is_sig = 1

            elif p_value > 0.075 and p_value < 0.1:
                stat_sig = p_value[0]
                stat_sig_argument = "มีความสัมพันธฺระหว่างตัวแปร"
                is_sig = 1

            else:
                stat_sig = p_value[0]
                stat_sig_argument = "ไม่มีความสัมพันธ์ระหว่างตัวแปร"

            return is_sig, stat_sig, stat_sig_argument

        except:
            return 'Error: internal function error in _chi_sq function'
    
    def _anova_ttest(self, col):
        '''
        This function is use to test statistic hypothesis of indepedent category variable and dependent continuous variable
        when data is normally distributed
        '''
        is_sig = 0
        stat_sig = 0
        stat_sig_argument = ""
        
        #encoded categorical to numeric
        df_label = self._label_encoder()

        try:
            dummy_list = []
            for i in df_label[col].values:
                temp_list = []
                temp_list.append(i)
                dummy_list.append(temp_list)

        except ValueError:
            return 'Error: incorrect column name error in _anova_ttest function'

        X = dummy_list
        y = df_label[self.target].values

        try:
            if len(self.df[col].unique()) > 2:
                f_score, p_value = feature_selection.f_oneway(X, y)
                
                if p_value <= 0.05:
                    stat_sig = p_value[0]
                    stat_sig_argument = "ข้อมูล {0} ส่งผลต่อเป้าหมาย {1} อย่างมากโดยมีค่าเฉลี่ยแตกต่างกันระหว่างกลุ่มข้อมูล".format(col, self.target)
                    is_sig = 1

                elif p_value > 0.05 and p_value < 0.1:
                    stat_sig = p_value[0]
                    
                    stat_sig_argument =  "ข้อมูล {0} ส่งผลต่อเป้าหมาย {1} โดยมีค่าเฉลี่ยแตกต่างกันระหว่างกลุ่มข้อมูล".format(col, self.target)
                    is_sig = 1

                else:
                    stat_sig = p_value[0]
                    stat_sig_argument =  "ข้อมูล {0} ไม่ส่งผลต่อเป้าหมาย {1}".format(col, self.target)
                    
                return is_sig, stat_sig, stat_sig_argument, 'anova'

            elif len(self.df[col].unique()) == 2:
                u_score, p_value = stats.ttest_ind(X,y)

                if p_value <= 0.05:
                    stat_sig = p_value[0]
                    stat_sig_argument = "ข้อมูล {0} ส่งผลต่อเป้าหมาย {1} อย่างมากโดยมีค่าเฉลี่ยแตกต่างกันระหว่างกลุ่มข้อมูล".format(col, self.target)
                    is_sig = 1

                elif p_value > 0.05 and p_value < 0.1:
                    stat_sig = p_value[0]
                    
                    stat_sig_argument =  "ข้อมูล {0} ส่งผลต่อเป้าหมาย {1} โดยมีค่าเฉลี่ยแตกต่างกันระหว่างกลุ่มข้อมูล".format(col, self.target)
                    is_sig = 1
                else:
                    stat_sig = p_value[0]
                    stat_sig_argument =  "ข้อมูล {0} ไม่ส่งผลต่อเป้าหมาย {1}".format(col, self.target)
                    
                return is_sig, stat_sig, stat_sig_argument, 't-test'

            else:
                return None, None, None, None

        except:
            return 'Error: internal function error in _anova_ttest function'

    def _kruskal_u_test(self, col):
        '''
        This function is use to test statistic hypothesis of indepedent category variable and dependent continuous variable 
        when data is not normally distributed
        '''
        is_sig = 0
        stat_sig = 0
        stat_sig_argument = ""
        
        #encoded categorical to numeric
        df_label = self._label_encoder()

        try:
            dummy_list = []
            for i in df_label[col].values:
                temp_list = []
                temp_list.append(i)
                dummy_list.append(temp_list)

        except ValueError:
            return 'Error: incorrect column name error in _kruskal_u_test function'

        X = dummy_list
        y = df_label[self.target].values

        try:
            if len(self.df[col].unique()) > 2:
                h_score, p_value = stats.kruskal(X, y)
                
                if p_value <= 0.05:
                    stat_sig = p_value[0]
                    stat_sig_argument = "ข้อมูล {0} ส่งผลต่อเป้าหมาย {1} อย่างมากโดยมีค่ามัธยฐานแตกต่างกันระหว่างกลุ่มข้อมูล".format(col, self.target)
                    is_sig = 1

                elif p_value > 0.05 and p_value < 0.1:
                    stat_sig = p_value[0]
                    
                    stat_sig_argument =  "ข้อมูล {0} ส่งผลต่อเป้าหมาย {1} โดยมีค่ามัธยฐานแตกต่างกันระหว่างกลุ่มข้อมูล".format(col, self.target)
                    is_sig = 1
                else:
                    stat_sig = p_value[0]
                    stat_sig_argument =  "ข้อมูล {0} ไม่ส่งผลต่อเป้าหมาย {1}".format(col, self.target)
                    
                return is_sig, stat_sig, stat_sig_argument, 'kruskal'

            elif len(self.df[col].unique()) == 2:
                h_score, p_value = stats.mannwhitneyu(X,y)

                if p_value <= 0.05:
                    stat_sig = p_value[0]
                    stat_sig_argument = "ข้อมูล {0} ส่งผลต่อเป้าหมาย {1} อย่างมากโดยมีค่ามัธยฐานแตกต่างกันระหว่างกลุ่มข้อมูล".format(col, self.target)
                    is_sig = 1

                elif p_value > 0.05 and p_value < 0.1:
                    stat_sig = p_value[0]
                    
                    stat_sig_argument =  "ข้อมูล {0} ส่งผลต่อเป้าหมาย {1} โดยมีค่ามัธยฐานแตกต่างกันระหว่างกลุ่มข้อมูล".format(col, self.target)
                    is_sig = 1
                else:
                    stat_sig = p_value[0]
                    stat_sig_argument =  "ข้อมูล {0} ไม่ส่งผลต่อเป้าหมาย {1}".format(col, self.target)
                    
                return is_sig, stat_sig, stat_sig_argument, 'u-test'

            else:
                return None, None, None, None

        except:
            return 'Error: internal function error in _kruskal_u_test function'


    def _f_regression_sign(self, col):
        '''
        This function is use to test statistic hypothesis of indepedent category variable and dependent continuous variable
        '''
        is_sig = 0
        stat_sig = 0
        stat_sig_argument = ""

        try:
            dummy_list = []
            for i in self.df[col].values:
                temp_list = []
                temp_list.append(i)
                dummy_list.append(temp_list)

        except ValueError:
            return 'Error: incorrect column name error in _f_regression_sign function'

        X = dummy_list
        y = self.df[self.target].values

        try:
            if (self._numercial_data_distribution(col)[1] == 'มีการแจกแจงแบบสมมาตร' and
            self._numercial_data_distribution(self.target)[1] == 'มีการแจกแจงแบบสมมาตร') or (len(self.df[col]) >= 30 and len(self.df[self.target]) >= 30):
                f_score, p_value = feature_selection.f_regression(X, y)
                
                if p_value <= 0.05:
                    stat_sig = p_value[0]
                    stat_sig_argument = "ข้อมูล {0} มีความแตกต่างของความแปรปรวนกับเป้าหมาย {1} อย่างชัดเจน".format(col, self.target)
                    is_sig = 1

                elif p_value > 0.05 and p_value < 0.1:
                    stat_sig = p_value[0]
                    stat_sig_argument =  "ข้อมูล {0} มีความแตกต่างของความแปรปรวนกับเป้าหมาย {1}".format(col, self.target)
                    is_sig = 1

                else:
                    stat_sig = p_value[0]
                    stat_sig_argument =  "ข้อมูล {0} ไม่มีความแตกต่างของความแปรปรวนกับเป้าหมาย {1}".format(col, self.target)
                    
                return is_sig, stat_sig, stat_sig_argument, 'f-test'

            else:
                sign_score, p_value = stats.wilcoxon(X, y) 

                if p_value <= 0.05:
                    stat_sig = p_value[0]
                    stat_sig_argument = "ข้อมูล {0} มีความแตกต่างของความมัธยฐานกับเป้าหมาย {1} อย่างชัดเจน".format(col, self.target)
                    is_sig = 1

                elif p_value > 0.05 and p_value < 0.1:
                    stat_sig = p_value[0]
                    stat_sig_argument =  "ข้อมูล {0} มีความแตกต่างของความมัธยฐานกับเป้าหมาย {1}".format(col, self.target)
                    is_sig = 1

                else:
                    stat_sig = p_value[0]
                    stat_sig_argument =  "ข้อมูล {0} ไม่มีความแตกต่างของความมัธยฐานกับเป้าหมาย {1}".format(col, self.target)
                    
                return is_sig, stat_sig, stat_sig_argument, 'sign test'
            
            return None, None, None, None

        except:
            return 'Error: internal function error in _f_regression_sign function'

    def _target_mutual(self, col):
        """
        This function is use to find the correlation of target and each feature 
        """
        is_sig = 0
        stat_sig = 0
        stat_arg = ''
        
        #encoded categorical to numeric
        df_label = self._label_encoder()
        try:
            if self.data_type[self.data_type['col_name'] == self.target]['col_type'].values[0] == 'category':
                try:
                    dummy_list = []
                    for i in df_label[col].values:
                        temp_list = []
                        temp_list.append(i)
                        dummy_list.append(temp_list)
                                    
                except ValueError:
                    return 'Error: incorrect column name'

                X = dummy_list
                y = df_label[self.target].values
                mutual = feature_selection.mutual_info_classif(X, y, discrete_features='auto')
                if mutual > 0:
                    is_sig = 1
                    stat_sig = mutual[0]
                    stat_arg = 'สามารถบ่งบอกข้อมูลของเป้าหมายได้'
                else: 
                    stat_sig = mutual[0]
                    stat_arg = 'ไม่สามารถบ่งบอกข้อมูลของเป้าหมายได้'

            elif self.data_type[self.data_type['col_name'] == self.target]['col_type'].values[0] == 'numeric':
                dummy_list = []
                for i in df_label[col].values:
                    temp_list = []
                    temp_list.append(i)
                    dummy_list.append(temp_list)
                X = dummy_list
                y = df_label[self.target].values
                mutual = feature_selection.mutual_info_regression(X, y, discrete_features=False)
                if mutual > 0:
                    is_sig = 1
                    stat_sig = mutual[0]
                    stat_arg = 'สามารถบ่งบอกข้อมูลของเป้าหมายได้'
                else: 
                    stat_sig = mutual[0]
                    stat_arg = 'ไม่สามารถบ่งบอกข้อมูลของเป้าหมายได้'
                    
            return is_sig, stat_sig, stat_arg

        except:
            return 'Error: internal function error in target_mutual function'

    def _numerical_test(self, col, g_type):
        if g_type == 'ecdf':
            res_ecdf =  self._prep_ecdf(col)
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
                return col, res_box[1:9]

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

    def _numerical_test_target(self, col, g_type):
        if g_type == 'ecdf':
            res_ecdf =  self._prep_ecdf(col)
            score = res_ecdf[0]
            if score == 1:
                return col, res_ecdf[2:5]
                
        elif g_type == 'histogram':
            score_his, dis_type = self._numercial_data_distribution(col)
            score_multi, mode_type = self._find_multimodal(col)
            score = score_his+score_multi  
            res_mutual = self._target_mutual(col)
            score_mutual = res_mutual[0]   
            res_f_sign = self._f_regression_sign(col)
            stat_test_used = res_f_sign[-1]
            stat_sig = res_f_sign[0] + res_mutual[0]  
            if stat_sig >= 1 and score >= 1:
                priority = 3 
                return col, dis_type, mode_type, res_f_sign[1:3], priority, stat_test_used, res_mutual[1:3]

            elif stat_sig == 0 and score >= 1:
                priority = 2 
                return col, dis_type, mode_type, res_f_sign[1:3], priority, stat_test_used, res_mutual[1:3]
            
            elif stat_sig >= 1 and score == 0:
                priority = 1 
                return col, dis_type, mode_type, res_f_sign[1:3], priority, stat_test_used, res_mutual[1:3]

        elif g_type == 'box':
            res_box = self._find_outlier_box(col)
            score = res_box[0]
            if score >= 1:
                return col, res_box[1:9]

        return None

    def _num_num_test_target(self, col_1, col_2, g_type):
        if g_type == 'scatter':

            if (self._numercial_data_distribution(col_1)[1] == 'มีการแจกแจงแบบสมมาตร' and
            self._numercial_data_distribution(col_2)[1] == 'มีการแจกแจงแบบสมมาตร') or (len(self.df[col_1]) >= 30 and len(self.df[col_2]) >= 30):
                df_corr = self.df.corr(method ='pearson')
                score, corr_type, corr_target = self._find_corr(df_corr, col_1, col_2) 
                corr_method = 'pearson'
                if score >= 1:
                    return col_1, col_2, corr_type, corr_target, corr_method

            else:
                df_corr = self.df.corr(method ='spearman')
                score, corr_type, corr_target = self._find_corr(df_corr, col_1, col_2)
                corr_method = 'spearman'
                if score >= 1:
                    return col_1, col_2, corr_type, corr_target, corr_method

    def _categorical_test_target(self, col, g_type):
        if g_type == "bar":
            res_ratio = self._data_ratio(col)
            res_mutual = self._target_mutual(col)
            score_mutual = res_mutual[0]
            score = res_ratio[0]

            if self.data_type[self.data_type['col_name'] == self.target]['col_type'].values[0] == 'category':
                res_stat_chi = self._chi_sq(col)
                stat_test_used = 'chi-square'
                stat_sig = res_stat_chi[0] + score_mutual
    #         score_ratio, arg, attribute, value, percent_dominate = self._data_ratio(col)
                if stat_sig >= 1 and score == 1:
                    priority = 3 
                    return col, res_ratio[1:5], res_stat_chi[1:3], priority, stat_test_used, res_mutual[1:3]

                elif stat_sig == 0 and score == 1:
                    priority = 2 
                    return col, res_ratio[1:5], res_stat_chi[1:3], priority, stat_test_used, res_mutual[1:3]
                
                elif stat_sig >= 1 and score == 0:
                    priority = 1 
                    return col, res_ratio[1:5], res_stat_chi[1:3], priority, stat_test_used, res_mutual[1:3]

            elif self.data_type[self.data_type['col_name'] == self.target]['col_type'].values[0] == 'numeric':
                if self._numercial_data_distribution(self.target)[1] == 'มีการแจกแจงแบบสมมาตร' or len(self.df[self.target]) >= 30:
                    res_stat_cat_normal = self._anova_ttest(col)
                    stat_test_used = res_stat_cat_normal[-1]
                    stat_sig = res_stat_cat_normal[0] + score_mutual

                    if stat_sig >= 1 and score == 1:
                        priority = 3 
                        return col, res_ratio[1:5], res_stat_cat_normal[1:3], priority, stat_test_used, res_mutual[1:3]

                    elif stat_sig == 0 and score == 1:
                        priority = 2 
                        return col, res_ratio[1:5], res_stat_cat_normal[1:3], priority, stat_test_used, res_mutual[1:3]
                    
                    elif stat_sig >= 1 and score == 0:
                        priority = 1 
                        return col, res_ratio[1:5], res_stat_cat_normal[1:3], priority, stat_test_used, res_mutual[1:3]

                else:
                    res_stat_kruskal = self._kruskal_u_test(col)
                    stat_test_used = res_stat_kruskal[-1]
                    stat_sig = res_stat_kruskal[0] + score_mutual

                    if stat_sig >= 1 and score == 1:
                        priority = 3 
                        return col, res_ratio[1:5], res_stat_kruskal[1:3], priority, stat_test_used, res_mutual[1:3]

                    elif stat_sig == 0 and score == 1:
                        priority = 2 
                        return col, res_ratio[1:5], res_stat_kruskal[1:3], priority, stat_test_used, res_mutual[1:3]
                    
                    elif stat_sig >= 1 and score == 0:
                        priority = 1 
                        return col, res_ratio[1:5], res_stat_kruskal[1:3], priority, stat_test_used, res_mutual[1:3]
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
        col_name, argument, value, p_value, stat_arg, priority, stat_test_used = ([] for i in range(7))

        #ecdf_graph
        break_percent = []
        
        #box
        exceed_lower, exceed_upper, total, outlier_percent, box_min, box_max, box_mean = ([] for i in range(7))

        #bar
        anomal_attribute = []
        percent_dominate = []
        mutual = []
        stat_arg_mutual = []

        #scatter 
        col_1_name, col_2_name, corr_type, corr_target, corr_method = ([] for i in range(5))
        
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

        switcher_target = {
            'numeric': self._numerical_test_target,
            'category': self._categorical_test_target,
            ('numeric','numeric'): self._num_num_test_target,
            ('numeric','category'): self._num_cat_test,
            ('category','numeric'): self._num_cat_test,
            ('category','category'): self._cat_cat_test,
        }
        
        # if self.target != None:
        #     mutual xxx
        #     res_mutual = mutual xxx
        #     #append res_mutual
        #     #increase priority of grpah by mutual info
        #     #end

        if self.target != None:
            # self.data_type[self.data_type['col_name'] == self.target]['col_type'].values[0] != 'ordinal' and 'unique':
            if g_type in single_col:
                for i,r in df_type_filter.iterrows():
                    func_single = switcher_target.get(r.values[1], lambda: "Error: Invalid column type presented")
                    result_single = func_single(r.values[0], g_type)
                    if result_single != None:
                        if g_type == "histogram":
                            col_name.append(result_single[0])
                            dis_type.append(result_single[1])
                            mode_type.append(result_single[2])
                            p_value.append(result_single[3][0])
                            stat_arg.append(result_single[3][1])
                            priority.append(result_single[4])
                            stat_test_used.append(result_single[5])
                            mutual.append(result_single[6][0])
                            stat_arg_mutual.append(result_single[6][1])

                            data_return = {'col_name':col_name, 'dis_type':dis_type, 'mode_type': mode_type,
                            'p_value': p_value, 'stat_arg': stat_arg, 'priority': priority, 'stat_test_used': stat_test_used,
                            'mutual': mutual, 'stat_arg_mutual': stat_arg_mutual}
                            df_return = pd.DataFrame(data_return)
                            df_return = df_return [df_return['col_name'] != self.target]
                                
                        elif g_type == "ecdf":
                            col_name.append(result_single[0])
                            break_percent.append(result_single[1][0])
                            value.append(result_single[1][1])
                            argument.append(result_single[1][2])
                            data_return = {'col_name':col_name, 'break_percent':break_percent, 'value': value, 'argument': argument}
                            df_return = pd.DataFrame(data_return)
                            
                        elif g_type == "bar":
                            if self.data_type[self.data_type['col_name'] == self.target]['col_type'].values[0] == 'category':
                                col_name.append(result_single[0])
                                argument.append(result_single[1][0])
                                anomal_attribute.append(result_single[1][1])
                                value.append(result_single[1][2])
                                percent_dominate.append(result_single[1][3]) 
                                p_value.append(result_single[2][0])
                                stat_arg.append(result_single[2][1])
                                priority.append(result_single[3])
                                stat_test_used.append(result_single[4])
                                mutual.append(result_single[5][0])
                                stat_arg_mutual.append(result_single[5][1])

                                data_return = {'col_name':col_name, 'argument':argument, 'anomal_attribute': anomal_attribute,
                                            'anomal_value': value, 'percent_dominate': percent_dominate, 'p_value': p_value,
                                            'stat_arg': stat_arg, 'priority': priority, 'stat_test_used': stat_test_used,
                                            'mutual': mutual, 'stat_arg_mutual': stat_arg_mutual}
                                df_return = pd.DataFrame(data_return)
                                df_return = df_return[df_return['col_name'] != self.target]

                            elif self.data_type[self.data_type['col_name'] == self.target]['col_type'].values[0] == 'numeric':
                                col_name.append(result_single[0])
                                argument.append(result_single[1][0])
                                anomal_attribute.append(result_single[1][1])
                                value.append(result_single[1][2])
                                percent_dominate.append(result_single[1][3]) 
                                p_value.append(result_single[2][0])
                                stat_arg.append(result_single[2][1])
                                priority.append(result_single[3])
                                stat_test_used.append(result_single[4])
                                mutual.append(result_single[5][0])
                                stat_arg_mutual.append(result_single[5][1])

                                data_return = {'col_name':col_name, 'argument':argument, 'anomal_attribute': anomal_attribute,
                                            'anomal_value': value, 'percent_dominate': percent_dominate, 'p_value': p_value,
                                            'stat_arg': stat_arg, 'priority': priority, 'stat_test_used': stat_test_used,
                                            'mutual': mutual, 'stat_arg_mutual': stat_arg_mutual}
                                df_return = pd.DataFrame(data_return)
                                df_return = df_return[df_return['col_name'] != self.target]
                        
                        elif g_type == "box":
                            col_name.append(result_single[0])
                            exceed_lower.append(result_single[1][0])
                            exceed_upper.append(result_single[1][1])
                            total.append(result_single[1][2])
                            outlier_percent.append(result_single[1][3])
                            argument.append(result_single[1][4])
                            box_min.append(result_single[1][5])
                            box_max.append(result_single[1][6])
                            box_mean.append(result_single[1][7])

                            data_return = {'col_name':col_name, 'exceed_lower':exceed_lower, 'exceed_upper': exceed_upper,
                                        'total': total, 'outlier_percent': outlier_percent, 'argument': argument, 
                                        'min': box_min, 'max': box_max, 'mean': box_mean}
                            df_return = pd.DataFrame(data_return)


            elif g_type in double_col:
                for i,r in df_combine_filter.iterrows():
                    func_double = switcher_target.get((r.values[2],r.values[3]), lambda: "Error: Invalid column type presented")
                    result_double = func_double(r.values[0], r.values[1], g_type)
                    if result_double != None:
                        if g_type == "scatter":
                            col_1_name.append(result_double[0])
                            col_2_name.append(result_double[1])
                            corr_type.append(result_double[2])
                            corr_target.append(result_double[3])
                            corr_method.append(result_double[4])
                            data_return = {'col_1_name':col_1_name, 'col_2_name':col_2_name, 'corr_type': corr_type, 'corr_target': corr_target, 'corr_method': corr_method}
                            df_return = pd.DataFrame(data_return)

        else:
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
                            box_min.append(result_single[1][5])
                            box_max.append(result_single[1][6])
                            box_mean.append(result_single[1][7])
                            data_return = {'col_name':col_name, 'exceed_lower':exceed_lower, 'exceed_upper': exceed_upper,
                                        'total': total, 'outlier_percent': outlier_percent, 'argument': argument, 
                                        'min': box_min, 'max': box_max, 'mean': box_mean}
                            df_return = pd.DataFrame(data_return)


            elif g_type in double_col:
                for i,r in df_combine_filter.iterrows():
                    func_double = switcher.get((r.values[2],r.values[3]), lambda: "Error: Invalid column type presented")
                    result_double = func_double(r.values[0], r.values[1], g_type)
                    if result_double != None:
                        if g_type == "scatter":
                            col_1_name.append(result_double[0])
                            col_2_name.append(result_double[1])
                            corr_type.append(result_double[2])
                            corr_target.append(result_double[3])
                            data_return = {'col_1_name':col_1_name, 'col_2_name':col_2_name, 'corr_type': corr_type, 'corr_target': corr_target}
                            df_return = pd.DataFrame(data_return)
                                  
        return df_return

