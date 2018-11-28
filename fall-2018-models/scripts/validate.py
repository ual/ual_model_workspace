import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from urbansim_templates.models import SmallMultinomialLogitStep
import orca
from collections import OrderedDict

def get_predicted_choices(model_obj):
    if model_obj.probabilities is None:
        return 'The model needs to be run first!'
    
    predicted_choices = model_obj.probabilities[
    model_obj.probabilities.groupby(['_obs_id'])['_probability'].transform('max') ==  model_obj.probabilities['_probability']
]['_alt_id'].reset_index(drop=True)
    
    return predicted_choices.rename('predicted')

def tp_rates(model_obj):
    '''
    This returns a list of true-positive rates of the model.
    '''
    if model_obj.probabilities is None:
        return 'The model needs to be run first!'
    
    N = len(model_obj.choices)
    predicted_choices = get_predicted_choices(model_obj)
    
    crosstab = pd.crosstab(model_obj.choices, predicted_choices)
    rowsum = crosstab.sum(axis = 1)
    
    mutual_choices = set(crosstab.index.values) & set(crosstab.columns.values)
    all_choices = set(crosstab.index.values) | set(crosstab.columns.values)
    
    tp_rate_all = sum([crosstab.at[c,c] for c in mutual_choices]) / N
    tp_rate_table = pd.DataFrame(columns = all_choices, index = ['True Positive rate'])
    for c in all_choices:
        if c not in mutual_choices:
            tp_rate_table.iloc[0,c] = 0
        else:
            tp_rate_table.iloc[0,c] = crosstab.at[c,c] / rowsum.at[c]
    tp_rate_table['all'] = tp_rate_all
    
    return tp_rate_table

def model_crosstab(model_obj):
    if model_obj.probabilities is None:
        return 'The model needs to be run first!'

    crosstab = pd.crosstab(model_obj.choices.rename('observed'), get_predicted_choices(model_obj), normalize = 'index')
    return crosstab
