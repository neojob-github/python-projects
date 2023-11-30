import numpy as np
import pandas as pd


df = pd.read_csv("real_estate_data.csv", sep="\t")
# Fill nans to value=0 and confirms it in main dataframe with inplace=True
df["parks_nearest"].fillna(value=0, inplace=True)
print(df.head(15))