import pandas as pd
import numpy as np

def prep_ecdf(data):
    ''' function to plot ecdf taking a column of data as input
    and return axis & yaxis for ploting graph. Also return percentage & 
    value of data & argument for use in NLG and score 
    that use for selecting graph
    Recommended graph label: title = "ECDF Plot", xlabel = 'Data Values', ylabel = 'Percentage'
    '''
    
    temp = 0
    data_length = len(data)
    xaxis = np.sort(data)
    yaxis = np.arange(1, data_length+1)/data_length
    
    for i,v in enumerate(xaxis):
        if i > 0:
            if v/temp > 1.5:
                if i < data_length/2:
                    return (1, xaxis, yaxis, (i/data_length)*100, v, 'less_than')
                else:
                     return (1, xaxis, yaxis, (1-i/data_length)*100, v, 'more_than')
        temp = v
    
    return (0, xaxis, yaxis, 50, xaxis[int(data_length/2)], 'less_than')