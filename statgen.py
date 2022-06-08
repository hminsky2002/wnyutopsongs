import pandas as pd

df = pd.read_csv('2022-05-15_to_2022-05-21.csv')
df = df.apply(lambda x: x.astype(str).str.lower())
df2 = df.iloc[: , 1:]
df2 =  df2.apply(lambda x: x.astype(str).str.lower())

df2 = df2[df2['title'].duplicated()]
listy = df2['title'].astype(str).tolist()
print(df2)
