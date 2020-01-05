import pandas as pd
import numpy as np

def prep_ecdf(data):
    ''' function to plot ecdf taking a column of data as input
    and return axis & yaxis for ploting graph. Also return percentage & 
    value of data & argument for use in NLG and
    score for selecting graph
    Recommended graph label: title = "ECDF Plot", xlabel = 'Data Values', ylabel = 'Percentage'
    '''
    
    temp = 0
    data_length = len(data)
    xaxis = np.sort(data)
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