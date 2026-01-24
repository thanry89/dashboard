from functions import prep_data
import pickle
import os

# Prepare Data
[data_3g, data_lte] = prep_data()

# Save data

file_path = os.getcwd().replace('routine\\cells','') + 'data\\cells.pkl'

with open(file_path,'wb') as file:
    pickle.dump([data_3g, data_lte], file)
