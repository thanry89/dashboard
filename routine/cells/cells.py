from functions import prep_data
import pickle
import pandas as pd
import os

# Prepare Data
[data_3g_actual, data_lte_actual] = prep_data()

file_path = os.getcwd().replace('routine/cells','') + 'data/cells.pkl'

# Unir Data
with open(file_path, 'rb') as file:
    [data_3g_previo, data_lte_previo] = pickle.load(file)

data_3g = pd.concat([data_3g_previo, data_3g_actual]).drop_duplicates().reset_index(drop=True)
data_lte = pd.concat([data_lte_previo, data_lte_actual]).drop_duplicates().reset_index(drop=True)

# Save data
with open(file_path,'wb') as file:
    pickle.dump([data_3g, data_lte], file)
