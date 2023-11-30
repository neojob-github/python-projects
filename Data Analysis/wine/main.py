import numpy as np
import pandas as pd

# Сброс ограничений на количество выводимых рядов
pd.set_option('display.max_rows', None)
 
# Сброс ограничений на число столбцов
pd.set_option('display.max_columns', None)
 
# Сброс ограничений на количество символов в записи
'''pd.set_option('display.max_colwidth', None)'''

# Получаем размеры датафрейма
def get_size(df : pd.DataFrame):
    return df.size

# Получаем все np.nan
def get_nans(df : pd.DataFrame):
    return df.size - df[df.isna().any(axis=1)].size

# Получаем все типы data в dataframe
def get_types(df : pd.DataFrame):
    return df.dtypes

# Получаем best province с ее средним рейтингом
def best_province(df : pd.DataFrame):
    uniq = df["province"].unique()
    best_raiting = 0
    best_province = np.float64()
    for province in uniq:
        province_mean_raiting = df[df.province == province]["points"].mean()
        if best_raiting < province_mean_raiting:
            best_raiting = province_mean_raiting
            best_province = province
    return best_province, province_mean_raiting

# Исходя из словаря присваиваем значения в новый столбец dataframe
def wine_colorize(df : pd.DataFrame, wine_colors : dict):
    color_df = pd.DataFrame({"variety" : [i for i in wine_colors.keys()], "color" : [i for i in wine_colors.values()]})
    return pd.DataFrame.merge(df, color_df)

# Работа с вином разных типов
def red_white(df : pd.DataFrame):
    uniq = sorted(df["country"].unique())
    for country in uniq:
        red = df[df.country == country]["color"].value_counts().get("red")
        white = df[df.country == country]["color"].value_counts().get("white")
        print(country, red, white)
    pass

color = {
"Chardonnay": "white",
"Pinot Noir": "red",
"Cabernet Sauvignon": "red",
"Red Blend": "red",
"Bordeaux-style Red Blend": "red",
"Sauvignon Blanc": "white",
"Syrah": "red",
"Riesling": "white",
"Merlot": "red",
"Zinfandel": "red",
"Sangiovese": "red",
"Malbec": "red",
"White Blend": "white",
"Rosé": "other",
"Tempranillo": "red",
"Nebbiolo": "red",
"Portuguese Red": "red",
"Sparkling Blend": "other",
"Shiraz": "red",
"Corvina, Rondinella, Molinara": "red",
"Rhône-style Red Blend": "red",
"Barbera": "red",
"Pinot Gris": "white",
"Viognier": "white",
"Bordeaux-style White Blend": "white",
"Champagne Blend": "other",
"Port": "red",
"Grüner Veltliner": "white",
"Gewürztraminer": "white",
"Portuguese White": "white",
"Petite Sirah": "red",
"Carmenère": "red"
}

df = pd.read_csv("wine_reviews.csv")
dataframe_size = get_size(df)
dataframe_nulls = get_nans(df)
df_all_types = get_types(df)
df_best_province, df_bp_mean = best_province(df)
df_colored_wines = wine_colorize(df, color)
df_pieces = red_white(df_colored_wines)
print(df_colored_wines["designation"].isna().value_counts())
print(df_best_province)
